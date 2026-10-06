"""Validate and analyse an export before writing a single atomic snapshot."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import json
from time import perf_counter
from zoneinfo import ZoneInfo

import pandas as pd
from sqlalchemy import text, inspect

from fonctions.analysis import SCORING_VERSION
from fonctions.runes import Rune
from fonctions.artefact import Artefact
from fonctions.gestion_bdd import transaction, get_user, requete_perso_bdd, sauvegarde_bdd, supprimer_data, update_info_compte
from params.coef import coef_set, coef_set_spd, liste_substat_arte


class InvalidExport(ValueError):
    pass


def validate_export(raw):
    try:
        data = json.loads(raw) if isinstance(raw, (bytes, str)) else deepcopy(raw)
        if not isinstance(data, dict):
            raise ValueError('Expected an object')
        from fonctions.validation import validate_values, validate_inventory
        validate_values(data)
        wizard = data['wizard_info']
        if not isinstance(wizard['wizard_name'], str) or not wizard['wizard_name'].strip():
            raise ValueError('wizard_name')
        if not isinstance(wizard['wizard_id'], int) or wizard['wizard_id'] <= 0:
            raise ValueError('wizard_id')
        for key in ('runes', 'unit_list'):
            if not isinstance(data[key], list):
                raise ValueError(key)
        data.setdefault('artifacts', [])
        data.setdefault('rune_craft_item_list', [])
        for key in ('artifacts', 'rune_craft_item_list'):
            if not isinstance(data[key], list):
                raise ValueError(key)
        runes = list(data['runes'])
        artifacts = list(data['artifacts'])
        for unit in data['unit_list']:
            for key in ('unit_id', 'unit_master_id'):
                if not isinstance(unit[key], int):
                    raise ValueError(key)
            for key in ('runes', 'artifacts'):
                value = unit.get(key, [])
                if isinstance(value, dict):
                    value = list(value.values())
                if not isinstance(value, list):
                    raise ValueError(key)
                unit[key] = value
            runes.extend(unit['runes'])
            artifacts.extend(unit['artifacts'])
            slots = [r['slot_no'] for r in unit['runes']]
            if len(slots) != len(set(slots)):
                raise ValueError('duplicate equipped slots')
        for rune in runes:
            for key in ('rune_id', 'set_id', 'slot_no', 'occupied_id', 'class', 'rank', 'extra', 'upgrade_curr'):
                if not isinstance(rune[key], int):
                    raise ValueError(key)
            if not 1 <= rune['slot_no'] <= 6 or not 0 <= rune['upgrade_curr'] <= 15:
                raise ValueError('slot or level')
            for key in ('pri_eff', 'prefix_eff'):
                if len(rune[key]) != 2 or not all(isinstance(x, (int, float)) for x in rune[key]):
                    raise ValueError(key)
            required = min(rune['upgrade_curr'] // 3, 4)
            if len(rune['sec_eff']) < required or any(len(s) < 4 or not all(isinstance(v, (int, float)) for v in s[:4]) for s in rune['sec_eff']):
                raise ValueError('sec_eff')
        for arte in artifacts:
            for key in ('rid', 'type', 'attribute', 'occupied_id', 'unit_style', 'level'):
                if not isinstance(arte[key], int):
                    raise ValueError(key)
            if len(arte['pri_effect']) < 2 or len(arte['sec_effects']) < min(arte['level']//3, 4):
                raise ValueError('artifact effects')
        validate_inventory(data, runes, artifacts)
        return data
    except (KeyError, TypeError, ValueError, IndexError, UnicodeError) as error:
        raise InvalidExport('Export JSON incompatible / incompatible JSON export: ' + str(error)) from error


def fingerprint(data):
    return sha256(json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def monster_frame(data, reference):
    names = reference.set_index('com2us_id')['name'].to_dict() if not reference.empty else {}
    rows = []
    fields = {'class': '*', 'unit_level': 'level', 'atk': 'atk', 'def': 'def', 'spd': 'spd', 'resist': 'resist', 'accuracy': 'accuracy', 'critical_rate': 'CRIT', 'critical_damage': 'DCC', 'create_time': 'Date_invocation'}
    for unit in data['unit_list']:
        row = {'id_unit': unit['unit_id'], 'id_monstre': unit['unit_master_id'], 'name_monstre': names.get(unit['unit_master_id'], f"#{unit['unit_master_id']}")}
        row.update({target: unit.get(key, 0) for key, target in fields.items()})
        row.update({f'Rune{i}': 0 for i in range(1, 7)})
        row.update({f"Rune{r['slot_no']}": r['rune_id'] for r in unit['runes']})
        rows.append(row)
    return pd.DataFrame(rows, columns=['id_unit', 'id_monstre', *fields.values(), *[f'Rune{i}' for i in range(1,7)], 'name_monstre'])


def analyse_export(data, reference, progress=lambda message: None):
    started = perf_counter()
    reference = reference.copy()
    for column in ['com2us_id','name','image_filename','element','natural_stars','awaken_level']:
        if column not in reference: reference[column] = pd.Series(dtype='object')
    reference['url'] = 'https://swarfarm.com/static/herders/images/monsters/' + reference['image_filename'].fillna('')
    wizard = data['wizard_info']
    guild = (data.get('guild') or {}).get('guild_info') or {}
    pvp = data.get('pvp_info') or {}
    wb = data.get('my_worldboss_best_ranking') or {}
    result = dict(data_json=data, swarfarm=reference, pseudo=wizard['wizard_name'], compteid=wizard['wizard_id'],
                  guilde=guild.get('name', 'Aucune'), guildeid=guild.get('guild_id', 0), lang=wizard.get('wizard_last_country', ''),
                  mana=wizard.get('wizard_mana', 0), arena_win=pvp.get('arena_win', 0), arena_lose=pvp.get('arena_lose', 0),
                  rank_wb=wb.get('ranking'), dmg_wb=wb.get('accumulate_damage'), import_hash=fingerprint(data), scoring_version=SCORING_VERSION)
    result['df_mobs'] = monster_frame(data, reference)
    collection = result['df_mobs'].copy()
    if not reference.empty:
        collection = collection.merge(reference, left_on='id_monstre', right_on='com2us_id', how='left')
        collection['element_number'] = collection['element'].map({'Fire':0,'Water':1,'Wind':2,'Light':3,'Dark':4})
        collection['url'] = 'https://swarfarm.com/static/herders/images/monsters/' + collection['image_filename'].fillna('')
    result['df_mobs_name_all'] = collection

    monsters = result['df_mobs'].set_index('id_unit')['name_monstre'].to_dict()
    result['identification_monsters'] = monsters
    progress('Runes')
    runes = result['data_rune'] = Rune(data, monsters)
    result['set_rune'] = sorted(runes.set_to_show.values())
    result['tcd'], result['score'] = runes.scoring_rune(list(coef_set), coef_set)
    result['tcd_detail_score'] = runes.tcd_df_efficiency.copy()
    result['tcd_spd'], result['score_spd'] = runes.scoring_spd(list(coef_set_spd), coef_set_spd)
    result['df_scoring_com2us_summary'] = runes.scoring_com2us()
    result['data_avg'] = runes.calcul_efficiency_describe()
    result['df_scoring_quality'], result['score_qual'] = runes.score_quality(coef_set_spd)
    result['df_quality'], result['df_quality_per_slot'] = runes.data_qual, runes.data_qual_per_slot
    result['df_max'] = runes.calcul_value_max()
    result['df_max_slot'] = runes.calcul_value_max_per_slot()
    progress('Vitesse / Speed')
    result['best_speeds'] = {f'spd_{short}_{suffix}': runes.optimisation_max_speed(name, secondary)[1]
        for name, short in [('Violent', 'vio'), ('Swift', 'swift'), ('Despair', 'despair')]
        for secondary, suffix in [(None, 'broken'), ('Will', 'will')]}
    progress('Artéfacts / Artifacts')
    arte = result['data_arte'] = Artefact(data, monsters)
    result['tcd_arte'], result['score_arte'] = arte.scoring_arte()
    arte.calcul_value_max()
    arte.top()
    result['arte_count'] = pd.DataFrame([{'substat': stat, **{f'count{n}': arte.count_substat(stat,n)[1] for n in (2,3,4)}} for stat in liste_substat_arte])
    result['analysis_seconds'] = perf_counter() - started
    return result


def persist_analysis(result, date=None, progress=lambda message: None):
    from fonctions.access import require_account
    require_account(result['compteid'])
    date = date or datetime.now(ZoneInfo('Europe/Paris')).strftime('%d/%m/%Y')
    with transaction() as conn:
        if conn.dialect.name == 'postgresql':
            conn.execute(text('SELECT pg_advisory_xact_lock(:account)'), {'account': int(result['compteid'])})
        conn.execute(text('CREATE TABLE IF NOT EXISTS sw_imports (id_joueur BIGINT NOT NULL, payload_sha TEXT NOT NULL, scoring_version TEXT NOT NULL, date TEXT NOT NULL, PRIMARY KEY(id_joueur, payload_sha, scoring_version))'))
        requete_perso_bdd('INSERT INTO sw_guilde(guilde,guilde_id) VALUES (:name,:id) ON CONFLICT(guilde_id) DO NOTHING', {'name':result['guilde'],'id':result['guildeid']})
        try:
            user = get_user(result['compteid'], type='id')
        except IndexError:
            from fonctions.access import oidc_required
            try:
                if oidc_required():
                    raise IndexError('Strict account binding')
                user = get_user(result['pseudo'], id_compte=result['compteid'])
            except IndexError:
                requete_perso_bdd('INSERT INTO sw_user(joueur,visibility,guilde_id,joueur_id) VALUES (:name,0,:guild,:account)', {'name':result['pseudo'],'guild':result['guildeid'],'account':result['compteid']})
                user = get_user(result['compteid'], type='id')
        user_id, visibility, _, rank = user
        from fonctions.journey import previous_report, import_summary
        summary = import_summary(result, previous_report(conn, user_id))
        params = {'id': int(user_id), 'sha': result['import_hash'], 'version': SCORING_VERSION}
        previous = conn.execute(text('SELECT date FROM sw_imports WHERE id_joueur=:id AND payload_sha=:sha AND scoring_version=:version'), params).scalar()
        metadata = dict(id_joueur=user_id, visibility=visibility, rank=rank, report_date=previous or date)
        result['import_summary'] = summary
        if previous:
            from fonctions.snapshots import save_snapshot
            progress('Sauvegarde du détail des runes / Saving rune details')
            save_snapshot(conn,user_id,result,previous)
            return metadata, False
        # One complete snapshot per account/day, preserving earlier days.
        progress('Sauvegarde des scores / Saving scores')
        supprimer_data(user_id, date, keep_rune_snapshots=True)
        def save(frame, table, index=True, latest=False):
            data = frame.copy()
            data['id'], data['date'] = user_id, date
            if latest and inspect(conn).has_table(table):
                requete_perso_bdd(f'DELETE FROM {table} WHERE id=:id', {'id':user_id})
            sauvegarde_bdd(data, table, 'append', index=index)
        save(result['tcd'], 'sw')
        save(result['df_scoring_com2us_summary'], 'sw_scoring_com2us')
        save(result['df_scoring_quality'], 'sw_score_qual')
        detail = result['tcd_detail_score'].copy()
        avg = result['data_avg']
        for target, source in [('moyenne','moyenne'), ('max','max'), ('mediane','mediane'), ('nb','Nombre runes')]:
            detail[target] = avg[source]
        values = result['data_rune'].data['efficiency']
        detail.loc['Total', ['moyenne','max','mediane','nb']] = [values.mean(), values.max(), values.median(), len(values)]
        save(detail, 'sw_detail')
        save(result['tcd_spd'], 'sw_spd')
        save(result['tcd_arte'], 'sw_arte')
        save(result['data_arte'].df_max, 'sw_arte_max', latest=True)
        save(result['df_max'], 'sw_max', latest=True)
        save(result['arte_count'], 'sw_arte_substats', index=False)
        top = result['data_arte'].df_top.drop(columns='main_type').copy()
        top['id'] = user_id
        if inspect(conn).has_table('sw_arte_top'):
            requete_perso_bdd('DELETE FROM sw_arte_top WHERE id=:id', {'id': user_id})
        sauvegarde_bdd(top, 'sw_arte_top', 'append', index=False)
        score = dict(id_joueur=user_id, date=date, score_general=int(result['score']), score_spd=int(result['score_spd']), score_arte=int(result['score_arte']), score_qual=int(result['score_qual']), mana=int(result['mana']), **result['best_speeds'])
        sauvegarde_bdd(pd.DataFrame([score]), 'sw_score', 'append', index=False)
        sauvegarde_bdd(pd.DataFrame([dict(id_joueur=user_id,date=date,win=result['arena_win'],lose=result['arena_lose'])]), 'sw_pvp','append',index=False)
        sauvegarde_bdd(pd.DataFrame([dict(id_joueur=user_id,date=date,rank=result['rank_wb'],damage=result['dmg_wb'])]), 'sw_wb','append',index=False)
        monsters = result['df_mobs'].groupby('id_monstre').size().rename('quantité').reset_index()
        monsters['storage'] = False
        storage = pd.DataFrame(result['data_json'].get('unit_storage_list', []))
        if not storage.empty:
            storage = storage.rename(columns={'unit_master_id':'id_monstre','quantity':'quantité'})
            storage['storage'] = True
            monsters = pd.concat([monsters,storage[['id_monstre','quantité','storage']]],ignore_index=True)
        monsters['id'] = user_id
        if inspect(conn).has_table('sw_monsters'):
            requete_perso_bdd('DELETE FROM sw_monsters WHERE id=:id', {'id':user_id})
        sauvegarde_bdd(monsters,'sw_monsters','append',index=False)
        update_info_compte(result['pseudo'],result['guildeid'],result['compteid'])
        requete_perso_bdd('UPDATE sw_user SET lang=:lang WHERE id=:id', {'id':user_id,'lang':result['lang']})
        conn.execute(text('INSERT INTO sw_imports(id_joueur,payload_sha,scoring_version,date) VALUES (:id,:sha,:version,:date)'), {**params,'date':date})
        from fonctions.snapshots import save_snapshot
        progress('Sauvegarde du détail des runes / Saving rune details')
        save_snapshot(conn, user_id, result, date)
        progress('Validation de la transaction / Committing transaction')
    return metadata, True


def publish_analysis(state, result, metadata):
    # Clear widget/cached views only after the new import committed successfully.
    preferences = {k:state[k] for k in ('translations_selected','translations','langue') if k in state}
    if state.get('compteid') == result['compteid']:
        from fonctions.workspace import PREFIXES
        preferences.update({k:state[k] for k in state if k in ('_workspace','saved_filter_presets') or k.startswith(PREFIXES)})
    for key in list(state):
        if key not in {'upload_file','upload_submit'}:
            del state[key]
    state.update(preferences)
    state.update(result)
    state.update(metadata)
    state['tcd'] = result['tcd'].assign(date=metadata['report_date'], id=metadata['id_joueur'])
    state['analysis_ready'] = state['submitted'] = True
