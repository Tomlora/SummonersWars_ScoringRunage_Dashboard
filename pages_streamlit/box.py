
import streamlit as st
from fonctions.gestion_bdd import lire_bdd_perso, lire_bdd
import os
from st_pages import add_indentation
from datetime import timedelta
import pandas as pd

from fonctions.visuel import css
css()

add_indentation()


@st.cache_data(ttl=timedelta(hours=1))
def charge_df_box():
    df = lire_bdd_perso('''SELECT sw_monsters.*, sw_user.joueur, sw_guilde.* from sw_monsters
                    INNER JOIN sw_user ON sw_user.id = sw_monsters.id
                    INNER JOIN sw_guilde ON sw_guilde.guilde_id = sw_user.guilde_id
                    ''', index_col='id').transpose().reset_index()
    return df

def box():
    st.info('Mise à jour toutes les heures', icon="ℹ️")
    df_box_complet = charge_df_box()
    

    id_guilde = st.number_input('Identifiant guilde', value=0, key='identifiant_guilde', format='%i')
    
    try:
        df_box = df_box_complet[df_box_complet['guilde_id'] == id_guilde]
        
        swarfarm = lire_bdd('sw_ref_monsters').T.drop('index', axis=1)
        
        storage_bool = st.checkbox('Inclure autel de scellement', value=True)

        df_mob = pd.merge(df_box, swarfarm, left_on='id_monstre', right_on='com2us_id')
        
        if not storage_bool:
            df_mob = df_mob[df_mob['storage'] == False]

        df_mob_complet = df_mob.groupby(['joueur', 'name']).agg({'quantité' :'sum'})
        
        liste_mob = df_mob['name'].unique().tolist()
        liste_mob.sort()
        
        select_monsters = st.multiselect('Selectionner les monstres', options=liste_mob)
        
        selected_players = df_mob_complet.loc[([joueur for joueur in df_mob_complet.index.levels[0]], select_monsters), ['quantité']] 
        
        tcd = selected_players.pivot_table(values='quantité',
                                        index='joueur',
                                        columns='name',
                                        fill_value=0,
                                        aggfunc='sum'
                                        )
        
        st.text('Guilde sélectionnée : ' + df_box['guilde'].unique()[0])
        
        # on ajoute le total
        tcd['Total'] = tcd.sum(axis=1)
        tcd.loc['total'] = tcd.sum(axis=0)
        tcd.loc['moyenne'] = round(tcd.mean(axis=0),1)

        
        # # st.dataframe(selected_players)
        
        st.dataframe(tcd, use_container_width=True)
    except IndexError:
        st.warning('Guilde inexistante')
    
    

        

mdp = st.text_input('mot de passe', '', type='password')
if mdp == os.environ.get('pass_visual'):
    box()
elif mdp == '':
    st.write('')
else:
    st.warning('Mot de passe incorrect')
    
    
st.caption('Made by Tomlora :sunglasses:')