from fonctions.gestion_bdd import lire_bdd_perso, cleaning_only_guilde
import pandas as pd
import streamlit as st
from datetime import timedelta
from streamlit_extras.no_default_selectbox import selectbox

from fonctions.visuel import css
css()






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
    df['joueur'] = df.apply(
            lambda x: "***" if x['visibility'] == 4 and st.session_state['pseudo'] != x['joueur'] and st.session_state['guilde'] != x['guilde'] else x['joueur'], axis=1)
    # on filtre pour ceux qui veulent only guilde :
    df = df.apply(cleaning_only_guilde, axis=1)
    df = df[df['private'] == 0]

    df = df[['joueur', variable, 'date', 'guilde']]

    filtre_guilde = st.checkbox(st.session_state.langue['filter_guilde'])

    if filtre_guilde:
        df = df[df['guilde']
                == st.session_state.guilde]

    df.reset_index(inplace=True, drop=True)
    height_dataframe = 50 * df.shape[0]


    if variable == 'max_value':
        column_rename = {'max_value' : 'Max substat'}
    else:
        column_rename = {variable : f'Moyenne {variable.capitalize()}'}
        
    st.dataframe(df.rename(columns=column_rename), height=height_dataframe,
                 use_container_width=True)

    return df




def classement_value():
    # On lit la BDD
    # on récupère la data
    
    if st.session_state.visibility == 0:
        st.warning(st.session_state.langue['no_visibility'], icon="ℹ️")
    
    st.info(f'**Note** : {st.session_state.langue["update_ladder"]}', icon="ℹ️")
    
    type_ranking = st.radio(st.session_state.langue['Classement'], ['Max', st.session_state.langue["avg"].capitalize()], horizontal=True)

    @st.cache_data(ttl=timedelta(minutes=10), show_spinner=st.session_state.langue["loading_data"])
    def load_data_value():
        data = lire_bdd_perso('''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_max.date, sw_max.substat, sw_max.max_value, sw_max.rune_set, (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw_max ON sw_user.id = sw_max.id
                            where sw_user.visibility != 0 and sw_max.substat != 'Aucun' ''').transpose().reset_index()
        return data
    
    @st.cache_data(ttl=timedelta(minutes=10), show_spinner=st.session_state.langue["loading_data"])
    def load_data_value_avg(top):
        data = lire_bdd_perso(f'''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_max.date, sw_max.substat, sw_max.{top}, sw_max.rune_set, (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw_max ON sw_user.id = sw_max.id
                            where sw_user.visibility != 0''').transpose().reset_index()
        return data        

    if type_ranking == 'Max':
        data = load_data_value()
        value = 'max_value'
    
    elif type_ranking == st.session_state.langue["avg"].capitalize():
        var_top = st.radio('Top', [5,10,15,25], horizontal=True)
        value = f'top{var_top}' 
        data = load_data_value_avg(value)

    st.subheader('Ranking value')

    stat = st.selectbox('Substat', options=data['substat'].unique())
    
    data_tri = data[data['substat'] == stat]
    
    rune = selectbox('Set Rune', options=st.session_state.set_rune)
    
    if rune != None:
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
        st.title('Classement des valeurs de runes')
        classement_value()
    
    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")
    
    
st.caption('Made by Tomlora :sunglasses:')