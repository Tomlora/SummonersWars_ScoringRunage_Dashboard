import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from math import ceil
from streamlit_extras.metric_cards import style_metric_cards
import json
from st_pages import add_indentation

from fonctions.visuel import css

css()

add_indentation()

@st.cache_data
def translation(langue):
    if langue == 'Français':
        return json.load(open('langue/fr.json', encoding='utf-8'))
    elif langue == 'English':
        return json.load(open('langue/en.json', encoding='utf-8'))
    

    
try:
    if not 'langue' in st.session_state:
        st.session_state.langue = translation("Français") 
except:
    pass  
    
style_metric_cards(background_color='#03152A', border_color='#0083B9', border_left_color='#0083B9', border_size_px=0, box_shadow=False, border_radius_px=300)


st.title('Calculateur DMG Artefact')

add_vertical_space(1)
col1, col2, col3, col4, col5 = st.columns([0.15,0.40,0.10, 0.40,0.15])

def input_stats(key, format_hp=None, value=0, max_hp=None, max_atk=None, max_def=None, max_vit=None, value_spd=0):
    
    value_hp = value
    min_value_hp = 0
    step_hp = 1
    if format_hp is not None:
        min_value_hp = 0.0
        value_hp = float(value)
        step_hp = 0.10
    hp = st.number_input('HP', min_value=min_value_hp, max_value=max_hp, value=value_hp, key=f'{key}_hp', format=format_hp, step=step_hp)
    atk = st.number_input('ATK', min_value=0, value=value, max_value=max_atk, key=f'{key}_atk')
    defense = st.number_input('DEF', min_value=0, value=value, max_value=max_def, key=f'{key}_def')
    vit = st.number_input('SPD', min_value=0, value=value_spd, max_value=max_vit, key=f'{key}_vit')
    
    return hp, atk, defense, vit


def arte(hp, atk, defense, vit, number):
    col1, col2 = st.columns(2)
    with col1:
        arte_hp, arte_atk, arte_def, arte_vit = input_stats(f'artefact_{number}', format_hp='%.2f', max_hp=7.0, max_atk=70, max_def=70, max_vit=400)
        arte_hp = arte_hp / 100
        arte_atk = arte_atk / 100
        arte_def = arte_def / 100
        arte_vit = arte_vit / 100
        
        dmg_hp = round(hp * arte_hp,1)
        dmg_atk = round(atk * arte_atk,2)
        dmg_def = round(defense * arte_def,2)
        dmg_vit = round(vit * arte_vit,2)
    with col2:
        st.write('DMG')
        st.markdown(f':green[{dmg_hp}]')
        add_vertical_space(3)
        st.markdown(f':blue[{dmg_atk}]')
        add_vertical_space(3)
        st.markdown(f':violet[{dmg_def}]')
        add_vertical_space(3)
        st.markdown(f':orange[{dmg_vit}]')
         
        st.metric('Total', round(dmg_hp + dmg_atk + dmg_def + dmg_vit,1))
    

with col2:
    
    with st.expander('%', True):
        col2_1, col2_2 = st.columns(2)

        with col2_1:
            st.subheader(f'{st.session_state.langue["Batiments"]} (%)')
            hp_bat, atk_bat, def_bat, vit_bat = input_stats('batiments', value=20, max_hp=20, max_atk=20, max_def=20, max_vit=15, value_spd=15)
        with col2_2:
            st.subheader('Lead (%)')
            hp_lead, atk_lead, def_lead, vit_lead = input_stats('lead', max_hp=50, max_atk=50, max_def=44, max_vit=33)


with col4:
    
    with st.expander('Stats', True):
        col4_1, col4_2 = st.columns(2)
        
        with col4_1:
            st.subheader('Stats de base')
            hp_base, atk_base, def_base, vit_base = input_stats('base', max_hp=15000, max_atk=1200, max_def=1200, max_vit=150)
            
        with col4_2:
            st.subheader('Bonus Runes')
            hp_rune, atk_rune, def_rune, vit_rune = input_stats('rune', max_hp=60000, max_atk=3000, max_def=3000, max_vit=240)

# Calcul

## Valeurs en %
hp_bat = hp_bat/100
atk_bat = atk_bat/100
def_bat = def_bat/100
vit_bat = vit_bat/100

hp_lead = hp_lead/100
atk_lead = atk_lead/100
def_lead = def_lead/100
vit_lead = vit_lead/100


hp_bonus = hp_base + ceil(hp_base * hp_bat) + ceil(hp_base * hp_lead) + hp_rune
atk_bonus = atk_base + ceil(atk_base * atk_bat) + ceil(atk_base * atk_lead) + atk_rune
def_bonus = def_base + ceil(def_base * def_bat) + ceil(def_base * def_lead) + def_rune
vit_bonus = vit_base + ceil(vit_base * vit_bat) + ceil(vit_base * vit_lead) + vit_rune

add_vertical_space(3)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader('Arte 1')
    arte(hp_bonus, atk_bonus, def_bonus, vit_bonus, 1)

with col2:
    st.subheader('Arte 2')
    arte(hp_bonus, atk_bonus, def_bonus, vit_bonus, 2)
    
with col3:
    st.subheader('Arte 3')
    arte(hp_bonus, atk_bonus, def_bonus, vit_bonus, 3)

with col4:
    st.subheader('Arte 4')
    arte(hp_bonus, atk_bonus, def_bonus, vit_bonus, 4)

st.caption('Made by Tomlora :sunglasses:')