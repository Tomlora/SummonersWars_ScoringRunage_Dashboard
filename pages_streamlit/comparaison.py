import streamlit as st
import pandas as pd
from fonctions.gestion_bdd import lire_bdd_perso
from fonctions.visuel import load_lottieurl, css
from streamlit_lottie import st_lottie
from fonctions.compare import comparaison, comparaison_rune_graph
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.button_selector import button_selector


css()




def comparaison_entre_joueurs():
    
    size_general, avg_score_general, max_general, size_guilde, avg_score_guilde, max_guilde, df_max, df_guilde = comparaison(
                    st.session_state['guildeid'])
                
    size_general_arte, avg_arte, max_arte, size_arte_guilde, avg_score_arte_guilde, max_arte_guilde, df_arte_max, df_arte_guilde = comparaison(
                    st.session_state['guildeid'], 'score_arte')


    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f'Rune ({st.session_state["score"]} pts)')



    # tab_general, tab_guilde = st.tabs(['General', st.session_state['guilde']])

    liste_options = ['General', st.session_state['guilde']]
                # Par rapport à tous les joueurs

    button_select = button_selector(liste_options)
    # with tab_general:

    if button_select == 0:

        comparaison1_1, comparaison1_2, comparaison1_3 , comparaison1_4 = st.columns(4)

        with comparaison1_1:
            st.metric(st.session_state.langue['joueurs'], size_general)

        with comparaison1_2:
            delta1_2 = int(
                            st.session_state['score']) - avg_score_general
            st.metric(st.session_state.langue['Avg_score'], avg_score_general, delta1_2)

        with comparaison1_3:
            delta1_3 = int(st.session_state['score']) - max_general
            st.metric(st.session_state.langue['Best_score'], max_general, delta1_3)
                        
                    
                        

        rank2_1, rank2_2 = st.columns(2)

        with comparaison1_4:
            try:
                rank_general = int(
                                df_max.loc[st.session_state['pseudo']]['rank'])
                st.metric(st.session_state.langue['Classement'], rank_general)
            except KeyError:
                rank_general = 'Non-noté'
                st.metric(st.session_state.langue['Classement'], rank_general)

        with rank2_1:
            fig_general = comparaison_rune_graph(df_max, 'General')
            st.plotly_chart(fig_general)
                        
        with rank2_2:
            add_vertical_space(10)
            st.info(st.session_state.langue['explain_graph'])

                    # Par rapport à sa guilde
    # with tab_guilde:
    elif button_select == 1:

        comparaison2_1, comparaison2_2, comparaison2_3, comparaison2_4 = st.columns(4)

        with comparaison2_1:
            st.metric(st.session_state.langue['joueurs'], size_guilde)

        with comparaison2_2:
            delta2_2 = int(
                            st.session_state['score']) - avg_score_guilde
            st.metric(st.session_state.langue['Avg_score'], avg_score_guilde, delta2_2)

        with comparaison2_3:
            delta2_3 = int(st.session_state['score']) - max_guilde
            st.metric(st.session_state.langue['Best_score'], max_guilde, delta2_3)

        with comparaison2_4:
            try:
                rank_guilde = int(
                                df_guilde.loc[st.session_state['pseudo']]['rank'])
                st.metric(st.session_state.langue['Classement'], rank_guilde)
            except KeyError:
                rank_guilde = 'Non-noté'
                st.metric(st.session_state.langue['Classement'], rank_guilde)
                        
        rank3_1, rank3_2 = st.columns(2)

        with rank3_1:
            fig_guilde = comparaison_rune_graph(
                            df_guilde, st.session_state['guilde'])
            st.plotly_chart(fig_guilde)
                    
        with rank3_2:
            add_vertical_space(10)
            st.info(st.session_state.langue['explain_graph'])
                        
                    
        # artefact
            
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f'Artefact ({st.session_state["score_arte"]} pts)')
    with col2:
        img = load_lottieurl(
                        'https://assets4.lottiefiles.com/temporary_files/jXGKLw.json')
        st_lottie(img, width=60, height=60)

    # tab_general, tab_guilde = st.tabs(['General', st.session_state['guilde']])

    button_select_arte = button_selector(liste_options, key='button_selector_arte')
        # Par rapport à tous les joueurs
    # with tab_general:

    if button_select_arte == 0:

        comparaison1_1, comparaison1_2, comparaison1_3 , comparaison1_4 = st.columns(4)

        with comparaison1_1:
                st.metric(st.session_state.langue['joueurs'], size_general_arte)

        with comparaison1_2:
                delta1_2 = int(
                    st.session_state['score_arte']) - avg_arte
                st.metric(st.session_state.langue['Avg_score'], avg_arte, delta1_2)

        with comparaison1_3:
                delta1_3 = int(st.session_state['score_arte']) - max_arte
                st.metric(st.session_state.langue['Best_score'], max_arte, delta1_3)

        rank2_1, rank2_2 = st.columns(2)

        with comparaison1_4:
                rank_general_arte = int(
                            df_arte_max.loc[st.session_state['pseudo']]['rank'])
                st.metric(st.session_state.langue['Classement'], rank_general_arte)

                        # with rank2_2:
        fig_general = comparaison_rune_graph(df_arte_max, 'General', 'score_arte', 'score_arte')
        st.plotly_chart(fig_general)

                    # Par rapport à sa guilde
    # with tab_guilde:

    if button_select_arte == 1:

        comparaison2_1, comparaison2_2, comparaison2_3, comparaison2_4 = st.columns(4)

        with comparaison2_1:
                st.metric(st.session_state.langue['joueurs'], size_arte_guilde)

        with comparaison2_2:
                delta2_2 = int(
                            st.session_state['score']) - avg_score_arte_guilde
                st.metric(st.session_state.langue['Avg_score'], avg_score_arte_guilde, delta2_2)

        with comparaison2_3:
                delta2_3 = int(st.session_state['score_arte']) - max_arte_guilde
                st.metric(st.session_state.langue['Best_score'], max_arte_guilde, delta2_3)

        with comparaison2_4:

                rank_arte_guilde = int(
                            df_arte_guilde.loc[st.session_state['pseudo']]['rank'])
                st.metric(st.session_state.langue['Classement'], rank_arte_guilde)

        fig_guilde_arte = comparaison_rune_graph(
                        df_arte_guilde, st.session_state['guilde'], 'score_arte', score_joueur='score_arte')
        st.plotly_chart(fig_guilde_arte)
    
    
    
if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Comparaison')
        comparaison_entre_joueurs()
    
    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")
    
    
st.caption('Made by Tomlora :sunglasses:')