import pandas as pd

import streamlit as st


from fonctions.visuel import load_lottieurl, css
from streamlit_lottie import st_lottie
from st_pages import add_indentation

try:
    st.set_page_config(layout='wide')
except:
    pass


css()
add_indentation()


st.subheader('Mise à jour')

col1, col2, col3 = st.columns([0.4,0.2,0.4])
with col2:
    img = load_lottieurl('https://assets7.lottiefiles.com/private_files/lf30_rzhdjuoe.json')
    st_lottie(img, height=200, width=200)
    
with st.expander('Version 24/06/2023', expanded=True):
    st.info("- Amélioration visuelle des tableaux")    

with st.expander('Version 10/06/2023', expanded=True):
    st.info("- Ajout des ladder Arene et World Boss \n\n"+
            "- Ajout du nombre d'utilisateurs, scores, guildes")
    
with st.expander('Version 13/05/2023', expanded=True):
    st.info("- Ajout du calcul des dmg additionnels Artefact \n\n"+
            "- Ajout de Where2Use pour les artefacts")