
import streamlit as st
from fonctions.gestion_bdd import requete_perso_bdd
from fonctions.artefact import Artefact
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.dataframe_explorer import dataframe_explorer
from fonctions.visualisation import filter_dataframe
import pandas as pd

from st_pages import add_indentation

add_indentation()


def grind_arte():
    

    
    st.session_state.data_arte.identify_monsters(st.session_state.identification_monsters)
    
    df_filter = filter_dataframe(st.session_state.data_arte.df_max)
    
    st.dataframe(df_filter)
    
    tab1, tab2, tab3, tab4 = st.tabs(['Par Type', 'Par Attribut', 'Par substat', 'Par mot clé'])

    with tab1:
        st.dataframe(st.session_state.data_arte.df_max_arte_type.sort_values(by=['arte_type', 'substat'], ascending=True))
        
    with tab2:
        st.dataframe(st.session_state.data_arte.df_max_element.sort_values(by=['arte_attribut', 'substat'], ascending=True))
    
    with tab3:
        st.dataframe(st.session_state.data_arte.df_max_substat.sort_values(by=['substat'], ascending=True))
        
    with tab4:
        liste_substat = ['DMG SUPP', 'REDUCTION', 'DMG SUR', 'HP PERDUS', 'CRIT DMG']
        count2 = []
        count3 = []
        count4 = []

        for substat in liste_substat:
            df, count_sub2 = st.session_state.data_arte.count_substat(substat, 2)
            count2.append(count_sub2)
            df, count_sub3 = st.session_state.data_arte.count_substat(substat, 3)
            count3.append(count_sub3)
            df, count_sub4 = st.session_state.data_arte.count_substat(substat, 4)
            count4.append(count_sub4)
            
        df_count = pd.DataFrame([liste_substat, count2, count3, count4], index=['Substat', '2', '3', '4']).T
        
        st.dataframe(df_count)



if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Artefact')
        grind_arte()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')


st.caption('Made by Tomlora')