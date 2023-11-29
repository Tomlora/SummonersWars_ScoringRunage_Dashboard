import streamlit as st
from st_pages import add_indentation
from fonctions.artefact import max_sub_by_proc
from fonctions.visuel import css
css()

add_indentation()


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

st.caption('Made by Tomlora :sunglasses:')