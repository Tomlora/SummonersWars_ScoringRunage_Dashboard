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
    
with st.expander('Version 01/07/2023', expanded=True):
    st.info("- Ajout des Pages Upgrade (Rune + Artefact)\n\n"+
            "- Amélioration de la lisibilité des tableaux dans Optimisation de Runes\n\n"+
            "- Ajout de l'onglet Monstres et des Pages Donjon/Raid")    
    
with st.expander('Version 30/06/2023', expanded=True):
    st.info("- Ajout des nouveaux sets \n\n"+
            "- Ajout des nouveaux bonus d'artefacts\n\n"+
            "- Ajout des nouveaux monstres\n\n"+
            "- Amélioration de l'onglet Inventaire d'Artefact\n\n"+
            "- Refonte de l'onglet Statistiques pour Runes et Artefacts")        
    
with st.expander('Version 29/06/2023', expanded=True):
    st.info("- Ajout de la courbe d'efficience des runes et artefacts dans Statistiques")
    
with st.expander('Version 25/06/2023', expanded=False):
    st.info("- Amélioration visuelle des tableaux \n\n"+
            "- Correction d'une erreur dans le calcul du score général \n\n"+
            "- Nouvelles statistiques de runes dans Statistiques")    

with st.expander('Version 10/06/2023', expanded=False):
    st.info("- Ajout des ladder Arene et World Boss \n\n"+
            "- Ajout du nombre d'utilisateurs, scores, guildes")
    
with st.expander('Version 13/05/2023', expanded=False):
    st.info("- Ajout du calcul des dmg additionnels Artefact \n\n"+
            "- Ajout de Where2Use pour les artefacts")