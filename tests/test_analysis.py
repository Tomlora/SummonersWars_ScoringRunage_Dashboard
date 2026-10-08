import itertools
import random
from copy import deepcopy
import pandas as pd
import pytest
from fonctions.analysis import objective_counts, fastest_build, select_snapshots
from fonctions.import_service import validate_export, analyse_export, publish_analysis, InvalidExport, monster_frame
from fonctions.runes import Rune
from fonctions.gestion_bdd import optimisation_int

def test_objective_order_and_missing_tiers():
    df=pd.DataFrame({'rune_set':['Swift']*3,'rune_slot':[1,2,3],'efficiency':[115,105,150]})
    result=objective_counts(df)
    assert result.query('Quantité > 0').set_index('rune_slot')['efficience'].to_dict()=={1:110,2:100,3:110}
    assert objective_counts(df.iloc[:1])['Quantité'].sum()==1
    assert objective_counts(df.iloc[:0]).empty

@pytest.mark.parametrize('empty',[True,False])
def test_whole_analysis_without_ancients_or_artifacts(export,empty):
    if empty: export['runes']=[]
    result=analyse_export(validate_export(export),pd.DataFrame())
    assert result['score_arte']==0
    assert result['score_qual']==(0 if empty else 66)
    assert result['data_arte'].df_top.empty
    result['data_rune'].calcul_potentiel()
    result['data_rune'].grind()

def test_substat_maxima_keep_sparse_positions(export):
    export['runes']=export['runes'][:1]
    runes=Rune(export,{})
    actual=runes.calcul_value_max()
    assert set(actual.index)=={'HP%','ATQ%','CRIT','SPD'}
    assert actual.loc['SPD','max_value']==34
    assert actual.loc['SPD','top5']==34
    assert pd.isna(actual.loc['SPD','2'])
    assert len(runes.calcul_value_max_per_slot())==4

def test_speed_does_not_invent_main_stat(export):
    export['runes']=[r for r in export['runes'] if r['set_id']==3]
    runes=Rune(export,{})
    build,score=runes.optimisation_max_speed('Swift')
    assert len(build)==6 and score==212
    export['runes'][1]['pri_eff']=[4,63]
    build,score=Rune(export,{}).optimisation_max_speed('Swift')
    assert build.empty and score is None
    assert Rune(export,{}).optimisation_max_speed('Swift',slot2_speed=False)[1]==170

def speed_rows(seed):
    rng=random.Random(seed)
    rows=[]
    for slot in range(1,7):
        for index in range(3):
            row={'rune_slot':slot,'rune_set':rng.choice(['Swift','Will','Blade','Intangible']),'main_type':'HP','main_value':100}
            for sub in ['first_sub','second_sub','third_sub','fourth_sub']:
                row[sub]='SPD' if sub=='first_sub' else 'HP%'
                row[sub+'_value_total']=rng.randrange(1,32) if sub=='first_sub' else 0
            rows.append(row)
    return pd.DataFrame(rows,index=range(2**34,2**34+18))

@pytest.mark.parametrize('seed',range(20))
@pytest.mark.parametrize('secondary',[None,'Will'])
def test_speed_matches_exhaustive_reference(seed,secondary):
    data=speed_rows(seed)
    brute=[]
    for selected in itertools.product(*[data[data.rune_slot==i].to_dict('records') for i in range(1,7)]):
        sets=[r['rune_set'] for r in selected]
        wild=sets.count('Intangible')
        deficit=max(0,4-sets.count('Swift'))+(max(0,2-sets.count('Will')) if secondary else 0)
        eligible = [name for name in ['Swift','Will','Blade'] if sets.count(name) % (4 if name == 'Swift' else 2) == (3 if name == 'Swift' else 1)]
        available = wild if len(eligible)==1 else 0
        if wild<=1 and deficit<=available:
            brute.append(sum(r['first_sub_value_total'] for r in selected))
    build,actual=fastest_build(data,'Swift',secondary,False)
    assert actual==(max(brute) if brute else None)
    if actual is not None:
        assert build.index.is_unique
        assert (build.id_rune>=2**34).all()

def test_snapshot_selection_keeps_real_observation():
    data=pd.DataFrame({'id':[1,1,2],'joueur':['same']*3,'date':['30/09/2026','01/10/2026','01/10/2026'],'score':[100,80,90],'other':[1,3,2]})
    assert select_snapshots(data,'score').set_index('id').loc[1,'score']==80
    record=select_snapshots(data,'score','record').set_index('id').loc[1]
    assert record['other']==1 and record['date']=='30/09/2026'

@pytest.mark.parametrize('raw',['{','[]','{}','{"wizard_info": []}'])
def test_bad_json(raw):
    with pytest.raises(InvalidExport): validate_export(raw)

def test_slot_mapping_and_input_immutability(export):
    unit={'unit_id':99,'unit_master_id':3,'runes':{'b':export['runes'][5],'a':export['runes'][1]}}
    export['unit_list']=[unit]
    export['runes']=[r for r in export['runes'] if r['rune_id'] not in {302,306}]
    original=deepcopy(export)
    clean=validate_export(export)
    row=monster_frame(clean,pd.DataFrame()).iloc[0]
    assert row.Rune6==306 and row.Rune2==302 and row.Rune1==0
    assert export==original

def test_publish_clears_old_account_views(export):
    data=analyse_export(validate_export(export),pd.DataFrame())
    state={'old_filter':123,'langue':{},'translations_selected':'English'}
    publish_analysis(state,data,{'id_joueur':1,'report_date':'04/10/2026'})
    assert state['analysis_ready'] and state['translations_selected']=='English'
    assert 'old_filter' not in state

def test_identifiers_never_overflow():
    data=pd.DataFrame({'id_rune':[2**40], 'score':[40000], 'small':[2]})
    result=optimisation_int(data,['int64'])
    assert result.iloc[0].to_dict()==data.iloc[0].to_dict()
