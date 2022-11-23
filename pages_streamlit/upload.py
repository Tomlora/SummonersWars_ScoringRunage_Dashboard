import pandas as pd

import streamlit as st
import json
from datetime import datetime


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
        st.session_state.file = st.file_uploader('Choisis un json', type=['json'], help='Json SW Exporter')
        st.session_state['submitted'] = st.form_submit_button('Calcule mon score')
        
        
    if st.session_state['file'] is not None and st.session_state.submitted:

        # On charge le json
        data_json = json.load(st.session_state['file'])
        st.session_state.data_json = data_json


        # infos du compte 

        st.session_state.pseudo = data_json['wizard_info']['wizard_name']
        st.session_state.guildeid = data_json['guild']['guild_info']['guild_id']
        st.session_state.guilde = data_json['guild']['guild_info']['name']
        st.session_state.compteid = data_json['wizard_info']['wizard_id']

        data_rune = Rune(data_json)
        
        data_arte = Artefact(data_json)

        st.session_state.data_grind = data_rune.data.copy()
    
        
        # --------------------- calcul score rune
        
        tcd_value, st.session_state.score = data_rune.scoring_rune(category_selected, coef_set) 
        
        # -------------------------- calcul score spd rune
        
        st.session_state.tcd_spd, st.session_state.score_spd = data_rune.scoring_spd(category_selected_spd, coef_set_spd)
        
        # calcul score arte
        
        st.session_state.tcd_arte, st.session_state.score_arte = data_arte.scoring_arte()

        # -------------------------- on enregistre
        try:
            st.session_state.id_joueur, guilde, st.session_state.visibility, guilde_id = get_user(st.session_state['compteid'], type='id')
        except IndexError:
            try:
                st.session_state.id_joueur, guilde, st.session_state.visibility, guilde_id = get_user(st.session_state['pseudo'], id_compte=st.session_state['compteid'])
            except IndexError: #le joueur n'existe pas ou est dans l'ancien système
                requete_perso_bdd('''INSERT INTO sw_user(joueur, guilde, visibility, guilde_id, joueur_id) VALUES (:joueur, :guilde, 0, :guilde_id, :joueur_id);''',
                                    {'joueur' : st.session_state['pseudo'],
                                    'guilde' : st.session_state['guilde'],
                                    'guilde_id' : st.session_state['guildeid'],
                                    'joueur_id' : st.session_state['compteid']})
                
                st.session_state.id_joueur, guilde, st.session_state.visibility, guilde_id = get_user(st.session_state['pseudo'])
        
        # Enregistrement SQL
        
        tcd_value['id'] = st.session_state['id_joueur']
        tcd_value['date'] = date_du_jour()
        
        st.session_state.tcd = tcd_value
        
        sauvegarde_bdd(tcd_value, 'sw', 'append')
        
       
        df_scoring = pd.DataFrame({'id' : [st.session_state['id_joueur']], 'score' : [st.session_state['score']],
                                   'date' : [date_du_jour()]})
        df_scoring.set_index('id', inplace=True)
        
        sauvegarde_bdd(df_scoring, 'sw_score', 'append')
        
        # MAJ guilde
        
        update_info_compte(st.session_state['pseudo'], st.session_state['guilde'], st.session_state['guildeid'], st.session_state['compteid']) # on update le compte
        
        st.subheader(f'Validé pour le joueur {st.session_state["pseudo"]} !')
        st.write('Tu peux désormais aller sur les autres onglets disponibles')
        
        st.session_state['submitted'] = True
        