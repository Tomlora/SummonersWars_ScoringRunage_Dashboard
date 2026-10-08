"""Versioned rune snapshots; no raw player export is stored."""
import json
from math import isfinite
from datetime import datetime, timezone
import pandas as pd
from sqlalchemy import text, inspect
from fonctions.access import require_user
from fonctions.gestion_bdd import connection
from params.coef import coef_set

SCHEMA_VERSION = 1
FIELDS = ('set_id','slot_no','occupied_id','class','rank','extra','upgrade_curr','pri_eff','prefix_eff','sec_eff')
DDL = '''CREATE TABLE IF NOT EXISTS sw_rune_snapshots (
 id_joueur BIGINT NOT NULL, payload_sha TEXT NOT NULL, scoring_version TEXT NOT NULL,
 date TEXT NOT NULL, imported_at TEXT NOT NULL, schema_version INTEGER NOT NULL,
 payload TEXT NOT NULL, PRIMARY KEY(id_joueur,payload_sha,scoring_version))'''


def snapshot(result):
    raw = result['data_json']
    all_runes = [*raw['runes'], *(r for unit in raw['unit_list'] for r in unit['runes'])]
    records = {}
    for rune in all_runes:
        row = result['data_rune'].data.loc[rune['rune_id']]
        efficiency = float(row['efficiency'])
        # Incomplete rune stats can yield NaN even in a valid export. Preserve
        # the missing value, with no score contribution, as in scoring_rune.
        efficiency = efficiency if isfinite(efficiency) else None
        tier = sum(efficiency >= edge for edge in (100,110,120)) if efficiency is not None else 0
        records[str(rune['rune_id'])] = {**{key:rune[key] for key in FIELDS},
            'efficiency':efficiency, 'points':tier * coef_set.get(row['rune_set'], 1)}
    return {'version':SCHEMA_VERSION, 'scoring_version':result['scoring_version'],
            'score':int(result['score']), 'runes':records}


def save_snapshot(conn, user_id, result, date):
    require_user(user_id)
    conn.execute(text(DDL))
    conn.execute(text('''INSERT INTO sw_rune_snapshots VALUES (:id,:sha,:scoring,:date,:at,:version,:payload)
        ON CONFLICT(id_joueur,payload_sha,scoring_version) DO NOTHING'''),
        {'id':int(user_id),'sha':result['import_hash'],'scoring':result['scoring_version'],'date':date,
         'at':datetime.now(timezone.utc).isoformat(), 'version':SCHEMA_VERSION,
         'payload':json.dumps(snapshot(result),allow_nan=False,separators=(',',':'))})


def list_snapshots(user_id):
    require_user(user_id)
    with connection() as conn:
        if not inspect(conn).has_table('sw_rune_snapshots'):
            return []
        return [dict(row) for row in conn.execute(text('''SELECT payload_sha,scoring_version,date,imported_at
            FROM sw_rune_snapshots WHERE id_joueur=:id ORDER BY imported_at,payload_sha'''), {'id':int(user_id)}).mappings()]


def load_snapshot(user_id, sha, version):
    require_user(user_id)
    with connection() as conn:
        payload = conn.execute(text('''SELECT payload FROM sw_rune_snapshots
          WHERE id_joueur=:id AND payload_sha=:sha AND scoring_version=:version'''),
          {'id':int(user_id),'sha':sha,'version':version}).scalar_one()
    return json.loads(payload)


def compare_snapshots(before, after):
    if before['version'] != SCHEMA_VERSION or after['version'] != SCHEMA_VERSION:
        raise ValueError('Format de comparaison incompatible / Incompatible snapshot format')
    if before['scoring_version'] != after['scoring_version']:
        raise ValueError('Versions de calcul différentes : scores non comparables / Different scoring versions')
    rows=[]
    for key in sorted(before['runes'].keys() | after['runes'].keys(), key=int):
        old,new=before['runes'].get(key),after['runes'].get(key)
        if old == new:
            continue
        improved = (old is not None and new is not None
                    and old['efficiency'] is not None and new['efficiency'] is not None
                    and new['efficiency'] > old['efficiency'])
        status = 'added' if old is None else 'removed' if new is None else 'improved' if improved else 'changed'
        changes = [field for field in FIELDS if old and new and old[field] != new[field]]
        rows.append({'id_rune':str(key),'status':status,'changes':', '.join(changes),
                     'efficiency_before':old['efficiency'] if old else None,
                     'efficiency_after':new['efficiency'] if new else None,
                     'score_delta':(new['points'] if new else 0)-(old['points'] if old else 0)})
    return pd.DataFrame(rows,columns=['id_rune','status','changes','efficiency_before','efficiency_after','score_delta'])
