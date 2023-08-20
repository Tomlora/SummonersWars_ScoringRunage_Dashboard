import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from st_pages import add_indentation

from streamlit_extras.no_default_selectbox import selectbox

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


def stats(df, n):
    

    column1, column2, column3, column4, column5, column6 = st.columns([
                                                                      1, 1, 1, 1, 1, 1])

    with column1:
        stats_selected = selectbox(
            f'Substat {n}', options=max_sub_by_proc(4).keys(), key=f'substat{n}')

    if stats_selected != None:
        with column2:
            proc = st.number_input(
                f'Proc Substat {n}', min_value=0, max_value=4, format='%i', key=f'proc{n}')

        with column3:
            value = st.number_input(
                st.session_state.langue['valeur'], format='%i', min_value=0, key=f'value{n}')

        with column5:
            max_stats = max_sub_by_proc(proc)[stats_selected]
            st.metric('Max possible', value=max_stats, delta=value-max_stats)

        
        # on filtre
        
        df = df[((df['first_sub'] == stats_selected) & (df['first_sub_value'] > value)) |
            ((df['second_sub'] == stats_selected) & (df['second_sub_value'] > value)) |
            ((df['third_sub'] == stats_selected) & (df['third_sub_value'] > value)) |
            ((df['fourth_sub'] == stats_selected) & (df['fourth_sub_value'] > value))]

    else:
        value = 0
    
    

    return df, stats_selected, value


sub_max = max_sub_by_proc(4)


def upgrade_a():
    
    # on identifie les monstres
            
    # on récupère les données        
    df_arte : pd.DataFrame = st.session_state.data_arte.data_a.copy()
    
    # on fusionne anciennes/nouvelles stats
    
    check_v8 = st.checkbox(st.session_state.langue['fusion_substat_arte_v8'], help=st.session_state.langue['fusion_substat_arte_v8_help'])
    
    if check_v8:
        df_arte[['first_sub', 'second_sub', 'third_sub', 'fourth_sub']] = df_arte[['first_sub', 'second_sub', 'third_sub', 'fourth_sub']].replace({'RENFORCEMENT ATK' : 'RENFORCEMENT ATK/DEF', 
                                                                                                                                                'RENFORCEMENT DEF' : 'RENFORCEMENT ATK/DEF',
                                                                                                                                                'CRIT DMG S3' : 'CRIT DMG S3/S4',
                                                                                                                                                'CRIT DMG S4' : 'CRIT DMG S3/S4',
                                                                                                                                                'REVENGE' : 'REVENGE ET COOP',
                                                                                                                                                'COOP DMG' : 'REVENGE ET COOP',})
    list_type = df_arte['arte_type'].unique().tolist()
    
        
    list_type.sort()     
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        
        set_selected = selectbox('Type', options=list_type, key='type_arte_upgrade')
        
        if set_selected != None:
            df_arte = df_arte[df_arte['arte_type'] == set_selected]
    
    with col2:
        
        list_attribut = df_arte['arte_attribut'].unique().tolist()
            
        slot_selected = selectbox('Attribut', options=list_attribut, key='attribut_arte_upgrade')
        
        if slot_selected != None:
            df_arte = df_arte[df_arte['arte_attribut'] == slot_selected]


    with col3:
        
        list_main_type = df_arte['main_type'].unique().tolist()
        main_type_selected = selectbox('Type', options=list_main_type, key='maintype_arte_upgrade')
        
        if main_type_selected != None:
            df_arte = df_arte[df_arte['main_type'] == main_type_selected]
        

    st.markdown("***")


    # 1

    df_arte, stats1, value1 = stats(df_arte, 1)

    # 2

    df_arte, stats2, value2 = stats(df_arte, 2)

    # 3

    df_arte, stats3, value3 = stats(df_arte, 3)

    # 4

    df_arte, stats4, value4 = stats(df_arte, 4)
    
    
    

    st.markdown("***")
    
    if stats1 != None:
        if df_arte.shape[0] > 0:
            st.text(st.session_state.langue['improve_artefact'].format(df_arte.shape[0]))
        else:
            st.text(st.session_state.langue['best_artefact'])
        
        with st.expander(st.session_state.langue['show_artefact']):
            if df_arte.shape[0] > 0:
                st.dataframe(df_arte[['arte_equiped', 'level', 'efficiency', 'main_type', 'first_sub', 'first_sub_value', 'second_sub', 'second_sub_value', 'third_sub', 'third_sub_value', 'fourth_sub', 'fourth_sub_value']]\
                    .sort_values(by='efficiency', ascending=False)\
                        .rename(columns={'first_sub': 'Sub1',
                                         'first_sub_value': 'Value1',
                                         'second_sub': 'Sub2',
                                         'second_sub_value': 'Value2',
                                         'third_sub': 'Sub3',
                                         'third_sub_value': 'Value3',
                                         'fourth_sub': 'Sub4',
                                         'fourth_sub_value': 'Value4'}))

    else:
        st.info(st.session_state.langue['fill_first_value'])






if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Upgrade Artefact')
        st.text(st.session_state.langue['description_upgrade'])
        upgrade_a()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')

st.caption('Made by Tomlora')