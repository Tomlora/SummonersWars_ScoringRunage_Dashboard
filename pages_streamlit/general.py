import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

from gestion_bdd import lire_bdd

def comparaison():
    df_actuel = lire_bdd('sw_score')
    df_actuel = df_actuel.transpose()
    df_actuel.reset_index(inplace=True)
    df_max = df_actuel.groupby('Joueur').max()
    df_max['rank'] = df_max['score'].rank(ascending=False, method='min')
    size_general = len(df_max)
    avg_score_general = int(round(df_max['score'].mean(),0))
    max_general = int(df_max['score'].max())
    
    
    df_endless = df_actuel[df_actuel['guilde'] == '[Endless]']
    df_endless_max = df_endless.groupby('Joueur').max()
    size_endless = len(df_endless_max)
    avg_score_endless = int(round(df_endless_max['score'].mean(),0))
    max_endless = int(df_endless_max['score'].max())
    df_endless_max['rank'] = df_endless_max['score'].rank(ascending=False, method='min')
    
    return size_general, avg_score_general, max_general, size_endless, avg_score_endless, max_endless, df_max, df_endless_max


def comparaison_graph(df, name):
    fig = go.Figure()
        
    fig.add_trace(go.Box(
            y = df['score'],
            marker_color='#2C75FF',
            name=name
        ))
        
    fig.add_trace(go.Scatter(
                x=['Score personnel'],
                y=[int(st.session_state['score'])],
                name='Score personnel',
                mode='markers',
                marker_color='rgba(255,255,255,1)', # à modifier
                marker=dict(size=[30]),
                ))
        
    fig.update_layout({
                    'plot_bgcolor': 'rgb(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgb(0, 0, 0, 0)',
                    'font_color' : "white",
                    })
    return fig


def general_page():
    try:
        tcd_column, score_column = st.columns(2)
            
        with tcd_column:
            st.dataframe(st.session_state.tcd[[100, 110, 120]])
            
        with score_column:
            st.metric('Score', st.session_state['score'])
            st.metric('Date', st.session_state.tcd.iloc[0]['date'])
            
        size_general, avg_score_general, max_general, size_endless, avg_score_endless, max_endless, df_max, df_endless = comparaison()
            
        st.title('Comparaison')
        st.subheader('General')
        
        comparaison1_1, comparaison1_2, comparaison1_3 = st.columns(3)
        
        with comparaison1_1:
            st.metric('Joueurs', size_general)
        
        with comparaison1_2:
            delta1_2 = int(st.session_state['score']) - avg_score_general
            st.metric('Moyenne Score', avg_score_general, delta1_2)
            
        with comparaison1_3:
            delta1_3 = int(st.session_state['score']) - max_general
            st.metric('Record score', max_general, delta1_3)
            
        rank2_1, rank2_2 = st.columns(2)
            
        with rank2_1:
            rank_general = int(df_max.loc[st.session_state['pseudo']]['rank'])
            st.metric('Classement', rank_general)
                
        # with rank2_2:    
        fig_general = comparaison_graph(df_max, 'General')
        st.write(fig_general)
            
        if st.session_state["guilde"] == '[Endless]':
            st.subheader('Endless')
        
            comparaison2_1, comparaison2_2, comparaison2_3 = st.columns(3)
            
            with comparaison2_1:
                st.metric('Joueurs', size_endless)
            
            with comparaison2_2:
                delta2_2 = int(st.session_state['score']) - avg_score_endless
                st.metric('Moyenne Score', avg_score_endless, delta2_2)
                
            with comparaison2_3:
                delta2_3 = int(st.session_state['score']) - max_endless
                st.metric('Record score', max_endless, delta2_3)
                
            rank2_1, rank2_2 = st.columns(2)
            
            with rank2_1:
                rank_endless = int(df_endless.loc[st.session_state['pseudo']]['rank'])
                st.metric('Classement', rank_endless)
                
            # with rank2_2:    
            fig_endless = comparaison_graph(df_endless, 'Endless')
            st.write(fig_endless)
            
    
    except:
        st.subheader('Erreur')
        st.write('Pas de JSON chargé')