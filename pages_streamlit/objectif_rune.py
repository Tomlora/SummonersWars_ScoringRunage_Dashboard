import streamlit as st
from fonctions.access import require_saved_page
from fonctions.analysis import objective_counts
from fonctions.goals import (rune_goals, save_goals, RUNE_SETS, RUNE_KEYS,
    previous_goal_snapshot, snapshot_rune_counts, rune_progress)
from fonctions.goal_ui import goal_summary, goal_table
from fonctions.journey import tr
from fonctions.visuel import css, page_header

require_saved_page()
css()
page_header(tr('Objectifs de runes','Rune goals'),tr('Repérez les emplacements à renforcer.','See which slots need more runes.'),icon='🎯')
params=rune_goals(st.session_state.id_joueur)
with st.expander(tr('Définir mes objectifs','Set my goals')):
    st.caption(tr('Nombre de runes souhaité pour chaque emplacement. Les paliers sont distincts : 100 à moins de 110, puis 110 et plus.',
                  'Desired rune count for each slot. Tiers are separate: 100 to below 110, then 110 and above.'))
    for i,name in enumerate(RUNE_SETS):
        cols=st.columns(2)
        for j,tier in enumerate((100,110)):
            key=RUNE_KEYS[i*2+j]
            params[key]=cols[j].slider(f'{name} · '+('100–109.99' if tier==100 else '110+'),2,60,max(2,min(60,int(params[key]))),key='goal_'+key)
    if st.button(tr('Enregistrer mes objectifs','Save my goals')):
        save_goals(st.session_state.id_joueur,'rune',params)
        st.success(tr('Vos objectifs sont enregistrés.','Your goals have been saved.'))

previous,date=previous_goal_snapshot(st.session_state.id_joueur,st.session_state.get('import_hash'),st.session_state.get('scoring_version'))
old=snapshot_rune_counts(previous,st.session_state.data_rune.set_to_show) if previous else None
counts=objective_counts(st.session_state.data_rune.count_efficience_per_slot())
rows=rune_progress(counts,params,old)
goal_summary(rows,date,'rune')
st.caption(tr('Chaque objectif correspond à un set, un palier d’efficience et un emplacement. Un surplus sur un emplacement ne compense pas un manque sur un autre.',
              'Each goal covers one set, efficiency tier and slot. Extra runes in one slot do not make up for missing runes in another.'))
for tier,tab in zip((100,110),st.tabs([tr('Efficience 100 à <110','Efficiency 100 to <110'),tr('Efficience 110 et plus','Efficiency 110 and above')])):
    with tab:
        selected=rows[rows.tier.eq(tier)]
        cols=st.columns(3)
        for i,name in enumerate(RUNE_SETS):
            group=selected[selected.group.eq(name)]
            with cols[i%3]:
                st.metric(name,f'{int(group.achieved.sum())} / 6',help=tr('Emplacements ayant atteint leur objectif','Slots that reached their goal'))
                st.progress(float(group.progress.mean()/100),text=tr(f'{int(group.remaining.sum())} runes manquantes',f'{int(group.remaining.sum())} runes missing'))
        goal_table(selected,'rune',f'goal_rune_view_{tier}')
