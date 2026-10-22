"""Reproduce the reported regressions with a configured database, without OIDC."""
import json
from io import BytesIO
from pathlib import Path
import pandas as pd
import pytest
import streamlit as st
from sqlalchemy import text
from streamlit.testing.v1 import AppTest
from fonctions import access
from fonctions.import_service import analyse_export, persist_analysis, validate_export

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture
def reference_database(engine,monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv('API_SQL','test-engine-injected')
    monkeypatch.setattr(access,'access_config',lambda:{})
    monkeypatch.setattr(access,'identity',lambda:None)
    reference=pd.DataFrame([dict(com2us_id=18911,name='Test monster',image_filename='test.png',natural_stars=5,element='Fire',awaken_level=1)])
    usage=pd.DataFrame([{'index':0,'Family':'Test family','Element':'Fire','Awakened':'Test monster',
                       'Attribute':'Attack','Preferred stats':'Any','Include':1,'Damage S1':3,'Accuracy S1':2}])
    with engine.begin() as conn:
        reference.to_sql('sw_ref_monsters',conn,index=False)
        usage.to_sql('sw_where2use',conn,index=False)
    return engine


@pytest.mark.parametrize('save',[True,False])
def test_upload_names_and_default_saving_without_oidc(reference_database,export,monkeypatch,save):
    export['unit_list']=[dict(unit_id=987,unit_master_id=18911,runes=[],artifacts=[])]
    monkeypatch.setattr(st,'file_uploader',lambda *args,**kwargs:BytesIO(json.dumps(export).encode()))
    at=AppTest.from_file(str(ROOT/'scoring_runage.py'),default_timeout=30).run()
    assert not at.exception
    assert at.checkbox(key='save_import').value is True
    assert not at.checkbox(key='save_import').disabled
    if not save:
        at.checkbox(key='save_import').uncheck().run()
    at.button(key='upload_submit').click().run()
    assert not at.exception and not at.error
    assert at.session_state['df_mobs'].name_monstre.tolist()==['Test monster']
    assert (at.session_state['id_joueur'] is not None)==save
    with reference_database.connect() as conn:
        if save:
            assert conn.execute(text('SELECT COUNT(*) FROM sw_score')).scalar()==1
    at.switch_page('pages_streamlit/general.py').run()
    at.segmented_control(key='overview_view').set_value('Monstres').run()
    assert not at.exception
    assert at.dataframe[-1].value['name'].tolist()==['Test monster']
    if save:
        for page in ['evolution','comparaison','ladder','ladder_value','ladder_arte','ladder_others']:
            at.switch_page('pages_streamlit/'+page+'.py').run()
            assert not at.exception,(page,[e.message for e in at.exception])


@pytest.mark.parametrize('language',['Français','English'])
def test_use_arte_connected_optional_selector(reference_database,language):
    at=AppTest.from_file(str(ROOT/'scoring_runage.py'),default_timeout=30)
    at.session_state['translations_selected']=language
    at.run().switch_page('pages_streamlit/use_arte.py').run()
    assert not at.exception
    assert at.selectbox(key='stats1').value is None
    assert 'Stats préférées' not in at.selectbox(key='stats1').options
    at.selectbox(key='stats1').set_value('Damage S1').run()
    assert not at.exception
    at.selectbox(key='stats1').set_value(None).run()
    assert not at.exception
    at.multiselect(key='monster').set_value(['Test monster']).run()
    assert not at.exception
    assert len(at.dataframe[-1].value)==1


def test_legacy_account_keeps_history_and_identity(reference_database,export):
    with reference_database.begin() as conn:
        conn.execute(text('INSERT INTO sw_user(id,joueur,joueur_id,guilde_id,visibility,rank) VALUES (99,:name,0,0,3,0)'),{'name':export['wizard_info']['wizard_name']})
    result=analyse_export(validate_export(export),pd.DataFrame())
    metadata,created=persist_analysis(result,'06/10/2026')
    assert created and metadata['id_joueur']==99 and metadata['visibility']==3
    assert not persist_analysis(result,'06/10/2026')[1]
    with reference_database.connect() as conn:
        assert conn.execute(text('SELECT COUNT(*) FROM sw_user')).scalar()==1
        assert conn.execute(text('SELECT joueur_id FROM sw_user WHERE id=99')).scalar()==1


def test_old_oidc_config_does_not_implicitly_block_saving(monkeypatch):
    monkeypatch.setattr(access,'access_config',lambda:{'accounts':[]})
    monkeypatch.setattr(access,'identity',lambda:None)
    assert access.can_access(123)
    monkeypatch.setattr(access,'access_config',lambda:{'require_oidc':True,'accounts':[]})
    assert not access.can_access(123)


def test_import_failure_has_safe_diagnostic_and_preserves_analysis(reference_database, export, monkeypatch, caplog):
    from fonctions import snapshots
    monkeypatch.setattr(st, 'file_uploader', lambda *args, **kwargs: BytesIO(json.dumps(export).encode()))
    at = AppTest.from_file(str(ROOT/'scoring_runage.py'), default_timeout=30).run()
    at.button(key='upload_submit').click().run()
    assert not at.exception and not at.error
    previous_hash = at.session_state['import_hash']
    previous_score = at.session_state['score']
    export['runes'][0]['sec_eff'][0][1] += 1
    def fail(*args):
        raise ValueError('private-export-and-database-secret')
    monkeypatch.setattr(snapshots, 'save_snapshot', fail)
    at.run().button(key='upload_submit').click().run()
    assert not at.exception and len(at.error) == 1
    captions = '\n'.join(item.value for item in at.caption)
    assert 'ValueError' in captions
    assert 'Étape : Sauvegarde du détail des runes' in captions
    assert 'Référence à transmettre :' in captions
    assert 'private-export-and-database-secret' not in captions + caplog.text
    assert 'snapshots' in caplog.text or '(fail)' in caplog.text
    assert at.session_state['import_hash'] == previous_hash
    assert at.session_state['score'] == previous_score
    with reference_database.connect() as conn:
        assert conn.execute(text('SELECT COUNT(*) FROM sw_imports')).scalar() == 1
        assert conn.execute(text('SELECT COUNT(*) FROM sw_rune_snapshots')).scalar() == 1
