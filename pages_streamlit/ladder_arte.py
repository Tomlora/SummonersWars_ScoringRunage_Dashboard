from fonctions.gestion_bdd import lire_bdd_perso, cleaning_only_guilde
import streamlit as st
from datetime import timedelta

from fonctions.visuel import css
from fonctions.artefact import dict_arte_effect_english, dataframe_replace_to_english
css()



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
        df['joueur'] = df.apply(
            lambda x: "***" if x['visibility'] == 4 and st.session_state['pseudo'] != x['joueur'] and st.session_state['guilde'] != x['guilde'] else x['joueur'], axis=1)
        # on filtre pour ceux qui veulent only guilde :
        df = df.apply(cleaning_only_guilde, axis=1)
        df = df[df['private'] == 0] # on retire les private 0 + ceux ayant coché "only guilde"

        df = df[columns]

        filtre_guilde = st.checkbox(st.session_state.langue['filter_guilde'])

        if filtre_guilde:
            df = df[df['guilde']
                    == st.session_state.guilde]

        df.reset_index(inplace=True, drop=True)
        height_dataframe = 60 * df.shape[0]

        
        st.dataframe(df.rename(columns={'arte_type' : 'Type',
                                        'arte_attribut' : 'Attribut',
                                        }), height=height_dataframe,
                    use_container_width=True)
    
    else:
        st.warning(st.session_state.langue['no_data'])

    return df

@st.cache_data(ttl=timedelta(minutes=10))
def load_data_arte():
    data = lire_bdd_perso('''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_arte_max.date, sw_arte_max.arte_type, sw_arte_max.arte_attribut, sw_arte_max.max_value as valeur, sw_arte_max.substat, (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                                FROM sw_user
                                INNER JOIN sw_arte_max ON sw_user.id = sw_arte_max.id
                                where sw_user.visibility != 0''').transpose().reset_index()
    return data

def classement_arte():
    # On lit la BDD
    # on récupère la data
    
    st.info(f'**Note** : {st.session_state.langue["update_ladder"]}', icon="ℹ️")

    if st.session_state.visibility == 0:
        st.warning(st.session_state.langue['no_visibility'], icon="ℹ️")

    data = load_data_arte()
    
    if st.session_state.translations_selected == 'Français':
        liste_attribut = ['Tous', 'EAU', 'FEU', 'VENT', 'LUMIERE', 'TENEBRE', 'INTANGIBLE', 'ATTACK', 'DEFENSE', 'HP', 'SUPPORT', 'AUCUN']
        liste_filtre = ['Tous', 'ELEMENT', 'ARCHETYPE', 'AUCUN']
    elif st.session_state.translations_selected == 'English':
        liste_attribut = ['All', 'WATER', 'FIRE', 'WIND', 'LIGHT', 'DARK', 'INTANGIBLE', 'ATTACK', 'DEFENSE', 'HP', 'SUPPORT', 'NONE']
        
        data['arte_attribut'] = data['arte_attribut'].replace(dataframe_replace_to_english)
        data['substat'] = data['substat'].replace(dict_arte_effect_english)
        
        liste_filtre = ['ALL', 'ELEMENT', 'ARCHETYPE', 'NONE']
    
            
    liste_substat = list(data['substat'].unique())
    liste_substat.sort()
        
    filtre_attribut = st.selectbox(st.session_state.langue['filter_one_attribut'], liste_attribut, len(liste_attribut)-1)
    filtre_type = st.selectbox(st.session_state.langue['filter_one_type'], liste_filtre, len(liste_filtre)-1)
    filtre_substat = st.selectbox(st.session_state.langue['filter_one_substat'], liste_substat)
    
    print(data['arte_attribut'].unique())
        
    if not filtre_attribut in ['Tous', 'ALL'] and not filtre_attribut in ['AUCUN', 'NONE']:
        data = data[data['arte_attribut'] == filtre_attribut]
            
    if not filtre_type in ['Tous', 'ALL'] and not filtre_type in ['AUCUN', 'NONE']:
        data = data[data['arte_type'] == filtre_type]
        
            
    if not filtre_substat in ['Tous', 'ALL']:
        data = data[data['substat'] == filtre_substat]
            

    if filtre_attribut in ['AUCUN', 'NONE'] and not filtre_type in ['AUCUN', 'NONE']:
        data_filtre = data.groupby(['joueur', 'arte_type', 'substat', 'date', 'guilde']).agg({'valeur' : 'max', 'visibility': 'max'}).reset_index()
        mise_en_forme_classement(data_filtre, 'valeur', ['joueur', 'valeur', 'date', 'guilde'])
    
    elif filtre_type in ['AUCUN', 'NONE'] and not filtre_attribut in ['AUCUN', 'NONE']:
        data_filtre = data.groupby(['joueur', 'arte_attribut', 'substat', 'date', 'guilde']).agg({'valeur' : 'max', 'visibility': 'max'}).reset_index()
        mise_en_forme_classement(data_filtre, 'valeur', ['joueur', 'valeur', 'date', 'guilde'])
        
    elif filtre_attribut in ['AUCUN', 'NONE'] and filtre_type in ['AUCUN', 'NONE']:
        data_filtre = data.groupby(['joueur', 'substat', 'date', 'guilde']).agg({'valeur' : 'max', 'visibility': 'max'}).reset_index()
        mise_en_forme_classement(data_filtre, 'valeur', ['joueur', 'valeur', 'date', 'guilde'])
    
    else:
        mise_en_forme_classement(data, 'valeur', ['joueur', 'arte_type', 'arte_attribut', 'valeur', 'date', 'guilde'])
    
    
    

    
    
if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Classement des valeurs Artefact')
        classement_arte()
    
    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")
    
    
st.caption('Made by Tomlora :sunglasses:')