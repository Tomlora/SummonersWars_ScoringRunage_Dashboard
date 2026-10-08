import pandas as pd
import streamlit as st
from fonctions.access import require_saved_page
from fonctions.goals import (artifact_goals, save_goals, ARTIFACT_STATS,
    previous_goal_snapshot, artifact_progress)
from fonctions.goal_ui import goal_summary, goal_table
from fonctions.journey import tr
from fonctions.visuel import css, page_header

require_saved_page()
css()
page_header(tr('Objectifs d’artéfacts','Artifact goals'),tr('Suivez les effets qui vous manquent.','Track the effects you still need.'),icon='🎯')
saved=artifact_goals(st.session_state.id_joueur)
params={}
keys=dict(zip(ARTIFACT_STATS,('reduction','dmg_elem','crit_dmg','precision','soin','spd')))
labels={'REDUCTION':tr('Réduction des dégâts','Damage reduction'),'DMG ELEM':tr('Dégâts par élément','Element damage'),
        'CRIT DMG':tr('Dégâts critiques','Critical damage'),'PRECISION':tr('Précision','Accuracy'),
        'SOIN':tr('Soins','Healing'),'SPD':tr('Vitesse','Speed')}
with st.expander(tr('Définir mes objectifs','Set my goals')):
    st.caption(tr('Un objectif est atteint quand la meilleure valeur dépasse le seuil choisi. Les seuils sont exprimés en %.',
                  'A goal is reached when your best value exceeds the selected threshold. Thresholds are percentages.'))
    for group,dbkey in keys.items():
        maximum=60 if group=='SPD' else 30
        params[group]=st.slider(tr('Seuil','Threshold')+' '+group,10,maximum,max(10,min(maximum,int(saved[dbkey]))),key='goal_arte_'+dbkey)
        for stat,col in zip(('HP','ATK','DEF'),st.columns(3)):
            params[f'{group}_{stat}']=col.checkbox(stat,value=bool(saved[f'{dbkey}_{stat.lower()}']),key=f'{group}_{stat}')
    if st.button(tr('Enregistrer mes objectifs','Save my goals')):
        values={}
        for group,dbkey in keys.items():
            values[dbkey]=params[group]
            for stat in ('HP','ATK','DEF'):
                values[f'{dbkey}_{stat.lower()}']=params[f'{group}_{stat}']
        save_goals(st.session_state.id_joueur,'arte',values)
        st.success(tr('Vos objectifs sont enregistrés.','Your goals have been saved.'))

previous,date=previous_goal_snapshot(st.session_state.id_joueur,st.session_state.get('import_hash'),st.session_state.get('scoring_version'))
old=None
if previous is not None and 'goal_artifacts' in previous:
    old=pd.DataFrame(previous['goal_artifacts'],columns=['main_type','substat','arte_attribut','1'])
else:
    date=None
rows=artifact_progress(st.session_state.data_arte.df_top,params,old)
goal_summary(rows,date,'arte')
st.caption(tr('Chaque objectif associe une statistique principale, un effet et un attribut présents dans l’un des deux imports. La meilleure valeur est utilisée ; les anciennes lignes S3 et S4 sont regroupées.',
              'Each goal combines a main stat, effect and attribute found in either import. The best value is used; legacy S3 and S4 effects are merged.'))
if not rows.empty:
    for group,tab in zip(keys,st.tabs(list(labels.values()))):
        with tab:
            selected=rows[rows.group.eq(group)]
            if not selected.empty:
                st.progress(float(selected.progress.mean()/100),text=tr(f'{int(selected.achieved.sum())} / {len(selected)} objectifs atteints',
                                                                     f'{int(selected.achieved.sum())} / {len(selected)} goals reached'))
            goal_table(selected,'arte','goal_arte_view_'+keys[group])
