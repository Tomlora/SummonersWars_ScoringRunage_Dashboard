
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


    st.session_state.run_logger = st.file_uploader(
                'Fichier CSV généré par SWEX', type=['csv'], help="Il faut activer l'option RunLogger dans SWEX")

    
    if st.session_state.run_logger is not None:
        df_run = pd.read_csv(st.session_state.run_logger)
        # on crée les teams
        df_run['team'] = df_run.apply(lambda x : f"{x['team1']}(L),{x['team2']},{x['team3']},{x['team4']},{x['team5']}", axis=1)
        df_run.fillna(0, inplace=True)
        # date au bon format
        df_run['date'] = pd.to_datetime(df_run['date'])
        df_run['time'] = pd.to_datetime(df_run['time'], format='%M:%S').dt.time
        # on convertit tout en secondes car le groupby time n'existe pas
        # df_run['time'] = df_run['time'].apply(lambda x : x.minute*60 + x.second)
        
        # type de donjon
        
        list_donjon = df_run['dungeon'].unique()
        
        donjon_selected = selectbox('Donjon', list_donjon)
        
        if donjon_selected != None:
            df_run = df_run[df_run['dungeon'] == donjon_selected]
       
     
        col1, col2 = st.columns(2)    
        
        with col1:   
            fig = px.pie(df_run, names='team', title='Répartition des équipes')
            
            st.plotly_chart(fig)
        
        with col2:    
            fig = px.pie(df_run, names='dungeon', title='Répartition des donjons')
            
            st.plotly_chart(fig)
        
        col3, col4 = st.columns(2)
            
        with col3:
            
            fig = px.pie(df_run, names='drop', title='Répartition des butins')
            
            st.plotly_chart(fig)
            
 
        with col4:
            
            
                df_grp = df_run[df_run['drop'].isin(['Artifact', 'Rune'])].groupby(['dungeon', 'set', 'rarity'], as_index=False).count()
                
                if df_grp.shape[0] > 0:
                
                    fig = px.sunburst(df_grp, path=['dungeon', 'set', 'rarity'], values='result', title='Répartition des runes/artefacts')
                    
                    fig.update_traces(textinfo='value+label')
                    
                    st.plotly_chart(fig)
            
            
            
            
        


if 'submitted' in st.session_state:
    if st.session_state.submitted:
        st.info("La v8 n'est pas encore détectée par RunLogger")
        st.title('Donjon')
        donjon()

    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')


st.caption('Made by Tomlora')
