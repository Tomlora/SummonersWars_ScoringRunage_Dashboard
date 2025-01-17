import pandas as pd
from params.coef import coef_set, coef_set_spd
import streamlit as st
# from st_pages import Page, Section, show_pages, add_indentation
from streamlit_extras.switch_page_button import switch_page


st.set_page_config(layout="wide")

# Supprime les Future Warnings sur les copies
pd.options.mode.chained_assignment = None  # default='warn'

# set ++ importance



@st.cache_data
def chargement_params():
    category_selected = ['Violent', 'Seal', 'Will', 'Destroy', 'Despair', 'Intangible']
    category_value = ", ".join(category_selected)


    category_selected_spd = ['Violent', 'Seal', 'Will', 'Destroy', 'Despair', 'Swift', 'Intangible']
    category_value_spd = ", ".join(category_selected_spd)
    
    return category_selected,category_selected_spd, coef_set, coef_set_spd




def main_page():
                        st.session_state.category_selected, st.session_state.category_selected_spd, st.session_state.coef_set, st.session_state.coef_set_spd = chargement_params()
    
   
                        pages = {'Accueil' : [
                        st.Page('pages_streamlit/upload.py', title='Upload JSON', icon='📁'),
                        st.Page('pages_streamlit/update.py', title='Version 09/01/25', icon='🔈'),
                        st.Page('pages_streamlit/timeline_summon.py', title='Invocation', icon='👻')],
                        # Section(name='Scoring', icon=':bar_chart:'),
                        "Scoring" : [
                        st.Page('pages_streamlit/general.py', title='General', icon='📚'),
                        st.Page('pages_streamlit/evolution.py', title='Evolution', icon='📈'),
                        st.Page('pages_streamlit/comparaison.py', title='Comparaison', icon='💹')],
                        # Section(name='Live', icon=':japanese_ogre:'),
                        "Live" : [
                        st.Page('pages_streamlit/donjons.py', title='Donjons', icon='🏯'),
                        st.Page('pages_streamlit/raid.py', title='Raid', icon='🐲')],
                        # Page('pages_streamlit/spdtune.py', 'SpeedTune', icon=':sparkler:'),
                        # Page('pages_streamlit/timelapse.py', 'Timelapse', ':bookmark_tabs:'), 
                        # Section(name='Classement', icon=':trophy:'),
                        "Classement" : [
                        st.Page('pages_streamlit/ladder.py', title='Scoring', icon='🥇'),
                        st.Page('pages_streamlit/ladder_value.py', title='Rune', icon='🏆'),
                        st.Page('pages_streamlit/ladder_arte.py', title='Artefact', icon='🏆'), 
                        st.Page('pages_streamlit/ladder_others.py', title='Ladder PvP | WB', icon='🏆')],
                        # Section(name='Runages', icon=':crossed_swords:'),
                        "Runages" : [
                        st.Page('pages_streamlit/grind_runes.py', title='Optimisation', icon='🔍'),
                        st.Page('pages_streamlit/stats_runes.py', title='Statistiques', icon='📊'),
                        st.Page('pages_streamlit/objectif_rune.py', title='Objectif Efficience', icon='💪'),
                        st.Page('pages_streamlit/upgrade_runes.py', title='Upgrade', icon='⬆️'),
                        st.Page('pages_streamlit/todolist.py', title='ToDoList', icon='📋'),
                        st.Page('pages_streamlit/build.py', title='Créer un build', icon='🔨'),
                        st.Page('pages_streamlit/calculator.py', title='Calculateur efficience', icon='🔢'),
                        st.Page('pages_streamlit/optimisation_spd.py', title='Best Speed', icon='💻')],
                        # Section(name='Artefacts', icon=':gem:'),
                        "Artefacts" : [
                        st.Page('pages_streamlit/inventaire_artefact.py', title='Inventaire', icon='📂'),
                        st.Page('pages_streamlit/top_artefact.py', title='Best Artefacts', icon='💣'),
                        st.Page('pages_streamlit/stats_artefact.py', title='Statistiques', icon='📊'),
                        st.Page('pages_streamlit/upgrade_artefact.py', title='Upgrade', icon='⬆️'),
                        st.Page('pages_streamlit/objectif_arte.py', title='Objectif', icon='💪'),
                        st.Page('pages_streamlit/dmg_add.py', title='Calculateur dmg', icon='🔢'),
                        st.Page('pages_streamlit/use_arte.py', title='Where2Use', icon='🧠'),
                        st.Page('pages_streamlit/calculator_arte.py', title='Calculateur efficience', icon='🔢')],
                        # Section(name='Paramètres', icon=':gear:'),
                        "Paramètres" : [
                        st.Page('pages_streamlit/visibility.py', title='Ma visibilité', icon='👀'),
                        st.Page('pages_streamlit/options.py', title='Mes données', icon='📱')]}
                        # st.Page('pages_streamlit/feedback.py', title='Feedback', icon='📣')]}

        

                        # si submitted n'est pas initialisé, c'est que le joueur vient d'arriver et n'a pas upload de json. C'est donc false.
                        if 'submitted' not in st.session_state:
                            st.session_state.submitted = False
                            
                            pages = {'Accueil' : [
                            st.Page('pages_streamlit/upload.py', title='Upload JSON', icon='📁'),
                            st.Page('pages_streamlit/update.py', title='Version 09/01/25', icon='🔈')],
                            "Runages" : [
                            st.Page('pages_streamlit/calculator.py', title='Calculateur efficience', icon='🔢'),
                            ],

                            # Section(name='Artefacts', icon=':gem:'),
                            "Artefacts" : [
                            st.Page('pages_streamlit/dmg_add.py', title='Calculateur dmg', icon='🔢'),
                            st.Page('pages_streamlit/use_arte.py', title='Where2Use', icon='🧠'),
                            st.Page('pages_streamlit/calculator_arte.py', title='Calculateur efficience', icon='🔢')],
                            }

                        
                                
                        pg = st.navigation(pages)    

                        pg.run()


main_page()
