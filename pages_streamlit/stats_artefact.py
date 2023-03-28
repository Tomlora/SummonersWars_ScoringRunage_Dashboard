
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from fonctions.visualisation import filter_dataframe
import pandas as pd

from st_pages import add_indentation
from fonctions.visuel import css
css()

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
        st.dataframe(st.session_state.arte_count[['substat', 'count2', 'count3', 'count4']].rename(
            columns={'count2': '2', 'count3': '3', 'count4': '4'}))



if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Artefact')
        grind_arte()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')


st.caption('Made by Tomlora')