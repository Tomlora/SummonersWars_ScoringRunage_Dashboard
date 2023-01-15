
import streamlit as st
import plotly.graph_objects as go
from fonctions.visualisation import transformation_stats_visu, plotline_evol_rune_visu, filter_dataframe
from fonctions.visuel import load_lottieurl
from streamlit_lottie import st_lottie
import pandas as pd

@st.cache
def filter_data(df, selected_options):
    df_filtered = df[df['date'].isin(selected_options)]
    return df_filtered


def palier_page():

    try:
        data_detail = transformation_stats_visu(
            'sw', st.session_state['id_joueur'], distinct=True)
        data_scoring = transformation_stats_visu(
            'sw_score', st.session_state['id_joueur'], distinct=True)
        

        col1, col2 = st.columns(2)
        
        
        with col2:
            img = load_lottieurl('https://assets10.lottiefiles.com/packages/lf20_sfiiilbf.json')
            st_lottie(img, width=150, height=150)
            options_date = data_scoring['date'].unique().tolist()
            options_select = st.multiselect('Selectionner les dates à afficher :', options_date, options_date)
            
            
            data_detail = filter_data(data_detail, options_select)
            data_scoring = filter_data(data_scoring, options_select)
            
        with col1: # on met la col1 après, pour bien prendre en compte les modifs dans data_scoring
            st.subheader('Evolution')
            st.dataframe(data_scoring.set_index('date'))


        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data_scoring['date'], y=data_scoring['score_general'], mode='lines+markers'))

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
        fig.update_yaxes(showgrid=False)
        
        data_100 = data_detail[data_detail['Palier'] == '100']
        data_110 = data_detail[data_detail['Palier'] == '110']
        data_120 = data_detail[data_detail['Palier'] == '120']
        
        
        tab1, tab2, tab3, tab4 = st.tabs(['General', 'Palier 100', 'Palier 110', 'Palier 120'])
        
        with tab1:
            st.plotly_chart(fig)

        with tab2:
            fig1 = plotline_evol_rune_visu(data_100)
            st.plotly_chart(fig1)
            
        with tab3:
            fig2 = plotline_evol_rune_visu(data_110)
            st.plotly_chart(fig2)

        with tab4:
            fig3 = plotline_evol_rune_visu(data_120)
            st.plotly_chart(fig3)

    except:
        st.subheader('Erreur')
        st.write('Pas de JSON chargé')
