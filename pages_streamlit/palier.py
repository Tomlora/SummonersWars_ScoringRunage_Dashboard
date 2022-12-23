
import streamlit as st
import plotly.graph_objects as go
from fonctions.visualisation import transformation_stats_visu, plotline_evol_rune_visu, filter_dataframe
from fonctions.visuel import load_lottieurl
from streamlit_lottie import st_lottie


def palier_page():
    try:

        data_detail = transformation_stats_visu(
            'sw', st.session_state['id_joueur'], distinct=True)
        data_scoring = transformation_stats_visu(
            'sw_score', st.session_state['id_joueur'], distinct=True)

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('Evolution')
            st.dataframe(data_scoring.set_index('date'))
        
        with col2:
            img = load_lottieurl('https://assets10.lottiefiles.com/packages/lf20_sfiiilbf.json')
            st_lottie(img, width=150, height=150)


        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data_scoring['date'], y=data_scoring['score'], mode='lines+markers'))

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig)

        data_100 = data_detail[data_detail['Palier'] == '100']
        data_110 = data_detail[data_detail['Palier'] == '110']
        data_120 = data_detail[data_detail['Palier'] == '120']

        st.write('Palier 100')
        fig1 = plotline_evol_rune_visu(data_100)
        st.plotly_chart(fig1)

        st.write('Palier 110')
        fig2 = plotline_evol_rune_visu(data_110)
        st.plotly_chart(fig2)

        st.write('Palier 120')
        fig3 = plotline_evol_rune_visu(data_120)
        st.plotly_chart(fig3)

    except:
        st.subheader('Erreur')
        st.write('Pas de JSON chargé')
