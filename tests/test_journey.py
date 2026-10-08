from copy import deepcopy
from pathlib import Path
import pandas as pd
import pytest
from sqlalchemy import text
from streamlit.testing.v1 import AppTest
from fonctions.import_service import analyse_export, validate_export, persist_analysis, publish_analysis
from fonctions.journey import period_rows, deletion_preview
from fonctions.tasks import load_tasks, save_tasks

ROOT=Path(__file__).resolve().parents[1]


def imported(export):
    return analyse_export(validate_export(export),pd.DataFrame())


def seeded(engine,export,monkeypatch,language='Français'):
    monkeypatch.chdir(ROOT)
    result=imported(export)
    metadata,_=persist_analysis(result,'06/10/2026')
    state={};publish_analysis(state,result,metadata)
    at=AppTest.from_file(str(ROOT/'scoring_runage.py'),default_timeout=30)
    for key,value in state.items():at.session_state[key]=value
    at.session_state['translations_selected']=language
    return at.run(),metadata['id_joueur']


def test_import_summary_compares_before_replacing_day(engine,export):
    result=imported(export)
    meta,_=persist_analysis(result,'06/10/2026')
    assert result['import_summary']['previous_date'] is None
    original=result['import_summary']['scores'].copy()
    extra=deepcopy(export['runes'][0]);extra['rune_id']=9999999
    export['runes'].append(extra)
    changed=imported(export)
    persist_analysis(changed,'06/10/2026')
    summary=changed['import_summary']
    assert summary['previous_date']=='06/10/2026'
    assert summary['changes']['added']==1
    assert summary['deltas']=={key:value-original[key] for key,value in summary['scores'].items()}
    assert not persist_analysis(changed,'07/10/2026')[1]
    assert set(changed['import_summary']['deltas'].values())=={0}
    assert set(changed['import_summary']['changes'].values())=={0}
    with engine.begin() as conn:
        conn.execute(text("UPDATE sw_imports SET scoring_version='old'"))
    persist_analysis(changed,'07/10/2026')
    assert changed['import_summary']['deltas']=={}
    assert changed['import_summary']['changes'] is None


def test_import_summary_never_uses_another_account(engine,export,monkeypatch):
    from fonctions import access
    monkeypatch.setattr(access,'access_config',lambda:{})
    persist_analysis(imported(export))
    export['wizard_info'].update(wizard_id=2,wizard_name='Other account')
    result=imported(export)
    persist_analysis(result)
    assert result['import_summary']['previous_date'] is None
    assert result['import_summary']['deltas']=={}


def test_period_boundaries_and_chronological_order():
    frame=pd.DataFrame({'date':['31/12/2025','06/10/2026','06/09/2026','07/09/2026','01/01/2026']})
    assert period_rows(frame,30).date.tolist()==['07/09/2026','06/10/2026']
    assert period_rows(frame,None).date.tolist()==['31/12/2025','01/01/2026','06/09/2026','07/09/2026','06/10/2026']
    assert period_rows(frame.iloc[:0],30).empty


def test_filtered_task_save_preserves_hidden_tasks_and_is_atomic(engine,export,monkeypatch):
    meta,_=persist_analysis(imported(export));uid=meta['id_joueur']
    tasks=pd.DataFrame([dict(notes='first',stat_to_replace='ATK',stat_objectif='SPD',fait=False),dict(notes='hidden',stat_to_replace='',stat_objectif='',fait=False)],index=pd.Index([301,302],name='id_rune'))
    save_tasks(uid,tasks)
    edited=tasks.iloc[:1].copy();edited.loc[301,'notes']='updated'
    save_tasks(uid,edited)
    assert load_tasks(uid).loc[302,'notes']=='hidden'
    before=load_tasks(uid)
    invalid=tasks.copy();invalid.index=[301,'invalid']
    with pytest.raises(ValueError):save_tasks(uid,invalid)
    pd.testing.assert_frame_equal(load_tasks(uid),before)
    cleared=edited.copy()
    for key in cleared.columns:cleared[key]=None
    save_tasks(uid,cleared)
    assert load_tasks(uid).index.tolist()==[302]
    from fonctions import access
    monkeypatch.setattr(access,'identity',lambda:('https://test.invalid','other'))
    with pytest.raises(access.AccessDenied):save_tasks(uid,edited)


