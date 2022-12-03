import pandas as pd
import numpy as np
import plotly.express as px
import ast
import streamlit as st
from io import BytesIO
from fonctions.visualisation import filter_dataframe


# fix plotly express et Visual Studio Code
import plotly.io as pio
pio.renderers.default = "notebook_connected"

# Supprime les Future Warnings sur les copies
pd.options.mode.chained_assignment = None  # default='warn'


# In[113]:


def extraire_variables_imbriquees(df, colonne):
    df[colonne] = [ast.literal_eval(str(item))
                   for index, item in df[colonne].iteritems()]

    df = pd.concat([df.drop([colonne], axis=1),
                   df[colonne].apply(pd.Series)], axis=1)
    return df


def export_excel(data, data_short, data_property, data_count, data_inventaire):

    output = BytesIO()
    # https://xlsxwriter.readthedocs.io/working_with_pandas.html

    # Pour travailler avec xlswriter et pendas et faire des tableaux, il faut reset l'index
    data.reset_index(inplace=True)
    data.rename(columns={'index': 'Id_rune'}, inplace=True)
    data_short.reset_index(inplace=True)
    data_short.rename(columns={'index': 'Set'}, inplace=True)
    data_property.reset_index(inplace=True)
    data_property.rename(columns={'index': 'Set'}, inplace=True)

    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    data_short.to_excel(
        writer, startrow=1, sheet_name='Par rune et monstre', index=False, header=False)
    data.to_excel(writer, startrow=1, sheet_name='Data_complete',
                  index=False, header=False)
    data_property.to_excel(
        writer, startrow=1, sheet_name='Par set', index=False, header=False)
    data_count.to_excel(
        writer, startrow=1, sheet_name='Par set et propriété', index=False, header=False)
    data_inventaire.to_excel(
        writer, startrow=1, sheet_name='Inventaire', index=False, header=False)

    workbook = writer.book
    worksheet2 = writer.sheets['Par rune et monstre']
    worksheet1 = writer.sheets['Data_complete']
    worksheet3 = writer.sheets['Par set']
    worksheet4 = writer.sheets['Par set et propriété']
    worksheet5 = writer.sheets['Inventaire']

    # Gestion de la taille des colonnes

    cell_format = workbook.add_format({'valign': 'vcenter', 'align': 'center'})
    cell_format.set_text_wrap()
    for i, col in enumerate(data.columns):
        # colonne, colonne, len_colonne, format colonne
        worksheet1.set_column(i, i+1, 20, cell_format)
    for i, col in enumerate(data_short.columns):
        # colonne, colonne, len_colonne, format colonne
        worksheet2.set_column(i, i+1, 20, cell_format)
    for i, col in enumerate(data_property.columns):
        # colonne, colonne, len_colonne, format colonne
        worksheet3.set_column(i, i+1, 20, cell_format)
    for i, col in enumerate(data_count.columns):
        # colonne, colonne, len_colonne, format colonne
        worksheet4.set_column(i, i+1, 20, cell_format)
    for i, col in enumerate(data_inventaire.columns):
        # colonne, colonne, len_colonne, format colonne
        worksheet5.set_column(i, i+1, 20, cell_format)

    # Ajout d'un graphique dans l'onglet 3

    chart = workbook.add_chart({'type': 'column'})
    (max_row, max_col) = data_property.shape

    chart.add_series({'categories': ['Par set', 1, 0, max_row, 0], 'values': [
                     'Par set', 1, 1, max_row, 1]})

    worksheet3.insert_chart(1, 3, chart)

    # Tableau

    def tableau(data, worksheet):
        column_settings = [{'header': column} for column in data.columns]
        (max_row, max_col) = data.shape

        worksheet.add_table(0, 0, max_row, max_col-1,
                            {'columns': column_settings})

    tableau(data, worksheet1)
    tableau(data_short, worksheet2)
    tableau(data_property, worksheet3)
    tableau(data_count, worksheet4)
    tableau(data_inventaire, worksheet5)

    writer.save()

    processed_data = output.getvalue()

    return processed_data


