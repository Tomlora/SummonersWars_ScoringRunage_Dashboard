
import streamlit as st
import pandas as pd
from streamlit_extras.no_default_selectbox import selectbox

from fonctions.visuel import css
import plotly_express as px
import re

css()




def identifier_donjon(df):

    if df['set'] != '0':
            if 'Attribute' in df['set'] and df['dungeon'] == 'Abysses (Autres)':
                return 'Forteresse Abyssal'
            elif 'Archetype' in df['set'] and df['dungeon'] == 'Abysses (Autres)':
                return 'Crypte'
            elif df['set'] in ['Blade', 'Fatal', 'Despair', 'Swift', 'Energy'] and df['dungeon'] == 'Abysses (Autres)' : 
                return 'GB Abyssal'
            elif df['set'] in ['Guard', 'Endure', 'Violent', 'Revenge', 'Shield', 'Focus'] and df['dungeon'] == 'Abysses (Autres)':
                return 'DB Abyssal'
            elif df['set'] in ['Rage', 'Destroy', 'Will', 'Vampire', 'Nemesis'] and df['dungeon'] == 'Abysses (Autres)':
                return 'Necro Abyssal'
            elif df['set'] in ['Seal', 'Fight', 'Determination', 'Accuracy', 'Tolerance', 'Enhance'] and df['dungeon'] == 'Abysses (Autres)':
                return 'Royaume spirituel'
            else :
                return df['dungeon']
            
    elif df['set'] == '0':
            
            if 'Harmony' in df['drop'] and df['dungeon'] == 'Abysses (Autres)':
                return 'GB Abyssal'
            elif 'Transcendence' in df['drop'] and df['dungeon'] == 'Abysses (Autres)':
                return 'DB Abyssal'
            elif 'Chaos' in df['drop'] and df['dungeon'] == 'Abysses (Autres)':
                return 'Necro Abyssal'
            else:
                return df['dungeon']



def donjon():


    st.session_state.run_logger = st.file_uploader(
                'Fichier CSV généré par SWEX', type=['csv'], help="Il faut activer l'option RunLogger dans SWEX. Le fichier se nomme 'pseudo-runs.csv' ")

    
    if st.session_state.run_logger is not None:
        st.info("Ne pas hésiter à zoomer sur les graphiques lorsqu'il y a beaucoup de données. La fonctionnalité est disponible en haut à droite du graphique, en passant la souris dessus.")
        df_run = pd.read_csv(st.session_state.run_logger)
        # on crée les teams
        df_run['team'] = df_run.apply(lambda x : f"{x['team1']}(L),{x['team2']},{x['team3']},{x['team4']},{x['team5']}", axis=1)
        df_run.fillna(0, inplace=True)
        # date au bon format
        df_run['date'] = pd.to_datetime(df_run['date'])
        df_run['time'] = pd.to_datetime(df_run['time'], format='%M:%S').dt.time
        df_run['set'] = df_run['set'].astype(str)
        


        # Tant que les abysses ne sont pas séparés par RunLogger
        df_run['dungeon'] = df_run['dungeon'].replace({'Unknown' : 'Abysses (Autres)'})
        
        df_run['dungeon'] = df_run.apply(lambda x : identifier_donjon(x), axis=1)
        
        df_stats = df_run.melt(id_vars=['dungeon', 'set'], value_vars=['sub1', 'sub2', 'sub3', 'sub4'])
        
        df_stats = df_stats[~df_stats['value'].isin([0, None])] # si pas de substat, on retire
        
        def retirer_pourcentage(x):
            return re.sub(r'(\d+\s*%|\+|\+\(\d+\)|-|\b\d+\b)', '', x)

        
        df_stats['value'] = df_stats['value'].apply(retirer_pourcentage)
        
        # type de donjon
        
        list_donjon = df_run['dungeon'].unique()
       
        
        
        donjon_selected = selectbox('Donjon', list_donjon)


        
        if donjon_selected != None:
            df_run = df_run[df_run['dungeon'] == donjon_selected]
            df_stats = df_stats[df_stats['dungeon'] == donjon_selected]
        
        list_set = df_run['set'].unique()
        set_selected = selectbox('Set', list_set)   
                  
        if set_selected != None:
            df_run = df_run[df_run['set'] == set_selected]
            df_stats = df_stats[df_stats['set'] == set_selected]            
       
     
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
        
        col5, col6 = st.columns(2) 
                   
        with col5:
        
            df_grp = df_run[df_run['drop'] == 'Rune']
            
            if df_grp.shape[0] > 0:
                fig = px.pie(df_grp, names='slot', title='Slot')
                
                st.plotly_chart(fig)
            
        with col6:
            
            df_grp = df_run[df_run['drop'] == 'Artifact']
            
            if df_grp.shape[0] > 0:
                fig = px.pie(df_grp, names='main_stat', title='Stat Arté')
                
                st.plotly_chart(fig)
            
        col7, col8 = st.columns(2)
        
        with col7:
            
            fig = px.pie(df_stats, names='value', title='Value')
            
            st.plotly_chart(fig)
        
        
        with col8:
            
            df_grp = df_stats.groupby(['dungeon', 'set', 'value'], as_index=False).count()
                    
            if df_grp.shape[0] > 0:
                    
                fig = px.sunburst(df_grp, path=['dungeon', 'set', 'value'], values='variable', title='Répartition des runes/artefacts')            
                
                fig.update_traces(textinfo='value+label')
                
                st.plotly_chart(fig)
        


if 'submitted' in st.session_state:
    if st.session_state.submitted:
        st.title('Donjon')
        donjon()

    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")


st.caption('Made by Tomlora :sunglasses:')
