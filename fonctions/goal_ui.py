"""Readable progress shared by rune and artifact objectives."""
import pandas as pd
import streamlit as st
from fonctions.journey import tr


def goal_summary(rows, previous_date, kind):
    if rows.empty:
        st.info(tr('Aucun objectif à afficher avec ces catégories. Activez une statistique principale dans les paramètres.',
                   'No goals for these categories. Enable a main stat in settings.'))
        return
    completed=int(rows.achieved.sum())
    columns=st.columns(3)
    columns[0].metric(tr('Objectifs atteints','Goals reached'),f'{completed} / {len(rows)}')
    columns[1].metric(tr('Objectifs restants','Goals remaining'),len(rows)-completed)
    columns[2].metric(tr('Nouveaux objectifs atteints','Newly reached goals'),int(rows.new.sum()) if previous_date else '—')
    st.progress(completed/len(rows),text=tr('Part des objectifs atteints','Share of goals reached'))
    if previous_date:
        date=pd.to_datetime(previous_date,utc=True).tz_convert('Europe/Paris').strftime('%d/%m/%Y %H:%M')
        st.caption(tr(f'Comparaison avec l’import du {date}. Les deux imports sont évalués avec les paramètres actuels.',
                      f'Compared with the import on {date}. Both imports use the current goal settings.'))
        if rows.new.any():
            count=int(rows.new.sum())
            st.success(tr('Un nouvel objectif atteint depuis cet import.', 'One new goal reached since that import.')
                       if count==1 else tr(f'{count} nouveaux objectifs atteints depuis cet import.',
                                            f'{count} new goals reached since that import.'))
    else:
        st.info(tr('Les nouveaux objectifs atteints seront affichés dès qu’un import précédent comparable sera disponible.' +
                   (' Les anciens instantanés ne contiennent pas le détail des artéfacts.' if kind=='arte' else ''),
                   'Newly reached goals will appear when a comparable previous import is available.' +
                   (' Older snapshots do not contain artifact details.' if kind=='arte' else '')))


def goal_table(rows, kind, key):
    if rows.empty:
        st.info(tr('Aucune catégorie disponible.','No categories available.'))
        return
    labels={'all':tr('Tous','All'),'remaining':tr('À atteindre','Remaining'),
            'new':tr('Nouveaux objectifs atteints','Newly reached goals')}
    mode=st.radio(tr('Afficher','Show'),list(labels),format_func=labels.get,
        horizontal=True,key=key)
    shown=rows.copy()
    if mode=='remaining': shown=shown[~shown.achieved]
    if mode=='new': shown=shown[shown.new]
    if shown.empty:
        st.info(tr('Aucun objectif dans cette sélection.','No goals in this selection.'))
        return
    shown['status']=shown.apply(lambda r:tr('Nouveau ✓','New ✓') if r['new'] else tr('Atteint','Reached') if r.achieved else tr('En cours','In progress'),axis=1)
    if kind=='arte' and st.session_state.get('translations_selected')=='English':
        from fonctions.artefact import dataframe_replace_to_english, dict_arte_effect_english
        shown['stat']=shown.stat.replace(dict_arte_effect_english)
        shown['attribute']=shown.attribute.replace(dataframe_replace_to_english)
    columns=['group','slot'] if kind=='rune' else ['main','stat','attribute']
    columns+=['current','target','remaining','progress','status']
    if shown.delta.notna().any(): columns+=['delta']
    config={'group':'Set','slot':tr('Emplacement','Slot'),'main':tr('Principale','Main stat'),
        'stat':tr('Effet','Effect'),'attribute':tr('Attribut','Attribute'),
        'current':tr('Runes possédées','Runes owned') if kind=='rune' else tr('Meilleure valeur (%)','Best value (%)'),
        'target':tr('Objectif','Target') if kind=='rune' else tr('Valeur à atteindre (%)','Target value (%)'),
        'remaining':tr('Runes manquantes','Runes missing') if kind=='rune' else tr('Points manquants','Points missing'),
        'progress':st.column_config.ProgressColumn(tr('Progression','Progress'),min_value=0,max_value=100,format='%.0f %%'),
        'status':tr('État','Status'),
        'delta':st.column_config.NumberColumn(tr('Depuis l’import précédent','Since previous import'),format='%+g')}
    st.dataframe(shown[columns],column_config=config,hide_index=True,width='stretch',height='content')
