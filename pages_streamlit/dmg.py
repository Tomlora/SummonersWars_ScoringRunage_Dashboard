import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import add_indentation
import numpy as np
from fonctions.visuel import css
css()

add_indentation()




st.title('Calculateur dmg')


def calcul_dmg():
    
    monstre_selected = st.radio('Monstre', ['Lushen'])
    
    
    if monstre_selected == 'Lushen':
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.expander('Stats', expanded=True):
            
                base_atk = st.number_input('Base atk', value=900, step=1)
                
                runes_atk = st.number_input('Runes atk', value=0, step=1)
                
                crit_dmg = st.number_input('Crit dmg', value=150, step=1) / 100
                
        with col2:
            with st.expander(st.session_state.langue["Batiments"], expanded=True):
                
                tower_atk = st.number_input('Tower atk', value=20, max_value=20, step=1) / 100
                tower_atk_vent = st.number_input('Tower atk vent', value=21, max_value=21, step=1) / 100
                cd_building = st.number_input('CD (Tower + Flag)', value=25, max_value=60, step=1) / 100
                guild_flag = st.number_input('Guild flag', value=20, max_value=60, step=1) / 100
                leader_skill = st.number_input('Leader skill', value=0, max_value=50, step=1) / 100
                fight_runes = st.number_input('Fight runes', value=0, max_value=100, step=1) / 100
                guild_bonus = st.number_input('Guild bonus', value=0, max_value=60, step=1) / 100
                skill_multi = st.number_input('Skill multi', value=68, max_value=120, step=1) / 100
                skill_ups = st.number_input('Skill ups', value=30, max_value=30, step=1) / 100
                
        with col3:
            with st.expander(st.session_state.langue['artefacts'], expanded=True):
                
                add_dmg = st.number_input('Add dmg', value=0, step=1) / 100
                atk_buff = st.number_input('Atk buff', value=0, step=1) / 100
                cd_S3 = st.number_input('CD S3', value=0, step=1) / 100
                
        base_atk_with_bonus = (base_atk * (tower_atk + tower_atk_vent))
        base_atk_guild_flag = base_atk * (guild_flag) 
        base_atk_leaderskill = base_atk * (leader_skill)
        base_atk_fight_runes = base_atk * (fight_runes)
        base_atk_guild_bonus = base_atk * (guild_bonus)
        coefficient_dmg = 0.877193
        
        crit_dmg_total = 1+crit_dmg + cd_building + skill_ups      
        base_atk_total = base_atk_with_bonus + base_atk_guild_flag + base_atk_leaderskill + base_atk_fight_runes + base_atk_guild_bonus
        
        
        
        original = round((base_atk_total + base_atk + runes_atk) * (crit_dmg_total) * skill_multi * 1.5 * coefficient_dmg)
        
        
        total_dmg_1 = round((base_atk_total + base_atk + runes_atk) * (crit_dmg_total) * skill_multi * 1.5 * coefficient_dmg)
        total_dmg_2 = round((base_atk_total + base_atk + runes_atk) * (crit_dmg_total) * skill_multi * (0.5*atk_buff + 1.5) * coefficient_dmg)
        total_dmg_3 = round((base_atk_total + base_atk + runes_atk) * (crit_dmg_total + cd_S3) * skill_multi * 1.5 * coefficient_dmg)
        
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric('DMG originaux' , value=original)
        
        with col2:
            st.metric('DMG total par carte' , value=round(original + (base_atk_with_bonus + base_atk + runes_atk) * 1.5 * add_dmg + (total_dmg_2 - original) + (total_dmg_3 - original)))
        
        with st.expander('Détail :'):
            
            col1, col2, col3 = st.columns(3)
        
            with col1:
                add_dmg_total = (base_atk_with_bonus + base_atk + runes_atk) * 1.5 * add_dmg
                st.metric('Avec DMG SUPP', value=total_dmg_1, delta=add_dmg_total)
                
            with col2:
                st.metric('Avec ATKBuff', value=total_dmg_2, delta=total_dmg_2 - original)
                
            with col3:
                st.metric('Avec CD S3', value=total_dmg_3, delta=total_dmg_3 - original)
               
        

                
                
                
                
        
calcul_dmg()

st.caption('Made by Tomlora :sunglasses:')