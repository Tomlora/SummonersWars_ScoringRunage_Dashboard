"""Save only edited rune tasks, atomically, without erasing hidden tasks."""
import pandas as pd
from sqlalchemy import inspect, text
from fonctions.access import require_user
from fonctions.gestion_bdd import connection, transaction

FIELDS={'notes':"TEXT DEFAULT ''",'stat_to_replace':"TEXT DEFAULT ''",'stat_objectif':"TEXT DEFAULT ''",'fait':'BOOLEAN DEFAULT FALSE'}


def load_tasks(user_id):
    require_user(user_id)
    with connection() as conn:
        if not inspect(conn).has_table('sw_todolist'):
            return pd.DataFrame(columns=list(FIELDS),index=pd.Index([],name='id_rune'))
        data=pd.read_sql(text('SELECT * FROM sw_todolist WHERE id_joueur=:id'),conn,params={'id':int(user_id)})
    if 'notes' not in data and 'note' in data:
        data=data.rename(columns={'note':'notes'})
    return data.drop_duplicates('id_rune',keep='last').set_index('id_rune').reindex(columns=list(FIELDS)).fillna({'notes':'','stat_to_replace':'','stat_objectif':'','fait':False})


def save_tasks(user_id, edited):
    require_user(user_id)
    with transaction() as conn:
        conn.execute(text('CREATE TABLE IF NOT EXISTS sw_todolist (id_joueur BIGINT NOT NULL,id_rune BIGINT NOT NULL,notes TEXT,stat_to_replace TEXT,stat_objectif TEXT,fait BOOLEAN)'))
        columns={c['name'] for c in inspect(conn).get_columns('sw_todolist')}
        for name,definition in FIELDS.items():
            if name not in columns:
                conn.execute(text(f'ALTER TABLE sw_todolist ADD COLUMN {name} {definition}'))
                if name=='notes' and 'note' in columns:
                    conn.execute(text("UPDATE sw_todolist SET notes=COALESCE(note,'')"))
        for rune_id,row in edited.iterrows():
            params={'id':int(user_id),'rune':int(rune_id),**{key:(bool(row[key]) if pd.notna(row[key]) else False) if key=='fait' else (str(row[key]) if pd.notna(row[key]) else '') for key in FIELDS}}
            conn.execute(text('DELETE FROM sw_todolist WHERE id_joueur=:id AND id_rune=:rune'),params)
            if params['fait'] or any(params[key].strip() for key in FIELDS if key!='fait'):
                conn.execute(text('INSERT INTO sw_todolist (id_joueur,id_rune,notes,stat_to_replace,stat_objectif,fait) VALUES (:id,:rune,:notes,:stat_to_replace,:stat_objectif,:fait)'),params)
