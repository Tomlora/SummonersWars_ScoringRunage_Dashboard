"""Account-owned preferences and locks, portable as a versioned JSON document."""
import json
import math
from copy import deepcopy
from sqlalchemy import text, inspect
from fonctions.access import require_user
from fonctions.gestion_bdd import connection, transaction

PREFIXES = ('optimisation_filter_', 'optimisation_min_', 'optimisation_display',
            'optimisation_show_', 'optimisation_substat_', 'plan_')
DDL = '''CREATE TABLE IF NOT EXISTS sw_workspace (
 id_joueur BIGINT PRIMARY KEY, payload TEXT NOT NULL)'''


def settings(value=None):
    result = {'version':1, 'filters':{}, 'presets':{}, 'locked_runes':[], 'locked_monsters':[], 'locked_builds':[]}
    if value is None:
        return result
    if not isinstance(value, dict) or value.get('version') != 1:
        raise ValueError('Format de préférences incompatible / Incompatible preferences')
    for key in ('locked_runes','locked_monsters','locked_builds'):
        items = value.get(key, [])
        if not isinstance(items,list) or any(type(v) is not int or v <= 0 or v > 2**63-1 for v in items):
            raise ValueError('Identifiants de verrouillage invalides / Invalid lock IDs')
        result[key] = sorted(set(items))
    for key in ('filters','presets'):
        if not isinstance(value.get(key,{}),dict):
            raise ValueError('Invalid preferences')
    def clean(filters):
        enums={'optimisation_filter_priority':{'all','high','medium','low'},
               'optimisation_substat_display_mode':{'total','with_grind'},
               'optimisation_display_limit':{50,100,200,400},
               'plan_primary':{'Swift','Violent','Despair','Fatal','Rage','Vampire'},
               'plan_secondary':{'any','Will','Focus','Energy','Guard','Blade','Endure','Nemesis','Shield','Revenge','Destroy','Tolerance'}}
        lists={'optimisation_filter_sets','optimisation_filter_actions','optimisation_displayed_substats','optimisation_filtered_substats','plan_sets'}
        booleans={'optimisation_filter_equipped','optimisation_show_substats','plan_slot2'}
        result={}
        for k,v in filters.items():
            if k in enums:
                valid=isinstance(v,(str,int)) and v in enums[k]
            elif k in lists:
                valid=isinstance(v,list) and len(v)<=100 and all(isinstance(x,str) and len(x)<80 for x in v)
                if valid and k=='optimisation_filter_actions':
                    valid=set(v)<={'reappraisal','gem','legendary_grind','hero_grind','review'}
            elif k in booleans:
                valid=type(v) is bool
            elif k in ('plan_speed','plan_accuracy','optimisation_filter_gain') or k.startswith('optimisation_min_'):
                maximum={'plan_speed':400,'plan_accuracy':300}.get(k,100000)
                valid=type(v) in (int,float) and math.isfinite(v) and 0<=v<=maximum
                if k!='optimisation_filter_gain':
                    valid=valid and type(v) is int
            else:
                continue
            if not valid:
                raise ValueError(f'Invalid preference: {k}')
            result[k]=deepcopy(v)
        return result
    result['filters'] = clean(value.get('filters',{}))
    result['presets'] = {str(k)[:80]:clean(v) for k,v in value.get('presets',{}).items() if isinstance(v,dict)}
    # No NaN, arbitrary Python objects, or unbounded documents from portable imports.
    if len(json.dumps(result,allow_nan=False)) > 200000:
        raise ValueError('Preferences too large')
    return result


def load_settings(user_id):
    require_user(user_id)
    with connection() as conn:
        if not inspect(conn).has_table('sw_workspace'):
            return settings()
        value=conn.execute(text('SELECT payload FROM sw_workspace WHERE id_joueur=:id'),{'id':int(user_id)}).scalar()
    return settings(json.loads(value)) if value else settings()


def save_settings(user_id,value):
    require_user(user_id)
    value=settings(value)
    with transaction() as conn:
        conn.execute(text(DDL))
        conn.execute(text('''INSERT INTO sw_workspace VALUES (:id,:payload)
          ON CONFLICT(id_joueur) DO UPDATE SET payload=:payload'''),
          {'id':int(user_id),'payload':json.dumps(value,allow_nan=False)})


def current_settings():
    import streamlit as st
    if '_workspace' not in st.session_state:
        user_id=st.session_state.get('id_joueur')
        value=load_settings(user_id) if user_id is not None else settings()
        st.session_state['_workspace']=value
        st.session_state['saved_filter_presets']=deepcopy(value['presets'])
        st.session_state.update(deepcopy(value['filters']))
    return st.session_state['_workspace']


def save_current():
    import streamlit as st
    value=current_settings()
    value['filters'].update({k:st.session_state[k] for k in st.session_state if k.startswith(PREFIXES)})
    value['presets']=st.session_state.get('saved_filter_presets',{})
    value=settings(value)
    user_id=st.session_state.get('id_joueur')
    if user_id is not None:
        save_settings(user_id,value)
    st.session_state['_workspace']=value
    return value


def locked_ids(raw, preferences, builds=()):
    locked=set(preferences['locked_runes'])
    units=set(preferences['locked_monsters'])
    for unit in raw.get('unit_list',[]):
        if unit['unit_id'] in units:
            locked.update(r['rune_id'] for r in unit['runes'])
    for build in builds:
        if int(build['id_build']) in preferences['locked_builds']:
            locked.update(int(build[f'rune{i}']) for i in range(1,7) if build.get(f'rune{i}'))
    return locked


def saved_builds(user_id):
    require_user(user_id)
    with connection() as conn:
        if not inspect(conn).has_table('sw_build'):
            return []
        return [dict(row) for row in conn.execute(text('SELECT * FROM sw_build WHERE id=:id'),{'id':int(user_id)}).mappings()]


def active_locks():
    import streamlit as st
    user_id=st.session_state.get('id_joueur')
    prefs=current_settings()
    builds=saved_builds(user_id) if user_id is not None and prefs['locked_builds'] else []
    return locked_ids(st.session_state.data_json,prefs,builds)
