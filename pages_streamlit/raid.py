
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from streamlit_extras.no_default_selectbox import selectbox
from st_pages import add_indentation
from fonctions.visuel import css
import plotly_express as px

css()

add_indentation()




def donjon():


    st.session_state.run_logger_raid = st.file_uploader(
                'Fichier CSV généré par SWEX', type=['csv'], help="Il faut activer l'option RunLogger dans SWEX. Le fichier se nomme 'pseudo-raid-runs.csv' ")

    
    if st.session_state.run_logger_raid is not None:
        df_run = pd.read_csv(st.session_state.run_logger_raid)


        st.info("Ne pas hésiter à zoomer sur les graphiques lorsqu'il y a beaucoup de données. La fonctionnalité est disponible en haut à droite du graphique, en passant la souris dessus.")

        # date au bon format
        df_run['date'] = pd.to_datetime(df_run['date'])

        # Le R5 n'est pas détecté
        df_run['dungeon'].fillna('R5', inplace=True)
        # type de donjon
        
        list_donjon = df_run['dungeon'].unique()
        
        donjon_selected = selectbox('Donjon', list_donjon)
        
        if donjon_selected != None:
            df_run = df_run[df_run['dungeon'] == donjon_selected]
       
        
        col1, col2 = st.columns(2)    
        
        with col1:   
            fig = px.pie(df_run, names='result', title='Répartition des résultats')
            
            st.plotly_chart(fig)
        
        df_run = df_run[df_run['result'] == 'Win']  # on ne va pas s'embêter avec les défaites
        
        with col2:    
            fig = px.pie(df_run, names='dungeon', title='Répartition des donjons')
            
            st.plotly_chart(fig)
        
        col3, col4 = st.columns(2)
            
        with col3:
            
            fig = px.pie(df_run, names='main_stat', title='Répartition des main stat')
            
            st.plotly_chart(fig)
            
 
        with col4:
            
            
                df_grp = df_run[df_run['drop'].isin(['Grindstone', 'Enchanted Gem'])].groupby(['dungeon', 'set', 'drop', 'main_stat'], as_index=False).count()
                
                if df_grp.shape[0] > 0:
                
                    fig = px.sunburst(df_grp, path=['dungeon', 'set', 'drop', 'main_stat'], values='result', title='Répartition des runes/artefacts')
                    
                    fig.update_traces(textinfo='value+label')
                    
                    st.plotly_chart(fig)
        
        col5, col6 = st.columns(2) 
                   
        with col5:
        
            df_grp = df_run[df_run['drop'] == 'Grindstone']
            
            if df_grp.shape[0] > 0:
                fig = px.pie(df_grp, names='set', title='Set (Meules)')
                
                st.plotly_chart(fig)
            
        with col6:
            
            df_grp = df_run[df_run['drop'] == 'Enchanted Gem']
            
            if df_grp.shape[0] > 0:
                fig = px.pie(df_grp, names='set', title='Set (Gemmes)')
                
                st.plotly_chart(fig)
            
            
            
if 'submitted' in st.session_state:
    if st.session_state.submitted:
        st.title('Raid')
        donjon()

    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')


st.caption('Made by Tomlora')
