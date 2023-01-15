
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from fonctions.visualisation import transformation_stats_visu, plotline_evol_rune_visu, filter_dataframe
from fonctions.visuel import load_lottieurl
from streamlit_lottie import st_lottie
import pandas as pd

@st.cache
def filter_data(df, selected_options):
    df_filtered = df[df['date'].isin(selected_options)]
    return df_filtered


def palier_page():

    # try:
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
            
        type_palier = st.radio("Type d'évolution", options=['score_general', 'score_spd', 'score_arte'], horizontal=True)    

        if type_palier == 'score_general':
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
                
        elif type_palier == 'score_spd':
            
            data_detail_spd = transformation_stats_visu(
            'sw_spd', st.session_state['id_joueur'], distinct=True)
            data_scoring_spd = transformation_stats_visu(
            'sw_score', st.session_state['id_joueur'], distinct=True, score='score_spd')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data_scoring_spd['date'], y=data_scoring_spd['score_spd'], mode='lines+markers'))

            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
            fig.update_yaxes(showgrid=False)
            
            data_25 = data_detail_spd[data_detail_spd['Palier'] == '23-25']
            data_28 = data_detail_spd[data_detail_spd['Palier'] == '26-28']
            data_31 = data_detail_spd[data_detail_spd['Palier'] == '29-31']
            data_35 = data_detail_spd[data_detail_spd['Palier'] == '32-35']
            data_36 = data_detail_spd[data_detail_spd['Palier'] == '36+']
            
                       
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['General', '23-25', '26-28', '29-31', '32-35', '36+'])
            
            with tab1:
                st.plotly_chart(fig)

            with tab2:
                fig25 = plotline_evol_rune_visu(data_25)
                st.plotly_chart(fig25)
                
            with tab3:
                fig28 = plotline_evol_rune_visu(data_28)
                st.plotly_chart(fig28)
            with tab4:
                fig31 = plotline_evol_rune_visu(data_31)
                st.plotly_chart(fig31)
            with tab5:
                fig35 = plotline_evol_rune_visu(data_35)
                st.plotly_chart(fig35)
            with tab6:
                fig36 = plotline_evol_rune_visu(data_36)
                st.plotly_chart(fig36)
                
        elif type_palier =='score_arte':
            data_detail_arte = transformation_stats_visu(
            'sw_arte', st.session_state['id_joueur'], distinct=True)
            data_scoring_arte = transformation_stats_visu(
            'sw_score', st.session_state['id_joueur'], distinct=True, score='score_arte')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                    x=data_scoring_arte['date'], y=data_scoring_arte['score_arte'], mode='lines+markers'))
            
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['General', '80', '85', '90', '95', '100+'])
            
            data_80 = data_detail_arte[data_detail_arte['Palier'] == '80']
            data_85 = data_detail_arte[data_detail_arte['Palier'] == '85']
            data_90 = data_detail_arte[data_detail_arte['Palier'] == '90']
            data_95 = data_detail_arte[data_detail_arte['Palier'] == '95']
            data_100 = data_detail_arte[data_detail_arte['Palier'] == '100+']
            
            
            
            print(data_80)
            with tab1:
                st.plotly_chart(fig)
            with tab2:
                fig25 = px.line(data_80, x="date", y="Nombre", color='arte_type', text='type')
                st.plotly_chart(fig25)
            with tab3:
                fig28 = px.line(data_85, x="date", y="Nombre", color='arte_type', text='type')
                st.plotly_chart(fig28)
            with tab4:
                fig31 = px.line(data_90, x="date", y="Nombre", color='arte_type', text='type')
                st.plotly_chart(fig31)
            with tab5:
                fig35 = px.line(data_95, x="date", y="Nombre", color='arte_type', text='type')
                st.plotly_chart(fig35)
            with tab6:
                fig36 = px.line(data_100, x="date", y="Nombre", color='arte_type', text='type')
                st.plotly_chart(fig36)

                
                
    # except:
    #     st.subheader('Erreur')
    #     st.write('Pas de JSON chargé')
