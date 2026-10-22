from copy import deepcopy
import json
import pandas as pd
import pytest
from sqlalchemy import text
from fonctions.analysis import select_snapshots, objective_counts
from fonctions.leaderboards import rank_movement, nearby_players, visible_players, report_versions
from fonctions.goals import (rune_progress, artifact_progress, RUNE_KEYS, RUNE_DEFAULTS,
    previous_goal_snapshot, snapshot_rune_counts, save_goals, rune_goals)
from fonctions.import_service import analyse_export, validate_export, persist_analysis
from fonctions.snapshots import snapshot


def ranking_history():
    return pd.DataFrame([
        [1,'01/10/2026',100],[2,'01/10/2026',200],[3,'01/10/2026',150],
        [1,'07/10/2026',220],[2,'06/10/2026',200],[3,'07/10/2026',220],
        [4,'07/10/2026',300]],columns=['id','date','score']).assign(scoring_version='v2')


def test_rank_reconstruction_counts_ties_entrants_and_cutoff():
    history=ranking_history()
    current=select_snapshots(history,'score')
    change=rank_movement(history,current,1,check_versions=True)
    assert change==dict(date='01/10/2026',before=3,now=2,delta=1,players_before=3,players_now=4)
    assert rank_movement(history,current,4) is None  # new account
    assert rank_movement(history,current,99) is None
    history.loc[0,'date']='invalid'
    assert rank_movement(history,current,1) is None


@pytest.mark.parametrize('method',[None,'v1'])
def test_rank_does_not_compare_unknown_or_changed_scoring(method):
    history=ranking_history()
    history.loc[0,'scoring_version']=method
    assert rank_movement(history,select_snapshots(history,'score'),1,check_versions=True) is None


def test_rank_record_uses_record_at_each_cutoff():
    history=ranking_history()
    history.loc[(history.id==1)&(history.date=='07/10/2026'),'score']=80
    current=select_snapshots(history,'score','record')
    change=rank_movement(history,current,1,mode='record')
    assert change['before']==3 and change['now']==4
    assert change['date']=='01/10/2026'


def test_rank_scope_and_nearby_do_not_leak_hidden_accounts():
    history=ranking_history().assign(joueur='Player',guilde_id=7,visibility=3)
    history.loc[history.id.eq(4),'visibility']=0
    history.loc[history.id.eq(2),'visibility']=1
    history=visible_players(history,1,7)
    current=select_snapshots(history,'score')
    assert rank_movement(history,current,1)['now']==1
    current['Rang']=current.score.rank(method='min',ascending=False)
    close=nearby_players(current,'score',1)
    assert 4 not in close.id.values
    assert close.loc[close.id.eq(2),'joueur'].item()=='***'
    assert nearby_players(current,'score',99).empty


def test_nearby_keeps_viewer_when_many_players_tie():
    frame=pd.DataFrame({'id':range(1,30),'score':100,'Rang':1})
    close=nearby_players(frame,'score',29)
    assert len(close)==7 and 29 in close.id.values
    assert close.id.nunique()==7


def test_rune_goals_do_not_offset_missing_slots_or_mix_tiers():
    targets=dict(zip(RUNE_KEYS,RUNE_DEFAULTS));targets['vio100']=2
    counts=pd.DataFrame([['Violent',1,100,20],['Violent',2,100,2],['Violent',3,110,3]],
        columns=['rune_set','rune_slot','efficience','Quantité'])
    old=counts.copy();old.loc[1,'Quantité']=1
    rows=rune_progress(counts,targets,old)
    selected=rows[(rows.group=='Violent')&(rows.tier==100)]
    assert selected.remaining.sum()==8
    assert selected.achieved.sum()==2
    assert selected.new.sum()==1
    assert selected.progress.max()==100
    assert selected.loc[selected.slot==3,'current'].item()==0
    assert not rune_progress(counts,targets).new.any()


def artifact_params():
    return {'CRIT DMG':10,'CRIT DMG_HP':True,'SOIN':10,'SOIN_HP':True}


def test_artifact_goals_threshold_missing_cells_merged_skills_and_new():
    cols=['main_type','substat','arte_attribut','1']
    old=pd.DataFrame([['HP','CRIT DMG S3','ATTACK',10],['HP','SOIN S1','SUPPORT',20]],columns=cols)
    now=pd.DataFrame([['HP','CRIT DMG S3','ATTACK',9],['HP','CRIT DMG S4','ATTACK',11]],columns=cols)
    rows=artifact_progress(now,artifact_params(),old)
    crit=rows[rows.group=='CRIT DMG'].iloc[0]
    assert crit.current==11 and crit.target==11 and crit['new']
    assert crit.delta==1 and crit.remaining==0
    missing=rows[rows.group=='SOIN'].iloc[0]
    assert missing.current==0 and not missing.achieved and missing.remaining==11
    same=artifact_progress(old,artifact_params())
    assert not same.new.any()
    assert same.loc[same.group=='CRIT DMG','remaining'].item()==1
    assert artifact_progress(now,{}).empty
    assert artifact_progress(pd.DataFrame(columns=cols),artifact_params()).empty


def test_artifact_matrix_retains_unfilled_effect_attribute_combinations():
    frame=pd.DataFrame([['HP','SOIN S1','ATTACK',12],['HP','SOIN S2','SUPPORT',15]],
                       columns=['main_type','substat','arte_attribut','1'])
    rows=artifact_progress(frame,artifact_params())
    assert len(rows)==4 and rows.achieved.sum()==2
    assert rows.remaining.sum()==22


