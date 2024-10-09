import pandas as pd
import streamlit as st
from fonctions.visuel import css
from fonctions.gestion_bdd import lire_bdd_perso
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.metric_cards import style_metric_cards
from math import floor
css()
style_metric_cards(background_color='#03152A', border_color='#0083B9', border_left_color='#0083B9', border_size_px=0, box_shadow=False)


@st.cache_data()
def load_monsters():
    df_mob = lire_bdd_perso('''SELECT name, speed, image_filename from sw_ref_monsters
                                    INNER JOIN sw_ref_monsters_stats on sw_ref_monsters.id = sw_ref_monsters_stats.id
                                    WHERE sw_ref_monsters.awaken_level = 1 and sw_ref_monsters.natural_stars >= 3''' , index_col='name').T  
        
    df_mob['url'] = df_mob.apply(
                            lambda x:  f'https://swarfarm.com/static/herders/images/monsters/{x["image_filename"]}', axis=1)
        
    return df_mob

def opti_speed():
    # On lit la BDD
    # on récupère la data
    
    df_speed = st.session_state.data_rune
    
    st.session_state.df_mob_optimisation = load_monsters()
    
    set_4= ['Violent', 'Will', 'Despair', 'Swift', 'Fatal','Rage', 'Vampire']
    
    set_2 = ['Will', 'Destroy', 'Blade', 'Endure', 'Energy', 'Focus', 'Guard', 'Nemesis', 'Shield', 'Revenge', 'Tolerance']
    
    speed_slot2 = st.checkbox('Speed en Slot 2', True)
    
    # set 1
    
    set1 = selectbox('Set 4 slots', set_4)
    
    # set 2
    
    set2 = selectbox('Set 2 slots', set_2)
    
    if set1 != None:
    
        st.session_state.optimisation = df_speed.optimisation_max_speed(set1, set2, speed_slot2)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(st.session_state.optimisation[0])
        
        with col2:
            st.metric('Speed Max', st.session_state.optimisation[1])
        
    
        st.subheader('Sur un monstre')
        

        @st.experimental_fragment
        def calcul_monsters():
        
            monster_selected = st.selectbox('Selectionner le monstre', st.session_state.df_mob_optimisation.index.unique())
            
            add_vertical_space(3)
            
            
            col3, col4 = st.columns([0.75, 0.25])
            
            with col3:
                speed_monster = st.session_state.df_mob_optimisation.loc[monster_selected]['speed']
                
                col1_1, col1_2, col1_3 = st.columns(3)
                
                with col1_1:
                    st.metric('Speed Base', speed_monster)
                    
                with col1_2:
                    if set1 == 'Swift':
                        bonus_swift = floor(speed_monster * 0.25)
                    else:
                        bonus_swift = 0
                    st.metric('Swift Bonus', bonus_swift)
                
                with col1_3:
                    st.metric('Speed Total', speed_monster + bonus_swift + st.session_state.optimisation[1])
                    
            
            with col4:
                st.image(st.session_state.df_mob_optimisation.loc[monster_selected]['url'], width=120, caption=monster_selected)
                
        calcul_monsters()

    


if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Optimisation Speed')
        opti_speed()
    
    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")
    
    
st.caption('Made by Tomlora :sunglasses:')