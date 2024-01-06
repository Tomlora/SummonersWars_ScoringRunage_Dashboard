import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from st_pages import add_indentation
from fonctions.artefact import dict_arte_effect_english, dataframe_replace_to_english, max_sub_by_proc
from streamlit_extras.no_default_selectbox import selectbox


from fonctions.visuel import css
css()

add_indentation()






def stats(df, n):
    

    column1, column2, column3, column4, column5, column6 = st.columns([
                                                                      1, 1, 1, 1, 1, 1])

    with column1:
        stats_selected = selectbox(
            f'Substat {n}', options=max_sub_by_proc(4, st.session_state.translations_selected).keys(), key=f'substat{n}')

    if stats_selected != None:
        with column2:
            proc = st.number_input(
                f'Proc Substat {n}', min_value=0, max_value=4, format='%i', key=f'proc{n}')

        with column3:
            value = st.number_input(
                st.session_state.langue['valeur'], format='%i', min_value=0, key=f'value{n}')

        with column5:
            max_stats = max_sub_by_proc(proc, st.session_state.translations_selected)[stats_selected]
            st.metric('Max possible', value=max_stats, delta=value-max_stats)

        
        # on filtre
        
        df = df[((df['first_sub'] == stats_selected) & (df['first_sub_value'] > value)) |
            ((df['second_sub'] == stats_selected) & (df['second_sub_value'] > value)) |
            ((df['third_sub'] == stats_selected) & (df['third_sub_value'] > value)) |
            ((df['fourth_sub'] == stats_selected) & (df['fourth_sub_value'] > value))]

    else:
        value = 0
    
    

    return df, stats_selected, value


sub_max = max_sub_by_proc(4, st.session_state.translations_selected)


def upgrade_a():
    
    # on identifie les monstres
            
    # on récupère les données        
    df_arte : pd.DataFrame = st.session_state.data_arte.data_a.copy()
    
    # on fusionne anciennes/nouvelles stats
    
    if st.session_state.translations_selected == 'English':
        df_arte['arte_attribut'] = df_arte['arte_attribut'].replace(dataframe_replace_to_english)
        
        for column in ['first_sub', 'second_sub', 'third_sub', 'fourth_sub']:
            df_arte[column] = df_arte[column].replace(dict_arte_effect_english)
                

    check_v8 = st.checkbox(st.session_state.langue['fusion_substat_arte_v8'], help=st.session_state.langue['fusion_substat_arte_v8_help'])
    
    if check_v8:
        if st.session_state.translations_selected == 'Français':
            df_arte[['first_sub', 'second_sub', 'third_sub', 'fourth_sub']] = df_arte[['first_sub', 'second_sub', 'third_sub', 'fourth_sub']].replace({'RENFORCEMENT ATK' : 'RENFORCEMENT ATK/DEF', 
                                                                                                                                                'RENFORCEMENT DEF' : 'RENFORCEMENT ATK/DEF',
                                                                                                                                                'CRIT DMG S3' : 'CRIT DMG S3/S4',
                                                                                                                                                'CRIT DMG S4' : 'CRIT DMG S3/S4',
                                                                                                                                                'REVENGE' : 'REVENGE ET COOP',
                                                                                                                                                'COOP DMG' : 'REVENGE ET COOP',})
        
        elif st.session_state.translations_selected == 'English':

            df_arte[['first_sub', 'second_sub', 'third_sub', 'fourth_sub']] = df_arte[['first_sub', 'second_sub', 'third_sub', 'fourth_sub']].replace({'ATK Increased' : 'ATK/DEF Increased', 
                                                                                                                                                    'DEF Increased' : 'ATK/DEF Increased',
                                                                                                                                                    'CRIT DMG S3' : 'CRIT DMG S3/S4',
                                                                                                                                                    'CRIT DMG S4' : 'CRIT DMG S3/S4',
                                                                                                                                                    'REVENGE' : 'REVENGE AND COOP',
                                                                                                                                                    'COOP DMG' : 'REVENGE AND COOP',})            
            
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

st.caption('Made by Tomlora :sunglasses:')