"""Shared presentation and history helpers for the account journey."""
import json
import pandas as pd
import streamlit as st
from sqlalchemy import inspect, text

SCORES = {'score_general': 'score', 'score_spd': 'score_spd', 'score_arte': 'score_arte', 'score_qual': 'score_qual'}


def tr(fr, en):
    return en if st.session_state.get('translations_selected') == 'English' else fr


def score_labels():
    return dict(zip(SCORES, [tr('Runes', 'Runes'), tr('Vitesse', 'Speed'), tr('Artéfacts', 'Artifacts'), tr('Qualité', 'Quality')]))


def dated(frame):
    return frame.assign(_date=pd.to_datetime(frame.date, dayfirst=True, format='mixed', errors='coerce')).sort_values('_date', kind='stable', na_position='first')


def period_rows(frame, days, end=None):
    if frame.empty:
        return frame.copy()
    result = dated(frame)
    end = end if end is not None else result._date.max()
    if days is not None:
        result = result[result._date.between(end - pd.Timedelta(days=days-1), end)]
    return result.drop(columns='_date')


def previous_report(conn, user_id):
    """Read the baseline inside the import transaction, before replacing a day."""
    if not inspect(conn).has_table('sw_score'):
        return None
    rows = pd.read_sql(text('SELECT date,score_general,score_spd,score_arte,score_qual FROM sw_score WHERE id_joueur=:id'), conn, params={'id':int(user_id)})
    if rows.empty:
        return None
    last = dated(rows).iloc[-1].drop(labels='_date').to_dict()
    versions = conn.execute(text('SELECT DISTINCT scoring_version FROM sw_imports WHERE id_joueur=:id AND date=:date'), {'id':int(user_id), 'date':last['date']}).scalars().all()
    last['scoring_version'] = versions[0] if len(versions) == 1 else None
    if inspect(conn).has_table('sw_rune_snapshots'):
        payload = conn.execute(text('SELECT payload FROM sw_rune_snapshots WHERE id_joueur=:id AND date=:date AND scoring_version=:version ORDER BY imported_at DESC LIMIT 1'), {'id':int(user_id), 'date':last['date'], 'version':last['scoring_version']}).scalar()
        last['snapshot'] = json.loads(payload) if payload else None
    return last


def import_summary(result, previous=None):
    from fonctions.snapshots import snapshot, compare_snapshots
    compatible = previous is not None and previous.get('scoring_version') == result['scoring_version']
    summary = {'scores':{column:int(result[key]) for column,key in SCORES.items()},
               'previous_date':previous.get('date') if previous else None, 'deltas':{}, 'changes':None}
    if compatible:
        summary['deltas'] = {column:int(result[key])-int(previous[column]) for column,key in SCORES.items()}
        if previous.get('snapshot'):
            changes = compare_snapshots(previous['snapshot'], snapshot(result))
            summary['changes'] = {status:int(changes.status.eq(status).sum()) for status in ('added','improved','changed','removed')}
    return summary


def show_import_summary(summary):
    st.subheader(tr('Bilan de l’import', 'Import summary'))
    for col,(key,label) in zip(st.columns(4), score_labels().items()):
        delta = summary['deltas'].get(key)
        col.metric(label, f"{summary['scores'][key]:,} pts".replace(',', ' '), None if delta is None else f'{delta:+d} pts')
    if summary['previous_date']:
        st.caption(tr('Comparaison au relevé du ', 'Compared with the report dated ') + summary['previous_date'])
        if not summary['deltas']:
            st.info(tr('Méthode précédente inconnue ou différente : écarts non calculés.', 'Previous scoring method unknown or different: changes are not calculated.'))
    else:
        st.caption(tr('Premier relevé disponible : les prochains imports permettront de mesurer la progression.', 'First available report: future imports will show progress.'))
    if summary['changes'] is not None:
        names = [tr('Nouvelles runes','New runes'),tr('Runes améliorées','Improved runes'),tr('Runes modifiées','Changed runes'),tr('Runes absentes','Missing runes')]
        for col,(key,label) in zip(st.columns(4), zip(('added','improved','changed','removed'), names)):
            col.metric(label, summary['changes'][key])
    else:
        st.caption(tr('Détail des anciennes runes indisponible pour cette comparaison.', 'Previous rune details unavailable for this comparison.'))


def deletion_preview(conn, user_id, date):
    from fonctions.access import require_user
    from fonctions.gestion_bdd import HISTORY_TABLES
    require_user(user_id)
    available = set(inspect(conn).get_table_names())
    counts = {}
    for table,column in {**HISTORY_TABLES, 'sw_rune_snapshots':'id_joueur'}.items():
        if table in available:
            cols = {c['name'] for c in inspect(conn).get_columns(table)}
            if table == 'sw_score_qual' and column not in cols:
                column = 'id_joueur'
            counts[table] = conn.execute(text(f'SELECT COUNT(*) FROM "{table}" WHERE "{column}"=:id AND date=:date'), {'id':int(user_id),'date':date}).scalar_one()
    return counts
