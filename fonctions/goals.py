"""Named defaults remain valid when database columns are reordered."""
from fonctions.access import require_user
from fonctions.gestion_bdd import lire_bdd_perso
import pandas as pd

RUNE_SETS = ('Violent', 'Destroy', 'Will', 'Despair', 'Swift', 'Nemesis')
RUNE_KEYS = tuple(f'{name}{tier}' for name in ('vio','destroy','will','despair','swift','nemesis') for tier in (100,110))
RUNE_DEFAULTS = (20,10,10,5,20,10,20,10,20,10,10,5)
ARTIFACT_STATS = {
    'REDUCTION': ['REDUCTION SUR '+element for element in ('FEU','EAU','VENT','LUMIERE','DARK')],
    'DMG ELEM': ['DMG SUR '+element for element in ('FEU','EAU','VENT','LUMIERE','DARK')],
    'CRIT DMG': ['CRIT DMG S1','CRIT DMG S2','CRIT DMG S3/S4','PREMIER HIT CRIT DMG'],
    'PRECISION': ['PRECISION S1','PRECISION S2','PRECISION S3'],
    'SOIN': ['SOIN S1','SOIN S2','SOIN S3'],
    'SPD': ['RENFORCEMENT SPD'],
}


def rune_goals(user_id):
    require_user(user_id)
    rows = lire_bdd_perso('SELECT * FROM sw_objectifs_rune WHERE id=:id', index_col='id', params={'id':int(user_id)}).T
    defaults = dict(zip(RUNE_KEYS, RUNE_DEFAULTS))
    if not rows.empty:
        defaults.update({key:int(value) for key,value in rows.iloc[0].items() if key in defaults and pd.notna(value)})
    return defaults


def save_goals(user_id, kind, values):
    """A settings save is atomic and scoped to the current account."""
    from sqlalchemy import text
    from fonctions.gestion_bdd import transaction
    require_user(user_id)
    if kind not in ('rune','arte'):
        raise ValueError('Invalid goal settings')
    allowed = set(RUNE_KEYS) if kind == 'rune' else set(artifact_goals(user_id))
    if set(values) != allowed:
        raise ValueError('Invalid goal settings')
    table = 'sw_objectifs_'+kind
    with transaction() as conn:
        conn.execute(text(f'DELETE FROM {table} WHERE id=:id'), {'id':int(user_id)})
        columns = ','.join('"'+key+'"' for key in values)
        placeholders = ','.join(':'+key for key in values)
        conn.execute(text(f'INSERT INTO {table}(id,{columns}) VALUES (:id,{placeholders})'), {'id':int(user_id),**values})


def previous_goal_snapshot(user_id, payload_sha, scoring_version):
    """Anchor to the displayed import, never a newer import or another account."""
    from fonctions.snapshots import list_snapshots, load_snapshot
    reports = list_snapshots(user_id)
    position = next((i for i,row in enumerate(reports)
                     if row['payload_sha']==payload_sha and row['scoring_version']==scoring_version), None)
    if position is None or position == 0:
        return None, None
    previous = reports[position-1]
    if previous['scoring_version'] != scoring_version:
        return None, None
    return load_snapshot(user_id, previous['payload_sha'], scoring_version), previous['imported_at']


def snapshot_rune_counts(payload, set_names):
    from fonctions.analysis import objective_counts
    rows = [{'rune_set':set_names.get(row['set_id']), 'rune_slot':row['slot_no'],
             'efficiency':row['efficiency']} for row in payload['runes'].values()]
    return objective_counts(pd.DataFrame(rows, columns=['rune_set','rune_slot','efficiency']))


def rune_progress(counts, targets, previous=None):
    """Keep the existing disjoint efficiency tiers; cap each slot separately."""
    keys = ['rune_set','efficience','rune_slot']
    current = counts.set_index(keys)['Quantité']
    old = previous.set_index(keys)['Quantité'] if previous is not None else None
    rows=[]
    for i,name in enumerate(RUNE_SETS):
        for j,tier in enumerate((100,110)):
            target = max(1,int(targets[RUNE_KEYS[i*2+j]]))
            for slot in range(1,7):
                key=(name,tier,slot)
                value=int(current.get(key,0))
                before=int(old.get(key,0)) if old is not None else None
                rows.append(dict(group=name,tier=tier,slot=slot,current=value,target=target,
                    remaining=max(0,target-value),progress=min(100,100*value/target),
                    achieved=value>=target,new=before is not None and before<target<=value,
                    delta=value-before if before is not None else None))
    return pd.DataFrame(rows)


def artifact_progress(top, params, previous=None):
    """Use best values, including merged legacy S3/S4. Missing known cells are zero.

    Keep the existing effect x attribute matrix for each selected main stat and
    group, using categories observed in either import. Both use today's settings.
    """
    keys=['main_type','substat','arte_attribut']
    def values(frame):
        if frame is None or frame.empty:
            return pd.Series(dtype=float, index=pd.MultiIndex.from_tuples([], names=keys))
        frame=frame.copy()
        frame['substat']=frame.substat.replace({'CRIT DMG S3':'CRIT DMG S3/S4','CRIT DMG S4':'CRIT DMG S3/S4'})
        return frame.groupby(keys,observed=True)['1'].max().fillna(0)
    current, old = values(top), values(previous)
    from itertools import product
    observed=current.index.union(old.index)
    rows=[]
    for main in ('HP','ATK','DEF'):
        for group,allowed_stats in ARTIFACT_STATS.items():
            if not params.get(f'{group}_{main}',False):
                continue
            cells=[key for key in observed if key[0]==main and key[1] in allowed_stats]
            stats=sorted({key[1] for key in cells})
            attributes=sorted({key[2] for key in cells})
            for stat,attribute in product(stats,attributes):
                key=(main,stat,attribute)
                value=float(current.get(key,0))
                before=float(old.get(key,0)) if previous is not None else None
                # Existing goals require a value strictly above the integer threshold.
                target=float(params[group])+1
                rows.append(dict(group=group,main=main,stat=stat,attribute=attribute,
                    current=value,target=target,remaining=max(0,target-value),
                    progress=min(100,100*value/target),achieved=value>=target,
                    new=before is not None and before<target<=value,
                    delta=value-before if before is not None else None))
    return pd.DataFrame(rows,columns=['group','main','stat','attribute','current','target','remaining','progress','achieved','new','delta'])


def artifact_goals(user_id):
    require_user(user_id)
    defaults={name:10 for name in ('reduction','dmg_elem','crit_dmg','precision','soin','spd')}
    defaults.update({f'{name}_{stat}':True for name in tuple(defaults) for stat in ('hp','atk','def')})
    rows=lire_bdd_perso('SELECT * FROM sw_objectifs_arte WHERE id=:id',index_col='id',params={'id':int(user_id)}).T
    if not rows.empty:
        defaults.update({key:value for key,value in rows.iloc[0].items() if key in defaults and pd.notna(value)})
    return defaults
