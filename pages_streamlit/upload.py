import pandas as pd

import streamlit as st
import json
from datetime import datetime
from fonctions.visuel import load_lottieurl
from streamlit_lottie import st_lottie


from fonctions.gestion_bdd import sauvegarde_bdd, update_info_compte, get_user, requete_perso_bdd
from fonctions.runes import Rune
from fonctions.artefact import Artefact


def date_du_jour():
    currentMonth = str(datetime.now().month)
    currentYear = str(datetime.now().year)
    currentDay = str(datetime.now().day)
    return f'{currentDay}/{currentMonth}/{currentYear}'


def upload_json(category_selected, coef_set, category_selected_spd, coef_set_spd):
    with st.form('Data du compte'):
        st.session_state.file = st.file_uploader(
            'Choisis un json', type=['json'], help='Json SW Exporter')
        st.session_state['submitted'] = st.form_submit_button(
            'Calcule mon score')
        st.warning(body='Seuls les scorings sont sauvegardés.', icon="🚨")
        st.success("28/02/2023 : Ajout des monstres de la collab", icon='🔥')
    if not st.session_state.submitted:
        col1, col2, col3 = st.columns(3)
        with col2:
            img = load_lottieurl('https://assets5.lottiefiles.com/packages/lf20_ABViugg18Y.json')
            st_lottie(img, height=200, width=200)

    if st.session_state['file'] is not None and st.session_state.submitted:

        # On charge le json
        data_json = json.load(st.session_state['file'])
        st.session_state.data_json = data_json

        # infos du compte

        st.session_state.pseudo = data_json['wizard_info']['wizard_name']
        try:
            st.session_state.guildeid = data_json['guild']['guild_info']['guild_id']
            st.session_state.guilde = data_json['guild']['guild_info']['name']
        except TypeError: # pas de guilde
            st.session_state.guildeid = 0
            st.session_state.guilde = 'Aucune'          
        st.session_state.compteid = data_json['wizard_info']['wizard_id']

        data_rune = Rune(data_json)
        
        st.session_state.data_rune = data_rune

        data_arte = Artefact(data_json)

        # st.session_state.data_grind = data_rune.data.copy()
        st.session_state.data_avg = data_rune.data.copy()

        # --------------------- calcul score rune

        tcd_value, st.session_state.score = data_rune.scoring_rune(
            category_selected, coef_set)
        
        st.session_state.tcd_detail_score = data_rune.tcd_df_efficiency

        # -------------------------- calcul score spd rune

        st.session_state.tcd_spd, st.session_state.score_spd = data_rune.scoring_spd(
            category_selected_spd, coef_set_spd)

        # calcul score arte

        st.session_state.tcd_arte, st.session_state.score_arte = data_arte.scoring_arte()
        
        # calcul max value rune
        
        st.session_state.df_max = data_rune.calcul_value_max()

        # -------------------------- on enregistre
        try:
            st.session_state.id_joueur, st.session_state.visibility, guilde_id, st.session_state.rank = get_user(
                st.session_state['compteid'], type='id')
        except IndexError:
            try:
                st.session_state.id_joueur, st.session_state.visibility, guilde_id, st.session_state.rank  = get_user(
                    st.session_state['pseudo'], id_compte=st.session_state['compteid'])
            except IndexError:  # le joueur n'existe pas ou est dans l'ancien système
                requete_perso_bdd('''INSERT INTO sw_user(joueur, visibility, guilde_id, joueur_id) VALUES (:joueur, 0, :guilde_id, :joueur_id);
                                  INSERT INTO sw_guilde(guilde, guilde_id) VALUES (:guilde, :guilde_id)
                                  ON CONFLICT (guilde_id)
                                  DO NOTHING;''',
                                  {'joueur': st.session_state['pseudo'],
                                   'guilde': st.session_state['guilde'],
                                   'guilde_id': st.session_state['guildeid'],
                                   'joueur_id': st.session_state['compteid']})

                st.session_state.id_joueur, st.session_state.visibility, guilde_id, st.session_state.rank  = get_user(
                    st.session_state['pseudo'])

        # Enregistrement SQL

        # Scoring general 
        tcd_value['id'] = st.session_state['id_joueur']
        tcd_value['date'] = date_du_jour()
        
        st.session_state.tcd = tcd_value

        sauvegarde_bdd(tcd_value, 'sw', 'append')

        df_scoring = pd.DataFrame({'id': [st.session_state['id_joueur']], 'score_general': [st.session_state['score']],
                                   'date': [date_du_jour()], 'score_spd' : st.session_state['score_spd'], 'score_arte' : st.session_state['score_arte']})
        df_scoring.set_index('id', inplace=True)

        sauvegarde_bdd(df_scoring, 'sw_score', 'append')
        
        # Scoring speed
        tcd_spd_save : pd.DataFrame = st.session_state.tcd_spd.copy()
        
        tcd_spd_save['id'] = st.session_state['id_joueur']
        tcd_spd_save['date'] = date_du_jour()
        
        sauvegarde_bdd(tcd_spd_save, 'sw_spd', 'append')
        
        # Scoring arte
        
        tcd_arte_save : pd.DataFrame = st.session_state.tcd_arte.copy()
        
        tcd_arte_save['id'] = st.session_state['id_joueur']
        tcd_arte_save['date'] = date_du_jour()
        
        sauvegarde_bdd(tcd_arte_save, 'sw_arte', 'append')
        
        # Scoring max_value
        
        df_max = st.session_state.df_max.copy()
        
        df_max['id'] = st.session_state['id_joueur']
        df_max['date'] = date_du_jour()
        
        # on supprime les anciennes données
        requete_perso_bdd('''DELETE FROM sw_max WHERE "id" = :id''', dict_params={'id' : st.session_state['id_joueur']})
        
        # on met à jour
        sauvegarde_bdd(df_max, 'sw_max', 'append')        
        
        # MAJ guilde

        update_info_compte(st.session_state['pseudo'], st.session_state['guildeid'],
                           st.session_state['compteid'])  # on update le compte

        st.subheader(f'Validé pour le joueur {st.session_state["pseudo"]} !')
        st.write('Tu peux désormais aller sur les autres onglets disponibles')

        st.session_state['submitted'] = True