def test_legacy_task_notes_survive_schema_upgrade(engine,export):
    meta,_=persist_analysis(imported(export));uid=meta['id_joueur']
    with engine.begin() as conn:
        conn.execute(text('CREATE TABLE sw_todolist (id_joueur BIGINT,id_rune BIGINT,note TEXT)'))
        conn.execute(text('INSERT INTO sw_todolist VALUES (:id,301,:note),(:id,302,:note)'),{'id':uid,'note':'legacy note'})
    before=load_tasks(uid)
    assert before.notes.tolist()==['legacy note','legacy note']
    edited=before.iloc[:1].copy();edited.loc[301,'notes']='updated'
    save_tasks(uid,edited)
    after=load_tasks(uid)
    assert after.loc[301,'notes']=='updated'
    assert after.loc[302,'notes']=='legacy note'
    assert not after.fait.any()


@pytest.mark.parametrize('language',['Français','English'])
def test_find_me_search_visibility_and_navigation(engine,export,monkeypatch,language):
    at,uid=seeded(engine,export,monkeypatch,language)
    with engine.begin() as conn:
        for i in range(2,62):
            conn.execute(text('INSERT INTO sw_user(id,joueur,joueur_id,guilde_id,visibility) VALUES (:id,:name,:id,0,:visibility)'),{'id':i,'name':'Hidden player' if i==2 else 'Other player','visibility':0 if i==2 else 3})
            conn.execute(text('INSERT INTO sw_score(id_joueur,date,score_general,score_spd,score_arte,score_qual) VALUES (:id,:date,:score,:score,:score,:score)'),{'id':i,'date':'06/10/2026','score':1000+i})
    at.switch_page('pages_streamlit/ladder.py').run()
    assert not at.exception
    assert not at.dataframe[0].value.joueur.str.contains('Hidden').any()
    at.button(key='action_ui_ladder_locate').click().run()
    assert at.number_input(key='ui_ladder_page').value==3
    assert at.dataframe[0].value.joueur.str.contains(r'\((?:vous|you)\)').any()
    at.text_input(key='ui_ladder_query').set_value('Hidden').run()
    assert at.dataframe[0].value.empty
    at.button(key='action_ui_ladder_locate').click().run()
    at.selectbox(key='ui_ladder_kind').set_value('score_spd').run()
    at.radio(key='ui_ladder_mode').set_value('record').run()
    at.switch_page('pages_streamlit/general.py').run()
    at.switch_page('pages_streamlit/ladder.py').run()
    assert not at.exception
    assert at.selectbox(key='ui_ladder_kind').value=='score_spd'
    assert at.radio(key='ui_ladder_mode').value=='record'
    assert at.number_input(key='ui_ladder_page').value==3
    at.switch_page('pages_streamlit/upload.py').run()
    at.radio(key='translations_selected').set_value('English' if language=='Français' else 'Français').run()
    at.switch_page('pages_streamlit/ladder.py').run()
    assert not at.exception
    assert at.selectbox(key='ui_ladder_kind').value=='score_spd'


