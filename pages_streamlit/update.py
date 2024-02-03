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


tab2024, tab2023 = st.tabs(['2024', '2023'])

with tab2024:
    with st.expander('Version 03/02/2024', expanded=True):
        st.info("- Correction d'un bug d'upload sur MacOS") 

    with st.expander('Version 31/01/2024', expanded=True):
        st.info("- Ajout des monstres Assassin Creed") 
        
        
    with st.expander('Version 29/01/2024', expanded=True):
        st.info("- Les filtres ne sont plus cachés") 

    with st.expander('Version 12/01/2024', expanded=True):
        st.info("- Correction des stats améliorables des runes antiques dans l'onglet Optimisation") 

    with st.expander('Version 07/01/2024', expanded=False):
        st.info("- Ajout SpeedTuning") 
            
    with st.expander('Version 06/01/2024', expanded=False):
        st.info(" Bonne année :) ! \n\n"+
                "- Amélioration de l'onglet Donjon avec plus de stats") 

with tab2023:
    with st.expander('Version 28/12/2023', expanded=False):
        st.info("- Meilleur process pour filtrer les données") 

    with st.expander('Version 16/12/2023', expanded=False):
        st.info("- Ajout des Anges \n\n"+
                "- Les pages Artefacts (Detail) et Optimisation Runes sont plus rapides") 
        
        
    with st.expander('Version 08/12/2023', expanded=False):
        st.info("- Ajout des Artefacts Intangible (sowwy !) \n\n")   
        
        
    with st.expander('Version 29/11/2023', expanded=False):
        st.info("- Ajout d'une page Objectifs dans les Artefacts\n\n")   

    with st.expander('Version 20/10/2023', expanded=False):
        st.info("- Possibilité de télécharger les tableaux Artefacts dans General\n\n"+
                "- Correction des Artefacts dmg supp hp qui étaient arrondis à l'entier supérieur\n\n"+
                "- Correction d'une erreur qui pouvait ignorer des artefacts dans la vue Artefact dans General\n\n"+
                "- Detail par Slot dans Statistiques (Top 10 stats)")   

    with st.expander('Version 30/09/2023', expanded=False):
        st.info("- Ajout des nouveaux monstres \n\n"+
                "- Correction des tableaux Artefacts qui n'étaient plus en couleur \n\n"+
                "- Correction de bugs")   
        
        
    with st.expander('Version 30/08/2023', expanded=False):
        st.info("- Ajout d'un tag Reap paramétrable dans Optimisation")   
        
    with st.expander('Version 29/08/2023', expanded=False):
        st.info("- Ajout d'un calculateur de DMG Lushen  \n\n"+
                "- Ajout d'une ToDoList téléchargeable ou sauvegardable sur ses runes") 
        
    with st.expander('Version 20/08/2023', expanded=False):
        st.info("- English Version ") 

    with st.expander('Version 09/08/2023', expanded=False):
        st.info("- Détail des stats artefacts dans l'onglet General ") 
        
    with st.expander('Version 27/07/2023', expanded=False):
        st.info("- Ajout du classement par rune dans Statistiques (Runes)")      
        
    with st.expander('Version 18/07/2023', expanded=False):
        st.info("- Ajout du scoring qualité\n\n"+
                "- Amélioration de la stabilité de l'app :+1:\n\n"+
                "- Amélioration de certains filtres \n\n"+
                "- Ajout de la qualité et qualité originelle des runes dans les différents onglets")   
        
    with st.expander('Version 14/07/2023', expanded=False):
        st.info("- Amélioration de l'onglet Evolution\n\n"+
                "- Amélioration de la lisibilité de l'onglet Creer un build")   
            
    with st.expander('Version 08/07/2023', expanded=False):
        st.info("- Amélioration de l'onglet Inventaire Artefact")   
        
    with st.expander('Version 01/07/2023', expanded=False):
        st.info("- Ajout des Pages Upgrade (Rune + Artefact)\n\n"+
                "- Amélioration de la lisibilité des tableaux dans Optimisation de Runes\n\n"+
                "- Ajout de l'onglet Monstres et des Pages Donjon/Raid")    
        
    with st.expander('Version 30/06/2023', expanded=False):
        st.info("- Ajout des nouveaux sets \n\n"+
                "- Ajout des nouveaux bonus d'artefacts\n\n"+
                "- Ajout des nouveaux monstres\n\n"+
                "- Amélioration de l'onglet Inventaire d'Artefact\n\n"+
                "- Refonte de l'onglet Statistiques pour Runes et Artefacts")        
        
    with st.expander('Version 29/06/2023', expanded=False):
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
    


st.caption('Made by Tomlora :sunglasses:')