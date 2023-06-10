import pandas as pd

import streamlit as st
import json
from datetime import datetime, timedelta
from fonctions.visuel import load_lottieurl, css
from streamlit_lottie import st_lottie
from params.coef import coef_set, coef_set_spd, liste_substat_arte
from streamlit_extras.switch_page_button import switch_page
from fonctions.gestion_bdd import sauvegarde_bdd, update_info_compte, get_user, requete_perso_bdd, cancel, get_number_row
from fonctions.runes import Rune
from fonctions.artefact import Artefact
from st_pages import add_indentation
from sqlalchemy.exc import InternalError, OperationalError
from dateutil import tz

try:
    st.set_page_config(layout='wide')
except:
    pass


css()
add_indentation()


st.subheader('Mise à jour')


with st.expander('Version 10/06/2023', expanded=True):
    st.info("- Ajout des ladder Arene et World Boss \n\n"+
            "- Ajout du nombre d'utilisateurs, scores, guildes")
    
with st.expander('Version 13/05/2023', expanded=True):
    st.info("- Ajout du calcul des dmg additionnels Artefact \n\n"+
            "- Ajout de Where2Use pour les artefacts")