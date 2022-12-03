from fonctions.gestion_bdd import lire_bdd_perso
import pandas as pd
import streamlit as st
import numpy as np


def cleaning_only_guilde(x):
    x['private'] = 0
    if x['visibility'] == 2:
        if x['guilde'] != st.session_state.guilde:
            x['private'] = 1

    return x


def classement():
    # On lit la BDD
    # on récupère la data
    data = lire_bdd_perso('''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_score.date, sw_score.score, (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                        FROM sw_user
                        INNER JOIN sw_score ON sw_user.id = sw_score.id
                        where sw_user.visibility != 0''').transpose().reset_index()

    # on transpose la date au format date
    data['date'] = pd.to_datetime(data['date'], format="%d/%m/%Y")

    # on groupby : score, dernière date et visibilité
    data_ranking = data.groupby(['joueur', 'guilde']).agg(
        {'score': 'max', 'date': 'max', 'visibility': 'max'})
    # on met en forme la date
    data_ranking['date'] = data_ranking['date'].dt.strftime('%d/%m/%Y')
    # on sort_value
    data_ranking.reset_index(inplace=True)
    data_ranking.sort_values('score', ascending=False, inplace=True)
    # on anonymise
    data_ranking['joueur'] = data_ranking.apply(
        lambda x: "***" if x['visibility'] == 1 else x['joueur'], axis=1)
    # on filtre pour ceux qui veulent only guilde :
    data_ranking = data_ranking.apply(cleaning_only_guilde, axis=1)
    data_ranking = data_ranking[data_ranking['private'] == 0]
    # on supprime le param de visibilité
    data_ranking.drop(['visibility', 'private'], axis=1, inplace=True)

    # on revoit l'ordre :

    data_ranking = data_ranking[['joueur', 'score', 'date', 'guilde']]

    # ----- Page

    st.subheader('Ranking')

    filtre_guilde = st.checkbox('Filtrer sur ma guilde')

    if filtre_guilde:
        data_ranking = data_ranking[data_ranking['guilde']
                                    == st.session_state.guilde]

    data_ranking.reset_index(inplace=True, drop=True)
    height_dataframe = 36 * data_ranking.shape[0]
    st.dataframe(data_ranking, height=height_dataframe,
                 use_container_width=True)
