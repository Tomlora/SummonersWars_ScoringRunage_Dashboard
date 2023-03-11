import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from st_pages import add_indentation

add_indentation()


sub_max_lgd = {'HP': 550, 'HP%': 10, 'ATQ': 30, 'ATQ%': 10, 'DEF': 30, 'DEF%': 10, 'SPD': 5}
sub_max_heroique = {'HP': 450, 'HP%': 7, 'ATQ': 22, 'ATQ%': 7, 'DEF': 22, 'DEF%': 7, 'SPD': 4}

def max_sub_by_proc(proc):
    "1 à 4"
    
    proc += 1 # le proc à +0
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




def stats(n):
     
    column1, column2, column3, column4, column5, column6 = st.columns([1,1,1,1,1,1])
    
    with column1:
        stats_selected = st.selectbox(f'Substat {n}', options=max_sub_by_proc(4).keys(), key=f'substat{n}')
        
    with column2:
        proc = st.number_input(f'Proc Substat {n}', min_value=0, max_value=4, format='%i', key=f'proc{n}')
        
    with column3:
        value = st.number_input(f'Valeur de base', format='%i', min_value=0, key=f'value{n}')
        
    with column5:
        max_stats = max_sub_by_proc(proc)[stats_selected]
        st.metric('Max possible', value=max_stats, delta=value-max_stats)
    
    if stats_selected in sub_max_lgd.keys():     # si meulable
        
        with column6:
            value_meule = st.number_input('Meule', format='%i', min_value=0, key=f'meule{n}')
                        
    else:
        value_meule = 0
        
    value_total = value + value_meule
    value_max_hero = value + sub_max_heroique.get(stats_selected,0)
    value_max_lgd = value + sub_max_lgd.get(stats_selected,0)
    
    return stats_selected, value, value_total, value_max_hero, value_max_lgd

sub_max = max_sub_by_proc(4)

def calculateur_efficiency():
    
    st.success("Cet onglet n'a pas besoin de json")
      
    column0_0, column0_1 = st.columns(2)
    
    
    with column0_0:
        innate_stats = st.selectbox('Innate', options=max_sub_by_proc(4).keys(), key='innate')
    
    with column0_1:
        value0 = st.number_input(f'Valeur', format='%i', min_value=0, key='value0')
        
    st.markdown("***") 
    
    # 1

    
    stats1, value1, total1, value_max_hero1, value_max_lgd1 = stats(1)
    
    #2
    
    
    stats2, value2, total2, value_max_hero2, value_max_lgd2  = stats(2)
    
    #3
  
    stats3, value3, total3,  value_max_hero3, value_max_lgd3  = stats(3)
    
    #4

    stats4, value4, total4,  value_max_hero4, value_max_lgd4  = stats(4)
    
    
    st.subheader('Efficience')
    
    
    if value0 == 0:
        efficiency = round(((1 + total1 / sub_max[stats1]
                                                    + total2 / sub_max[stats2]
                                                    + total3 / sub_max[stats3]
                                                    + total4 / sub_max[stats4])
                                                    / 2.8)*100, 2)
        
        efficiency_max_hero = round(((1 + value_max_hero1 / sub_max[stats1]
                                                    + value_max_hero2 / sub_max[stats2]
                                                    + value_max_hero3 / sub_max[stats3]
                                                    + value_max_hero4 / sub_max[stats4])
                                                    / 2.8)*100, 2)

        efficiency_max_lgd = round(((1 + value_max_lgd1 / sub_max[stats1]
                                                    + value_max_lgd2 / sub_max[stats2]
                                                    + value_max_lgd3 / sub_max[stats3]
                                                    + value_max_lgd4 / sub_max[stats4])
                                                    / 2.8)*100, 2)
    else:
        efficiency = round(((1 + value0 / sub_max[innate_stats] + 
                             total1 / sub_max[stats1]
                                                    + total2 / sub_max[stats2]
                                                    + total3 / sub_max[stats3]
                                                    + total4 / sub_max[stats4])
                                                    / 2.8)*100, 2)
        
        efficiency_max_hero = round(((1 + value0 / sub_max[innate_stats] + 
                             value_max_hero1 / sub_max[stats1]
                                                    + value_max_hero2 / sub_max[stats2]
                                                    + value_max_hero3 / sub_max[stats3]
                                                    + value_max_hero4 / sub_max[stats4])
                                                    / 2.8)*100, 2)

        efficiency_max_lgd = round(((1 + value0 / sub_max[innate_stats] + 
                             value_max_lgd1 / sub_max[stats1]
                                                    + value_max_lgd2 / sub_max[stats2]
                                                    + value_max_lgd3 / sub_max[stats3]
                                                    + value_max_lgd4 / sub_max[stats4])
                                                    / 2.8)*100, 2)
        
    
    
    st.markdown(f'Efficience : :green[{efficiency}]')
    st.markdown(f'Efficience max heroique : :violet[{efficiency_max_hero}]')
    st.markdown(f'Efficience max lgd : :orange[{efficiency_max_lgd}]')
    
    
    def reset():
        '''Reset les boutons'''
        st.session_state.innate = 'HP'
        st.session_state.substat1 = 'HP'
        st.session_state.substat2 = 'HP'
        st.session_state.substat3 = 'HP'
        st.session_state.substat4 = 'HP'
        st.session_state.proc1 = 0
        st.session_state.proc2 = 0
        st.session_state.proc3 = 0
        st.session_state.proc4 = 0
        st.session_state.value0 = 0
        st.session_state.value1 = 0
        st.session_state.value2 = 0
        st.session_state.value3 = 0
        st.session_state.value4 = 0
        st.session_state.meule1 = 0
        st.session_state.meule2 = 0
        st.session_state.meule3 = 0
        st.session_state.meule4 = 0
        

    st.markdown('***')
    st.button('Reset', on_click=reset)
        
    




calculateur_efficiency()

