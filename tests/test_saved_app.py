import pandas as pd
from sqlalchemy import text
from pathlib import Path
from streamlit.testing.v1 import AppTest
from fonctions.import_service import validate_export,analyse_export,persist_analysis,publish_analysis
from fonctions import gestion_bdd as db

ROOT=Path(__file__).resolve().parents[1]

def test_saved_pages(engine,export,monkeypatch):
    from fonctions import access
    monkeypatch.setattr(access,'access_config',lambda:{})
    monkeypatch.setattr(access,'identity',lambda:None)
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv('API_SQL','test-engine-injected')
    with engine.begin() as c:
        for ddl in [
        'CREATE TABLE IF NOT EXISTS sw_objectifs_rune(id BIGINT,'+','.join(f'{name} INTEGER' for name in ['vio100','vio110','destroy100','destroy110','will100','will110','despair100','despair110','swift100','swift110','nemesis100','nemesis110'])+')',
        'CREATE TABLE IF NOT EXISTS sw_objectifs_arte(id BIGINT,'+','.join(f'"{name}" INTEGER' for name in ['reduction','dmg_elem','crit_dmg','precision','soin'])+','+','.join(f'{stat}_{suffix} BOOLEAN' for stat in ['reduction','dmg_elem','crit_dmg','precision','soin'] for suffix in ['hp','atk','def'])+',spd INTEGER,spd_hp BOOLEAN,spd_atk BOOLEAN,spd_def BOOLEAN)',
        'CREATE TABLE IF NOT EXISTS sw_build(id_build INTEGER PRIMARY KEY,id BIGINT,monstre TEXT,nom_build TEXT,'+','.join(f'rune{i} BIGINT' for i in range(1,7))+')',
        'CREATE TABLE IF NOT EXISTS sw_ref_monsters(id BIGINT,com2us_id BIGINT,name TEXT,speed INTEGER,element TEXT,awaken_level INTEGER,natural_stars INTEGER,image_filename TEXT)',
        'CREATE TABLE IF NOT EXISTS sw_ref_monsters_stats(id BIGINT,speed INTEGER)',
        'CREATE TABLE IF NOT EXISTS sw_todolist(id_joueur BIGINT,id_rune BIGINT,note TEXT)'
        ]:c.execute(text(ddl))

    export['unit_list']=[dict(unit_id=987,unit_master_id=123,class_=6,unit_level=40,spd=100,create_time='2026-01-01 00:00:00',runes=[],artifacts=[])]
    export['unit_list'][0]['class']=6
    reference=pd.DataFrame([dict(id=1,com2us_id=123,name='Test monster',speed=100,element='Fire',awaken_level=1,natural_stars=5,image_filename='')])
    with engine.begin() as c:
        reference.to_sql('sw_ref_monsters',c,if_exists='append',index=False)
        pd.DataFrame([{'id':1,'speed':100}]).to_sql('sw_ref_monsters_stats',c,if_exists='append',index=False)
    result=analyse_export(validate_export(export),reference)
    metadata,_=persist_analysis(result,'05/10/2026')
    db.requete_perso_bdd('UPDATE sw_user SET visibility=3 WHERE id=:id',{'id':metadata['id_joueur']})
    metadata['visibility']=3
    state={};publish_analysis(state,result,metadata)
    at=AppTest.from_file(str(ROOT/'scoring_runage.py'),default_timeout=30)
    for key,value in state.items():at.session_state[key]=value
    at.session_state['translations_selected']='Français'
    import streamlit as st
    navigation=st.navigation
    menus=[]
    def capture_menu(pages,**kwargs):
        menus.append((list(pages),kwargs))
        return navigation(pages,**kwargs)
    monkeypatch.setattr(st,'navigation',capture_menu)
    at.run()
    assert menus[-1][0][-1]=='Calculateurs'
    assert 'Classements' in menus[-1][0]
    assert menus[-1][1]['expanded'] is True
    for page in ['evolution','comparaison','ladder','ladder_value','ladder_arte','ladder_others','objectif_rune','objectif_arte','build_manager','optimisation_spd','options','visibility','planning','import_changes']:
        at.switch_page('pages_streamlit/'+page+'.py').run()
        assert not at.exception,(page,[e.message for e in at.exception])
        assert not at.error,(page,[e.value for e in at.error])
        if page=='ladder':
            for choice in at.selectbox[0].options:
                at.selectbox[0].set_value(choice).run()
                assert not at.exception,(choice,[e.message for e in at.exception])
        if page=='optimisation_spd':
            at.selectbox[0].set_value('Swift').run()
            assert not at.exception,[e.message for e in at.exception]
        if page=='objectif_arte':
            next(s for s in at.slider if s.label.endswith(' SOIN')).set_value(20).run()
            next(s for s in at.slider if s.label.endswith(' SPD')).set_value(45).run()
            at.checkbox(key='SPD_HP').uncheck().run()
            at.button[0].click().run()
            assert not at.exception
            at.switch_page('pages_streamlit/general.py').run()
            at.switch_page('pages_streamlit/objectif_arte.py').run()
            assert next(s for s in at.slider if s.label.endswith(' SOIN')).value==20
            assert next(s for s in at.slider if s.label.endswith(' SPD')).value==45
            assert not at.checkbox(key='SPD_HP').value
            assert at.checkbox(key='SOIN_HP').value
    # A second same-day import is selectable and shows the changed rune.
    export['runes'][0]['sec_eff'][0][1]+=1
    persist_analysis(analyse_export(validate_export(export),reference),'05/10/2026')
    at.switch_page('pages_streamlit/import_changes.py').run()
    assert not at.exception
    assert len(at.dataframe[0].value)==1
