from fonctions.gestion_bdd import lire_bdd_perso
import plotly.graph_objects as go
import streamlit as st

@st.cache_data(ttl='1h')
def comparaison(guilde_id, score='score_general'): 
    """_Genere les éléments globaux puis spécifiques à la guilde spécifiée par son id_

    Parameters
    ----------
    guilde_id : int
        guilde_id de la guilde spécifiée

    Returns
    -------
    size_general : int
        _nombre de joueurs dans la base de données_
    avg_score_general : int
        _score moyen de tous les joueurs_
    max_general : int
        _meilleur score de tous les joueurs_
    size_guilde : int
        _nombre de joueurs dans la guilde_
    avg_score_guilde : int
        _score moyen de tous les joueurs de la guilde_
    max_guilde : int
        _meilleur score de tous les joueurs de la guilde_
    df_max : DataFrame
        _tableau des scores max de tous les joueurs_
    df_guilde_max : DataFrame
        _tableau des scores max de tous les joueurs de la guilde_
    """
    # Lire la BDD
    df_actuel = lire_bdd_perso(
        'SELECT * from sw_user, sw_score WHERE sw_user.id = sw_score.id_joueur')
    df_actuel = df_actuel.transpose()
    df_actuel.reset_index(inplace=True)
    df_actuel.drop(['id'], axis=1, inplace=True)
    
    
    df_actuel = df_actuel[df_actuel[score] != 0]

    # On regroupe les scores max de tous les joueurs enregistrés
    df_max = df_actuel.groupby('joueur').max()

    # On trie du plus grand au plus petit
    df_max['rank'] = df_max[score].rank(ascending=False, method='min')

    # Nb joueurs
    size_general = len(df_max)

    # Score moyen
    avg_score_general = int(round(df_max[score].mean(), 0))

    # Meilleur score
    max_general = int(df_max[score].max())

    # On refait les mêmes étapes pour la guilde Endless
    df_guilde = df_actuel[df_actuel['guilde_id'] == guilde_id]
    # df_guilde = df_actuel[df_actuel['guilde'] == guilde]
    df_guilde_max = df_guilde.groupby('joueur').max()
    size_guilde = len(df_guilde_max)
    avg_score_guilde = int(round(df_guilde_max[score].mean(), 0))
    max_guilde = int(df_guilde_max[score].max())
    df_guilde_max['rank'] = df_guilde_max[score].rank(
        ascending=False, method='min')

    return size_general, avg_score_general, max_general, size_guilde, avg_score_guilde, max_guilde, df_max, df_guilde_max

def comparaison_rune_graph(df, name, score='score_general', score_joueur='score'):
    """_Génère le graphique de comparaison_

    Parameters
    ----------
    df : _type_
        
    name : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    fig = go.Figure()

    fig.add_trace(go.Box(
        y=df[score],
        marker_color='#2C75FF',
        name=name,
        quartilemethod='inclusive',
    ))


    fig.add_trace(go.Scatter(
        x=['Score personnel'],
        y=[int(st.session_state[score_joueur])],
        name='Score personnel',
        mode='markers',
        marker_color='rgba(255,255,255,1)',  # à modifier
        marker=dict(size=[30]),
    ))

    return fig
