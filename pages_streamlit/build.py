import pandas as pd
import streamlit as st
from fonctions.visualisation import filter_dataframe
import requests
from math import ceil
from io import BytesIO
from fonctions.export import export_excel
from fonctions.gestion_bdd import lire_bdd_perso, requete_perso_bdd


from streamlit_extras.switch_page_button import switch_page
from st_pages import add_indentation

add_indentation()




st.title('Création de build')


def build():

    data_mobs = pd.DataFrame.from_dict(
        st.session_state['data_json'], orient="index").transpose()

    data_mobs = data_mobs['unit_list']

    # On va boucler et retenir ce qui nous intéresse..
    list_mobs = []

    for monstre in data_mobs[0]:
        unit = monstre['unit_id']
        master_id = monstre['unit_master_id']
        list_mobs.append([unit, master_id, monstre['unit_level'], monstre['atk'], monstre['def'], monstre['spd'], monstre['resist'], monstre['accuracy'],
                          monstre['critical_rate'], monstre['critical_damage']])

        for i in range(6):  # itération sur les runes de 1 à 6
            if len(monstre['runes']) > i:
                list_mobs[-1].append(monstre['runes'][i]['rune_id'])
            else:  # s'il n'a pas de rune dans le slot, on met 0
                list_mobs[-1].append(0)

    # On met ça en dataframe
    df_mobs = pd.DataFrame(list_mobs, columns=['id_unit', 'id_monstre', 'level', 'atk', 'def', 'spd',
                                               'resist', 'accuracy', 'CRIT', 'DCC',
                                               'Rune1', 'Rune2', 'Rune3', 'Rune4', 'Rune5', 'Rune6'])

    # Maintenant, on a besoin d'identifier les id.
    # Pour cela, on va utiliser l'api de swarfarm

    # swarfarm

    swarfarm = st.session_state.swarfarm[[
        'com2us_id', 'name', 'image_filename', 'url']].set_index('com2us_id')
    df_mobs['name_monstre'] = df_mobs['id_monstre'].map(
        swarfarm.to_dict(orient="dict")['name'])

    # On peut faire le mapping...

    df_mobs = df_mobs.set_index('id_unit')

    st.session_state.data_rune.identify_monsters(monsters=df_mobs.to_dict(
        orient="dict")['name_monstre'], data='data')

    st.session_state.data_rune.data_build = st.session_state.data_rune.data.copy()

    rename_column = {'rune_set': 'Set rune',
                     'rune_slot': 'Slot',
                     'rune_equiped': 'Equipé',
                     'main_type': 'Stat principal',
                     'main_value': 'Valeur stat principal',
                     'first_sub': 'Substat 1',
                     'second_sub': 'Substat 2',
                     'third_sub': 'Substat 3',
                     'fourth_sub': 'Substat 4',
                     'first_sub_value_total': 'Substat 1 total',
                     'second_sub_value_total': 'Substat 2 total',
                     'third_sub_value_total': 'Substat 3 total',
                     'fourth_sub_value_total': 'Substat 4 total',
                     }

    st.session_state.data_rune.data_build.rename(
        columns=rename_column, inplace=True)
    st.session_state.data_rune.data_build['Equipé'] = st.session_state.data_rune.data_build['Equipé'].astype(
        'str')
    st.session_state.data_rune.data_build['Equipé'].replace(
        {'0': 'Inventaire'}, inplace=True)

    st.session_state.data_rune.data_build = st.session_state.data_rune.data_build[['Set rune', 'Slot', 'Equipé', 'Stat principal', 'Valeur stat principal',
                                                                                   'innate_type', 'innate_value',
                                                                                   'Substat 1', 'Substat 1 total',
                                                                                   'Substat 2', 'Substat 2 total',
                                                                                   'Substat 3', 'Substat 3 total',
                                                                                   'Substat 4', 'Substat 4 total']]

    st.session_state.data_rune.data_build = st.session_state.data_rune.map_stats(st.session_state.data_rune.data_build, [
        'Stat principal', 'innate_type', 'Substat 1', 'Substat 2', 'Substat 3', 'Substat 4']).reset_index()

    st.session_state.data_rune.data_build.rename(
        columns={'index': 'id_rune'}, inplace=True)

    # on peut préparer la page
    st.warning('En beta', icon="⚠️")

    with st.expander('Chercher mes runes'):
        data_build_filter = filter_dataframe(
            st.session_state.data_rune.data_build.drop('id_rune', axis=1), 'data_build', type_number='int')
        st.dataframe(data_build_filter)


        data_xlsx = export_excel(data_build_filter, 'Id_rune', 'Runes')

        st.download_button('Télécharger la data (Excel)', data_xlsx, file_name='runes.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    col1, col2 = st.columns([0.8, 0.2])

    # DataFrame avec les monstres
    with col1:
        st.subheader('Chercher un monstre')
        monster_selected = st.selectbox(
            'Monstre', options=df_mobs['name_monstre'].unique())
    with col2:
        image = swarfarm.loc[swarfarm['name'] ==
                             monster_selected]['image_filename'].values[0]
        st.image(
            f'https://swarfarm.com/static/herders/images/monsters/{image}')

    # on charge les build sauvegardés
    df_build_save = lire_bdd_perso(
        f'''SELECT * FROM sw_build where monstre = '{monster_selected.lower()}' and id = {st.session_state.id_joueur}''', index_col='id_build').transpose()

    if len(df_build_save) > 0:
        # Si un build existe, on ouvre la liste déroulante des build
        with st.expander('Charger un build'):
            liste_build = df_build_save['nom_build'].unique().tolist()
            liste_build.append('Aucun')
            build_selected = st.selectbox(
                'Selection du build', options=liste_build, index=len(liste_build)-1, help="En cas de retour à la selection 'Aucun', il faut le selectionner deux fois")
    else:
        build_selected = 'Aucun'

    def calcul_substats(monster_selected, build_selected):
        '''Calcule le total de substat pour les 6 runes

        La variable build_selected est pour différencier le build actuel et ceux enregistrés'''
        dict_stat = {'ATQ': 0, 'ATQ%': 0, 'DEF%': 0, 'DEF': 0, 'HP': 0, 'HP%': 0,
                     'SPD': 0, 'CRIT': 0, 'DCC': 0, 'RES': 0, 'ACC': 0, 'Aucun': 0}
        set_equiped = []

        if build_selected == 'Aucun':
            df_rune_selected = df_mobs[df_mobs['name_monstre']
                                       == monster_selected]
        else:
            df_rune_selected = df_build_save[(df_build_save['monstre']
                                             == monster_selected.lower()) & (df_build_save['nom_build'] == build_selected)]

        for i in range(1, 7):  # par rune

            if build_selected == 'Aucun':
                id_rune = df_rune_selected[f'Rune{i}'].values[0]
            else:
                id_rune = df_rune_selected[f'rune{i}'].values[0]

            if id_rune == 0:
                continue
            type = st.session_state.data_rune.data_build.loc[
                st.session_state.data_rune.data_build['id_rune'] == id_rune][f"Stat principal"].values[0]

            dict_stat[type] = dict_stat[type] + \
                st.session_state.data_rune.data_build.loc[st.session_state.data_rune.data_build['id_rune']
                                                          == id_rune]["Valeur stat principal"].values[0]
            set_equiped.append(
                st.session_state.data_rune.data_build.loc[st.session_state.data_rune.data_build['id_rune'] == id_rune][f"Set rune"].values[0])

            type = st.session_state.data_rune.data_build.loc[
                st.session_state.data_rune.data_build['id_rune'] == id_rune][f"innate_type"].values[0]
            dict_stat[type] = dict_stat[type] + \
                st.session_state.data_rune.data_build.loc[st.session_state.data_rune.data_build['id_rune']
                                                          == id_rune]["innate_value"].values[0]

            for i in range(1, 5):  # par substat
                type = st.session_state.data_rune.data_build.loc[
                    st.session_state.data_rune.data_build['id_rune'] == id_rune][f"Substat {i}"].values[0]
                dict_stat[type] = dict_stat[type] + \
                    st.session_state.data_rune.data_build.loc[st.session_state.data_rune.data_build[
                        'id_rune'] == id_rune][f"Substat {i} total"].values[0]

        return dict_stat, set_equiped

    dict_bonus, set_equiped = calcul_substats(monster_selected, build_selected)

    def show_rune(num_rune, monster_selected, build_selected):
        '''Montre la rune et ses différentes caractéristiques

        La variable build_selected est pour différencier le build actuel et ceux enregistrés'''

        if build_selected == 'Aucun':
            id_rune = df_mobs[df_mobs['name_monstre'] ==
                              monster_selected][f'Rune{num_rune}'].values[0]

            if id_rune != 0 and id_rune != -1:
                index_rune = st.session_state.data_rune.data_build.loc[
                    st.session_state.data_rune.data_build['id_rune'] == id_rune].index[0]

                id_rune = st.number_input(
                    label=f'identifiant rune {num_rune}', value=index_rune, format='%i', key=f'number_{num_rune}')

                id_rune = st.session_state.data_rune.data_build.loc[id_rune]['id_rune']

            else:

                index_rune = 0

                id_rune = st.number_input(
                    label=f'identifiant rune {num_rune}', value=-1, format='%i', key=f'number_{num_rune}')

                id_rune = st.session_state.data_rune.data_build.loc[id_rune]['id_rune']

        else:
            selection = df_build_save[(df_build_save['monstre']
                                       == monster_selected.lower()) & (df_build_save['nom_build'] == build_selected)]

            id_rune = selection[f'rune{num_rune}'].values[0]

            st.session_state.number_1 = selection[f'rune1'].values[0]
            st.session_state.number_2 = selection[f'rune2'].values[0]
            st.session_state.number_3 = selection[f'rune3'].values[0]
            st.session_state.number_4 = selection[f'rune4'].values[0]
            st.session_state.number_5 = selection[f'rune5'].values[0]
            st.session_state.number_6 = selection[f'rune6'].values[0]

        df_rune = st.session_state.data_rune.data_build.loc[
            st.session_state.data_rune.data_build['id_rune'] == id_rune]

        if id_rune != 0 and id_rune != -1:
            if num_rune != df_rune['Slot'].values[0]:
                st.warning(
                    f'Slot de cette rune : {df_rune["Slot"].values[0]}', icon="🚨")

            return f'Rune {num_rune} : :blue[{df_rune["Set rune"].values[0]}] :orange[(Equipé sur {df_rune["Equipé"].values[0]})]\
            <br><br>Stat principal : :blue[{df_rune["Stat principal"].values[0]}] :green[({df_rune["Valeur stat principal"].values[0]})]\
            <br>Innate : :blue[{df_rune["innate_type"].values[0]}] :green[({df_rune["innate_value"].values[0]})]\
            <br><br>Sub1 : :blue[{df_rune["Substat 1"].values[0]}] :green[({df_rune["Substat 1 total"].values[0]})]\
            <br>Sub2 : :blue[{df_rune["Substat 2"].values[0]}] :green[({df_rune["Substat 2 total"].values[0]})]\
            <br>Sub3 : :blue[{df_rune["Substat 3"].values[0]}] :green[({df_rune["Substat 3 total"].values[0]})]\
            <br>Sub4 : :blue[{df_rune["Substat 4"].values[0]}] :green[({df_rune["Substat 4 total"].values[0]})]'

        else:
            return ''

    with st.expander('Stats'):
        set = ''
        stats1, stats2 = st.columns(2)

        # Ce code permet de calculer les statistiques d'un monstre sélectionné avec des sets équipés.
        # La première partie du code récupère les statistiques de base du monstre à partir de l'API Swarfarm et les stocke dans des variables.
        # La seconde partie calcule les bonus apportés par les sets équipés et affiche le résultat final.
        # Les bonus sont calculés en fonction du nombre de sets équipés (2, 3, 4, 5 ou 6).
        # Les bonus peuvent être appliqués aux statistiques HP, ATK, DEF, SPD, RES, ACC et CRIT.

        with stats1:
            selection = df_mobs[df_mobs["name_monstre"] == monster_selected]

            req_mob = requests.get(
                swarfarm.loc[swarfarm['name'] == monster_selected]['url'].values[0])
            req = req_mob.json()
            # Les HP de base ne sont pas dans le json. On prend donc l'api swarfarm pour le niveau max.
            hp = req['max_lvl_hp']
            atk = selection[f"atk"].values[0]
            defense = selection[f"def"].values[0]
            spd = selection[f"spd"].values[0]
            res = selection[f"resist"].values[0]
            acc = selection[f"accuracy"].values[0]
            crit = selection[f"CRIT"].values[0]
            dcc = selection[f"DCC"].values[0]

            # Energy
            if set_equiped.count('Energy') in (2, 3):
                st.caption(
                    f'HP : :blue[{hp}] :orange[(+{ceil(hp*(dict_bonus["HP%"]/100) + dict_bonus["HP"] + hp*0.15)})]')
            elif set_equiped.count('Energy') in (4, 5):
                st.caption(
                    f'HP : :blue[{hp}] :orange[(+{ceil(hp*(dict_bonus["HP%"]/100) + dict_bonus["HP"] + hp*0.30)})]')
            if set_equiped.count('Energy') == (6):
                st.caption(
                    f'HP : :blue[{hp}] :orange[(+{ceil(hp*(dict_bonus["HP%"]/100) + dict_bonus["HP"] + hp*0.45)})]')
            else:
                st.caption(
                    f'HP : :blue[{hp}] :orange[(+{ceil(hp*(dict_bonus["HP%"]/100) + dict_bonus["HP"])})]')

            # Fatal
            if set_equiped.count('Fatal') >= 4:
                st.caption(
                    f'ATK : :blue[{atk}] :orange[(+{ceil(atk*(dict_bonus["ATQ%"]/100) + dict_bonus["ATQ"] + atk*0.35)})]')
                set += 'Fatal '
            else:
                st.caption(
                    f'ATK : :blue[{atk}] :orange[(+{ceil(atk*(dict_bonus["ATQ%"]/100) + dict_bonus["ATQ"])})]')

            # Guard
            if set_equiped.count('Guard') in (2, 3):
                st.caption(
                    f'DEF : :blue[{defense}] :orange[(+{ceil(defense*(dict_bonus["DEF%"]/100) + dict_bonus["DEF"] + defense*0.15)})]')
                set += 'Guard '
            elif set_equiped.count('Guard') in (4, 5):
                st.caption(
                    f'DEF : :blue[{defense}] :orange[(+{ceil(defense*(dict_bonus["DEF%"]/100) + dict_bonus["DEF"] + defense*0.3)})]')
                set += 'Guard x2 '
            elif set_equiped.count('Guard') == 6:
                st.caption(
                    f'DEF : :blue[{defense}] :orange[(+{ceil(defense*(dict_bonus["DEF%"]/100) + dict_bonus["DEF"] + defense*0.45)})]')
                set += 'Guard x3 '
            else:
                st.caption(
                    f'DEF : :blue[{defense}] :orange[(+{ceil(defense*(dict_bonus["DEF%"]/100) + dict_bonus["DEF"])})]')

            # Swift
            if set_equiped.count('Swift') >= 4:
                st.caption(
                    f'SPD : :blue[{spd}] :orange[(+{ceil(dict_bonus["SPD"] + spd*0.25)})]')
                set += 'Swift '
            else:
                st.caption(
                    f'SPD : :blue[{spd}] :orange[(+{dict_bonus["SPD"]})]')

        with stats2:

            # Endure
            if set_equiped.count('Endure') in (2, 3):
                st.caption(
                    f'RES : :blue[{res}%] :orange[(+{dict_bonus["RES"] + 20})%]')
                set += 'Endure '
            elif set_equiped.count('Endure') in (4, 5):
                st.caption(
                    f'RES : :blue[{res}%] :orange[(+{dict_bonus["RES"] + 40})%]')
                set += 'Endure x2 '
            elif set_equiped.count('Endure') == 6:
                st.caption(
                    f'RES : :blue[{res}%] :orange[(+{dict_bonus["RES"] + 60})%]')
                set += 'Endure x3 '
            else:
                st.caption(
                    f'RES : :blue[{res}%] :orange[(+{dict_bonus["RES"]})%]')

            # Focus
            if set_equiped.count('Focus') in (2, 3):
                st.caption(
                    f'ACC : :blue[{acc}%] :orange[(+{dict_bonus["ACC"] + 20})%]')
                set += 'Focus '
            if set_equiped.count('Focus') in (3, 4):
                st.caption(
                    f'ACC : :blue[{acc}%] :orange[(+{dict_bonus["ACC"] + 40})%]')
                set += 'Focus x2 '
            if set_equiped.count('Focus') == 6:
                st.caption(
                    f'ACC : :blue[{acc}%] :orange[(+{dict_bonus["ACC"] + 60})%]')
                set += 'Focus x3 '
            else:
                st.caption(
                    f'ACC : :blue[{acc}%] :orange[(+{dict_bonus["ACC"]})%]')

            # Blade
            if set_equiped.count('Blade') in (2, 3):
                st.caption(
                    f'CRIT : :blue[{crit}%] :orange[(+{dict_bonus["CRIT"] + 12}%)]')
                set += 'Blade '
            elif set_equiped.count('Blade') in (4, 5):
                st.caption(
                    f'CRIT : :blue[{crit}%] :orange[(+{dict_bonus["CRIT"] + 24}%)]')
                set += 'Blade x2 '
            elif set_equiped.count('Blade') == 6:
                st.caption(
                    f'CRIT : :blue[{crit}%] :orange[(+{dict_bonus["CRIT"] + 36}%)]')
                set += 'Blade x3 '
            else:
                st.caption(
                    f'CRIT : :blue[{crit}%] :orange[(+{dict_bonus["CRIT"]}%)]')

            # Rage
            if set_equiped.count('Rage') >= 4:
                st.caption(
                    f'DCC : :blue[{dcc}%] :orange[(+{dict_bonus["DCC"] + 40}%)]')
                set += 'Rage '
            else:
                st.caption(
                    f'DCC : :blue[{dcc}%] :orange[(+{dict_bonus["DCC"]}%)]')

            if set_equiped.count('Violent') >= 4:
                set += 'Violent '

            if set_equiped.count('Nemesis') in (2, 3):
                set += 'Nemesis '

            elif set_equiped.count('Nemesis') in (4, 5):
                set += 'Nemesis x2 '

            elif set_equiped.count('Nemesis') == 6:
                set += 'Nemesis x3 '

            if set_equiped.count('Will') in (2, 3):
                set += 'Will '

            elif set_equiped.count('Will') in (4, 5):
                set += 'Will x2 '

            elif set_equiped.count('Will') == 6:
                set += 'Will x3 '

        if set != '':
            st.write(f'Sets : {set}')

    col3, col4 = st.columns(2)
    # Rune 1/3/5 à gauche. 2/4/6 à droite
    with col3:  # Rune 1/3/5
        with st.container():
            for i in [1, 3, 5]:
                try:
                    st.write(show_rune(i, monster_selected,
                             build_selected), unsafe_allow_html=True)
                except KeyError as e:
                    if e.args[0] == -1:
                        st.info("Pas de rune sur ce slot", icon="🚨")
                    else:
                        st.warning("Cette rune n'existe pas", icon="🚨")

    with col4:  # Rune 2/4/6
        with st.container():
            for i in [2, 4, 6]:
                try:
                    st.write(show_rune(i, monster_selected,
                             build_selected), unsafe_allow_html=True)
                except KeyError as e:
                    if e.args[0] == -1:
                        st.info("Pas de rune sur ce slot", icon="🚨")
                    else:
                        st.warning("Cette rune n'existe pas", icon="🚨")

    # Si le build est personnalisé, on affiche un bouton pour le supprimer.
    if build_selected != 'Aucun':
        col5, col6 = st.columns([0.7, 0.3])

        with col6:
            if st.button('Supprimer ce build'):
                requete_perso_bdd('DELETE FROM sw_build where id = :id_joueur and monstre =:monstre and nom_build = :nom_build',
                                  dict_params={'id_joueur': st.session_state.id_joueur, 'monstre': monster_selected.lower(), 'nom_build': build_selected})
                st.success('Build supprimé')

    # Formulaire pour sauvegarder les build
    with st.form('Sauvegarder ce build'):
        build_name = st.text_input('Nom du build : ', 'Par default')

        submitted_build = st.form_submit_button('Sauvegarder')

    if submitted_build:
        # on enregistre si formulaire validé.
        df_checking = lire_bdd_perso(f'''SELECT id, monstre, nom_build, id_build FROM sw_build
                                     where monstre = '{monster_selected.lower()}'
                                     and id = {st.session_state.id_joueur}
                                     and nom_build = '{build_name}' ''', index_col='id_build').transpose()

        if df_checking.empty:
            requete_perso_bdd('''INSERT INTO public.sw_build(
                                id, monstre, nom_build, rune1, rune2, rune3, rune4, rune5, rune6)
                                VALUES (:id, :monstre, :nom_build, :rune1, :rune2, :rune3, :rune4, :rune5, :rune6); ''',
                              {'id': st.session_state.id_joueur, 'monstre': monster_selected.lower(),
                               'nom_build': build_name,
                               'rune1': int(st.session_state.data_rune.data_build.loc[st.session_state.number_1]['id_rune']),
                               'rune2': int(st.session_state.data_rune.data_build.loc[st.session_state.number_2]['id_rune']),
                               'rune3': int(st.session_state.data_rune.data_build.loc[st.session_state.number_3]['id_rune']),
                               'rune4': int(st.session_state.data_rune.data_build.loc[st.session_state.number_4]['id_rune']),
                               'rune5': int(st.session_state.data_rune.data_build.loc[st.session_state.number_5]['id_rune']),
                               'rune6': int(st.session_state.data_rune.data_build.loc[st.session_state.number_6]['id_rune'])})
            st.success('Build sauvegardé !')
        else:
            st.warning('Nom de build déjà utilisé pour ce monstre', icon="⚠️")


if 'submitted' in st.session_state:
    if st.session_state.submitted:

        build()

    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')

st.caption('Made by Tomlora')