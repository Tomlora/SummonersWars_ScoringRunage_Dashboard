"""Deterministic finite-stock allocation and bounded exact build search."""
from collections import Counter
import pandas as pd
from fonctions.analysis import rune_speed, SUBS


def grind_plan(runes, items, locked=(), sets=()):
    stock=Counter()
    for item in items:
        if type(item.get('amount')) is not int or item['amount'] < 0:
            raise ValueError('Invalid craft quantity')
        if item.get('craft_type') in (2,4,6):
            stock[(item['craft_type'],int(item['craft_type_id']))] += item['amount']
    candidates=[]
    for rune_id,row in runes.data.iterrows():
        if rune_id in locked or (sets and row['rune_set'] not in sets):
            continue
        ancient=str(row['qualité_original']).startswith('ANTIQUE')
        for sub in ('first','second','third','fourth'):
            stat=int(row[f'{sub}_sub'])
            value=float(row[f'{sub}_sub_grinded_value'])
            denominator=float(row[f'{sub}_sub_value_max'])
            if denominator <= 0:
                continue
            for (kind,code),amount in stock.items():
                set_code,stat_code,quality=code//10000,(code//100)%100,code%100
                if amount <= 0 or stat_code != stat or quality not in (4,5) or ancient != (kind==6):
                    continue
                if kind != 4 and runes.set.get(set_code) != row['rune_set']:
                    continue
                maximum=(runes.sub_max_lgd_antique if ancient else runes.sub_max_lgd) if quality==5 else (runes.sub_max_heroique_antique if ancient else runes.sub_max_heroique)
                target=maximum.get(stat,0)
                if target > value:
                    gain=(target-value)/denominator/2.8*100
                    candidates.append((gain,int(rune_id),sub,kind,code,value,target,runes.property[stat]))
    # Greedy highest marginal gain first; reserve at most one grind per rune/stat.
    # Ordinary stones win equal-gain ties, preserving wildcard stock when possible.
    candidates.sort(key=lambda x:(-x[0],x[3]==4,x[1],x[2],x[4]))
    used=set(); rows=[]
    for gain,rune_id,sub,kind,code,value,target,stat in candidates:
        if (rune_id,sub) in used or stock[kind,code] <= 0:
            continue
        used.add((rune_id,sub)); stock[kind,code]-=1
        rows.append({'id_rune':str(rune_id),'stat':stat,'craft_type':kind,'craft_type_id':code,
                     'quantity':1,'current_grind':value,'max_grind':target,'max_gain':round(gain,4)})
    return pd.DataFrame(rows,columns=['id_rune','stat','craft_type','craft_type_id','quantity','current_grind','max_grind','max_gain']),stock


def rune_accuracy(data):
    result=pd.Series(0.0,index=data.index)
    for key in SUBS:
        result += data[f'{key}_value_total'].where(data[key].isin([12,'ACC']),0)
    for key in ('main','innate'):
        result += data[f'{key}_value'].where(data[f'{key}_type'].isin([12,'ACC']),0)
    return result


class SearchLimit(ValueError):
    pass


def constrained_build(data, primary, secondary=None, min_speed=0, min_accuracy=0,
                      locked=(), slot2_speed=True, max_states=100000):
    """Maximize actual rune SPD under rune-only minima and set constraints.

    Dynamic programming retains max speed for each (set counts, capped accuracy).
    A hard state budget raises explicitly; it never reports false infeasibility.
    """
    data=data.loc[~data.index.isin(locked)].copy()
    if min_accuracy == 0:
        from fonctions.analysis import fastest_build
        build,total=fastest_build(data,primary,secondary,slot2_speed)
        if total is None or total < min_speed:
            return pd.DataFrame(columns=['id_rune','rune_slot','rune_set','spd','acc'])
        build=build.reset_index()
        build['acc']=build.id_rune.map(rune_accuracy(data))
        return build[['id_rune','rune_slot','rune_set','spd','acc']]
    if secondary:
        data=data[data.rune_set.isin([primary,secondary,'Intangible'])]
    data['spd']=rune_speed(data)+data.main_value.where(data.main_type.isin([8,'SPD']),0)
    data['acc']=rune_accuracy(data)
    data['id_rune']=data.index
    if slot2_speed:
        data=data[(data.rune_slot.astype(int)!=2)|data.main_type.isin([8,'SPD'])]
    names=sorted(set(data.rune_set)); positions={name:i for i,name in enumerate(names)}
    states={(tuple(0 for _ in names),0):(0,[])}
    four={'Fatal','Swift','Rage','Despair','Vampire','Violent'}
    for slot in range(1,7):
        candidates=data[data.rune_slot.astype(int)==slot].sort_values(['spd','acc','id_rune'],ascending=[False,False,True])
        # Per-set Pareto frontier: a slower, no-more-accurate rune cannot help.
        frontier=[]
        for _,group in candidates.groupby('rune_set',observed=True):
            accuracy=-1
            for row in group.to_dict('records'):
                if row['acc'] > accuracy:
                    frontier.append(row); accuracy=row['acc']
        updated={}
        for (counts,acc),(speed,rows) in states.items():
            for row in frontier:
                changed=list(counts); changed[positions[row['rune_set']]]+=1
                if row['rune_set']=='Intangible' and changed[positions['Intangible']]>1:
                    continue
                key=(tuple(changed),min(min_accuracy,acc+row['acc']))
                total=speed+row['spd']
                if key not in updated or total>updated[key][0]:
                    updated[key]=(total,rows+[row])
                if len(updated)>max_states:
                    raise SearchLimit('Recherche trop large : réduisez les sets candidats / Search limit reached; narrow candidate sets')
        states=updated
    best=None
    for (counts,acc),(speed,rows) in states.items():
        if acc < min_accuracy or speed < min_speed:
            continue
        counts=dict(zip(names,counts))
        eligible=[name for name,n in counts.items() if name!='Intangible' and n%(4 if name in four else 2)==(3 if name in four else 1)]
        completed=eligible[0] if counts.get('Intangible',0)==1 and len(eligible)==1 else None
        if counts.get(primary,0)+int(completed==primary)<4:
            continue
        if secondary and counts.get(secondary,0)+int(completed==secondary)<(6 if secondary==primary else 2):
            continue
        if best is None or speed>best[0]:
            best=(speed,rows)
    columns=['id_rune','rune_slot','rune_set','spd','acc']
    return pd.DataFrame(best[1],columns=columns) if best else pd.DataFrame(columns=columns)
