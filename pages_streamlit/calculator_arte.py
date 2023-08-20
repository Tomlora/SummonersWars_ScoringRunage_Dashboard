import streamlit as st
from st_pages import add_indentation

from fonctions.visuel import css
css()

add_indentation()

@st.cache_data
def max_sub_by_proc(proc):
    "1 à 4"

    proc += 1  # le proc à +0

    
    sub_max = {
        'ATK EN FONCTION HP PERDUS' : 14 * proc, #ancien
        'DEF EN FONCTION HP PERDUS' : 14 * proc, # ancien
        'SPD EN FONCTION HP PERDUS' : 14 * proc, # ancien
        "SPD EN CAS D'INCAPACITE" : 6 * proc,
        'RENFORCEMENT ATK' : 5 * proc, #ancien
        'RENFORCEMENT DEF' : 4 * proc, # ancien
        'RENFORCEMENT SPD' : 6 * proc,
        'RENFORCEMENT CRITRATE' : 6 * proc,
        'REVENGE' : 4 * proc,
        'COOP DMG' : 4 * proc,
        'BOMBE DMG' : 4 * proc,
        'DMG RENVOYE' : 3 * proc,
        'CRUSHING DMG' : 4 * proc,
        "DMG RECU EN CAS D'INCAPACITE" : 3 * proc,
        'CRIT DMG RECU' : 4 * proc,
        'VOL DE VIE' : 8 * proc,
        'HP REVIVE' : 6 * proc,
        'ATB REVIVE' : 6 * proc,
        'DMG SUPP EN FONCTION DES HP' : 0.3 * proc,
        "DMG SUPP EN FONCTION DE L'ATQ" : 4 * proc,
        'DMG SUPP EN FONCTION DE LA DEF' : 4 * proc,
        'DMG SUPP EN FONCTION DE LA SPD' : 40 * proc,
        'CRIT DMG EN FONCTION DES HP ELEVES' : 6 * proc,
        'CRIT DMG EN FONCTION DES HP FAIBLES' : 12 * proc,
        'CRIT DMG SUR CIBLE UNIQUE' : 4 * proc,
        'REVENGE ET COOP' : 4 * proc,
        'RENFORCEMENT ATK/DEF' : 5 * proc,
        'DMG SUR FEU' : 5 * proc,
        'DMG SUR EAU' : 5 * proc,
        'DMG SUR VENT' : 5 * proc,
        'DMG SUR LUMIERE' : 5 * proc,
        'DMG SUR DARK' : 5 * proc,
        'REDUCTION SUR FEU' : 6 * proc,
        'REDUCTION SUR EAU' : 6 * proc,
        'REDUCTION SUR VENT' : 6 * proc,
        'REDUCTION SUR LUMIERE' : 6 * proc,
        'REDUCTION SUR DARK' : 6 * proc,
        'CRIT DMG S1' : 6 * proc,
        'CRIT DMG S2' : 6 * proc,
        'CRIT DMG S3' : 6 * proc, # ancien
        'CRIT DMG S4' : 6 * proc, # ancien
        'SOIN S1' : 6 * proc,
        'SOIN S2' : 6 * proc,
        'SOIN S3' : 6 * proc,
        'PRECISION S1' : 6 * proc,
        'PRECISION S2' : 6 * proc,
        'PRECISION S3' : 6 * proc,
        'CRIT DMG S3/S4'  : 6 * proc,
        'PREMIER HIT CRIT DMG' : 6 * proc
    }
    return sub_max

import json
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


def stats(n):

    column1, column2, column3, column4, column5 = st.columns([2.5, 1, 1, 1, 1])

    with column1:
        stats_selected = st.selectbox(
            f'Substat {n}', options=max_sub_by_proc(4).keys(), key=f'substat_arte{n}')

    with column2:
        proc = st.number_input(
            f'Proc Substat {n}', min_value=0, max_value=4, format='%i', key=f'proc_arte{n}')

    with column3:
        if stats_selected == 'DMG SUPP EN FONCTION DES HP': # float
            value = st.number_input(f'Valeur de base', min_value=0, key=f'value_arte{n}')
        else:
            value = st.number_input(
                f'Valeur de base', format='%i', min_value=0, key=f'value_arte{n}')

    with column5:
        max_stats = max_sub_by_proc(proc)[stats_selected]
        st.metric('Max possible', value=max_stats, delta=value-max_stats)


    return stats_selected, value


sub_max = max_sub_by_proc(0)


def calculateur_efficiency():

    st.info(st.session_state.langue['no_json_need'], icon="ℹ️")


    st.markdown("***")

    # 1

    stats1, value1 = stats(1)

    # 2

    stats2, value2 = stats(2)

    # 3

    stats3, value3 = stats(3)

    # 4

    stats4, value4 = stats(4)

    st.subheader('Efficience')


    
    efficiency = round(((value1 / sub_max[stats1]
                                            + value2 / sub_max[stats2]
                                            + value3 / sub_max[stats3]
                                            + value4 / sub_max[stats4])
                                           / 8)*100, 2)


    st.markdown(f'Efficience : :green[{efficiency}]')

    def reset():
        '''Reset les boutons'''
        st.session_state.substat_arte1 = 'REDUCTION SUR FEU'
        st.session_state.substat_arte2 = 'REDUCTION SUR FEU'
        st.session_state.substat_arte3 = 'REDUCTION SUR FEU'
        st.session_state.substat_arte4 = 'REDUCTION SUR FEU'
        st.session_state.proc_arte1 = 0
        st.session_state.proc_arte2 = 0
        st.session_state.proc_arte3 = 0
        st.session_state.proc_arte4 = 0
        st.session_state.value_arte1 = 0
        st.session_state.value_arte2 = 0
        st.session_state.value_arte3 = 0
        st.session_state.value_arte4 = 0


    st.markdown('***')
    st.button('Reset', on_click=reset)


st.title("Calculateur d'efficience")
calculateur_efficiency()

st.caption('Made by Tomlora')