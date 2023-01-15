
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
        img = load_lottieurl(
            'https://assets10.lottiefiles.com/packages/lf20_sfiiilbf.json')
        st_lottie(img, width=40, height=40)
        options_date = data_scoring['date'].unique().tolist()
        options_select = st.multiselect(
            'Selectionner les dates à afficher :', options_date, options_date)

        data_detail = filter_data(data_detail, options_select)
        data_scoring = filter_data(data_scoring, options_select)

    with col1:  # on met la col1 après, pour bien prendre en compte les modifs dans data_scoring
        st.subheader('Evolution')
        st.dataframe(data_scoring.set_index('date'))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data_scoring['date'], y=data_scoring['score_general'], mode='lines+markers'))

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
        fig.update_yaxes(showgrid=False)
        
        # sauter des lignes
        st.text("")
        st.text("")
        
        st.subheader('Score general')

        data_100 = data_detail[data_detail['Palier'] == '100']
        data_110 = data_detail[data_detail['Palier'] == '110']
        data_120 = data_detail[data_detail['Palier'] == '120']

        tab1, tab2, tab3, tab4 = st.tabs(
            ['General', 'Palier 100', 'Palier 110', 'Palier 120'])

        with tab1:
            st.plotly_chart(fig)

        with tab2:
            fig_rune_100 = plotline_evol_rune_visu(data_100)
            st.plotly_chart(fig_rune_100)

        with tab3:
            fig_rune_110 = plotline_evol_rune_visu(data_110)
            st.plotly_chart(fig_rune_110)

        with tab4:
            fig_rune_120 = plotline_evol_rune_visu(data_120)
            st.plotly_chart(fig_rune_120)

        st.subheader('Speed')

        data_detail_spd = transformation_stats_visu(
            'sw_spd', st.session_state['id_joueur'], distinct=True)
        data_scoring_spd = transformation_stats_visu(
            'sw_score', st.session_state['id_joueur'], distinct=True, score='score_spd')

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=data_scoring_spd['date'], y=data_scoring_spd['score_spd'], mode='lines+markers'))

        fig2.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
        fig2.update_yaxes(showgrid=False)

        data_25 = data_detail_spd[data_detail_spd['Palier'] == '23-25']
        data_28 = data_detail_spd[data_detail_spd['Palier'] == '26-28']
        data_31 = data_detail_spd[data_detail_spd['Palier'] == '29-31']
        data_35 = data_detail_spd[data_detail_spd['Palier'] == '32-35']
        data_36 = data_detail_spd[data_detail_spd['Palier'] == '36+']

        tab_spd_general, tab2325, tab2628, tab2931, tab3235, tab36 = st.tabs(
            ['General', '23-25', '26-28', '29-31', '32-35', '36+'])

        with tab_spd_general:
            st.plotly_chart(fig2)

        with tab2325:
            fig25 = plotline_evol_rune_visu(data_25)
            st.plotly_chart(fig25)

        with tab2628:
            fig28 = plotline_evol_rune_visu(data_28)
            st.plotly_chart(fig28)
        with tab2931:
            fig31 = plotline_evol_rune_visu(data_31)
            st.plotly_chart(fig31)
        with tab3235:
            fig35 = plotline_evol_rune_visu(data_35)
            st.plotly_chart(fig35)
        with tab36:
            fig36 = plotline_evol_rune_visu(data_36)
            st.plotly_chart(fig36)

        st.subheader('Artefact')
        data_detail_arte = transformation_stats_visu(
            'sw_arte', st.session_state['id_joueur'], distinct=True)
        data_scoring_arte = transformation_stats_visu(
            'sw_score', st.session_state['id_joueur'], distinct=True, score='score_arte')

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=data_scoring_arte['date'], y=data_scoring_arte['score_arte'], mode='lines+markers'))

        tab_arte_general, tab80, tab85, tab90, tab95, tab100 = st.tabs(
            ['General', '80', '85', '90', '95', '100+'])

        data_80 = data_detail_arte[data_detail_arte['Palier'] == '80']
        data_85 = data_detail_arte[data_detail_arte['Palier'] == '85']
        data_90 = data_detail_arte[data_detail_arte['Palier'] == '90']
        data_95 = data_detail_arte[data_detail_arte['Palier'] == '95']
        data_100 = data_detail_arte[data_detail_arte['Palier'] == '100+']

        with tab_arte_general:
            st.plotly_chart(fig3)
        with tab80:
            fig80 = px.line(data_80, x="date", y="Nombre",
                            color='arte_type', symbol='type')
            st.plotly_chart(fig80)
        with tab85:
            fig85 = px.line(data_85, x="date", y="Nombre",
                            color='arte_type', symbol='type')
            st.plotly_chart(fig85)
        with tab90:
            fig90 = px.line(data_90, x="date", y="Nombre",
                            color='arte_type', symbol='type')
            st.plotly_chart(fig90)
        with tab95:
            fig95 = px.line(data_95, x="date", y="Nombre",
                            color='arte_type', symbol='type')
            st.plotly_chart(fig95)
        with tab100:
            fig100 = px.line(data_100, x="date", y="Nombre",
                             color='arte_type', symbol='type')
            st.plotly_chart(fig100)

    # except:
    #     st.subheader('Erreur')
    #     st.write('Pas de JSON chargé')