def imported(export):
    return analyse_export(validate_export(export),pd.DataFrame())


def add_artifact(export):
    export['artifacts']=[dict(rid=7001,type=2,attribute=0,occupied_id=0,unit_style=1,
        level=15,pri_effect=[100,1500],sec_effects=[[400,12],[404,10],[408,13],[206,11]])]


def test_goal_history_same_day_anchor_reimport_and_versions(engine,export):
    first=imported(export);metadata,_=persist_analysis(first,'07/10/2026');uid=metadata['id_joueur']
    assert previous_goal_snapshot(uid,first['import_hash'],first['scoring_version'])==(None,None)
    export['runes'][0]['sec_eff'][0][1]+=1
    second=imported(export);persist_analysis(second,'07/10/2026')
    before,date=previous_goal_snapshot(uid,second['import_hash'],second['scoring_version'])
    assert date and before['runes']==snapshot(first)['runes']
    assert 'goal_artifacts' in before
    pd.testing.assert_frame_equal(snapshot_rune_counts(before,first['data_rune'].set_to_show),
                                  objective_counts(first['data_rune'].count_efficience_per_slot()),check_dtype=False,check_categorical=False)
    assert previous_goal_snapshot(uid,first['import_hash'],first['scoring_version'])==(None,None)
    assert previous_goal_snapshot(uid,'not-saved',first['scoring_version'])==(None,None)
    persist_analysis(second,'08/10/2026')  # replay is not a new milestone
    assert previous_goal_snapshot(uid,second['import_hash'],second['scoring_version'])[0]==before
    with engine.begin() as conn:
        conn.execute(text('UPDATE sw_rune_snapshots SET scoring_version=:version WHERE payload_sha=:sha'),
                     {'version':'old','sha':first['import_hash']})
    assert previous_goal_snapshot(uid,second['import_hash'],second['scoring_version'])==(None,None)


def test_goal_settings_named_columns_and_account_scope(engine,export,monkeypatch):
    uid=persist_analysis(imported(export))[0]['id_joueur']
    with engine.begin() as conn:
        conn.execute(text('CREATE TABLE sw_objectifs_rune(id BIGINT,'+','.join(f'{key} INTEGER' for key in reversed(RUNE_KEYS))+')'))
    targets=dict(zip(RUNE_KEYS,RUNE_DEFAULTS));targets['vio100']=7
    save_goals(uid,'rune',targets)
    assert rune_goals(uid)==targets
    from fonctions import access
    monkeypatch.setattr(access,'identity',lambda:('https://test.invalid','other'))
    with pytest.raises(access.AccessDenied): save_goals(uid,'rune',targets)
    with pytest.raises(access.AccessDenied): previous_goal_snapshot(uid,'sha','v2')


def test_rank_versions_keep_ambiguous_days_unknown(engine,export):
    result=imported(export)
    uid=persist_analysis(result,'07/10/2026')[0]['id_joueur']
    assert report_versions().scoring_version.item()==result['scoring_version']
    with engine.begin() as conn:
        conn.execute(text('INSERT INTO sw_imports(id_joueur,payload_sha,scoring_version,date) VALUES (:id,:sha,:v,:date)'),
                     {'id':uid,'sha':'legacy','v':'old','date':'07/10/2026'})
    report_versions.clear()
    versions=report_versions()
    assert len(versions)==1 and versions.scoring_version.isna().all()


def test_optional_snapshot_artifact_values_are_json_safe(export):
    add_artifact(export)
    result=imported(export)
    payload=json.loads(json.dumps(snapshot(result),allow_nan=False))
    assert payload['goal_artifacts']
    assert set(payload['goal_artifacts'][0])=={'main_type','substat','arte_attribut','1'}


@pytest.mark.parametrize('language',['Français','English'])
def test_goal_pages_and_nearby_controls(engine,export,monkeypatch,language):
    from test_journey import seeded
    add_artifact(export)
    at,uid=seeded(engine,export,monkeypatch,language)
    with engine.begin() as conn:
        conn.execute(text('CREATE TABLE sw_objectifs_rune(id BIGINT,'+','.join(f'{key} INTEGER' for key in RUNE_KEYS)+')'))
        from fonctions.goals import ARTIFACT_STATS
        names=['reduction','dmg_elem','crit_dmg','precision','soin','spd']
        conn.execute(text('CREATE TABLE sw_objectifs_arte(id BIGINT,'+','.join(f'"{key}" INTEGER' for key in names)+','+
                          ','.join(f'{key}_{stat} BOOLEAN' for key in names for stat in ('hp','atk','def'))+')'))
    for page in ('objectif_rune','objectif_arte'):
        at.switch_page('pages_streamlit/'+page+'.py').run()
        assert not at.exception
        assert at.metric[2].value=='—'
        if page=='objectif_rune':
            at.slider(key='goal_vio100').set_value(7).run()
            at.button[0].click().run()
            assert rune_goals(uid)['vio100']==7
            at.radio(key='goal_rune_view_100').set_value('new').run()
        else:
            for checkbox in at.checkbox: checkbox.uncheck()
            at.run()
            assert not at.exception and at.info
    at.switch_page('pages_streamlit/ladder.py').run()
    at.toggle(key='ui_ladder_nearby').set_value(True).run()
    assert not at.exception
    assert len(at.dataframe[0].value)==1 and 'Écart' in at.dataframe[0].value
