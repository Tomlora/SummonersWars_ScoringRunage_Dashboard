import pandas as pd
import streamlit as st
from fonctions.gestion_bdd import lire_bdd_perso
from streamlit_extras.metric_cards import style_metric_cards
import numpy as np

from st_pages import add_indentation
from fonctions.visuel import css
css()

add_indentation()

@st.cache_data()
def charger_data():
    df = lire_bdd_perso('''SELECT sw_ref_monsters.name, sw_ref_monsters_stats.speed,  sw_ref_monsters.image_filename,
                        sw_ref_leader.attribute_leader,  sw_ref_leader.amount_leader from sw_ref_monsters_stats 
                        INNER JOIN sw_ref_monsters ON sw_ref_monsters.id = sw_ref_monsters_stats.id
                        INNER JOIN sw_ref_leader ON sw_ref_leader.id_leader = sw_ref_monsters.id_leader
                        WHERE sw_ref_monsters_stats.awaken_level >= 1''', index_col=None).T
    
    df['img_url'] = df['image_filename'].apply(lambda x: f'https://swarfarm.com/static/herders/images/monsters/{x}')
    
    
    return df

def calcule_speed(base_speed, tower, lead, rune_speed, buff_spd, arte):
    
    cbt_spd = base_speed * (1 + tower + lead) + rune_speed    
    
    if buff_spd >= 0: # s'il y a un buff spd
        cbt_spd = cbt_spd * (1 + buff_spd * (1 + arte/100))
        
    return cbt_spd


def calcule_tick(speed):
    ranks = [
        (12, 130),
        (11, 143),
        (10, 159),
        (9, 179),
        (8, 205),
        (7, 239),
        (6, 286),
        (5, 358),
        (4, 477),
        (3, float('inf'))]

    for tickspeed, lp_threshold in ranks:
        if speed < lp_threshold:
            break
        
    return tickspeed

def spdtuning():
    style_metric_cards(background_color='#03152A', border_color='#0083B9', border_left_color='#0083B9', border_size_px=3, box_shadow=False)
    
    ranks = [
        (12, 130),
        (11, 143),
        (10, 159),
        (9, 179),
        (8, 205),
        (7, 239),
        (6, 286),
        (5, 358),
        (4, 477),
        (3, float('inf'))]

    # Créer un DataFrame
    df_tick = pd.DataFrame(ranks, columns=['Tick', 'Value (inférieur à)'])
    df_tick.set_index('Tick', inplace=True)
    df = charger_data()
    
    
    liste_monstres = df['name'].unique().tolist()
    
    monstre_selected = st.selectbox('Selectionner un monstre', liste_monstres, index=0)

    
    st.image(df[df['name'] == monstre_selected]['img_url'].values[0])
    
    base_speed = df[df['name'] == monstre_selected]['speed'].values[0]
    
    bool_lead_speed = df[df['name'] == monstre_selected]['attribute_leader'].values[0] == 'Attack Speed'
    
    if bool_lead_speed:
        bonus_lead = int(df[df['name'] == monstre_selected]['amount_leader'].values[0][:2])
    else:
        bonus_lead = 0

    
    col1, col2 = st.columns(2)
    col1.metric('Speed de base', base_speed)
    col2.metric('Lead Speed (%)', bonus_lead)
    
    tower = st.slider('Tower (%)', min_value=0, max_value=15, value=15)
    
    tower = tower / 100 # %
    
    lead = st.number_input('Lead (%)', min_value=0, max_value=50, value=int(bonus_lead))
    
    lead = lead / 100 # %
    
    rune_speed = st.number_input('Bonus Rune', min_value=0, max_value=300, value=0, step=1)
    
    bool_buff_speed = st.checkbox('Buff Speed (%)', help='Bonus de 30%')
    
    if bool_buff_speed:
        buff_speed = 0.3
    else:
        buff_speed = 0

    
    bonus_arte = st.slider('Arte Speed Effet (%)', min_value=0, max_value=70, value=0)
    
    
    speed_total = calcule_speed(base_speed, tower, lead, rune_speed, buff_speed, bonus_arte)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.expander('Help'):
            st.text('zzzz')
        st.metric('Speed total', int(np.ceil(speed_total)))
    with col2:
        with st.expander('Help'):
            st.dataframe(df_tick)
        st.metric('Tickspeed', calcule_tick(int(np.ceil(speed_total))))
    
    
    



   
st.title('SpeedTuning')
spdtuning()
    

    
    
st.caption('Made by Tomlora :sunglasses:')