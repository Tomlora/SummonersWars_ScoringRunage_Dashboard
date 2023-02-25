import pandas as pd
import streamlit as st
from fonctions.visualisation import filter_dataframe
import requests

from fonctions.gestion_bdd import lire_bdd_perso, requete_perso_bdd

from fonctions.runes import Rune


def build(data_class : Rune):
    
    data_mobs = pd.DataFrame.from_dict(
    st.session_state['data_json'], orient="index").transpose()

    data_mobs = data_mobs['unit_list']

    # On va boucler et retenir ce qui nous intéresse..
    list_mobs = []

    print(data_mobs[0][0])

    for monstre in data_mobs[0]:
        unit = monstre['unit_id']
        master_id = monstre['unit_master_id']
        list_mobs.append([unit, master_id, monstre['unit_level'], monstre['atk'], monstre['def'], monstre['spd'], monstre['resist'], monstre['accuracy'],
                          monstre['critical_rate'], monstre['critical_damage']])
                         
        for i in range(6): # itération sur les runes de 1 à 6
            if len(monstre['runes']) > i:
                list_mobs[-1].append(monstre['runes'][i]['rune_id'])
            else:
                list_mobs[-1].append(0)

    # On met ça en dataframe
    df_mobs = pd.DataFrame(list_mobs, columns=['id_unit', 'id_monstre', 'level', 'atk', 'def', 'spd', 'resist', 'accuracy', 'CRIT', 'CDMG',
                                               'Rune1', 'Rune2', 'Rune3', 'Rune4', 'Rune5', 'Rune6'])
    

    # Maintenant, on a besoin d'identifier les id.
    # Pour cela, on va utiliser l'api de swarfarm

    swarfarm = pd.read_excel('swarfarm.xlsx')
    # swarfarm

    swarfarm = swarfarm[['com2us_id', 'name', 'url']].set_index('com2us_id')
    df_mobs['name_monstre'] = df_mobs['id_monstre'].map(
            swarfarm.to_dict(orient="dict")['name'])

    # On peut faire le mapping...

    df_mobs = df_mobs.set_index('id_unit')

    data_class.identify_monsters(monsters=df_mobs.to_dict(orient="dict")['name_monstre'], data='data')
    
    data_class.data_build = data_class.data.copy()
    
    rename_column = {'rune_set' : 'Set rune',
                             'rune_slot' : 'Slot',
                             'rune_equiped' : 'Equipé',
                             'efficiency' : 'Efficience',
                             'efficiency_max_hero' : 'Efficience_max_hero',
                             'efficiency_max_lgd' : 'Efficience_max_lgd',
                             'quality' : 'qualité',
                             'amount' : 'montant',
                             'main_type' : 'Stat principal',
                             'main_value' : 'Valeur stat principal',
                             'first_sub' : 'Substat 1',
                             'second_sub' : 'Substat 2',
                             'third_sub' : 'Substat 3', 
                             'fourth_sub' : 'Substat 4',
                             'first_sub_value' : 'Substat valeur 1',
                             'second_sub_value' : 'Substat valeur 2',
                             'third_sub_value' : 'Substat valeur 3',
                             'fourth_sub_value' : 'Substat valeur 4',
                             'first_gemme_bool' : 'Gemmé 1 ?',
                             'second_gemme_bool' : 'Gemmé 2 ?',
                             'third_gemme_bool' : 'Gemmé 3 ?',
                             'fourth_gemme_bool' : 'Gemmé 4 ?',
                             'first_sub_grinded_value' : 'Valeur meule 1',
                             'second_sub_grinded_value' : 'Valeur meule 2',
                             'third_sub_grinded_value' : 'Valeur meule 3',
                             'fourth_sub_grinded_value' : 'Valeur meule 4',
                             'first_sub_value_max' : 'Substat 1 max',
                             'second_sub_value_max' : 'Substat 2 max',
                             'third_sub_value_max' : 'Substat 3 max',
                             'fourth_sub_value_max' : 'Substat 4 max',
                             'first_sub_value_total' : 'Substat 1 total',
                             'second_sub_value_total' : 'Substat 2 total',
                             'third_sub_value_total' : 'Substat 3 total',
                             'fourth_sub_value_total' : 'Substat 4 total',
                             'first_grind_value_max_lgd' : 'Meule 1 lgd Max',
                             'second_grind_value_max_lgd' : 'Meule 2 lgd Max',
                             'third_grind_value_max_lgd' : 'Meule 3 lgd Max',
                             'fourth_grind_value_max_lgd' : 'Meule 4 lgd Max',
                             'first_grind_value_max_hero' : 'Meule 1 hero Max',
                             'second_grind_value_max_hero' : 'Meule 2 hero Max',
                             'third_grind_value_max_hero' : 'Meule 3 hero Max',
                             'fourth_grind_value_max_hero' : 'Meule 4 hero Max'}
    
    data_class.data_build.rename(columns=rename_column, inplace=True)
    data_class.data_build['Equipé'] = data_class.data_build['Equipé'].astype('str')
    data_class.data_build['Equipé'].replace({'0' : 'Inventaire'}, inplace=True)
    
    data_class.data_build = data_class.data_build[['Set rune', 'Slot', 'Equipé', 'Stat principal', 'Valeur stat principal',
                                                   'innate_type', 'innate_value', 
                                                   'Substat 1', 'Substat 1 total',
                                                   'Substat 2', 'Substat 2 total',
                                                   'Substat 3', 'Substat 3 total',
                                                   'Substat 4', 'Substat 4 total']]

    data_class.data_build = data_class.map_stats(data_class.data_build, ['Stat principal', 'innate_type', 'Substat 1', 'Substat 2', 'Substat 3', 'Substat 4'])

    st.warning('En beta', icon="⚠️")
    with st.expander('Chercher mes runes'):
        data_build_filter = filter_dataframe(data_class.data_build, 'data_build', type_number='int')  
        st.dataframe(data_build_filter)
        

    
    col1, col2 = st.columns([0.8, 0.2])
    
   
    with col1:
        st.subheader('Chercher un monstre')
        monster_selected = st.selectbox('Monstre', options=df_mobs['name_monstre'].unique())
    with col2:
        req_mob = requests.get(swarfarm.loc[swarfarm['name'] == monster_selected]['url'].values[0])
        req = req_mob.json()
        image = req['image_filename']
        st.image(f'https://swarfarm.com/static/herders/images/monsters/{image}')
        
    df_build_save = lire_bdd_perso('''SELECT * FROM sw_build where monstre = %(monstre)s and id = %(id_joueur)s''', params={'id_joueur' : st.session_state.id_joueur, 'monstre' : monster_selected.lower()}, index_col='id_build').transpose()
    
    
    if len(df_build_save) > 0:
        with st.expander('Charger un build'):
            liste_build = df_build_save['nom_build'].unique().tolist()
            liste_build.append('Aucun')
            build_selected = st.selectbox('Selection du build', options=liste_build, index=len(liste_build)-1)
    else:
        build_selected = 'Aucun'
        
    def show_rune(num_rune, monster_selected, build_selected):
        
        if build_selected == 'Aucun':
            id_rune = df_mobs[df_mobs['name_monstre'] == monster_selected][f'Rune{num_rune}'].values[0]
            id_rune = st.number_input(label=f'identifiant rune {num_rune}', value=id_rune, format='%i', key=f'number_{num_rune}')
        else:
            id_rune = df_build_save[df_build_save['monstre'] == monster_selected.lower()][f'rune{num_rune}'].values[0] 
            st.session_state.number_1 = df_build_save[df_build_save['monstre'] == monster_selected.lower()][f'rune1'].values[0]
            st.session_state.number_2 = df_build_save[df_build_save['monstre'] == monster_selected.lower()][f'rune2'].values[0]
            st.session_state.number_3 = df_build_save[df_build_save['monstre'] == monster_selected.lower()][f'rune3'].values[0]
            st.session_state.number_4 = df_build_save[df_build_save['monstre'] == monster_selected.lower()][f'rune4'].values[0]
            st.session_state.number_5 = df_build_save[df_build_save['monstre'] == monster_selected.lower()][f'rune5'].values[0]
            st.session_state.number_6 = df_build_save[df_build_save['monstre'] == monster_selected.lower()][f'rune6'].values[0]

        
        # id_rune = st.number_input(label=f'identifiant rune {num_rune}', value=id_rune, format='%i', key=f'number_{num_rune}')
        
        return f'Rune {num_rune} : :blue[{data_class.data_build.loc[id_rune]["Set rune"]}]\
    <br>Stat principal : :blue[{data_class.data_build.loc[id_rune]["Stat principal"]}] :green[({data_class.data_build.loc[id_rune]["Valeur stat principal"]})]\
    <br>Sub1 : :blue[{data_class.data_build.loc[id_rune]["Substat 1"]}] :green[({data_class.data_build.loc[id_rune]["Substat 1 total"]})]\
    <br>Sub2 : :blue[{data_class.data_build.loc[id_rune]["Substat 2"]}] :green[({data_class.data_build.loc[id_rune]["Substat 2 total"]})]\
    <br>Sub3 : :blue[{data_class.data_build.loc[id_rune]["Substat 3"]}] :green[({data_class.data_build.loc[id_rune]["Substat 3 total"]})]\
    <br>Sub4 : :blue[{data_class.data_build.loc[id_rune]["Substat 4"]}] :green[({data_class.data_build.loc[id_rune]["Substat 4 total"]})]\
        '
    
    col3, col4 = st.columns(2)
    
    with col3:
        with st.container():
            for i in [1,3,5]:
                st.write(show_rune(i, monster_selected, build_selected), unsafe_allow_html=True)

    with col4: 
        with st.container():
            for i in [2,4,6]:
                st.write(show_rune(i, monster_selected, build_selected), unsafe_allow_html=True)   
     
    if build_selected != 'Aucun':
        col5, col6 = st.columns([0.7,0.3])
        
        with col6:
            if st.button('Supprimer ce build'):
                requete_perso_bdd('DELETE FROM sw_build where id = :id_joueur and monstre =:monstre and nom_build = :nom_build',
                                  dict_params={'id_joueur' : st.session_state.id_joueur, 'monstre' : monster_selected.lower(), 'nom_build' : build_selected})
                st.success('Build supprimé')      
 
    with st.form('Sauvegarder ce build'):
        build_name = st.text_input('Nom du build : ', 'Par default')
        
        
        submitted_build = st.form_submit_button('Sauvegarder')

    if submitted_build:
        requete_perso_bdd('''INSERT INTO public.sw_build(
	                        id, monstre, nom_build, rune1, rune2, rune3, rune4, rune5, rune6)
	                        VALUES (:id, :monstre, :nom_build, :rune1, :rune2, :rune3, :rune4, :rune5, :rune6); ''',
                         {'id' : st.session_state.id_joueur, 'monstre' : monster_selected.lower(),
                          'nom_build' : build_name, 'rune1' : st.session_state.number_1, 'rune2' : st.session_state.number_2,
                          'rune3' : st.session_state.number_3, 'rune4' : st.session_state.number_4,
                          'rune5' : st.session_state.number_5, 'rune6' : st.session_state.number_6})
        st.success('Build sauvegardé !')

        

    
    

