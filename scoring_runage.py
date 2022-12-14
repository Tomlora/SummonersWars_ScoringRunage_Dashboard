import pandas as pd
import numpy as np
import json

import plotly.express as px
import streamlit as st


from streamlit_option_menu import option_menu
from pages_streamlit.general import general_page
from pages_streamlit.palier import palier_page
from pages_streamlit.upload import upload_json
from pages_streamlit.visualisation_joueur import visu_page
from pages_streamlit.options import params
from pages_streamlit.grind_runes import optimisation_rune
from pages_streamlit.monster import find_monsters
from fonctions.gestion_bdd import requete_perso_bdd
from pages_streamlit.ladder import classement
from pages_streamlit.timelapse import timelapse_joueur



# https://stackoverflow.com/questions/7869592/how-to-do-an-update-join-in-postgresql SQL Join

# Supprime les Future Warnings sur les copies
pd.options.mode.chained_assignment = None  # default='warn'

# set ++ importance

category_selected = ['Violent', 'Will', 'Destroy', 'Despair']
category_value = ", ".join(category_selected)

coef_set = {'Violent': 3,
            'Will': 3,
            'Destroy': 2,
            'Despair': 2}

category_selected_spd = ['Violent', 'Will', 'Destroy', 'Despair', 'Swift']
category_value_spd = ", ".join(category_selected)

coef_set_spd = {'Violent': 3,
                'Will': 3,
                'Destroy': 2,
                'Despair': 2,
                'Swift': 3}

# CSS

st.markdown("<h1 style='text-align: center; color: white;'>Scoring SW </h1>",
            unsafe_allow_html=True)


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# import streamlit upload st.session_state.file (data)

# si submitted n'est pas initialis√©, c'est que le joueur vient d'arriver et n'a pas upload de json. C'est donc false.
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# PAs de json initialis√©. Donc menu avec Upload json
if st.session_state['submitted'] == False:
    menu_selected = ['Upload JSON', 'General', 'Evolution']
    icons_selected = ["gear", 'info', 'kanban']
else:  # Json upload, la premi√®re page n'est plus utile
    if 'guildeid' in st.session_state:  # Si on a l'info sur la guilde
        # if st.session_state['guildeid'] == 116424:  # si c'est l'id d'Endless, on peut ouvrir le suivi
        if st.session_state['pseudo'] == 'T√łml√łra':  # si c'est l'admin
            menu_selected = ['General', 'Evolution', 'Classement', 'Timelapse',
                             'Suivi', 'Runes', 'Bestiaire', 'Parametres']
            icons_selected = ["info", 'kanban', 'kanban', 'alarm',
                              'bag-check-fill', 'book', 'gear']
        else:  # si c'est pas l'admin
            menu_selected = ['General', 'Evolution',
                             'Classement', 'Timelapse', 'Runes', 'Bestiaire', 'Parametres']
            icons_selected = ["info", 'kanban', 'ladder', 'alarm',
                              'bag-check-fill', 'book', 'gear']
    else:  # si on a pas l'info sur la guilde
        menu_selected = ['General', 'Evolution',
                         'Classement', 'Runes', 'Parametres']
        icons_selected = ["info", 'kanban', 'ladder', 'bag-check-fill', 'gear']

# Menu
with st.sidebar:
    selected = option_menu("Menu", menu_selected,
                           icons=icons_selected, menu_icon='list', default_index=0,
                           styles={
                               "container": {"padding": "5!important", "background-color": "#03152A"},
                               "icon": {"color": "#0083B9", "font-size": "28px"},
                               "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#FFFFFF"},
                               "nav-link-selected": {"background-color": "#2C3845"},
                           })

    if 'pseudo' in st.session_state:  # si on a le pseudo du joueur, on l'affiche.
        # Visibilit√©
        list_visibility = ['Non-visible', 'Cach√©', 'Visible']  # Liste de choix
        # slider avec, par d√©faut, la value dans la bdd
        slider_visibility = st.radio('Visibilit√© Classement', [
                                     'Non-visible', 'Cach√©', 'Visible √† ma guilde', 'Visible √† tous'], index=st.session_state.visibility)
        dict_visibility = {'Non-visible': 0, 'Cach√©': 1,
                           'Visible √† ma guilde': 2, 'Visible √† tous': 3}
        # on enregistre si changement
        requete_perso_bdd('''UPDATE sw_user SET visibility = :visibility where joueur = :joueur''', {'visibility': dict_visibility[slider_visibility],
                                                                                                     'joueur': st.session_state["pseudo"]})
        st.subheader(f'Joueur : {st.session_state["pseudo"]}')
        st.subheader(f'Guilde : {st.session_state["guilde"]}')



# Pages :
if selected == "Upload JSON":
    upload_json(category_selected, coef_set,
                category_selected_spd, coef_set_spd)

elif selected == 'General':
    general_page()

elif selected == 'Classement':
    classement()

elif selected == 'Bestiaire':
    find_monsters()
    
elif selected == 'Timelapse':
    timelapse_joueur()

elif selected == 'Evolution':
    palier_page()

elif selected == 'Suivi':
    visu_page()

elif selected == 'Runes':
    optimisation_rune(category_selected, coef_set)

elif selected == 'Parametres':
    params()


st.markdown("<h6 style='text-align: right; color: white;'>by Tomlora </h6>",
            unsafe_allow_html=True)
