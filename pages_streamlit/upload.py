    
import pandas as pd

import streamlit as st
import json
from datetime import datetime, timedelta
from fonctions.visuel import load_lottieurl, css
from streamlit_lottie import st_lottie
from params.coef import coef_set, coef_set_spd, liste_substat_arte
from streamlit_extras.switch_page_button import switch_page
from fonctions.gestion_bdd import sauvegarde_bdd, update_info_compte, get_user, requete_perso_bdd, cancel, lire_bdd_perso, lire_bdd
from fonctions.runes import Rune
from fonctions.artefact import Artefact
from st_pages import add_indentation
from sqlalchemy.exc import InternalError, OperationalError
from dateutil import tz
# import tracemalloc
import gc

try:
    st.set_page_config(layout='wide')
except:
    pass


css()
add_indentation()

@st.cache_data
def show_lottie(img, height=300 , width=300):
    st_lottie(img, height=height, width=width)

@st.cache_data
def chargement_params():
    category_selected = ['Violent', 'Seal', 'Will', 'Destroy', 'Despair', 'Intangible']
    category_value = ", ".join(category_selected)

    category_selected_spd = ['Violent', 'Seal', 'Will', 'Destroy', 'Despair', 'Swift', 'Intangible']
    category_value_spd = ", ".join(category_selected_spd)
    
    return category_selected,category_selected_spd, coef_set, coef_set_spd

st.session_state.category_selected, st.session_state.category_selected_spd, st.session_state.coef_set, st.session_state.coef_set_spd = chargement_params()

@st.cache_data(ttl=timedelta(minutes=30))
def nb_data():
    timezone=tz.gettz('Europe/Paris')
    heure_update = datetime.now(timezone)
    heure = heure_update.strftime("%H:%M")
    # nb_user = get_number_row("sw_user")
    # nb_guilde = get_number_row("sw_guilde")
    # nb_score = get_number_row("sw_score")
    df_count = lire_bdd_perso('SELECT * from public.count_rows', index_col='table').T
    
    nb_user = df_count.loc['sw_user'].values[0]
    nb_guilde = df_count.loc['sw_guilde'].values[0]
    nb_score = df_count.loc['sw_score'].values[0]
    
    return nb_user, nb_guilde, nb_score, heure

@st.cache_data(ttl=timedelta(minutes=30))
def date_du_jour():
    currentMonth = str(datetime.now().month)
    currentYear = str(datetime.now().year)
    currentDay = str(datetime.now().day)
    return f'{currentDay}/{currentMonth}/{currentYear}'


# on charge swarfarm
@st.cache_data(show_spinner=False)
def load_swarfarm():
    swarfarm = lire_bdd('sw_ref_monsters').T.drop('index', axis=1)
    swarfarm[['element', 'archetype']] = swarfarm[['element', 'archetype']].astype('category')
    return swarfarm


def format_sql(df):
    df['id'] = st.session_state['id_joueur']
    df['date'] = date_du_jour()
    
    return df

if 'submitted' not in st.session_state:
    st.session_state.submitted = False



# def upload_json(category_selected, coef_set, category_selected_spd, coef_set_spd):


try:
    nb_user, nb_guilde, nb_score, heure = nb_data()
except InternalError as e:
    print(e)
    cancel()
    st.warning('Erreur')
    st.session_state['submitted'] = False

except OperationalError as e:
    print(e)
    cancel()
    st.warning('Erreur')
    st.session_state['submitted'] = False

@st.cache_data
def translation(langue):
    if langue == 'Français':
        return json.load(open('langue/fr.json', encoding='utf-8'))
    elif langue == 'English':
        return json.load(open('langue/en.json', encoding='utf-8'))
                    
