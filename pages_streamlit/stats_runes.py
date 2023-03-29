
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from fonctions.visualisation import filter_dataframe
import pandas as pd

from st_pages import add_indentation
from fonctions.visuel import css
from fonctions.gestion_bdd import lire_bdd_perso
css()

add_indentation()


def stats_runage():
    
    df_points = lire_bdd_perso(f'''SELECT rune_set, max(points) as points, max(moyenne) as moyenne, max(mediane) as mediane from sw_detail
                               WHERE id = {st.session_state['id_joueur']}
                               GROUP BY rune_set''', index_col='rune_set').transpose()
    
    df_points['points'] = df_points['points'].astype('int')
    
    df_max : pd.DataFrame = st.session_state.df_max.copy()
    
    df_max.reset_index(inplace=True)
    
    st.subheader('Total 10 stats')
    
    value_tcd = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    
    set_select = st.selectbox('Choisir un set', df_max['rune_set'].unique(), key='stat')
    
    df_max_selected = df_max[df_max['rune_set'] == set_select]
    

    
    st.markdown(f'Points : :green[{df_points.loc[set_select, "points"]}] | Efficience(Mediane) : :violet[{round(df_points.loc[set_select, "mediane"],2)}] | Efficience (Moyenne) : :orange[{round(df_points.loc[set_select, "moyenne"],2)}]')
    
    st.table(df_max_selected.pivot_table(values=value_tcd, index=['rune_set', 'substat'], aggfunc='max')[value_tcd].transpose())
    
    del df_max_selected, df_max



if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Runes')
        stats_runage()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')


st.caption('Made by Tomlora')