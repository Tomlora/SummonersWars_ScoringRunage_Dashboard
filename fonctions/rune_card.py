"""One rune presentation shared by recommendations, plans and tasks."""
import pandas as pd
import streamlit as st
from fonctions.journey import tr
from fonctions.rune_visual import rune_label, show_rune


def rune_card(runes, ids, key, gains=None, actions=True, gain_label=None):
    ids = list(dict.fromkeys(int(value) for value in ids if int(value) in runes.data.index))
    if gains is not None:
        gains = {int(value): gain for value, gain in gains.items()}
    if not ids:
        return
    labels = {value: rune_label(runes, value) for value in ids}
    if st.session_state.get(key) not in ids:
        st.session_state[key] = ids[0]
    selected = st.selectbox(tr('Rune à examiner','Rune to inspect'), ids, format_func=labels.get, key=key)
    row = runes.data.loc[selected]
    picture, information = st.columns([1.1, 1], gap='large')
    with picture:
        show_rune(runes, selected)
    with information:
        from fonctions.grind_efficiency import maximum_grind_efficiencies
        efficiency = row.efficiency
        hero, legendary = maximum_grind_efficiencies(runes, row)
        def value(number):
            return tr('Indisponible','Unavailable') if number is None or pd.isna(number) else f'{number:.2f}'
        current, planned = st.columns(2)
        current.metric(tr('Efficience actuelle (%)','Current efficiency (%)'), value(efficiency))
        gain = gains.get(selected) if gains is not None else row.get('gain')
        if gain is not None and pd.notna(gain):
            planned.metric(gain_label or tr('Gain maximal (points d’efficience)','Maximum gain (efficiency points)'), f'{gain:.2f}')
        epic_column, legendary_column = st.columns(2)
        eligibility=tr('Calcul disponible pour les runes 6★ de niveau +12 ou plus dont l’efficience est connue.', 'Available for 6-star runes at +12 or above with a known efficiency.')
        epic_column.metric(tr('Max. épique (%)','Max. hero grinds (%)'), value(hero), help=eligibility)
        legendary_column.metric(tr('Max. légendaire (%)','Max. legendary grinds (%)'), value(legendary), help=eligibility)
        st.caption(tr('Maxima avec les meilleurs jets de meules épiques (héroïques) ou légendaires, à statistiques actuelles et sans limite de stock. Une meule déjà meilleure est conservée. Le résultat réel reste aléatoire.', 'Maximum efficiency with the best hero or legendary grind rolls, using current substats and unlimited stock. Better existing grinds are kept. Actual rolls may be lower.'))
        with st.expander(tr('Détail des meules','Grind breakdown')):
            details = []
            for sub in ('first_sub','second_sub','third_sub','fourth_sub'):
                if row[sub] not in (0,'Aucun'):
                    stat = runes.property.get(row[sub], row[sub])
                    if stat in ('CRIT','DCC','RES','ACC'):
                        stat += ' (%)'
                    details.append({tr('Statistique','Stat'):stat, 'Base':row[f'{sub}_value'],tr('Meule','Grind'):row[f'{sub}_grinded_value'], 'Total':row[f'{sub}_value_total']})
            st.dataframe(pd.DataFrame(details),hide_index=True,width='stretch',height='content')
    with information:
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