@pytest.mark.parametrize('language',['Français','English'])
def test_history_period_details_and_delete_refresh(engine,export,monkeypatch,language):
    at,uid=seeded(engine,export,monkeypatch,language)
    export['runes'][0]['sec_eff'][0][1]+=1
    persist_analysis(imported(export),'31/12/2025')
    export['runes'][0]['sec_eff'][0][1]+=1
    persist_analysis(imported(export),'10/09/2026')
    at.switch_page('pages_streamlit/evolution.py').run()
    assert not at.exception
    at.radio(key='ui_history_period').set_value('30').run()
    assert len(at.dataframe[0].value)==2
    at.switch_page('pages_streamlit/general.py').run()
    at.switch_page('pages_streamlit/evolution.py').run()
    assert at.radio(key='ui_history_period').value=='30'
    for metric in ['score_general','score_spd','score_arte','score_qual']:
        at.radio(key='ui_history_metric').set_value(metric).run()
        assert not at.exception
    at.checkbox(key='ui_history_detail').check().run()
    assert not at.exception
    assert len(at.tabs)==9  # rune/quality panels plus their tier charts
    at.switch_page('pages_streamlit/options.py').run()
    assert at.selectbox(key='ui_delete_date').options==['06/10/2026','10/09/2026','31/12/2025']
    at.selectbox(key='ui_delete_date').set_value('10/09/2026').run()
    with engine.connect() as conn:
        assert deletion_preview(conn,uid,'10/09/2026')['sw_rune_snapshots']==1
    next(c for c in at.checkbox if 'relevé' in c.label or 'snapshot' in c.label).check()
    next(b for b in at.button if b.label in ('Supprimer le relevé','Delete snapshot')).click().run()
    assert not at.exception
    assert not any(w.value in ('Confirmez la suppression.','Confirm deletion first.') for w in at.warning)
    assert at.selectbox(key='ui_delete_date').options==['06/10/2026','31/12/2025']
    assert at.success
    with engine.connect() as conn:
        assert deletion_preview(conn,uid,'10/09/2026')['sw_rune_snapshots']==0
        assert deletion_preview(conn,uid,'06/10/2026')['sw_rune_snapshots']==1


def test_build_result_survives_navigation_and_rejects_changed_criteria(engine,export,monkeypatch):
    at,_=seeded(engine,export,monkeypatch)
    at.switch_page('pages_streamlit/planning.py').run()
    next(b for b in at.button if b.label=='Rechercher le build').click().run()
    assert not at.exception
    old_signature=at.session_state['_build_result'][0]
    at.switch_page('pages_streamlit/general.py').run()
    at.switch_page('pages_streamlit/planning.py').run()
    assert at.session_state['_build_result'][0]==old_signature
    at.number_input(key='plan_speed').set_value(123).run()
    assert any('Relancez la recherche' in info.value for info in at.info)


def test_delete_current_report_confirms_success_and_preserves_tasks(engine,export,monkeypatch):
    at,uid=seeded(engine,export,monkeypatch)
    tasks=pd.DataFrame([dict(notes='keep',stat_to_replace='',stat_objectif='',fait=False)],index=pd.Index([301],name='id_rune'))
    save_tasks(uid,tasks)
    at.switch_page('pages_streamlit/options.py').run()
    at.checkbox[0].check()
    next(b for b in at.button if b.label=='Supprimer le relevé').click().run()
    assert not at.exception
    assert not at.session_state['analysis_ready']
    assert any('Relevé supprimé' in message.value for message in at.success)
    assert load_tasks(uid).loc[301,'notes']=='keep'
    with engine.connect() as conn:
        assert conn.execute(text('SELECT COUNT(*) FROM sw_score')).scalar()==0


def test_changing_deletion_date_requires_new_confirmation(engine,export,monkeypatch):
    at,uid=seeded(engine,export,monkeypatch)
    export['runes'][0]['sec_eff'][0][1]+=1
    persist_analysis(imported(export),'05/10/2026')
    at.switch_page('pages_streamlit/options.py').run()
    at.checkbox[0].check().run()
    at.selectbox(key='ui_delete_date').set_value('05/10/2026').run()
    assert not at.checkbox[0].value
    next(b for b in at.button if b.label=='Supprimer le relevé').click().run()
    assert any('Confirmez' in message.value for message in at.warning)
    with engine.connect() as conn:
        assert conn.execute(text('SELECT COUNT(*) FROM sw_score')).scalar()==2


def test_rune_card_protection_and_task_shortcut(engine,export,monkeypatch):
    at,_=seeded(engine,export,monkeypatch)
    at.switch_page('pages_streamlit/optimisation.py').run()
    at.button[0].click().run()
    assert not at.exception
    selected=at.selectbox(key='ui_optimisation_rune').value
    at.button(key='action_ui_optimisation_rune_lock').click().run()
    assert not at.exception
    from fonctions.workspace import load_settings
    assert selected in load_settings(at.session_state['id_joueur'])['locked_runes']
    at.button(key='action_ui_optimisation_rune_task').click().run()
    assert not at.exception
    assert at.session_state['ui_task_rune']==at.selectbox(key='ui_tasks_card').value
