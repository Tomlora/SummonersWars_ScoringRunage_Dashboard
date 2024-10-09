import streamlit as st
import pandas as pd


from streamlit_extras.no_default_selectbox import selectbox

from fonctions.visuel import css
css()




sub_max_lgd = {'HP': 550, 'HP%': 10, 'ATQ': 30,
               'ATQ%': 10, 'DEF': 30, 'DEF%': 10, 'SPD': 5}
sub_max_heroique = {'HP': 450, 'HP%': 7, 'ATQ': 22,
                    'ATQ%': 7, 'DEF': 22, 'DEF%': 7, 'SPD': 4}

@st.cache_data
def max_sub_by_proc(proc):
    "1 à 4"

    proc += 1  # le proc à +0
    sub_max = {'HP': (375 * proc) * 2,  # PV flat
               'HP%': 8 * proc,  # PV%
               'ATQ': (20 * proc) * 2,  # ATQ FLAT
               'ATQ%': 8 * proc,  # ATQ%
               'DEF': (20 * proc) * 2,  # DEF FLAT
               'DEF%': 8 * proc,  # DEF %
               'SPD': 6 * proc,  # SPD
               'CRIT': 6 * proc,  # CRIT
               'DCC': 7 * proc,  # DCC
               'RES': 8 * proc,  # RES
               'ACC': 8 * proc}  # ACC
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

        if stats_selected in sub_max_lgd.keys():     # si meulable

            with column6:
                value_meule = st.number_input(
                    st.session_state.langue['meule'], format='%i', min_value=0, key=f'meule{n}')

        else:
            value_meule = 0

        value_total = value + value_meule
        
        # on filtre
        
        df = df[((df['first_sub'] == stats_selected) & (df['first_sub_value_total'] > value_total)) |
            ((df['second_sub'] == stats_selected) & (df['second_sub_value_total'] > value_total)) |
            ((df['third_sub'] == stats_selected) & (df['third_sub_value_total'] > value_total)) |
            ((df['fourth_sub'] == stats_selected) & (df['fourth_sub_value_total'] > value_total))]

    else:
        value = 0
        value_total = 0
    
    

    return df, stats_selected, value, value_total


sub_max = max_sub_by_proc(4)


def upgrade_r():
    
       
    # on récupère les données
    df_rune : pd.DataFrame = st.session_state.data_rune.data_set.copy()
    
    # on prépare les inputs
    set = df_rune['rune_set'].unique().tolist()
    
    slot = df_rune['rune_slot'].unique().tolist()
    
    main_stat = df_rune['main_type'].unique().tolist()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        
        set_selected = selectbox('Set', options=set)
        
        if set_selected != None:
            df_rune = df_rune[df_rune['rune_set'] == set_selected]
    
    with col2:
            
        slot_selected = st.selectbox('Slot', options=slot)
        
        df_rune = df_rune[df_rune['rune_slot'] == slot_selected]
        
    with col3:
            
        main_stat_selected = selectbox('Main stat', options=main_stat)
            
        if main_stat_selected != None:    
            df_rune = df_rune[df_rune['main_type'] == main_stat_selected]

    column0_0, column0_1 = st.columns(2)


    with column0_0:
        innate_stats = st.selectbox(
            'Innate', options=max_sub_by_proc(4).keys(), key='innate')

    with column0_1:
        value0 = st.number_input(
            f'Valeur', format='%i', min_value=0, key='value0', help="S'il n'y en a pas, mettre 0")

    st.markdown("***")

    # 1

    df_rune, stats1, value1, total1 = stats(df_rune, 1)

    # 2

    df_rune, stats2, value2, total2 = stats(df_rune, 2)

    # 3

    df_rune, stats3, value3, total3 = stats(df_rune, 3)

    # 4

    df_rune, stats4, value4, total4 = stats(df_rune, 4)
    
    
    

    st.markdown("***")
    
    if stats1 != None:
        if df_rune.shape[0] > 0:
            st.text(st.session_state.langue['improve_rune'].format(df_rune.shape[0]))
        else:
            st.text(st.session_state.langue['best_rune'])
        
        with st.expander(st.session_state.langue['show_rune']):
            if df_rune.shape[0] > 0:
                st.dataframe(df_rune[['rune_equiped', 'level', 'efficiency', 'main_type', 'innate_type', 'first_sub', 'first_sub_value_total', 'second_sub', 'second_sub_value_total', 'third_sub', 'third_sub_value_total', 'fourth_sub', 'fourth_sub_value_total']]\
                    .sort_values(by='efficiency', ascending=False)\
                        .rename(columns={'first_sub': 'Sub1',
                                         'first_sub_value_total': 'Value1',
                                         'second_sub': 'Sub2',
                                         'second_sub_value_total': 'Value2',
                                         'third_sub': 'Sub3',
                                         'third_sub_value_total': 'Value3',
                                         'fourth_sub': 'Sub4',
                                         'fourth_sub_value_total': 'Value4'}))

    else:
        st.info(st.session_state.langue['fill_first_value'])





if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Upgrade Rune')
        st.text(st.session_state.langue['description_upgrade'])
        upgrade_r()
    
    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")

st.caption('Made by Tomlora :sunglasses:')