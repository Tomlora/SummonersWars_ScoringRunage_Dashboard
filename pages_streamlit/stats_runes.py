"""Local rune statistics; only compute the selected view."""
import pandas as pd
import plotly.express as px
import streamlit as st
from fonctions.visuel import css, page_header, apply_plotly_theme
from fonctions.analysis import substat_table

def stats_runage():
    css()
    en = st.session_state.get('translations_selected') == 'English'
    def tr(fr, en_text): return en_text if en else fr
    page_header(tr('Statistiques des runes','Rune statistics'), tr('Explorez votre compte, par set et par slot.','Explore your account by set and slot.'), icon='📊')
    runes = st.session_state.data_rune
    data = runes.data.copy()
    if data.empty:
        st.info(tr('Aucune rune dans ce compte.','No runes in this account.'))
        return
    selected = st.selectbox('Set', sorted(data.rune_set.unique()), index=None)
    slot = st.selectbox('Slot', list(range(1,7)), index=None)
    if selected: data = data[data.rune_set == selected]
    if slot: data = data[data.rune_slot == slot]
    if data.empty:
        st.info(tr('Aucune rune pour ces filtres.','No runes match these filters.'))
        return
    view = st.segmented_control(tr('Vue','View'), ['Efficience','Top 10','Substats / Slot','Efficience / Slot','Qualité'], default='Efficience')
    if view == 'Efficience':
        runes.calcul_potentiel()
        data = runes.data_grind.loc[data.index.intersection(runes.data_grind.index)].sort_values('efficiency',ascending=False)
        if data.empty:
            st.info(tr('Aucune rune +12 ou +15 pour cette sélection.','No +12 or +15 rune for this selection.'))
            return
        top = st.number_input(tr('Nombre de runes','Number of runes'), 1, len(data), min(50,len(data)))
        shown = data.head(top).reset_index()
        st.plotly_chart(apply_plotly_theme(px.line(shown, y=['efficiency','efficiency_max_hero','efficiency_max_lgd'])),width='stretch')
        st.caption(tr('Les courbes suivent les mêmes runes, triées par efficience actuelle. Le potentiel est théorique.','Curves follow the same runes, sorted by current efficiency. Potential is theoretical.'))
        st.dataframe(shown,width='stretch',hide_index=True)
    elif view == 'Top 10':
        from fonctions.analysis import best_substats
        maxima = best_substats(substat_table(data, runes.property)).reset_index()
        st.dataframe(maxima,width='stretch',hide_index=True)
        st.caption(tr('Une case vide indique une rune absente. Les moyennes portent sur les runes disponibles.','A blank cell means a missing rune. Averages use the available runes.'))
    elif view == 'Substats / Slot':
        long = substat_table(data, runes.property)
        stat = st.selectbox('Substat', sorted(long.substat.unique()))
        threshold = st.number_input(tr('Valeur minimale','Minimum value'),0,10000,15)
        counts = long[(long.substat==stat)&(long.total>=threshold)].groupby('rune_slot').size().reindex(range(1,7),fill_value=0)
        st.bar_chart(counts.rename(tr('Runes','Runes')))
    elif view == 'Efficience / Slot':
        st.dataframe(data.groupby('rune_slot').efficiency.agg(['count','mean','median','max']).reindex(range(1,7)),width='stretch')
    else:
        st.dataframe(data.groupby(['rune_set','qualité']).size().unstack(fill_value=0),width='stretch')

if st.session_state.get('analysis_ready'):
    stats_runage()
