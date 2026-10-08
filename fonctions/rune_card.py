"""One rune presentation shared by recommendations, plans and tasks."""
import pandas as pd
import streamlit as st
from fonctions.journey import tr
from fonctions.rune_visual import rune_label, show_rune


def rune_card(runes, ids, key, gains=None, actions=True):
    ids = list(dict.fromkeys(int(value) for value in ids if int(value) in runes.data.index))
    if not ids:
        return
    labels = {value: rune_label(runes, value) for value in ids}
    if st.session_state.get(key) not in ids:
        st.session_state[key] = ids[0]
    selected = st.selectbox(tr('Rune à examiner','Rune to inspect'), ids, format_func=labels.get, key=key)
    row = runes.data.loc[selected]
    show_rune(runes, selected)
    def stat(code):
        label = runes.property.get(code, code)
        if label in (0,'Aucun'):
            return tr('Aucune','None')
        return f'{label} (%)' if label in ('CRIT','DCC','RES','ACC') else label
    st.write(tr('Principale','Main stat') + f" : {stat(row.main_type)} +{row.main_value:g}")
    if row.innate_type not in (0,'Aucun'):
        st.write(tr('Innée','Innate stat') + f" : {stat(row.innate_type)} +{row.innate_value:g}")
    columns = st.columns(2)
    efficiency = row.efficiency
    columns[0].metric(tr('Efficience (%)','Efficiency (%)'), tr('Indisponible','Unavailable') if pd.isna(efficiency) else f'{efficiency:.2f}')
    gain = gains.get(selected) if gains is not None else row.get('gain')
    if gain is not None and pd.notna(gain):
        columns[1].metric(tr('Gain maximal (points d’efficience)','Maximum gain (efficiency points)'),f'{gain:.2f}')
    st.caption(tr('Gain théorique, sans garantie de résultat. Les statistiques en % restent exprimées en points de pourcentage.', 'Theoretical gain, not a guaranteed result. Percentage stats are expressed in percentage points.'))
    details = []
    for sub in ('first_sub','second_sub','third_sub','fourth_sub'):
        if row[sub] not in (0,'Aucun'):
            details.append({tr('Statistique','Stat'):stat(row[sub]), 'Base':row[f'{sub}_value'],tr('Meule','Grind'):row[f'{sub}_grinded_value'], 'Total':row[f'{sub}_value_total']})
    st.dataframe(pd.DataFrame(details),hide_index=True,width='stretch',height='content')
    if actions:
        from fonctions.workspace import current_settings, save_current, active_locks
        preferences = current_settings()
        if selected in active_locks():
            st.caption(tr('Cette rune est protégée. Gérez ses verrous dans Planification.', 'This rune is protected. Manage its locks in Planning.'))
        elif st.button(tr('Protéger cette rune','Protect this rune'),key='action_'+key+'_lock'):
            preferences['locked_runes'].append(selected)
            st.session_state.pop('locks_runes',None)
            save_current()
            st.rerun()
        if st.session_state.get('id_joueur') is not None:
            if st.button(tr('Ouvrir dans mes tâches','Open in my tasks'),key='action_'+key+'_task'):
                st.session_state.ui_task_rune=selected
                st.session_state.ui_task_query=''
                st.session_state.ui_task_only=False
                st.switch_page('pages_streamlit/todolist.py')
        if st.button(tr('Gérer les verrous','Manage locks'),key='action_'+key+'_planning'):
            st.switch_page('pages_streamlit/planning.py')
