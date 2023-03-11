from fonctions.gestion_bdd import lire_bdd_perso
import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from st_pages import add_indentation

add_indentation()

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
    height_dataframe = 50 * df.shape[0]


    st.dataframe(df.rename(columns={'max_value' : 'Max substat',
                                    variable : f'Moyenne {variable.capitalize()}'}), height=height_dataframe,
                 use_container_width=True)

    return df




def classement_value():
    # On lit la BDD
    # on récupère la data
    
    type_ranking = st.radio('Type de ranking', ['Max', 'Moyenne'], horizontal=True)

    def load_data():
        data = lire_bdd_perso('''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_max.date, sw_max.substat, sw_max.max_value, sw_max.rune_set, (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw_max ON sw_user.id = sw_max.id
                            where sw_user.visibility != 0 and sw_max.substat != 'Aucun' ''').transpose().reset_index()
        
        return data
    
    def load_data_avg(top):
        data = lire_bdd_perso(f'''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_max.date, sw_max.substat, sw_max.{top}, sw_max.rune_set, (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw_max ON sw_user.id = sw_max.id
                            where sw_user.visibility != 0''').transpose().reset_index()
        return data        

    if type_ranking == 'Max':
        data = load_data()
        value = 'max_value'
    
    elif type_ranking == 'Moyenne':
        var_top = st.radio('Top', [5,10,15,25], horizontal=True)
        value = f'top{var_top}' 
        data = load_data_avg(value)

    st.subheader('Ranking value')

    stat = st.selectbox('Substat à selectionner', options=data['substat'].unique())
    
    data_tri = data[data['substat'] == stat]
    
    rune = st.selectbox('Set de runes', options=['*'] + data['rune_set'].unique().tolist())
    
    if rune != '*':
        data_tri = data_tri[data_tri['rune_set'] == rune]

    # on transpose la date au format date
    data_tri['date'] = pd.to_datetime(data['date'], format="%d/%m/%Y")

        # on groupby : score, dernière date et visibilité
    data_ranking = data_tri.groupby(['joueur', 'guilde']).agg(
            {value: 'max', 'date': 'max', 'visibility': 'max'})
        # on met en forme la date
    data_ranking['date'] = data_ranking['date'].dt.strftime('%d/%m/%Y')
        
    mise_en_forme_classement(data_ranking, value)


if 'submitted' in st.session_state:
    if st.session_state.submitted:    

        classement_value()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')