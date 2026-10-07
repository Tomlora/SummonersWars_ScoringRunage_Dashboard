from fonctions.access import require_saved_page
require_saved_page()
import pandas as pd
import streamlit as st
from fonctions.visuel import css
from fonctions.gestion_bdd import lire_bdd_perso
from fonctions.widgets import selectbox
from math import floor
css()



@st.cache_data()
def load_monsters():
    df_mob = lire_bdd_perso('''SELECT name, sw_ref_monsters_stats.speed AS speed, image_filename from sw_ref_monsters
                                    INNER JOIN sw_ref_monsters_stats on sw_ref_monsters.id = sw_ref_monsters_stats.id
                                    WHERE sw_ref_monsters.awaken_level = 1 and sw_ref_monsters.natural_stars >= 3''' , index_col='name').T  
        
    df_mob['url'] = 'https://swarfarm.com/static/herders/images/monsters/' + df_mob['image_filename']

    return df_mob

def opti_speed():
    # On lit la BDD
    # on récupère la data
    
    df_speed = st.session_state.data_rune
    
    st.session_state.df_mob_optimisation = load_monsters()
    
    set_4= ['Violent', 'Despair', 'Swift', 'Fatal','Rage', 'Vampire']
    
    set_2 = ['Will', 'Destroy', 'Blade', 'Endure', 'Energy', 'Focus', 'Guard', 'Nemesis', 'Shield', 'Revenge', 'Tolerance']
    
    speed_slot2 = st.checkbox('Principale SPD en slot 2 / SPD main in slot 2', True, help='Valeurs actuelles du JSON, sans projection à +15 / Current JSON values, no +15 projection')
    
    # set 1
    
    set1 = selectbox('Set 4 slots', set_4)
    
    # set 2
    
    set2 = selectbox('Set 2 slots', set_2)
    
    if set1 != None:
    
        from fonctions.analysis import fastest_build
        from fonctions.workspace import active_locks
        candidates=df_speed.data_set.loc[~df_speed.data_set.index.isin(active_locks())]
        st.session_state.optimisation = fastest_build(candidates,set1,set2,speed_slot2)
        
        if st.session_state.optimisation[1] is None:
            st.info('Aucune combinaison compatible / No compatible build')
            return
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(st.session_state.optimisation[0])
        
        with col2:
            st.metric('Speed Max', st.session_state.optimisation[1])

        from fonctions.rune_card import rune_card
        from fonctions.journey import tr
        with st.expander(tr('Retrouver les runes de ce build', 'Find the runes in this build')):
            rune_card(df_speed, st.session_state.optimisation[0].id_rune, 'ui_speed_rune')
        
    
        if st.session_state.df_mob_optimisation.empty:
            st.info('Référentiel des monstres indisponible / Monster reference unavailable.')
            return
        st.subheader('Sur un monstre')
        

        @st.fragment
        def calcul_monsters():
        
            monster_selected = st.selectbox('Selectionner le monstre', st.session_state.df_mob_optimisation.index.unique())
            
            st.space(84)
            
            
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
