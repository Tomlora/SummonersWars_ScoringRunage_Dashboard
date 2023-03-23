from fonctions.gestion_bdd import lire_bdd_perso
import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from params.coef import coef_set, coef_set_spd

from st_pages import add_indentation

add_indentation()


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


def mise_en_forme_classement(df, variable='score', columns='score'):
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
    
    if not df.empty:
        df['joueur'] = df.apply(
            lambda x: "***" if x['visibility'] == 1 and st.session_state['pseudo'] != x['joueur'] else x['joueur'], axis=1)
        # on filtre pour ceux qui veulent only guilde :
        df = df.apply(cleaning_only_guilde, axis=1)
        df = df[df['private'] == 0]

        df = df[columns]

        filtre_guilde = st.checkbox('Filtrer sur ma guilde')

        if filtre_guilde:
            df = df[df['guilde']
                    == st.session_state.guilde]

        df.reset_index(inplace=True, drop=True)
        height_dataframe = 36 * df.shape[0]

        
        st.dataframe(df.rename(columns={'arte_type' : 'Type',
                                        'arte_attribut' : 'Attribut',
                                        }), height=height_dataframe,
                    use_container_width=True)
    
    else:
        st.warning('Pas de données disponibles')

    return df

def load_data():
            data = lire_bdd_perso('''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_arte_max.date, sw_arte_max.arte_type, sw_arte_max.arte_attribut, sw_arte_max.max_value as valeur, sw_arte_max.substat, (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                                FROM sw_user
                                INNER JOIN sw_arte_max ON sw_user.id = sw_arte_max.id
                                where sw_user.visibility != 0''').transpose().reset_index()
            return data

def classement_arte():
    # On lit la BDD
    # on récupère la data
    
    st.info("**Note** : Nouvel onglet. Par conséquent, il sera rempli progressivement.", icon="✅")

    if st.session_state.visibility == 0:
        st.warning('Vous avez choisi de ne pas apparaitre. Vous pouvez changer cela dans les paramètres.', icon="ℹ️")




    data = load_data()
        

    liste_attribut = ['Tous', 'EAU', 'FEU', 'VENT', 'LUMIERE', 'TENEBRE', 'ATTACK', 'DEFENSE', 'HP', 'SUPPORT', 'AUCUN']
        

    liste_filtre = ['Tous', 'ELEMENT', 'ARCHETYPE', 'AUCUN']
        
    liste_substat = list(data['substat'].unique())
    liste_substat.sort()
        
    filtre_attribut = st.selectbox('Filtrer sur un attribut', liste_attribut)
    filtre_type = st.selectbox('Filtrer sur un type', liste_filtre)
    filtre_substat = st.selectbox('Filtrer sur un substat', liste_substat)
        
    if filtre_attribut != 'Tous' and filtre_attribut != 'AUCUN':
        data = data[data['arte_attribut'] == filtre_attribut]
            
    if filtre_type != 'Tous' and filtre_type != 'AUCUN':
        data = data[data['arte_type'] == filtre_type]
        
            
    if filtre_substat != 'Tous':
        data = data[data['substat'] == filtre_substat]
            

    if filtre_attribut == 'AUCUN' and filtre_type != 'AUCUN':
        data_filtre = data.groupby(['joueur', 'arte_type', 'substat', 'date', 'guilde']).agg({'valeur' : 'max', 'visibility': 'max'}).reset_index()
        mise_en_forme_classement(data_filtre, 'valeur', ['joueur', 'arte_type', 'substat', 'valeur', 'date', 'guilde'])
    
    elif filtre_type == 'AUCUN' and filtre_attribut != 'AUCUN':
        data_filtre = data.groupby(['joueur', 'arte_attribut', 'substat', 'date', 'guilde']).agg({'valeur' : 'max', 'visibility': 'max'}).reset_index()
        mise_en_forme_classement(data_filtre, 'valeur', ['joueur', 'arte_attribut', 'substat', 'valeur', 'date', 'guilde'])
        
    elif filtre_attribut == 'AUCUN' and filtre_type == 'AUCUN':
        data_filtre = data.groupby(['joueur', 'substat', 'date', 'guilde']).agg({'valeur' : 'max', 'visibility': 'max'}).reset_index()
        mise_en_forme_classement(data_filtre, 'valeur', ['joueur', 'substat', 'valeur', 'date', 'guilde'])
    
    else:
        mise_en_forme_classement(data, 'valeur', ['joueur', 'arte_type', 'arte_attribut', 'substat', 'valeur', 'date', 'guilde'])
    
    
    

    
    
if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Classement des valeurs Artefact')
        classement_arte()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')
    
    
st.caption('Made by Tomlora')