from copy import deepcopy
from itertools import product
import random
import pandas as pd
import pytest
from fonctions.import_service import validate_export, InvalidExport, analyse_export
from fonctions.planning import grind_plan, constrained_build, rune_accuracy, SearchLimit
from fonctions.analysis import rune_speed
from fonctions.runes import Rune
from fonctions.snapshots import snapshot, compare_snapshots
from fonctions.workspace import settings, locked_ids


@pytest.mark.parametrize('kind',['duplicate','equipped_duplicate','nan','infinity','boolean_id','boolean_stat','negative_stock','duplicate_unit','boolean_unit'])
def test_invalid_export_is_rejected(export,kind):
    if kind=='duplicate': export['runes'].append(deepcopy(export['runes'][0]))
    if kind=='equipped_duplicate': export['unit_list']=[{'unit_id':99,'unit_master_id':1,'runes':[deepcopy(export['runes'][0])]}]
    if kind=='nan': export['runes'][0]['pri_eff'][1]=float('nan')
    if kind=='infinity': export['runes'][0]['sec_eff'][0][1]=float('inf')
    if kind=='boolean_id': export['wizard_info']['wizard_id']=True
    if kind=='boolean_stat': export['runes'][0]['pri_eff'][1]=True
    if kind=='negative_stock': export['rune_craft_item_list']=[dict(craft_type=2,craft_type_id=30805,amount=-1)]
    if kind=='duplicate_unit': export['unit_list']=[dict(unit_id=99,unit_master_id=1)]*2
    if kind=='boolean_unit': export['unit_list']=[dict(unit_id=True,unit_master_id=1)]
    with pytest.raises(InvalidExport): validate_export(export)


def test_grind_stock_cannot_be_reused_and_locks_are_excluded(export):
    runes=Rune(export,{})
    items=[dict(craft_type=2,craft_type_id=30805,amount=1)]
    plan,remaining=grind_plan(runes,items)
    assert len(plan)==1 and remaining[2,30805]==0
    first=int(plan.id_rune.iloc[0])
    next_plan,_=grind_plan(runes,items,{first})
    assert len(next_plan)==1 and int(next_plan.id_rune.iloc[0])!=first
    assert grind_plan(runes,items,set(runes.data.index))[0].empty
    assert grind_plan(runes,items,sets=['Violent'])[0].empty
    # Multiple entries of the same craft type aggregate quantities.
    combined,remaining=grind_plan(runes,items*2)
    assert len(combined)==2 and all(v>=0 for v in remaining.values())
    assert not combined.duplicated(['id_rune','stat']).any()


def test_ancient_and_wildcard_grinds(export):
    export['runes']=export['runes'][:1]
    item=dict(craft_type=4,craft_type_id=80805,amount=1)
    assert len(grind_plan(Rune(export,{}),[item])[0])==1
    export['runes'][0].update(rank=15,extra=15,**{'class':16})
    assert grind_plan(Rune(export,{}),[item])[0].empty
    item.update(craft_type=6,craft_type_id=30805)
    assert len(grind_plan(Rune(export,{}),[item])[0])==1


def test_grind_recalculation_is_idempotent_with_pandas3(export):
    runes=Rune(export,{})
    runes.calcul_potentiel();runes.grind()
    before=runes.data_grind.copy(deep=True)
    runes.calcul_potentiel();runes.grind()
    pd.testing.assert_frame_equal(before,runes.data_grind)


def test_snapshot_changes_explain_score(export):
    before=snapshot(analyse_export(validate_export(export),pd.DataFrame()))
    export['runes'].pop(0)
    export['runes'][2]['sec_eff'][0][1]+=6
    added=deepcopy(export['runes'][-1]);added['rune_id']=2**55
    export['runes'].append(added)
    after=snapshot(analyse_export(validate_export(export),pd.DataFrame()))
    diff=compare_snapshots(before,after)
    assert {'added','removed','improved'}<=set(diff.status)
    assert str(2**55) in set(diff.id_rune)
    assert diff.score_delta.sum()==after['score']-before['score']
    assert compare_snapshots(before,before).empty
    after['scoring_version']='future'
    with pytest.raises(ValueError): compare_snapshots(before,after)


def test_monster_and_build_locks_use_ids(export):
    export['unit_list']=[dict(unit_id=55,runes=[export['runes'][0]])]
    prefs=settings();prefs['locked_monsters']=[55];prefs['locked_builds']=[9]
    build=dict(id_build=9,**{f'rune{i}':i for i in range(1,7)})
    assert locked_ids(export,prefs,[build])=={301,1,2,3,4,5,6}


@pytest.mark.parametrize('seed',range(12))
def test_constrained_search_matches_bruteforce(export,seed):
    rng=random.Random(seed)
    # Two candidates per slot; speed/accuracy tradeoffs must not be pruned away.
    data=Rune(export,{}).data_set.iloc[:12].copy()
    data['rune_set']=['Swift']*6+['Will']*6
    for key in ('first_sub','second_sub','third_sub','fourth_sub'):
        data[key]='Aucun';data[key+'_value_total']=0
    data['main_type']='HP';data['innate_type']='Aucun'
    data['first_sub']='SPD';data['second_sub']='ACC'
    data['first_sub_value_total']=[rng.randrange(5,31) for _ in range(12)]
    data['second_sub_value_total']=[rng.randrange(0,20) for _ in range(12)]
    minimum=55
    scores=[]
    for rows in product(*(data[data.rune_slot.astype(int)==slot].index for slot in range(1,7))):
        candidate=data.loc[list(rows)]
        if sum(candidate.rune_set=='Swift')!=4 or rune_accuracy(candidate).sum()<minimum:
            continue
        scores.append(rune_speed(candidate).sum())
    found=constrained_build(data,'Swift','Will',min_accuracy=minimum,slot2_speed=False)
    assert (None if found.empty else found.spd.sum())==(max(scores) if scores else None)


def test_search_minimum_speed_locks_and_limit(export):
    data=Rune(export,{}).data_set
    assert constrained_build(data,'Swift',min_speed=999).empty
    assert constrained_build(data,'Swift',locked=set(data.index)).empty
    with pytest.raises(SearchLimit):
        constrained_build(data,'Swift',min_accuracy=1,max_states=0)


@pytest.mark.parametrize('bad',[{'plan_speed':-1},{'plan_accuracy':False},{'optimisation_filter_actions':['Gemmer']},{'plan_primary':[]},{'optimisation_show_substats':1}])
def test_portable_preferences_reject_invalid_values(bad):
    value=settings();value['filters']=bad
    with pytest.raises(ValueError): settings(value)
