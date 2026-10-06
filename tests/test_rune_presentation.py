from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree
import pandas as pd
import pytest
import streamlit as st
from sqlalchemy import text
from streamlit.testing.v1 import AppTest
from fonctions.history import deduplicate_scores
from fonctions.import_service import analyse_export, validate_export, persist_analysis, publish_analysis
from fonctions.rune_visual import rune_svg, rune_label, stat_text

ROOT = Path(__file__).resolve().parents[1]


def test_deduplicate_only_matching_account_day_and_all_four_scores(engine, export):
    result = analyse_export(validate_export(export), pd.DataFrame())
    metadata, _ = persist_analysis(result, '06/10/2026')
    uid = metadata['id_joueur']
    with engine.begin() as conn:
        original = dict(conn.execute(text('SELECT * FROM sw_score')).mappings().one())
        rows = [original.copy(), original.copy()]
        for field in ['score_general', 'score_spd', 'score_arte', 'score_qual']:
            changed = original.copy(); changed[field] += 1; rows.append(changed)
        other_day = original.copy(); other_day['date'] = '05/10/2026'; rows.append(other_day)
        other_user = original.copy(); other_user['id_joueur'] = 999; rows.extend([other_user, other_user])
        pd.DataFrame(rows).to_sql('sw_score', conn, index=False, if_exists='append')
        snapshots = conn.execute(text('SELECT COUNT(*) FROM sw_rune_snapshots')).scalar_one()
    assert deduplicate_scores(uid) == 2
    assert deduplicate_scores(uid) == 0
    with engine.connect() as conn:
        assert conn.execute(text('SELECT COUNT(*) FROM sw_score WHERE id_joueur=:id'), {'id': uid}).scalar_one() == 6
        assert conn.execute(text('SELECT COUNT(*) FROM sw_score WHERE id_joueur=999')).scalar_one() == 2
        assert conn.execute(text('SELECT COUNT(*) FROM sw_rune_snapshots')).scalar_one() == snapshots
    from fonctions.access import AccessDenied
    with pytest.raises(AccessDenied):
        deduplicate_scores(999)


@pytest.mark.parametrize('language', ['Français', 'English'])
def test_visual_has_real_stats_units_grinds_and_escaped_owner(export, language):
    st.session_state['translations_selected'] = language
    runes = analyse_export(validate_export(export), pd.DataFrame())['data_rune']
    runes.data['rune_equiped'] = runes.data.rune_equiped.astype(object)
    runes.data.loc[301, 'rune_equiped'] = '<script>alert(1)</script> & Leo'
    svg = rune_svg(runes, 301)
    doc = ElementTree.fromstring(svg)
    visible = ' '.join(doc.itertext())
    assert '+160' in visible and '+15%' in visible and 'SPD +34' in visible
    assert '+4' in visible  # grind is included in 34, not added twice
    assert '<script>' not in svg and '&lt;script&gt;' in svg
    assert all('script' not in child.tag for child in doc.iter())
    assert stat_text(runes, 9, 12).endswith('+12%')
    assert stat_text(runes, 8, 22) == 'SPD +22'
    assert '#301' not in rune_label(runes, 301)


@pytest.mark.parametrize('language', ['Français', 'English'])
def test_build_images_task_identity_and_removed_accuracy(engine, export, monkeypatch, language):
    monkeypatch.chdir(ROOT)
    monkeypatch.delenv('API_SQL', raising=False)
    equipped = export['runes'][:6]
    export['runes'] = export['runes'][6:]
    for rune in equipped: rune['occupied_id'] = 987
    export['unit_list'] = [dict(unit_id=987, unit_master_id=123, runes=equipped, artifacts=[])]
    reference = pd.DataFrame([dict(com2us_id=123, name='Leo')])
    result = analyse_export(validate_export(export), reference)
    metadata, _ = persist_analysis(result, '06/10/2026')
    with engine.begin() as conn:
        conn.execute(text('CREATE TABLE sw_build (id_build INTEGER PRIMARY KEY,id BIGINT,monstre TEXT,nom_build TEXT,' + ','.join(f'rune{i} BIGINT' for i in range(1,7)) + ')'))
    state = {}; publish_analysis(state, result, metadata)
    app = AppTest.from_file(str(ROOT/'scoring_runage.py'), default_timeout=30)
    for key,value in state.items(): app.session_state[key] = value
    app.session_state['translations_selected'] = language
    app.session_state['plan_accuracy'] = 300  # retired preferences must not affect search
    app.run().switch_page('pages_streamlit/planning.py').run()
    assert not app.exception
    assert not any(widget.key == 'plan_accuracy' for widget in app.number_input)
    assert any('Leo' in label and 'Slot 1' in label for label in app.multiselect(key='locks_runes').options)
    next(b for b in app.button if b.label in ('Rechercher le build', 'Search build')).click().run()
    assert not app.exception and any('SPD +' in s.value for s in app.success)
    app.switch_page('pages_streamlit/build_manager.py').run()
    assert not app.exception
    assert len(app.image) >= 6
    assert [app.selectbox(key=f'build_manager_slot_{slot}').value for slot in range(1,7)] == [r['rune_id'] for r in equipped]
    app.switch_page('pages_streamlit/todolist.py').run()
    assert not app.exception
    shown = app.dataframe[0].value
    assert 'main_stat' in shown and 'substats' in shown
    assert shown.loc[301, 'rune_equiped'] == 'Leo'
    assert 'SPD +34' in shown.loc[301, 'substats']
