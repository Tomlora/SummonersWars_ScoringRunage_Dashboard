
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from fonctions.visualisation import filter_dataframe
import pandas as pd
from streamlit_extras.colored_header import colored_header
from st_pages import add_indentation
from fonctions.visuel import css
from streamlit_extras.no_default_selectbox import selectbox

import plotly_express as px

css()
add_indentation()


def grind_arte():
    
    # on identifie les monstres
    st.session_state.data_arte.identify_monsters(st.session_state.identification_monsters)
            
    # on récupère les données        
    df_efficience : pd.DataFrame = st.session_state.data_arte.data_a.copy()
    list_type = df_efficience['arte_type'].unique().tolist()
    list_attribut = df_efficience['arte_attribut'].unique().tolist()
        
    list_type.sort()
        
    type_select = selectbox('Choisir un type', list_type , key='type_arte')
    attribut_select = selectbox('Choisir un attribut', list_attribut , key='attribut_arte')
    top = st.slider("Nombre d'artefacts à afficher", 10, 1000, 400, 10) 
        
    # filtre sur un set ?
    if type_select != None:
        df_efficience = df_efficience[df_efficience['arte_type'] == type_select]
    
    if attribut_select != None:
        df_efficience = df_efficience[df_efficience['arte_attribut'] == attribut_select]
        
    # on sort par efficience    
    df_efficience = df_efficience.sort_values('efficiency', ascending=False)
        
    # top 400
    df_efficience = df_efficience.head(top).reset_index()
        
    fig = px.line(df_efficience, x=df_efficience.index, y='efficiency', hover_data=['arte_type', 'arte_attribut', 'arte_equiped'])
        
    st.plotly_chart(fig)    
    

    
    colored_header(
            label="Valeur maximale des artefacts",
            description="",
            color_name="blue-70",
        )
    
    
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
        st.info("Cet onglet montre le nombre d'artefacts ayant au minimum X substats combinés.", icon="ℹ️")
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