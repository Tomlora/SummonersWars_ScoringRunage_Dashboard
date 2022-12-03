import streamlit as st

import plotly.graph_objects as go

from fonctions.gestion_bdd import lire_bdd_perso, get_user
from fonctions.visualisation import transformation_stats_visu, plotline_evol_rune_visu


def visu_page():

    with st.form('Choisir un joueur'):
        df = lire_bdd_perso(
            'SELECT * from sw_user, sw_score WHERE sw_user.id = sw_score.id')
        df = df.transpose()
        # df.set_index('joueur', inplace=True)
        df.drop(['id', 'guilde_id'], axis=1, inplace=True)
        # sort l'index : Majuscule -> Minuscule -> caractères spéciaux
        df.sort_index(axis=0, inplace=True)
        liste_joueurs = df.index.unique().values.tolist()
        joueur_target = st.selectbox('Joueur', liste_joueurs)
        id_joueur, visibility, guildeid = get_user(joueur_target)

        submitted_joueur = st.form_submit_button('Valider')

    if submitted_joueur:
        data_detail = transformation_stats_visu('sw', id_joueur, distinct=True)
        data_scoring = transformation_stats_visu(
            'sw_score', id_joueur, distinct=True)

        st.subheader('Evolution')

        st.dataframe(data_scoring.set_index('date'))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data_scoring['date'], y=data_scoring['score'], mode='lines+markers'))
        fig.update_layout({
            'plot_bgcolor': 'rgb(255, 255, 255)',
            'paper_bgcolor': 'rgba(0, 0, 0,0)'
        })

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
