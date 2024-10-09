from fonctions.gestion_bdd import lire_bdd_perso, cleaning_only_guilde
import pandas as pd
import streamlit as st
from datetime import timedelta


from fonctions.visuel import css
css()



dict_type = {st.session_state.langue["arene"] : 'arene',
             'World Boss' : 'WB'}
    



def mise_en_forme_classement(df, variable='score', autres_var=None, ascending=False):
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
    df.sort_values(variable, ascending=ascending, inplace=True)
    # on anonymise
    
    if not df.empty:
        df['joueur'] = df.apply(
            lambda x: "***" if x['visibility'] == 1 and st.session_state['pseudo'] != x['joueur'] else x['joueur'], axis=1)
        df['joueur'] = df.apply(
            lambda x: "***" if x['visibility'] == 4 and st.session_state['pseudo'] != x['joueur'] and st.session_state['guilde'] != x['guilde'] else x['joueur'], axis=1)
        # on filtre pour ceux qui veulent only guilde :
        df = df.apply(cleaning_only_guilde, axis=1)
        df = df[df['private'] == 0]
        
        variable_to_show = ['joueur', variable, 'date', 'guilde']
        
        if autres_var is not None:
            variable_to_show += autres_var

        df = df[variable_to_show]

        filtre_guilde = st.checkbox(st.session_state.langue['filter_guilde'])

        if filtre_guilde:
            df = df[df['guilde']
                    == st.session_state.guilde]

        df.reset_index(inplace=True, drop=True)
        height_dataframe = 70 * df.shape[0]

        
        st.dataframe(df, height=height_dataframe,
                    use_container_width=True)
    
    else:
        st.warning(st.session_state.langue['no_data'])

    return df



def classement():
    # On lit la BDD
    # on récupère la data
    
    st.info(f'**Note** : {st.session_state.langue["update_ladder"]}', icon="ℹ️")

    if st.session_state.visibility == 0:
        st.warning(st.session_state.langue['no_visibility'], icon="ℹ️")

    @st.cache_data(ttl=timedelta(minutes=10), show_spinner=st.session_state.langue["loading_data"])
    def load_data_ladder():
        data = lire_bdd_perso('''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id,
                              sw_pvp.date, sw_pvp.win, sw_pvp.lose,
                              (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde,
                              sw_wb.rank, sw_wb.damage as "DMG", sw_wb.date as date_wb
                            FROM sw_user
                            INNER JOIN sw_pvp ON sw_user.id = sw_pvp.id_joueur
                            INNER JOIN sw_wb ON sw_user.id = sw_wb.id_joueur
                            where sw_user.visibility != 0''').transpose().reset_index()
        return data

    data = load_data_ladder()

    choice_radio = st.radio(st.session_state.langue['Classement'], options=dict_type.keys(), index=0, horizontal=True)
    
    
    classement = dict_type[choice_radio]

    if classement == 'arene':
        data['date'] = pd.to_datetime(data['date'], format="%d/%m/%Y")
        data_pvp = data.groupby(['joueur', 'guilde']).max()
        data_pvp['date'] = data_pvp['date'].dt.strftime('%d/%m/%Y')   

        data_pvp['score'] = round((data_pvp['win'] / (data_pvp['win'] + data_pvp['lose']))*100,1)
        mise_en_forme_classement(data_pvp, autres_var=['win', 'lose'])
        
    elif classement == 'WB':
        #on met la bonne colonne date
        data.drop(['date'], axis=1, inplace=True)
        data.rename(columns={'date_wb': 'date'}, inplace=True)
               
        data['date'] = pd.to_datetime(data['date'], format="%d/%m/%Y")
        data_pvp = data.groupby(['joueur', 'guilde']).agg({'rank': 'min', 'DMG': 'max', 'date': 'max', 'visibility' : 'max'})
        data_pvp['date'] = data_pvp['date'].dt.strftime('%d/%m/%Y') 
        data_pvp.rename(columns={'rank': 'meilleur rank'}, inplace=True) 
        
        mise_en_forme_classement(data_pvp, 'meilleur rank', autres_var=['DMG'], ascending=True)
        

    


if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Classement Scoring')
        classement()
    
    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")
    
    
st.caption('Made by Tomlora :sunglasses:')