def optimisation_rune(category_selected, coef_set):
    data = st.session_state['data_grind']

    data = data[data['level'] > 11]
    data = data[data['stars'] > 5]

    sub_max_lgd = {1: 550, 2: 10, 3: 30, 4: 10, 5: 30, 6: 10, 8: 5}
    sub_max_heroique = {1: 450, 2: 7, 3: 22, 4: 7, 5: 22, 6: 7, 8: 4}

    # Certaines stats ne sont pas meulables. On remplace donc le potentiel de meule par 0

    dict = {'first_grind_value_max': 'first_sub', 'second_grind_value_max': 'second_sub',
            'third_grind_value_max': 'third_sub', 'fourth_grind_value_max': 'fourth_sub'}

    with st.spinner('Calcul du potentiel des runes...'):
        for key, value in dict.items():

            data[key + '_lgd'] = data[value].replace(sub_max_lgd)
            data[key + '_hero'] = data[value].replace(sub_max_heroique)

            # Certaines stats ne sont pas meulables. On remplace donc le potentiel de meule par 0

            data[key + "_lgd"] = np.where(data[value]
                                          > 8, 0,  data[key + "_lgd"])
            data[key + "_hero"] = np.where(data[value]
                                           > 8, 0, data[key + "_hero"])

    st.success('Calcul du potentiel des runes effectué !')

    # Value stats de base + meule (max)

    data['first_sub_value_total_max_lgd'] = (
        data['first_sub_value'] + data['first_grind_value_max_lgd'])
    data['second_sub_value_total_max_lgd'] = (
        data['second_sub_value'] + data['second_grind_value_max_lgd'])
    data['third_sub_value_total_max_lgd'] = (
        data['third_sub_value'] + data['third_grind_value_max_lgd'])
    data['fourth_sub_value_total_max_lgd'] = (
        data['fourth_sub_value'] + data['fourth_grind_value_max_lgd'])

    data['first_sub_value_total_max_hero'] = (
        data['first_sub_value'] + data['first_grind_value_max_hero'])
    data['second_sub_value_total_max_hero'] = (
        data['second_sub_value'] + data['second_grind_value_max_hero'])
    data['third_sub_value_total_max_hero'] = (
        data['third_sub_value'] + data['third_grind_value_max_hero'])
    data['fourth_sub_value_total_max_hero'] = (
        data['fourth_sub_value'] + data['fourth_grind_value_max_hero'])

    data['efficiency_max_lgd'] = np.where(data['innate_type'] != 0,
                                          round(((1+data['innate_value'] / data['innate_value_max']
                                                + data['first_sub_value_total_max_lgd'] / data['first_sub_value_max']
                                                + data['second_sub_value_total_max_lgd'] / data['second_sub_value_max']
                                                + data['third_sub_value_total_max_lgd'] / data['third_sub_value_max']
                                                + data['fourth_sub_value_total_max_lgd'] / data['fourth_sub_value_max'])
                                                 / 2.8)*100, 2),
                                          round(((1 + data['first_sub_value_total_max_lgd'] / data['first_sub_value_max']
                                                + data['second_sub_value_total_max_lgd'] / data['second_sub_value_max']
                                                + data['third_sub_value_total_max_lgd'] / data['third_sub_value_max']
                                                + data['fourth_sub_value_total_max_lgd'] / data['fourth_sub_value_max'])
                                                 / 2.8)*100, 2))

    data['efficiency_max_hero'] = np.where(data['innate_type'] != 0,
                                           round(((1+data['innate_value'] / data['innate_value_max']
                                                   + data['first_sub_value_total_max_hero'] / data['first_sub_value_max']
                                                   + data['second_sub_value_total_max_hero'] / data['second_sub_value_max']
                                                   + data['third_sub_value_total_max_hero'] / data['third_sub_value_max']
                                                   + data['fourth_sub_value_total_max_hero'] / data['fourth_sub_value_max'])
                                                  / 2.8)*100, 2),
                                           round(((1 + data['first_sub_value_total_max_hero'] / data['first_sub_value_max']
                                                   + data['second_sub_value_total_max_hero'] / data['second_sub_value_max']
                                                   + data['third_sub_value_total_max_hero'] / data['third_sub_value_max']
                                                   + data['fourth_sub_value_total_max_hero'] / data['fourth_sub_value_max'])
                                                  / 2.8)*100, 2))

    data['potentiel_max_lgd'] = data['efficiency_max_lgd'] - data['efficiency']

    data['potentiel_max_hero'] = data['efficiency_max_hero'] - data['efficiency']

    # def scoring_rune(potentiel):

    #     data_scoring = data.copy()
    #     data_scoring = data[['rune_set', potentiel]]

    #     data_scoring['efficiency_binned'] = pd.cut(data_scoring[potentiel],bins=(100, 110, 119.99, 139.99), right=False)

    #     # en dessous de 100, renvoie null, on les enlève.

    #     data_scoring.dropna(inplace=True)

    #     result = data_scoring.groupby(['rune_set', 'efficiency_binned']).count()
    #     # pas besoin d'un multiindex
    #     result.reset_index(inplace=True)

    #     print(result)
    #     # palier
    #     palier_1 = result['efficiency_binned'].unique()[0] # '[100.0, 110.0)'
    #     palier_2 = result['efficiency_binned'].unique()[1] # '[110.0, 120.0)'
    #     palier_3 = result['efficiency_binned'].unique()[2] # '[120.0, 130.0)'

    #     # poids des paliers

    #     palier = {palier_1 : 1,
    #       palier_2 : 2,
    #       palier_3 : 3}

    #     result['factor'] = 0

    #     for key, value in palier.items():
    #         result['factor'] = np.where(result['efficiency_binned'] == key, value, result['factor'])

    #     result['points'] = result[potentiel] * result['factor']

    #     # on sépare les dataset à mettre en évidence et les autres

    #     value_selected = result[result['rune_set'].isin(category_selected)]
    #     value_autres = result[~result['rune_set'].isin(category_selected)]

    #     value_selected.drop(['factor'], axis=1, inplace=True)

    #     # on ajoute les poids des sets

    #     for set in category_selected:
    #         value_selected['points'] = np.where(value_selected['rune_set'] == set, value_selected['points'] * coef_set[set], value_selected['points'])

    #     value_autres = value_autres.groupby('efficiency_binned').sum()
    #     value_autres.reset_index(inplace=True)
    #     value_autres.insert(0, 'rune_set', 'Autre')
    #     value_autres.drop(['factor'], axis=1, inplace=True)

    #     # on regroupe

    #     df_value = pd.concat([value_selected, value_autres])

    #     # on replace pour plus de lisibilité

    #     df_value['efficiency_binned'] = df_value['efficiency_binned'].replace({palier_1 : 100,
    #                                                                         palier_2 : 110,
    #                                                                         palier_3 : 120})

    #     score_r = df_value['points'].sum()

    #     # Calcul du TCD :

    #     tcd_value = df_value.pivot_table(df_value, 'rune_set', 'efficiency_binned', 'sum')[potentiel]
    #     # pas besoin du multiindex
    #     tcd_value.columns.name = "efficiency_potentiel"
    #     tcd_value.index.name = 'Set'

    #     total_100 = tcd_value[100].sum()
    #     total_110 = tcd_value[110].sum()
    #     total_120 = tcd_value[120].sum()

    #     tcd_value.loc['Total'] = [total_100, total_110, total_120]

    #     return tcd_value, score_r

    # tcd_potentiel_hero, score_potentiel_hero = scoring_rune('efficiency_max_hero')
    # tcd_potentiel_lgd, score_potentiel_lgd = scoring_rune('efficiency_max_lgd')
    # # On supprime les variables inutiles

    data.drop(['max_efficiency', 'max_efficiency_reachable',
              'gain'], axis=1, inplace=True)

    # # Map
    # ## Propriété
    # Plus simple ici qu'avant

    property = {0: 'Aucun',
                1: 'HP',
                2: 'HP%',
                3: 'ATQ',
                4: 'ATQ%',
                5: 'DEF',
                6: 'DEF%',
                8: "SPD",
                9: 'CRIT',
                10: 'DCC',
                11: 'RES',
                12: 'ACC'}

    for c in ['innate_type', 'first_sub', 'second_sub', 'third_sub', 'fourth_sub', 'main_type']:
        data[c] = data[c].map(property)

    # ## Monstres

    data_mobs = pd.DataFrame.from_dict(
        st.session_state['data_json'], orient="index").transpose()

    data_mobs = data_mobs['unit_list']

    # On va boucler et retenir ce qui nous intéresse..
    list_mobs = []
    data_mobs[0]
    with st.spinner('Chargement des monstres...'):
        for monstre in data_mobs[0]:
            unit = monstre['unit_id']
            master_id = monstre['unit_master_id']
            list_mobs.append([unit, master_id])

        # On met ça en dataframe
        df_mobs = pd.DataFrame(list_mobs, columns=['id_unit', 'id_monstre'])

        # Maintenant, on a besoin d'identifier les id.
        # Pour cela, on va utiliser l'api de swarfarm

        swarfarm = pd.read_excel('swarfarm.xlsx')
        # swarfarm

        swarfarm = swarfarm[['com2us_id', 'name']].set_index('com2us_id')
        df_mobs['name_monstre'] = df_mobs['id_monstre'].map(
            swarfarm.to_dict(orient="dict")['name'])

        # On peut faire le mapping...

        df_mobs = df_mobs[['id_unit', 'name_monstre']].set_index('id_unit')
    st.success('Chargement des monstres effectués !')

    data['rune_equiped'] = data['rune_equiped'].replace(
        df_mobs.to_dict(orient="dict")['name_monstre'])

    # # Indicateurs
    # ## Runes +15

    data['indicateurs_level'] = (data['level'] == 15).astype(
        'int')  # Si 15 -> 1. Sinon 0

    # # Amélioration des Grind

    dict = {'amelioration_first_grind': ['first_sub_grinded_value', 'first_grind_value'],
            'amelioration_second_grind': ['second_sub_grinded_value', 'second_grind_value'],
            'amelioration_third_grind': ['third_sub_grinded_value', 'third_grind_value'],
            'amelioration_fourth_grind': ['fourth_sub_grinded_value', 'fourth_grind_value']}

    with st.spinner('Vérification des runes et des modifications possibles  ...'):
        for key, value in dict.items():
            # Améliorable ? (valeur)
            data[key + '_lgd_value'] = data[value[1] +
                                            '_max_lgd'] - data[value[0]]
            data[key + '_hero_value'] = data[value[1] +
                                             '_max_hero'] - data[value[0]]
            # Améliorable ? (bool)
            data[key +
                 '_lgd_ameliorable?'] = (data[key + '_lgd_value'] > 0).astype('int')
            data[key +
                 '_hero_ameliorable?'] = (data[key + '_hero_value'] > 0).astype('int')
    st.success('Vérification des runes et des modifications possibles effectué !')

    # # Commentaires

    with st.spinner('Ajout des observations pour chaque rune'):
        # Level
        data['Commentaires'] = np.where(
            data['level'] != 15, "A monter +15 \n", "")
        calcul_gemme = data['first_gemme_bool'] + data['second_gemme_bool'] + \
            data['third_gemme_bool'] + data['fourth_gemme_bool']
        data['Commentaires'] = np.where(
            calcul_gemme == 0, data['Commentaires'] + "Pas de gemme utilisée", data['Commentaires'])
        data['Grind_lgd'] = ""
        data['Grind_hero'] = ""

        dict = {'amelioration_first_grind': 'first_sub',
                'amelioration_second_grind': 'second_sub',
                'amelioration_third_grind': 'third_sub',
                'amelioration_fourth_grind': 'fourth_sub'}

        # meule

        for key, value in dict.items():
            nom = key + "_lgd_value"
            data['Grind_lgd'] = np.where(data[key + '_lgd_ameliorable?'] == 1, data['Grind_lgd'] +
                                         "Meule : " + data[value] + "(" + data[nom].astype('str') + ") \n", data['Grind_lgd'])

            nom = key + "_hero_value"
            data['Grind_hero'] = np.where(data[key + '_hero_ameliorable?'] == 1, data['Grind_hero'] +
                                          "Meule : " + data[value] + "(" + data[nom].astype('str') + ") \n", data['Grind_hero'])

        # gemme

        # sub des gemmes

        gemme_max_lgd = {'HP': 580, 'HP%': 13, 'ATQ': 40, 'ATQ%': 13, 'DEF': 40,
                         'DEF%': 13, 'SPD': 10, 'CRIT': 9, 'DCC': 10, 'RES': 11, 'ACC': 11}
        gemme_max_hero = {'HP': 420, 'HP%': 11, 'ATQ': 30, 'ATQ%': 11, 'DEF': 30,
                          'DEF%': 11, 'SPD': 8, 'CRIT': 7, 'DCC': 8, 'RES': 9, 'ACC': 9}

        # On les inclut au dataframe

        data['first_gemme_max_lgd'] = data['first_sub'].map(gemme_max_lgd)
        data['second_gemme_max_lgd'] = data['second_sub'].map(gemme_max_lgd)
        data['third_gemme_max_lgd'] = data['third_sub'].map(gemme_max_lgd)
        data['fourth_gemme_max_lgd'] = data['fourth_sub'].map(gemme_max_lgd)

        data['first_gemme_max_hero'] = data['first_sub'].map(gemme_max_hero)
        data['second_gemme_max_hero'] = data['second_sub'].map(gemme_max_hero)
        data['third_gemme_max_hero'] = data['third_sub'].map(gemme_max_hero)
        data['fourth_gemme_max_hero'] = data['fourth_sub'].map(gemme_max_hero)

        dict2 = {'first_gemme': 'first_sub',
                 'second_gemme': 'second_sub',
                 'third_gemme': 'third_sub',
                 'fourth_gemme': 'fourth_sub'}

        # On fait le calcul :

        for key, sub in dict2.items():

            condition = data[key + '_bool'] == 1  # si 1 -> gemme utilisée
            # différence entre le max et la gemme
            calcul_lgd = data[key + '_max_lgd'] - data[sub + '_value']
            # différence entre le max et la gemme
            calcul_hero = data[key + '_max_hero'] - data[sub + '_value']
            condition_lgd = calcul_lgd > 0  # s'il y a un écart, ce n'est pas la stat max
            condition_hero = calcul_hero > 0

            data['Grind_lgd'] = np.where(condition,
                                         np.where(condition_lgd,
                                                  data['Grind_lgd'] + "Gemme : " + data[sub] +
                                                  "(" + calcul_lgd.astype('str') + ")",
                                                  data['Grind_lgd']),
                                         data['Grind_lgd'])
            data['Grind_hero'] = np.where(condition,
                                          np.where(condition_hero,
                                                   data['Grind_hero'] + "Gemme : " + data[sub] +
                                                   "(" + calcul_hero.astype('str') + ")",
                                                   data['Grind_hero']),
                                          data['Grind_hero'])

    st.success('Ajout des observations pour chaque rune effectué !')

    # # Clean du xl

    data.drop(['stars', 'level'], axis=1, inplace=True)

    data_short = data[['rune_set', 'rune_slot', 'rune_equiped', 'efficiency', 'efficiency_max_hero',
                       'efficiency_max_lgd', 'potentiel_max_lgd', 'potentiel_max_hero', 'Commentaires', 'Grind_lgd', 'Grind_hero']]

    # ## Meules manquantes par stat
    with st.spinner('Calcul des stats manquantes...'):
        property_grind = {1: 'Meule : HP',
                          2: 'Meule : HP%',
                          3: 'Meule : ATQ',
                          4: 'Meule : ATQ%',
                          5: 'Meule : DEF',
                          6: 'Meule : DEF%',
                          8: "Meule : SPD"}

        list_property_type = []
        list_property_count = []

        for propriete in property_grind.values():
            count = data['Grind_hero'].str.count(propriete).sum()

            list_property_type.append(propriete)
            list_property_count.append(count)

        property_grind_gemme = {1: 'Gemme : HP',
                                2: 'Gemme : HP%',
                                3: 'Gemme : ATQ',
                                4: 'Gemme : ATQ%',
                                5: 'Gemme : DEF',
                                6: 'Gemme : DEF%',
                                8: "Gemme : SPD"}

        for propriete in property_grind_gemme.values():
            count = data['Grind_hero'].str.count(propriete).sum()

            list_property_type.append(propriete)
            list_property_count.append(count)

        df_property = pd.DataFrame(
            [list_property_type, list_property_count]).transpose()
        df_property = df_property.rename(columns={
                                         0: 'Propriété', 1: 'Meules/Gemmes (hero) manquantes pour atteindre la stat max'})

    st.success('Calcul des stats manquantes effectués !')

    dict_rune = {}
    list_type = []
    list_count = []
    list_propriete = []
    list_propriete_gemmes = []
    list_count_gemmes = []

    set = {1: "Energy", 2: "Guard", 3: "Swift", 4: "Blade", 5: "Rage", 6: "Focus", 7: "Endure", 8: "Fatal", 10: "Despair", 11: "Vampire", 13: "Violent",
           14: "Nemesis", 15: "Will", 16: "Shield", 17: "Revenge", 18: "Destroy", 19: "Fight", 20: "Determination", 21: "Enhance", 22: "Accuracy", 23: "Tolerance", 99: "Immemorial"}

    with st.spinner('Ajout des informations pour identifier les runes...'):
        for type_rune in set.values():
            for propriete in property_grind.values():
                data_type_rune = data[data['rune_set'] == type_rune]
                nb_rune = data[data['rune_set'] == type_rune].count().max()
                count = data_type_rune['Grind_hero'].str.count(propriete).sum()

                dict_rune[type_rune] = nb_rune

                list_type.append(type_rune)
                list_count.append(count)
                list_propriete.append(propriete)

                df_rune = pd.DataFrame.from_dict(
                    dict_rune, orient='index', columns=['Nombre de runes'])

            for propriete in property_grind_gemme.values():
                data_type_rune = data[data['rune_set'] == type_rune]
                nb_rune = data[data['rune_set'] == type_rune].count().max()
                count = data_type_rune['Grind_hero'].str.count(propriete).sum()

                # list_type.append(type_rune)
                list_count_gemmes.append(count)
                list_propriete_gemmes.append(propriete)

        df_count = pd.DataFrame([list_type, list_propriete, list_count,
                                list_propriete_gemmes, list_count_gemmes]).transpose()
        df_count = df_count.rename(columns={0: 'Set', 1: 'Propriété Meules',
                                   2: 'Meules (hero) manquantes pour la stat max', 3: 'Propriété Gemmes', 4: 'Gemmes (hero) manquantes'})

        # Graphique
        fig_hero_manquante = px.histogram(df_count, x='Set', y='Meules (hero) manquantes pour la stat max',
                                          color='Propriété Meules', title="Meules heroiques manquantes pour la stat max", text_auto=True)

        fig_lgd_manquante = px.histogram(df_count, x='Set', y='Gemmes (hero) manquantes',
                                         color='Propriété Gemmes', title="Gemmes heroiques manquantes pour la stat max", text_auto=True)

        # Inventaire

        # On va gérer l'inventaire maintenant...

        df_inventaire = pd.DataFrame.from_dict(
            st.session_state['data_json'], orient='index').transpose()

        df_inventaire = df_inventaire['rune_craft_item_list']

        # id des crafts

        CRAFT_TYPE_MAP = {
            1: 'Enchant_gem',
            2: 'Grindstone',
            3: 'Gemme_immemoriale',
            4: 'Grindstone_immemoriale',
            5: 'Ancienne_gemme',
            6: 'Ancienne_grindstone',
        }

        # id des qualités de runes
        COM2US_QUALITY_MAP = {
            1: 'NORMAL',
            2: 'MAGIQUE',
            3: 'RARE',
            4: 'HEROIQUE',
            5: 'LGD',
            # Original quality values
            11: 'ANTIQUE_NORMAL',
            12: 'ANTIQUE_MAGIQUE',
            13: 'ANTIQUE_RARE',
            14: 'ANTIQUE_HEROIQUE',
            15: 'ANTIQUE_LGD',
        }

        # Combien de gemmes/meules différentes ?

        nb_boucle = len(df_inventaire[0])

        for i in range(0, nb_boucle):
            objet = str(df_inventaire[0][i]['craft_type_id'])
            nb_chiffre = len(objet)

            type = int(df_inventaire[0][i]['craft_type'])
            rune = int(objet[:nb_chiffre-4])
            stat = int(objet[nb_chiffre-4:nb_chiffre-2])
            quality = int(objet[nb_chiffre-2:nb_chiffre])

            df_inventaire[0][i]['type'] = CRAFT_TYPE_MAP[type]
            df_inventaire[0][i]['rune'] = set[rune]
            df_inventaire[0][i]['stat'] = property[stat]
            df_inventaire[0][i]['quality'] = COM2US_QUALITY_MAP[quality]

    st.success('Les informations pour identifier les runes ont été ajoutés !')

    #     Exemple découpage : item : 150814
    #     rune : 15
    #     stat : 8
    #     quality : 14

    @st.cache(show_spinner=False, suppress_st_warning=True)
    def charge_data(data, data_short, df_rune, df_count, df_inventaire):
        with st.spinner('Chargement des données concaténées...Prévoir quelques secondes'):

            df_inventaire = pd.DataFrame(df_inventaire)

            # découpe le dictionnaire imbriqué en un dict = une variable
            df_inventaire = extraire_variables_imbriquees(
                df_inventaire, 'rune_craft_item_list')

            # on refait pour sortir toutes les variables de chaque dict.... et on concatène pour n'avoir qu'un seul dataframe
            df_combine = extraire_variables_imbriquees(df_inventaire, 0)
            df_combine = df_combine[['craft_item_id', 'wizard_id', 'craft_type',
                                     'craft_type_id', 'sell_value', 'amount', 'type', 'rune', 'stat', 'quality']]

            for i in range(1, len(df_inventaire.columns)):
                df_combine2 = extraire_variables_imbriquees(df_inventaire, i)
                df_combine2 = df_combine2[['craft_item_id', 'wizard_id', 'craft_type',
                                           'craft_type_id', 'sell_value', 'amount', 'type', 'rune', 'stat', 'quality']]
                df_combine = pd.concat([df_combine, df_combine2])

            # On retient les variables utiles

            df_inventaire = df_combine[[
                'type', 'rune', 'stat', 'quality', 'amount']]

            # on sort values

            df_inventaire.sort_values(by=['rune'],  inplace=True)

            data_xlsx = export_excel(
                data, data_short, df_rune, df_count, df_inventaire)

            # Mise en forme :

            data['rune_equiped'] = data['rune_equiped'].astype('str')
            data_short['rune_equiped'] = data['rune_equiped'].astype('str')
            data_short['rune_equiped'] = data_short['rune_equiped'].replace({
                                                                            '0': 'Inventaire'})

            data_short['efficiency'] = np.round(data_short['efficiency'], 2)

            try:
                data_short.drop('Set', axis=1,  inplace=True)
            except KeyError:  # déjà fait
                pass

            return data_xlsx, data, data_short, df_rune, df_count, df_inventaire

    data_xlsx, data, data_short, df_rune, df_count, df_inventaire = charge_data(
        data, data_short, df_rune, df_count, df_inventaire)

    st.success('Terminé !')

    st.title('Summary')
    st.text("Note : Aucune donnée n'est conservée")
    data_short_filter = filter_dataframe(data_short, 'data_short')
    st.dataframe(data_short_filter)

    st.download_button('Télécharger la data (Excel)', data_xlsx, file_name='grind.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # with st.expander('Potentiel scoring'):
    #     column1, column2 = st.columns(2)
    #     with column1:
    #         st.metric('Score Hero', score_potentiel_hero)
    #         st.dataframe(tcd_potentiel_hero)

    #     with column2:
    #         st.metric('Score Lgd', score_potentiel_lgd)
    #         st.dataframe(tcd_potentiel_lgd)

    with st.expander('Nombre de runes (Grind max Hero)'):
        df_rune_filter = filter_dataframe(df_rune, 'df_rune')
        st.dataframe(df_rune_filter)

    with st.expander('Nombre de meules/gemmes nécessaires'):
        df_count_filter = filter_dataframe(df_count, 'df_count')
        st.dataframe(df_count_filter)
        st.plotly_chart(fig_hero_manquante)
        st.plotly_chart(fig_lgd_manquante)

    with st.expander('Inventaire'):
        df_inventaire_filter = filter_dataframe(df_inventaire, 'df_inventaire')
        st.dataframe(df_inventaire_filter)