def upload_sw():
    
    # tracemalloc.start()
    
    # current, peak = tracemalloc.get_traced_memory()
    
    # print(current / (1024*1024))
    # print(peak / (1024 * 1024))
    

        
    
    

    col1, col2, col3 = st.columns([0.25,0.50,0.25])
    with col2:

        st.title('Scoring SW')
        
        st.session_state.translations_selected = st.radio('Langue', ['Français', 'English'], index=0, key='translations', horizontal=True, help='En cours... / Incoming...')
    
        st.session_state.langue = translation(st.session_state.translations_selected)
        with st.form('Data du compte'):
            st.file_uploader(st.session_state.langue['uploader_fichier'],
                            type=['json'],
                            help='Json SW Exporter',
                            key='file')
            
        
            st.session_state['submitted'] = st.form_submit_button(st.session_state.langue['calcul_upload'])
            
            st.info(body=st.session_state.langue['telechargement_wait'], icon="🚨")
            st.warning(body=st.session_state.langue['mode_appli'],
                       icon="⚠️")
            st.info(body=st.session_state.langue['warning_telechargement'], icon='☕')
            st.info(body=st.session_state.langue['warning_choice'], icon='🔒')
            
            st.markdown(f':blue[{heure}] : :green[{nb_user}] {st.session_state.langue["utilisateurs"]} | :violet[{nb_guilde}] {st.session_state.langue["guildes"]} | :orange[{nb_score}] {st.session_state.langue["scores"]}')


    if not st.session_state.submitted:
        col1, col2, col3 = st.columns(3)
        with col2:
            img = load_lottieurl('https://assets5.lottiefiles.com/packages/lf20_ABViugg18Y.json')
            show_lottie(img)

    if st.session_state['file'] is not None and st.session_state.submitted:
        
        # current, peak = tracemalloc.get_traced_memory()
    
        # print(current / (1024*1024))
        # print(peak / (1024 * 1024))
        
        def telechargement_json():
            st.session_state.swarfarm = load_swarfarm()
            
            
            with st.spinner(st.session_state.langue['loading_json']):
                try:

                    
                    st.session_state.data_json = json.load(st.session_state.file)
                    st.session_state.file.close()
                    st.session_state.pop('file')
                    

                    
                    # infos du compte
                    try:
                        st.session_state.pseudo = st.session_state.data_json['wizard_info']['wizard_name']
                        st.session_state.compteid = st.session_state.data_json['wizard_info']['wizard_id']
                        st.session_state.lang = st.session_state.data_json['wizard_info']['wizard_last_country']
                        st.session_state.mana = st.session_state.data_json['wizard_info']['wizard_mana']
                        
                        st.session_state.arena_win = st.session_state.data_json['pvp_info']['arena_win']
                        st.session_state.arena_lose = st.session_state.data_json['pvp_info']['arena_lose']
                        st.session_state.rank_wb = st.session_state.data_json['my_worldboss_best_ranking']['ranking']
                        st.session_state.dmg_wb = st.session_state.data_json['my_worldboss_best_ranking']['accumulate_damage']
                        
                    except KeyError: # fichier pas au bon format
                        st.warning(st.session_state.langue['error_incompatible'])
                        st.session_state.submitted = False
                        exit()
                    
                    
                    try:
                        st.session_state.guildeid = st.session_state.data_json['guild']['guild_info']['guild_id']
                        st.session_state.guilde = st.session_state.data_json['guild']['guild_info']['name']
                    except TypeError: # pas de guilde
                        st.session_state.guildeid = 0
                        st.session_state.guilde = 'Aucune' 
                        
                    # Base monsters
                        
                    data_mobs = pd.DataFrame.from_dict(
                            st.session_state['data_json'], orient="index").transpose()

                    data_mobs = data_mobs['unit_list']

                        # On va boucler et retenir ce qui nous intéresse..
                    list_mobs = []

                    for monstre in data_mobs[0]:
                        unit = monstre['unit_id']
                        master_id = monstre['unit_master_id']
                        stars = monstre['class']
                        level = monstre['unit_level']
                        list_mobs.append([unit, master_id, stars, level,
                                          monstre['atk'], monstre['def'], monstre['spd'], monstre['resist'], monstre['accuracy'],
                                        monstre['critical_rate'], monstre['critical_damage']])
                        
                        for i in range(6):  # itération sur les runes de 1 à 6
                            if len(monstre['runes']) > i:
                                list_mobs[-1].append(monstre['runes'][i]['rune_id'])
                            else:  # s'il n'a pas de rune dans le slot, on met 0
                                list_mobs[-1].append(0)

                            # On met ça en dataframe
                    st.session_state.df_mobs = pd.DataFrame(list_mobs, columns=['id_unit', 'id_monstre', '*', 'level',
                                                                                'atk', 'def', 'spd',
                                                                                'resist', 'accuracy', 'CRIT', 'DCC',
                                                                                'Rune1', 'Rune2', 'Rune3', 'Rune4', 'Rune5', 'Rune6'])
                        
                    # swarfarm

                    swarfarm = st.session_state.swarfarm[[
                                'com2us_id', 'name']].set_index('com2us_id')
                    st.session_state.df_mobs['name_monstre'] = st.session_state.df_mobs['id_monstre'].map(
                                swarfarm.to_dict(orient="dict")['name'])
                    

                    # On peut faire le mapping...

                    df_identification = st.session_state.df_mobs[['id_unit', 'name_monstre']].set_index('id_unit')
                    
                    st.session_state.identification_monsters = df_identification.to_dict(orient="dict")['name_monstre']         
                    
                    # On peut désormais s'occuper des runes
                    
                    data_rune = Rune(st.session_state.data_json, st.session_state.identification_monsters)
                        
                    st.session_state.data_rune = data_rune
                    

                    st.session_state.set_rune = list(data_rune.set_to_show.values())
                    st.session_state.set_rune.sort()
                    
                    # Artefact
            
                    st.session_state.data_arte = Artefact(st.session_state.data_json, st.session_state.identification_monsters)
                    
                    # st.session_state.data_grind = data_rune.data.copy()
                    st.session_state.data_avg = data_rune.calcul_efficiency_describe()

                        # --------------------- calcul score rune

                    tcd_value, st.session_state.score = data_rune.scoring_rune(
                            st.session_state.category_selected, coef_set)
                        
                    st.session_state.tcd_detail_score = data_rune.tcd_df_efficiency
                        

                        # -------------------------- calcul score spd rune

                    st.session_state.tcd_spd, st.session_state.score_spd = data_rune.scoring_spd(
                            st.session_state.category_selected_spd, coef_set_spd)


                        # calcul score arte

                    st.session_state.tcd_arte, st.session_state.score_arte = st.session_state.data_arte.scoring_arte()
                    


                        
                        # calcul max value rune
                        
                    st.session_state.df_max = data_rune.calcul_value_max() # TODO : Reduire le temps de calcul
                    
                    st.session_state.df_max_slot = data_rune.calcul_value_max_per_slot()
                    



                        # -------------------------- on enregistre
                    try:
                        st.session_state.id_joueur, st.session_state.visibility, guilde_id, st.session_state.rank = get_user(
                                st.session_state['compteid'], type='id')
                        
                        requete_perso_bdd('''INSERT INTO sw_guilde(guilde, guilde_id) VALUES (:guilde, :guilde_id)
                                                ON CONFLICT (guilde_id)
                                                DO NOTHING;''',
                                                {'guilde': st.session_state['guilde'],
                                                'guilde_id': st.session_state['guildeid']})
                    except IndexError:
                        try:
                            st.session_state.id_joueur, st.session_state.visibility, guilde_id, st.session_state.rank  = get_user(
                                    st.session_state['pseudo'], id_compte=st.session_state['compteid'])
                        except IndexError:  # le joueur n'existe pas ou est dans l'ancien système
                            requete_perso_bdd('''INSERT INTO sw_user(joueur, visibility, guilde_id, joueur_id) VALUES (:joueur, 0, :guilde_id, :joueur_id);
                                                INSERT INTO sw_guilde(guilde, guilde_id) VALUES (:guilde, :guilde_id)
                                                ON CONFLICT (guilde_id)
                                                DO NOTHING;''',
                                                {'joueur': st.session_state['pseudo'],
                                                'guilde': st.session_state['guilde'],
                                                'guilde_id': st.session_state['guildeid'],
                                                'joueur_id': st.session_state['compteid']})

                            st.session_state.id_joueur, st.session_state.visibility, guilde_id, st.session_state.rank  = get_user(
                                    st.session_state['pseudo'])
                            
                    try:
                        requete_perso_bdd('''UPDATE sw_user SET lang = :lang WHERE joueur_id = :joueur_id;''',
                                        {'lang': st.session_state['lang'], 'joueur_id': st.session_state['compteid']})
                    except:
                        cancel()

                    # Enregistrement SQL

                    # Scoring general 
                    tcd_value = format_sql(tcd_value)

                        
                    st.session_state.tcd = tcd_value.copy()

                    sauvegarde_bdd(tcd_value, 'sw', 'append')
                    
                    del tcd_value
                    
                    # Qualité des runes
                    
                    data_rune.count_quality()
                    
                    st.session_state.df_quality = st.session_state.data_rune.data_qual
                    st.session_state.df_quality_per_slot = st.session_state.data_rune.data_qual_per_slot

                    # Score qualité runes
                    
                    st.session_state.df_scoring_quality, st.session_state.score_qual = data_rune.score_quality(coef_set_spd)

                    
                    requete_perso_bdd('''INSERT INTO public.sw_score(score_general, date, id_joueur, score_spd, score_arte, mana, score_qual)
                    VALUES (:score_general, :date, :id_joueur, :score_spd, :score_arte, :mana, :score_qual);''',
                    {'id_joueur' : int(st.session_state['id_joueur']),
                    'date' : date_du_jour(),
                    'score_general' : int(st.session_state['score']),
                    'score_spd' : int(st.session_state['score_spd']),
                    'score_arte' : int(st.session_state['score_arte']),
                    'mana' : int(st.session_state['mana']),
                    'score_qual' : int(st.session_state['score_qual'])})
                    
                    df_scoring_quality_to_save = st.session_state.df_scoring_quality.copy()
                    
                    df_scoring_quality_to_save = format_sql(df_scoring_quality_to_save)
                    
                    # df_scoring_quality_to_save['id'] = st.session_state['id_joueur']
                    # df_scoring_quality_to_save['date'] = date_du_jour()
                    
                    sauvegarde_bdd(df_scoring_quality_to_save, 'sw_score_qual', 'append')
                    
                    del df_scoring_quality_to_save

                        
                        # scoring detail
                        
                    tcd_detail_score_save = st.session_state.tcd_detail_score.copy()
                    
                    tcd_detail_score_save = format_sql(tcd_detail_score_save)
                        
                    # tcd_detail_score_save['id'] = st.session_state['id_joueur']
                    # tcd_detail_score_save['date'] = date_du_jour()
                        
                        # on veut éviter les doublons donc :  
                        
                    requete_perso_bdd('''DELETE from sw_detail
                                        WHERE id = :id_joueur AND date = :date''', dict_params={'id_joueur' : st.session_state['id_joueur'],
                                                                                                    'date' : date_du_jour()})
                    
                    tcd_detail_score_save['moyenne'] = st.session_state.data_avg['moyenne']
                    tcd_detail_score_save['max'] = st.session_state.data_avg['max']
                    tcd_detail_score_save['mediane'] = st.session_state.data_avg['mediane']
                    tcd_detail_score_save['nb'] = st.session_state.data_avg['Nombre runes']
                    
                    tcd_detail_score_save.loc['Total', 'moyenne'] = st.session_state.data_avg['moyenne'].mean()  
                    tcd_detail_score_save.loc['Total', 'max'] = st.session_state.data_avg['max'].mean() 
                    tcd_detail_score_save.loc['Total', 'mediane'] = st.session_state.data_avg['mediane'].mean() 
                    tcd_detail_score_save.loc['Total', 'nb'] = st.session_state.data_avg['Nombre runes'].sum()   
                    sauvegarde_bdd(tcd_detail_score_save, 'sw_detail', 'append')
                    
                    
                    del tcd_detail_score_save
                    
                        
                        # Scoring speed
                    tcd_spd_save : pd.DataFrame = st.session_state.tcd_spd.copy()
                    
                    tcd_spd_save = format_sql(tcd_spd_save)

                        
                    sauvegarde_bdd(tcd_spd_save, 'sw_spd', 'append')
                    
                    del tcd_spd_save
                    
                        # Scoring arte
                        
                    tcd_arte_save : pd.DataFrame = st.session_state.tcd_arte.copy()
                    
                    tcd_arte_save = format_sql(tcd_arte_save)
                        

                        
                    sauvegarde_bdd(tcd_arte_save, 'sw_arte', 'append')
                    
                    st.session_state.data_arte.calcul_value_max()
                    
                    arte_max_save : pd.DataFrame = st.session_state.data_arte.df_max.copy()
                
                    
                    arte_max_save = format_sql(arte_max_save)
                    

                    
                    # on supprime les anciennes données
                    requete_perso_bdd('''DELETE FROM sw_arte_max WHERE "id" = :id''', dict_params={'id' : st.session_state['id_joueur']})
                    
                    sauvegarde_bdd(arte_max_save, 'sw_arte_max', 'append')
                    
                    del arte_max_save
                    
                    # count arte

                    
                    count2 = []
                    count3 = []
                    count4 = []

                    for substat in liste_substat_arte:
                        df, count_sub2 = st.session_state.data_arte.count_substat(substat, 2)
                        count2.append(count_sub2)
                        df, count_sub3 = st.session_state.data_arte.count_substat(substat, 3)
                        count3.append(count_sub3)
                        df, count_sub4 = st.session_state.data_arte.count_substat(substat, 4)
                        count4.append(count_sub4)
                    
                    st.session_state.arte_count = pd.DataFrame([liste_substat_arte, count2, count3, count4], index=['substat', 'count2', 'count3', 'count4']).T
                    
                    arte_count = st.session_state.arte_count.copy()

                    
                    arte_count = format_sql(arte_count)

                    
                    del df, count_sub2, count_sub3, count_sub4, count2, count3, count4
                    
                    df_top = st.session_state.data_arte.top()
                    
                    df_top.fillna(0, inplace=True)              
                    
                    df_top['id'] = st.session_state['id_joueur']
                    
                    requete_perso_bdd('''DELETE from sw_arte_top
                                        WHERE id = :id_joueur''', dict_params={'id_joueur' : st.session_state['id_joueur']})
                    
                    sauvegarde_bdd(df_top.drop('main_type', axis=1), 'sw_arte_top', 'append', index=False)
                    
                    del df_top

                    # on veut éviter les doublons donc :  
                        
                    requete_perso_bdd('''DELETE from sw_arte_substats
                                        WHERE id = :id_joueur AND date = :date''', dict_params={'id_joueur' : st.session_state['id_joueur'],
                                                                                                    'date' : date_du_jour()})

                    sauvegarde_bdd(arte_count, 'sw_arte_substats', 'append', index=False)
                
                        # Scoring max_value
                        
                    df_max = st.session_state.df_max.copy()
                    
                    df_max = format_sql(df_max)
                                                
                    # on supprime les anciennes données
                    requete_perso_bdd('''DELETE FROM sw_max WHERE "id" = :id''', dict_params={'id' : st.session_state['id_joueur']})
                        
                    #     # on met à jour
                    sauvegarde_bdd(df_max, 'sw_max', 'append')
                    
                    del df_max
                    

                    # MAJ guilde
                    
                    
                    update_info_compte(st.session_state['pseudo'], st.session_state['guildeid'],
                                        st.session_state['compteid'])  # on update le compte
                    


                    # Maintenant, on a besoin d'identifier les id.
                    # Pour cela, on va utiliser l'api de swarfarm

                                        
                    del df_identification, data_mobs
                    
                    # PVP / World Boss
                    
                    requete_perso_bdd('''INSERT INTO public.sw_pvp(id_joueur, win, lose, date)
                    VALUES (:id_joueur, :win, :lose, :date);
                    INSERT INTO public.sw_wb(id_joueur, rank, damage, date)
                    VALUES (:id_joueur, :rank, :damage, :date);''',
                    {'id_joueur' : int(st.session_state['id_joueur']),
                    'date' : date_du_jour(),
                    'win' : int(st.session_state['arena_win']),
                    'lose' : int(st.session_state['arena_lose']),
                    'rank' : int(st.session_state['rank_wb']),
                    'damage' : int(st.session_state['dmg_wb'])})
                    
                    # Tout est bon, on peut passer à la suite !

                    st.subheader(f'Validé pour le joueur {st.session_state["pseudo"]} !')
                    st.write('Tu peux désormais aller sur les autres onglets disponibles')

                    st.session_state['submitted'] = True
                    
                    
                    gc.collect()
                        
                    # On passe à la page suivante    
                    switch_page('General')


                
            # Gestions des erreurs    
                except InternalError as e:
                    print(e)
                    cancel()
                    st.warning('Erreur')
                    st.session_state['submitted'] = False

                except OperationalError as e:
                    print(e)
                    cancel()
                    st.warning('Erreur')
                    st.session_state['submitted'] = False
            
        telechargement_json()
        
            
upload_sw()    
 
st.caption('Made by Tomlora :sunglasses:')