"""Conservative inventory-aware grind opportunities (no gem/reappraisal promises)."""
import pandas as pd

def grind_opportunities(runes, items):
    stock=[]
    for item in items:
        code=int(item.get('craft_type_id',0))
        if int(item.get('amount',0))>0 and item.get('craft_type') in (2,4,6):
            stock.append((code//10000,(code//100)%100,code%100,item['craft_type']))
    rows=[]
    for rune_id,row in runes.data.iterrows():
        ancient=str(row['qualité_original']).startswith('ANTIQUE')
        gain=0.0; available=[]; missing=[]
        for sub in ('first','second','third','fourth'):
            stat=int(row[f'{sub}_sub'])
            if stat not in runes.sub_max_lgd: continue
            value=int(row[f'{sub}_sub_grinded_value'])
            best=value
            matched=False
            for set_code,stat_code,quality,kind in stock:
                if stat_code!=stat or (kind!=4 and runes.set.get(set_code)!=row['rune_set']):continue
                if ancient!=(kind==6):continue
                if quality not in (4,5):continue
                target=(runes.sub_max_lgd_antique if ancient else runes.sub_max_lgd) if quality==5 else (runes.sub_max_heroique_antique if ancient else runes.sub_max_heroique)
                if target.get(stat,0)>best:
                    best=target[stat]; matched=True
            maximum=(runes.sub_max_lgd_antique if ancient else runes.sub_max_lgd).get(stat,0)
            label=runes.property[stat]
            if matched:
                available.append(label)
                denominator=float(row[f'{sub}_sub_value_max'])
                if denominator>0: gain+=(best-value)/denominator/2.8*100
            elif maximum>value:
                missing.append(label)
        rows.append({'Id rune':rune_id,'Gain avec stock (max)':round(gain,2),'Meules disponibles':', '.join(available),'Meules à obtenir':', '.join(missing)})
    return pd.DataFrame(rows,columns=['Id rune','Gain avec stock (max)','Meules disponibles','Meules à obtenir']).set_index('Id rune')
