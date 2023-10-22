
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from fonctions.visualisation import filter_dataframe
import pandas as pd
from streamlit_extras.colored_header import colored_header
from st_pages import add_indentation
from fonctions.visuel import css
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.metric_cards import style_metric_cards
import plotly_express as px

css()
add_indentation()

style_metric_cards(background_color='#03152A', border_color='#0083B9', border_left_color='#0083B9', border_size_px=0, box_shadow=False)

def grind_arte():
    

            
    # on récupère les données        
    df_efficience : pd.DataFrame = st.session_state.data_arte.data_a.copy()
    
    if st.session_state.translations_selected == 'English':
        df_efficience['arte_attribut'] = df_efficience['arte_attribut'].replace({'EAU' : 'WATER',
                                                               'FEU' : 'FIRE',
                                                               'VENT' : 'WIND',
                                                               'LUMIERE' : 'LIGHT',
                                                               'TENEBRE' : 'DARK',
                                                               'ATTACK' : 'ATTACK',
                                                               'DEFENSE' : 'DEFENSE',
                                                               'HP' : 'HP',
                                                               'SUPPORT' : 'SUPPORT',
                                                               'AUCUN' : 'NONE',
                                                               'Tous' : 'ALL'})
    list_type = df_efficience['arte_type'].unique().tolist()
    list_attribut = df_efficience['arte_attribut'].unique().tolist()
        
    list_type.sort()
        
    type_select = selectbox(st.session_state.langue['filter_one_type'], list_type , key='type_arte')
    attribut_select = selectbox(st.session_state.langue['filter_one_attribut'], list_attribut , key='attribut_arte')
    
        # filtre sur un set ?
    if type_select != None:
        df_efficience = df_efficience[df_efficience['arte_type'] == type_select]
    
    if attribut_select != None:
        df_efficience = df_efficience[df_efficience['arte_attribut'] == attribut_select]
        
    top = st.slider(st.session_state.langue['nb_artefact_to_show'], 10, df_efficience.shape[0], round(df_efficience.shape[0]/2), 10) 
        

        
    # on sort par efficience    
    df_efficience = df_efficience.sort_values('efficiency', ascending=False)
        
    # top choisi
    df_efficience = df_efficience.head(top).reset_index()
    
    col1, col2 = st.columns(2)
     
    with col1:    
        fig = px.line(df_efficience, x=df_efficience.index, y='efficiency', hover_data=['arte_type', 'arte_attribut', 'arte_equiped'])
        st.plotly_chart(fig)  
        
    with col2:
        
        st.text(f'{st.session_state.langue["Efficience_avg"]} {df_efficience["efficiency"].mean():.2f}')
        st.text(f'{st.session_state.langue["artefact_50%"]} : {df_efficience["efficiency"].median():.2f}')
        st.text(f'{st.session_state.langue["eff_moyenne_archetype"]} {df_efficience[df_efficience["arte_type"] == "ARCHETYPE"]["efficiency"].mean():.2f}')
        st.text(f'{st.session_state.langue["eff_moyenne_element"]} {df_efficience[df_efficience["arte_type"] == "ELEMENT"]["efficiency"].mean():.2f}')
        
        st.subheader(f'Parmi le top {top}:')
        col2_1, col2_2 = st.columns(2)
        
        with col2_1:
            count_element = df_efficience[df_efficience["arte_type"] == "ELEMENT"]['efficiency'].count()
            st.metric('Element', count_element, round(count_element / top * 100,2), help="Le nombre coloré correspond au % du top")
        
        with col2_2:
            count_archetype = df_efficience[df_efficience["arte_type"] == "ARCHETYPE"]['efficiency'].count()
            st.metric('Archetype', count_archetype, round(count_archetype / top * 100,2), help="Le nombre coloré correspond au % du top")
            
    with st.expander(st.session_state.langue["detail"]):
        
        fig = px.pie(df_efficience.groupby(['arte_attribut'], as_index=False).count(),
                     values='efficiency',
                     names='arte_attribut',
                     title=st.session_state.langue["repartition_attribut"])
        
        fig.update_traces(textposition='inside', textinfo='percent+value+label')
            
        st.plotly_chart(fig, use_container_width=True)    
            
    
    
        
    col3, col4 = st.columns(2)
    
    with col3:
        try:
            df_archetype = df_efficience[df_efficience["arte_type"] == "ELEMENT"].reset_index(drop=True)
            fig = px.line(df_archetype, x=df_archetype.index, y='efficiency', hover_data=['arte_type', 'arte_attribut', 'arte_equiped'], title='Element')
            st.plotly_chart(fig)
        except ValueError:
            pass
    
    with col4:
        try:
            df_element = df_efficience[df_efficience["arte_type"] == "ARCHETYPE"].reset_index(drop=True)
            fig = px.line(df_element, x=df_element.index, y='efficiency', hover_data=['arte_type', 'arte_attribut', 'arte_equiped'], title='Archetype')
            st.plotly_chart(fig)  
        except ValueError:
            pass
        
        
    

    
    colored_header(
            label=st.session_state.langue["value_max"],
            description="",
            color_name="blue-70",
        )
    
    
    df_filter = filter_dataframe(st.session_state.data_arte.df_max)
    
    st.dataframe(df_filter)
    
    tab1, tab2, tab3, tab4 = st.tabs(['Type', 'Attribut', 'Substat', st.session_state.langue["mot-cle"]])

    with tab1:
        st.dataframe(st.session_state.data_arte.df_max_arte_type.sort_values(by=['arte_type', 'substat'], ascending=True))
        
    with tab2:
        st.dataframe(st.session_state.data_arte.df_max_element.sort_values(by=['arte_attribut', 'substat'], ascending=True))
    
    with tab3:
        st.dataframe(st.session_state.data_arte.df_max_substat.sort_values(by=['substat'], ascending=True))
        
    with tab4:
        st.info(st.session_state.langue["mot-cle_help"], icon="ℹ️")
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


st.caption('Made by Tomlora :sunglasses:')