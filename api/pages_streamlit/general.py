
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fonctions.visuel import load_lottieurl
from streamlit_lottie import st_lottie

from fonctions.gestion_bdd import lire_bdd_perso


def comparaison(guilde_id):  # à changer par guilde_id
    # Lire la BDD
    df_actuel = lire_bdd_perso(
        'SELECT * from sw_user, sw_score WHERE sw_user.id = sw_score.id')
    df_actuel = df_actuel.transpose()
    df_actuel.reset_index(inplace=True)
    df_actuel.drop(['id'], axis=1, inplace=True)

    # On regroupe les scores max de tous les joueurs enregistrés
    df_max = df_actuel.groupby('joueur').max()

    # On trie du plus grand au plus petit
    df_max['rank'] = df_max['score_general'].rank(ascending=False, method='min')

    # Nb joueurs
    size_general = len(df_max)

    # Score moyen
    avg_score_general = int(round(df_max['score_general'].mean(), 0))

    # Meilleur score
    max_general = int(df_max['score_general'].max())

    # On refait les mêmes étapes pour la guilde Endless
    df_guilde = df_actuel[df_actuel['guilde_id'] == guilde_id]
    # df_guilde = df_actuel[df_actuel['guilde'] == guilde]
    df_guilde_max = df_guilde.groupby('joueur').max()
    size_guilde = len(df_guilde_max)
    avg_score_guilde = int(round(df_guilde_max['score_general'].mean(), 0))
    max_guilde = int(df_guilde_max['score_general'].max())
    df_guilde_max['rank'] = df_guilde_max['score_general'].rank(
        ascending=False, method='min')

    return size_general, avg_score_general, max_general, size_guilde, avg_score_guilde, max_guilde, df_max, df_guilde_max


def comparaison_graph(df, name):
    fig = go.Figure()

    fig.add_trace(go.Box(
        y=df['score_general'],
        marker_color='#2C75FF',
        name=name,
        quartilemethod='inclusive',
    ))

    fig.add_trace(go.Scatter(
        x=['Score personnel'],
        y=[int(st.session_state['score'])],
        name='Score personnel',
        mode='markers',
        marker_color='rgba(255,255,255,1)',  # à modifier
        marker=dict(size=[30]),
    ))

    return fig


def highlight_max(data, color='yellow'):
    '''
    highlight the maximum in a Series or DataFrame

    ex : st.session_state.tcd_spd.style.apply(highlight_max, color='green', axis=1)
    '''
    attr = 'background-color: {}'.format(color)
    if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
        is_max = data == data.max()
        return [attr if v else '' for v in is_max]
    else:  # from .apply(axis=None)
        is_max = data == data.max().max()
        return pd.DataFrame(np.where(is_max, attr, ''),
                            index=data.index, columns=data.columns)


def general_page():
    # -------------- Scoring du compte
    try:
        tcd_column, score_column = st.columns(2)

        with tcd_column:
            # Stat du joueur
            st.dataframe(st.session_state.tcd[[100, 110, 120]])

        with score_column:
            # Score du joueur
            st.metric('Score Rune', st.session_state['score'])
            st.metric('Date', st.session_state.tcd.iloc[0]['date'])

        size_general, avg_score_general, max_general, size_guilde, avg_score_guilde, max_guilde, df_max, df_guilde = comparaison(
            st.session_state['guildeid'])

        tab1, tab2 = st.tabs(['Autres scoring', 'Efficience moyenne par set'])
        
        with tab1:
            with st.expander('Autre scorings'):

                # ---------------- Scoring arte + speed

                tcd_column_spd, score_column_arte = st.columns(2)

                with tcd_column_spd:
                    st.metric('Score Speed', st.session_state['score_spd'])

                with score_column_arte:
                    st.metric('Score Arte', st.session_state['score_arte'])

                # ---------------- Df arte + speed

                tcd_column_df_spd, score_column_df_arte = st.columns(2)
                #  df.style.highlight_max(axis=0)
                with tcd_column_df_spd:
                    st.dataframe(st.session_state.tcd_spd)

                with score_column_df_arte:
                    st.dataframe(st.session_state.tcd_arte)
                    
        with tab2:
            with st.expander('Efficience par set'):

  
                data_grp : pd.DataFrame = st.session_state['data_avg'].groupby('rune_set').agg({'efficiency' : ['mean', 'max', 'median']})
                data_grp = data_grp.droplevel(level=0, axis=1)
                st.dataframe(data_grp)

                fig = go.Figure()
                fig.add_trace(go.Histogram(y=data_grp['max'], x=data_grp.index, histfunc='avg', name='max'))
                fig.add_trace(go.Histogram(y=data_grp['mean'], x=data_grp.index, histfunc='avg', name='mean'))
                fig.update_layout(
                barmode="overlay",
                bargap=0.1)
                st.plotly_chart(fig)
                
        # ---------------- Comparaison

        col1, col2 = st.columns(2)
        with col1:
            st.header('Comparaison (Runes)')
        with col2:
            img = load_lottieurl('https://assets4.lottiefiles.com/packages/lf20_yMpiqXia1k.json')
            st_lottie(img, width=60, height=60)
            

        tab1, tab2 = st.tabs(['General', st.session_state['guilde']])
        # Par rapport à tous les joueurs
        with tab1:

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
            st.plotly_chart(fig_general)

        # Par rapport à sa guilde
        with tab2:

            comparaison2_1, comparaison2_2, comparaison2_3 = st.columns(3)

            with comparaison2_1:
                st.metric('Joueurs', size_guilde)

            with comparaison2_2:
                delta2_2 = int(st.session_state['score']) - avg_score_guilde
                st.metric('Moyenne Score', avg_score_guilde, delta2_2)

            with comparaison2_3:
                delta2_3 = int(st.session_state['score']) - max_guilde
                st.metric('Record score', max_guilde, delta2_3)

            rank2_1, rank2_2 = st.columns(2)

            with rank2_1:
                rank_guilde = int(df_guilde.loc[st.session_state['pseudo']]['rank'])
                st.metric('Classement', rank_guilde)

            # with rank2_2:
            fig_guilde = comparaison_graph(df_guilde, st.session_state['guilde'])
            st.plotly_chart(fig_guilde)

    except:
        st.subheader('Erreur')
        st.write('Pas de JSON chargé')
