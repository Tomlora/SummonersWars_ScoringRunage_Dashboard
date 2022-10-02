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




# Supprime les Future Warnings sur les copies
pd.options.mode.chained_assignment = None  # default='warn'

# set ++ importance

category_selected = ['Violent', 'Will', 'Destroy', 'Despair']
category_value = ", ".join(category_selected)

# CSS

st.markdown("<h1 style='text-align: center; color: white;'>Scoring runes SW </h1>", unsafe_allow_html=True )


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    


# import streamlit upload st.session_state.file (data)

if 'submitted' not in st.session_state: # si submitted n'est pas initialisé, c'est que le joueur vient d'arriver et n'a pas upload de json. C'est donc false.
    st.session_state.submitted = False

if st.session_state['submitted'] == False: # PAs de json initialisé. Donc menu avec Upload json
    menu_selected = ['Upload JSON', 'General', 'Evolution']
    icons_selected = ["gear", "gear", 'kanban']
else: # Json upload, la première page n'est plus utile
    if 'guildeid' in st.session_state:
        # if st.session_state['guildeid'] == 116424:  # si c'est l'id d'Endless, on peut ouvrir le suivi
        if st.session_state['pseudo'] == 'Tømløra':
            menu_selected = ['General', 'Evolution', 'Suivi', 'Parametres']
            icons_selected = ["gear", 'kanban', 'kanban', 'gear']
        else:
            menu_selected = ['General', 'Evolution', 'Parametres']
            icons_selected = ["gear", 'kanban', 'gear']
    else:    
        menu_selected = ['General', 'Evolution', 'Parametres']
        icons_selected = ["gear", 'kanban', 'gear']

with st.sidebar:
        selected = option_menu("Menu", menu_selected,
                            icons=icons_selected, menu_icon='list', default_index=0,
                            styles={
            "container": {"padding": "5!important", "background-color": "#03152A"},
            "icon": {"color": "#0083B9", "font-size": "28px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#FFFFFF"},
            "nav-link-selected": {"background-color": "#2C3845"},
        })
        st.write(f'Sets importants : {category_value}' )
        
        if 'pseudo' in st.session_state: # si on a le pseudo du joueur, on l'affiche.
            st.subheader(f'Joueur : {st.session_state["pseudo"]}')
            st.subheader(f'Guilde : {st.session_state["guilde"]}') 
        

if selected == "Upload JSON":
    upload_json(category_selected)
    
elif selected == 'General':
    general_page()
    
elif selected == 'Evolution':
    palier_page()

elif selected == 'Suivi':
    visu_page()
    
elif selected == 'Parametres':
    params()


st.markdown("<h6 style='text-align: right; color: white;'>by Tomlora </h6>", unsafe_allow_html=True )