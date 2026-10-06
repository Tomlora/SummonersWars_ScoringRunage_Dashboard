"""Database access with per-operation connections and an explicit import transaction."""
from contextlib import contextmanager
from contextvars import ContextVar
from os import environ
import re

import numpy as np
import pandas as pd
from streamlit import cache_resource, session_state
from sqlalchemy import create_engine, text, inspect

_active_connection = ContextVar('sw_connection', default=None)


@cache_resource
def init_connection(url=None):
    url = url or environ.get('API_SQL')
    if not url:
        raise RuntimeError('API_SQL is not configured')
    url = url.replace('postgresql://', 'postgresql+psycopg2://', 1).replace('postgres://', 'postgresql+psycopg2://', 1)
    options = {'connect_args': {'options': '-csearch_path=sw'}} if url.startswith('postgres') else {}
    return create_engine(url, pool_pre_ping=True, **options)


@contextmanager
def transaction():
    active = _active_connection.get()
    if active is not None:
        yield active
        return
    with init_connection().begin() as conn:
        token = _active_connection.set(conn)
        try:
            yield conn
        finally:
            _active_connection.reset(token)


@contextmanager
def connection():
    active = _active_connection.get()
    if active is not None:
        yield active
    else:
        with init_connection().connect() as conn:
            yield conn


def _identifier(value):
    if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*(\.[A-Za-z_][A-Za-z_0-9]*)?', value):
        raise ValueError('Invalid SQL identifier')
    return '.'.join('"' + part + '"' for part in value.split('.'))


def lire_bdd(nom_table, format='df', index=None, distinct=False):
    return lire_bdd_perso(f'SELECT {"DISTINCT " if distinct else ""}* FROM {_identifier(nom_table)}', format, index)


def lire_bdd_perso(requests, format='df', index_col='joueur', params=None):
    with connection() as conn:
        result = pd.read_sql(text(requests), con=conn, index_col=index_col, params=params).T
    return result.to_dict() if format == 'dict' else result


def sauvegarde_bdd(df, nom_table, methode_save='replace', dtype=None, index=True):
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df).T
    from fonctions.access import require_user
    for column in ('id', 'id_joueur'):
        if column in df:
            for user_id in df[column].dropna().unique():
                require_user(user_id)
    with transaction() as conn:
        df.to_sql(nom_table, con=conn, if_exists=methode_save, index=index, method='multi', chunksize=500, dtype=dtype)


def requete_perso_bdd(request, dict_params):
    from fonctions.access import require_user, require_account
    # Legacy page writes bind the internal owner as id/user_id/id_joueur.
    if 'sw_guilde' not in request and 'INSERT INTO sw_user' not in request:
        for key in ('id', 'user_id', 'id_joueur', 'joueur'):
            if key in dict_params and 'sw_' in request:
                require_user(dict_params[key])
    if 'account' in dict_params:
        require_account(dict_params['account'])
    with transaction() as conn:
        # Existing callers submit fixed multi-statement SQL with bound parameters.
        for statement in str(request).split(';'):
            if statement.strip():
                conn.execute(text(statement), dict_params)


def supprimer_bdd(nom_table):
    with transaction() as conn:
        conn.execute(text(f'DROP TABLE IF EXISTS {_identifier(nom_table)}'))


HISTORY_TABLES = {
    'sw': 'id', 'sw_score': 'id_joueur', 'sw_arte': 'id', 'sw_spd': 'id',
    'sw_detail': 'id', 'sw_max': 'id', 'sw_arte_max': 'id', 'sw_wb': 'id_joueur',
    'sw_pvp': 'id_joueur', 'sw_score_qual': 'id', 'sw_scoring_com2us': 'id',
    'sw_arte_substats': 'id', 'sw_imports': 'id_joueur',
}
ACCOUNT_TABLES = {'sw_arte_top': 'id', 'sw_build': 'id', 'sw_monsters': 'id',
                  'sw_objectifs_arte': 'id', 'sw_objectifs_rune': 'id', 'sw_todolist': 'id_joueur',
                  'sw_workspace': 'id_joueur'}


def _delete_account_rows(joueur, date=None, keep_rune_snapshots=False):
    from fonctions.access import require_user
    require_user(joueur)
    with transaction() as conn:
        inspector = inspect(conn)
        available = set(inspector.get_table_names())
        tables = dict(HISTORY_TABLES)
        if not keep_rune_snapshots:
            tables['sw_rune_snapshots'] = 'id_joueur'
        if date is None:
            tables.update(ACCOUNT_TABLES)
            tables['sw_user'] = 'id'  # parent last
        for table, column in tables.items():
            if table not in available:
                continue
            columns = {c['name'] for c in inspector.get_columns(table)}
            if column not in columns:
                # Legacy deployments may use the earlier quality key.
                if table == 'sw_score_qual' and 'id_joueur' in columns:
                    column = 'id_joueur'
                else:
                    raise ValueError(f'Unexpected account key in {table}')
            condition = ' AND date = :date' if date is not None else ''
            conn.execute(text(f'DELETE FROM {_identifier(table)} WHERE {_identifier(column)} = :id{condition}'), {'id': int(joueur), 'date': date})


def supprimer_data(joueur, date, keep_rune_snapshots=False):
    _delete_account_rows(joueur, date, keep_rune_snapshots)


def supprimer_data_all(joueur):
    _delete_account_rows(joueur)


def update_info_compte(joueur, guildeid, compteid):
    requete_perso_bdd('UPDATE sw_user SET guilde_id=:guild, joueur=:name WHERE joueur_id=:account', {'guild': guildeid, 'name': joueur, 'account': compteid})


def get_user(joueur, type='name_user', id_compte=0):
    from fonctions.access import require_account
    require_account(joueur if type == 'id' else id_compte)
    column = 'joueur_id' if type == 'id' else 'joueur'
    with transaction() as conn:
        row = conn.execute(text(f'SELECT id, guilde_id, visibility, joueur_id, rank FROM sw_user WHERE {column}=:player'), {'player': joueur}).mappings().first()
        if row is None or (type == 'name_user' and id_compte and row['joueur_id'] not in (0, id_compte)):
            raise IndexError('Unknown account')
        if row['joueur_id'] == 0:
            from fonctions.access import oidc_required
            if oidc_required():
                raise IndexError('Legacy account needs administrator binding')
            conn.execute(text('UPDATE sw_user SET joueur_id=:account WHERE id=:id'), {'account':id_compte,'id':row['id']})
        return row['id'], row['visibility'], row['guilde_id'], row['rank']


def cancel():
    # A transaction is rolled back by its context manager. Never touch another session.
    if _active_connection.get() is not None:
        raise RuntimeError('Abort the transaction by raising the original exception')


rollback = cancel


def optimisation_int(data, int_cols_before, int_cols_after='int16'):
    """Downcast only values that fit, preserving identifiers and missing values."""
    result = data.copy()
    for column in result.select_dtypes(include=int_cols_before).columns:
        if column in {'rune_equiped', 'arte_equiped'} or 'id' in str(column).lower():
            continue
        values = result[column]
        if int_cols_after.startswith('int'):
            bounds = np.iinfo(int_cols_after)
            if values.isna().any() or not values.between(bounds.min, bounds.max).all() or not (values % 1 == 0).all():
                continue
        result[column] = values.astype(int_cols_after)
    return result


def cleaning_only_guilde(x):
    x['private'] = int(x['visibility'] == 2 and x['guilde'] != session_state.guilde)
    return x


def get_number_row(table):
    with connection() as conn:
        return conn.execute(text(f'SELECT COUNT(*) FROM {_identifier(table)}')).scalar_one()
