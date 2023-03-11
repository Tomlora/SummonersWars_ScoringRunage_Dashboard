import pandas as pd
import numpy as np
from params.coef import coef_set, coef_set_spd

import plotly.express as px
import streamlit as st

from st_pages import Page, Section, show_pages, add_indentation
from fonctions.gestion_bdd import requete_perso_bdd

from streamlit_extras.switch_page_button import switch_page



# https://stackoverflow.com/questions/7869592/how-to-do-an-update-join-in-postgresql SQL Join

# Supprime les Future Warnings sur les copies
pd.options.mode.chained_assignment = None  # default='warn'

# set ++ importance


@st.cache_data
def chargement_params():
    category_selected = ['Violent', 'Will', 'Destroy', 'Despair']
    category_value = ", ".join(category_selected)


    category_selected_spd = ['Violent', 'Will', 'Destroy', 'Despair', 'Swift']
    category_value_spd = ", ".join(category_selected_spd)
    
    return category_selected,category_selected_spd, coef_set, coef_set_spd

st.session_state.category_selected, st.session_state.category_selected_spd, st.session_state.coef_set, st.session_state.coef_set_spd = chargement_params()

# CSS

st.markdown("<h1 style='text-align: center; color: white;'>Scoring SW </h1>",
            unsafe_allow_html=True)


# with open('style.css') as f:
#     st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    

add_indentation()
show_pages([
                    Page('pages_streamlit/upload.py', 'Upload JSON', icon=':file_folder:'),
                    Section(name='Scoring', icon=':bar_chart:'),
                    Page('pages_streamlit/general.py', 'General', ':books:'),
                    Page('pages_streamlit/palier.py', 'Evolution', ':chart_with_upwards_trend:'),
                    Page('pages_streamlit/timelapse.py', 'Timelapse', ':bookmark_tabs:'), 
                    Section(name='Classement', icon=':trophy:'),
                    Page('pages_streamlit/ladder.py', 'Scoring', icon='🥇'),
                    Page('pages_streamlit/ladder_value.py', 'Rune', icon=':trophy:'), 
                    Section(name='Runages', icon=':crossed_swords:'),
                    Page('pages_streamlit/grind_runes.py', 'Optimisation', icon=':mag:'),
                    Page('pages_streamlit/build.py', 'Créer un build', icon=':clipboard:'),
                    Page('pages_streamlit/calculator.py', 'Calculateur efficience', icon=':crown:'),
                    Section(name='Paramètres', icon=':gear:'),
                    Page('pages_streamlit/visibility.py', 'Ma visibilité', icon=':eyes:'),
                    Page('pages_streamlit/options.py', 'Mes données', icon=':iphone:'),
                    Section(name='Administration', icon=':star:'),
                    Page('pages_streamlit/visualisation_joueur.py', 'Visualisation', icon=':mag:'),
                    ])


# import streamlit upload st.session_state.file (data)

# si submitted n'est pas initialisé, c'est que le joueur vient d'arriver et n'a pas upload de json. C'est donc false.
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
    

   

switch_page('Upload JSON')    


# else:  # Json upload, la première page n'est plus utile
#     if 'guildeid' in st.session_state:  # Si on a l'info sur la guilde
#         if 'rank' in st.session_state:
#             if st.session_state.rank == 0:
#                 menu_selected = ['General', 'Evolution',
#                                 'Ranking score', 'Ranking substat', 'Build', 'Timelapse', 'Runes', 'Calculateur', 'Parametres']
#                 icons_selected = ["info", 'kanban', 'ladder', 'ladder', 'columns-gap', 'alarm',
#                                 'bag-check-fill', 'calculator', 'gear']
#             elif st.session_state.rank == 1:
#                 menu_selected = ['General', 'Evolution', 'Suivi(Admin)',
#                                 'Ranking score', 'Ranking substat', 'Build', 'Timelapse', 'Runes', 'Calculateur', 'Parametres']
#                 icons_selected = ["info", 'kanban', 'kanban', 'ladder', 'ladder', 'columns-gap', 'alarm',
#                                 'bag-check-fill', 'calculator', 'gear']
#         else:
#             st.session_state.rank = 0
#             menu_selected = ['General', 'Evolution',
#                                 'Ranking score', 'Ranking substat', 'Build', 'Timelapse', 'Runes', 'Calculateur', 'Parametres']
#             icons_selected = ["info", 'kanban', 'ladder', 'ladder', 'columns-gap', 'alarm',
#                                 'bag-check-fill', 'calculator', 'gear']
            

#     else:  # si on a pas l'info sur la guilde
#         menu_selected = ['General', 'Evolution',
#                          'Classement', 'Runes', 'Calculateur', 'Parametres']
#         icons_selected = ["info", 'kanban', 'ladder', 'bag-check-fill', 'calculator', 'gear']



# Menu
# with st.sidebar:
#     # selected = option_menu("Menu", menu_selected,
#     #                        icons=icons_selected, menu_icon='list', default_index=0,
#     #                        styles={
#     #                            "container": {"padding": "5!important", "background-color": "#03152A"},
#     #                            "icon": {"color": "#0083B9", "font-size": "28px"},
#     #                            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#FFFFFF"},
#     #                            "nav-link-selected": {"background-color": "#2C3845"},
#     #                        })

#     if 'pseudo' in st.session_state:  # si on a le pseudo du joueur, on l'affiche.
#         # Visibilité
#         list_visibility = ['Non-visible', 'Caché', 'Visible']  # Liste de choix
#         # slider avec, par défaut, la value dans la bdd
#         slider_visibility = st.radio('Visibilité Classement', [
#                                      'Non-visible', 'Caché', 'Visible à ma guilde', 'Visible à tous'], index=st.session_state.visibility)
#         dict_visibility = {'Non-visible': 0,
#                            'Caché': 1,
#                            'Visible à ma guilde': 2,
#                            'Visible à tous': 3}
#         # on enregistre si changement
#         requete_perso_bdd('''UPDATE sw_user SET visibility = :visibility where joueur = :joueur''', {'visibility': dict_visibility[slider_visibility],
#                                                                                                      'joueur': st.session_state["pseudo"]})
#         st.subheader(f'Joueur : {st.session_state["pseudo"]}')
#         st.subheader(f'Guilde : {st.session_state["guilde"]}')
        
#         if 'rank' in st.session_state:
#             if st.session_state.rank == 0:
#                 st.text('Role : Membre')
#             elif st.session_state.rank == 1:
                # st.text('Role : Admin')


# Pages :
# if selected == "Upload JSON":
#     upload_json(category_selected, coef_set,
#                 category_selected_spd, coef_set_spd)

# elif selected == 'General':
#     general_page()

# elif selected == 'Ranking score':
#     classement()

# elif selected == 'Ranking substat':
#     classement_value()

# # elif selected == 'Bestiaire':
# #     find_monsters()

# elif selected == 'Timelapse':
#     timelapse_joueur()

# elif selected == 'Evolution':
#     palier_page()

# elif selected == 'Suivi(Admin)':
#     visu_page()
    
# elif selected == 'Build':
#     build(st.session_state.data_rune)

# elif selected == 'Runes':
#     optimisation_rune(st.session_state.data_rune, category_selected, coef_set)
    
# elif selected == 'Calculateur':
#     calculateur_efficiency()


# elif selected == 'Parametres':
#     params()


# st.markdown("<h6 style='text-align: right; color: white;'>by Tomlora </h6>",
#             unsafe_allow_html=True)
