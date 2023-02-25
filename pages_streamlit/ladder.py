from fonctions.gestion_bdd import lire_bdd_perso
import pandas as pd
import streamlit as st

from params.coef import coef_set, coef_set_spd


dict_type = {'Score general' : 'score_general',
                 'Score speed' : 'score_spd',
                 'Score sur un set' : 'score sur un set',
                 'Score speed sur un set' : 'score spd sur un set',
                 'Score artefact' : 'score_arte'}
    
def cleaning_only_guilde(x):
    x['private'] = 0
    if x['visibility'] == 2:
        if x['guilde'] != st.session_state.guilde:
            x['private'] = 1

    return x


def mise_en_forme_classement(df, variable='score'):
    """Met en forme le classement final :  
    
    - Reset l'index
    - Trie du plus grand score au plus petit
    - Applique le paramètre de visibilité
    - Garde les variables à afficher
    - Filtre (optionnel) en fonction de si le filtre guilde est activé ou non
    
    Return le dataframe streamlit"""
    # on restreint à ce qu'on veut afficher

    # on sort_value
    df.reset_index(inplace=True)
    df.sort_values(variable, ascending=False, inplace=True)
    # on anonymise
    df['joueur'] = df.apply(
        lambda x: "***" if x['visibility'] == 1 and st.session_state['pseudo'] != x['joueur'] else x['joueur'], axis=1)
    # on filtre pour ceux qui veulent only guilde :
    df = df.apply(cleaning_only_guilde, axis=1)
    df = df[df['private'] == 0]

    df = df[['joueur', variable, 'date', 'guilde']]

    filtre_guilde = st.checkbox('Filtrer sur ma guilde')

    if filtre_guilde:
        df = df[df['guilde']
                == st.session_state.guilde]

    df.reset_index(inplace=True, drop=True)
    height_dataframe = 36 * df.shape[0]

    st.dataframe(df.rename(columns={'score_general' : 'General',
                                    'score_spd' : 'Speed',
                                    'score_arte' : 'Artefact'}), height=height_dataframe,
                 use_container_width=True)

    return df



def classement():
    # On lit la BDD
    # on récupère la data

    def load_data():
        data = lire_bdd_perso('''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_score.date, sw_score.score_general, sw_score.score_spd, sw_score.score_arte, (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw_score ON sw_user.id = sw_score.id
                            where sw_user.visibility != 0''').transpose().reset_index()
        return data

    data = load_data()

    st.subheader('Ranking')

    choice_radio = st.radio('Type de classement', options=[
                          'Score general', 'Score sur un set', 'Score speed', 'Score speed sur un set', 'Score artefact'], index=0, horizontal=True)
    
    
    classement = dict_type[choice_radio]

    if classement == 'score sur un set':
        set = st.radio('Quel set ?', options=coef_set.keys(), horizontal=True)

        data_set = lire_bdd_perso('''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw.date, sw."Set", sw."100", sw."110", sw."120", (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw ON sw_user.id = sw.id
                            where sw_user.visibility != 0
                            and sw."Set" = %(set)s;''', params={'set': set}).transpose().reset_index()

        data_set['date'] = pd.to_datetime(data_set['date'], format="%d/%m/%Y")

        data_set_grp = data_set.groupby(['joueur', 'guilde']).agg(
            {'100': 'max', '110': 'max', '120': 'max', 'date': 'max', 'visibility': 'max'})

        data_set_grp['date'] = data_set_grp['date'].dt.strftime('%d/%m/%Y')

        # calcul points
        data_set_grp['score'] = (data_set_grp['100'] * 1 + data_set_grp['110']
                                 * 2 + data_set_grp['120'] * 3) * coef_set[set]

        # on restreint à ce qu'on veut afficher

        mise_en_forme_classement(data_set_grp)

    elif classement == 'score spd sur un set':
        set_spd = st.radio(
            'Quel set ?', options=coef_set_spd.keys(), horizontal=True)

        data_spd = lire_bdd_perso('''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_spd.date, sw_spd."Set", sw_spd."23-25", sw_spd."26-28", sw_spd."29-31", sw_spd."32-35", sw_spd."36+", (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw_spd ON sw_user.id = sw_spd.id
                            where sw_user.visibility != 0
                            and sw_spd."Set" = %(set)s;''', params={'set': set_spd}).transpose().reset_index()

        data_spd['date'] = pd.to_datetime(data_spd['date'], format="%d/%m/%Y")

        data_spd_grp = data_spd.groupby(['joueur', 'guilde']).agg(
            {'23-25': 'max', '26-28': 'max', '29-31': 'max', '32-35': 'max', '36+': 'max', 'date': 'max', 'visibility': 'max'})

        data_spd_grp['date'] = data_spd_grp['date'].dt.strftime('%d/%m/%Y')

        data_spd_grp['score'] = (data_spd_grp['23-25'] * 1 + data_spd_grp['26-28'] * 2 +
                                 data_spd_grp['29-31'] * 3 + data_spd_grp['32-35'] *
                                 4 + data_spd_grp['36+'] * 5) * coef_set_spd[set_spd]
        
       
        mise_en_forme_classement(data_spd_grp)

    else:

        # on transpose la date au format date
        data['date'] = pd.to_datetime(data['date'], format="%d/%m/%Y")

        # on groupby : score, dernière date et visibilité
        data_ranking = data.groupby(['joueur', 'guilde']).agg(
            {classement: 'max', 'date': 'max', 'visibility': 'max'})
        # on met en forme la date
        data_ranking['date'] = data_ranking['date'].dt.strftime('%d/%m/%Y')
        
        mise_en_forme_classement(data_ranking, classement)
