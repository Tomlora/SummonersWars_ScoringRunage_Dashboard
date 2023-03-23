from st_pages import add_indentation
import pandas as pd
import numpy as np
import plotly.express as px
import ast
import streamlit as st
from io import BytesIO
from fonctions.visualisation import filter_dataframe
import plotly.graph_objects as go
from fonctions.runes import Rune
from streamlit_extras.switch_page_button import switch_page
# fix plotly express et Visual Studio Code
import plotly.io as pio
pio.renderers.default = "notebook_connected"

# Supprime les Future Warnings sur les copies
pd.options.mode.chained_assignment = None  # default='warn'


add_indentation()


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
        worksheet3.set_column(i, i+1, 30, cell_format)
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


def optimisation_rune():

    data_class = st.session_state.data_rune
    with st.spinner('Calcul du potentiel des runes...'):

        data_class.calcul_potentiel()

    st.success('Calcul du potentiel des runes effectué !')

    # ## Monstres

    data_mobs = pd.DataFrame.from_dict(
        st.session_state['data_json'], orient="index").transpose()

    data_mobs = data_mobs['unit_list']

    # On va boucler et retenir ce qui nous intéresse..
    list_mobs = []
    with st.spinner('Chargement des monstres...'):
        for monstre in data_mobs[0]:
            unit = monstre['unit_id']
            master_id = monstre['unit_master_id']
            list_mobs.append([unit, master_id])

        # On met ça en dataframe
        df_mobs = pd.DataFrame(list_mobs, columns=['id_unit', 'id_monstre'])

        # Maintenant, on a besoin d'identifier les id.
        # Pour cela, on va utiliser l'api de swarfarm

        # swarfarm

        swarfarm = st.session_state.swarfarm[[
            'com2us_id', 'name']].set_index('com2us_id')
        df_mobs['name_monstre'] = df_mobs['id_monstre'].map(
            swarfarm.to_dict(orient="dict")['name'])

        # On peut faire le mapping...

        df_mobs = df_mobs[['id_unit', 'name_monstre']].set_index('id_unit')
    st.success('Chargement des monstres effectués !')

    data_class.identify_monsters(st.session_state.identification_monsters)

    # # Indicateurs
    # ## Runes +15

    with st.spinner('Vérification des runes et des modifications possibles  ...'):
        data_class.grind()

    st.success('Vérification des runes et des modifications possibles effectué !')

    data = data_class.data_grind
    data_short = data_class.data_short

    # ## Meules manquantes par stat (total)
    with st.spinner('Calcul des stats manquantes...'):
        df_property = data_class.count_meules_manquantes()

    st.success('Calcul des stats manquantes effectués !')

    # Même calcul mais par set
    with st.spinner('Ajout des informations pour identifier les runes...'):

        data_class.count_rune_with_potentiel_left()

        df_rune = data_class.df_rune

        df_count = data_class.df_count

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
            df_inventaire[0][i]['rune'] = data_class.set[rune]
            df_inventaire[0][i]['stat'] = data_class.property[stat]
            df_inventaire[0][i]['quality'] = COM2US_QUALITY_MAP[quality]

    st.success('Les informations pour identifier les runes ont été ajoutés !')

    #     Exemple découpage : item : 150814
    #     rune : 15
    #     stat : 8
    #     quality : 14

    @st.cache_data(show_spinner=False)
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

            rename_column = {'rune_set': 'Set rune',
                             'rune_slot': 'Slot',
                             'rune_equiped': 'Equipé',
                             'efficiency': 'Efficience',
                             'efficiency_max_hero': 'Efficience_max_hero',
                             'efficiency_max_lgd': 'Efficience_max_lgd',
                             'quality': 'qualité',
                             'amount': 'montant',
                             'main_type': 'Stat principal',
                             'main_value': 'Valeur stat principal',
                             'first_sub': 'Substat 1',
                             'second_sub': 'Substat 2',
                             'third_sub': 'Substat 3',
                             'fourth sub': 'Substat 4',
                             'first_sub_value': 'Substat valeur 1',
                             'second_sub_value': 'Substat valeur 2',
                             'third_sub_value': 'Substat valeur 3',
                             'fourth_sub_value': 'Substat valeur 4',
                             'first_gemme_bool': 'Gemmé 1 ?',
                             'second_gemme_bool': 'Gemmé 2 ?',
                             'third_gemme_bool': 'Gemmé 3 ?',
                             'fourth_gemme_bool': 'Gemmé 4 ?',
                             'first_sub_grinded_value': 'Valeur meule 1',
                             'second_sub_grinded_value': 'Valeur meule 2',
                             'third_sub_grinded_value': 'Valeur meule 3',
                             'fourth_sub_grinded_value': 'Valeur meule 4',
                             'first_sub_value_max': 'Substat 1 max',
                             'second_sub_value_max': 'Substat 2 max',
                             'third_sub_value_max': 'Substat 3 max',
                             'fourth_sub_value_max': 'Substat 4 max',
                             'first_sub_value_total': 'Substat 1 total',
                             'second_sub_value_total': 'Substat 2 total',
                             'third_sub_value_total': 'Substat 3 total',
                             'fourth_sub_value_total': 'Substat 4 total',
                             'first_grind_value_max_lgd': 'Meule 1 lgd Max',
                             'second_grind_value_max_lgd': 'Meule 2 lgd Max',
                             'third_grind_value_max_lgd': 'Meule 3 lgd Max',
                             'fourth_grind_value_max_lgd': 'Meule 4 lgd Max',
                             'first_grind_value_max_hero': 'Meule 1 hero Max',
                             'second_grind_value_max_hero': 'Meule 2 hero Max',
                             'third_grind_value_max_hero': 'Meule 3 hero Max',
                             'fourth_grind_value_max_hero': 'Meule 4 hero Max'}

            for c in ['first_gemme_bool', 'second_gemme_bool', 'third_gemme_bool', 'fourth_gemme_bool']:
                data[c] = data[c].map({0: 'Non', 1: 'Oui'})

            data.rename(columns=rename_column, inplace=True)
            data_short.rename(columns=rename_column, inplace=True)
            df_rune.rename(columns=rename_column, inplace=True)
            df_count.rename(columns=rename_column, inplace=True)
            df_inventaire.rename(columns=rename_column, inplace=True)

            data_xlsx = export_excel(
                data, data_short, df_rune, df_count, df_inventaire)

            # Mise en forme :

            data['Equipé'] = data['Equipé'].astype('str')
            data_short['Equipé'] = data['Equipé'].astype('str')
            data_short['Equipé'] = data_short['Equipé'].replace(
                {'0': 'Inventaire'})

            data_short['Efficience'] = np.round(data_short['Efficience'], 2)

            try:
                data_short.drop('Set', axis=1,  inplace=True)
            except KeyError:  # déjà fait
                pass

            return data_xlsx, data, data_short, df_rune, df_count, df_inventaire

    data_xlsx, data, data_short, df_rune, df_count, df_inventaire = charge_data(
        data, data_short, df_rune, df_count, df_inventaire)

    st.success('Terminé !')

    st.subheader('Summary')
    st.text("Note : Aucune donnée n'est conservée")
    data_short_filter = filter_dataframe(data_short, 'data_short')
    st.dataframe(data_short_filter)

    st.download_button('Télécharger la data (Excel)', data_xlsx, file_name='grind.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ['Potentiel max hero', 'Potentiel max lgd', 'Nombre de runes (Grid max Hero)', 'Meules/Gemmes nécessaires', 'Inventaire'])

    def potentiel_max(variable):
        data_grp: pd.DataFrame = data_short.groupby('Set rune').agg({f'Efficience_max_{variable}': ['mean', 'max', 'median'],
                                                                     f'potentiel_max_{variable}': ['mean', 'max', 'median']})
        data_grp.columns.set_levels(
            ['Moyenne', 'Max', 'Mediane'], level=1, inplace=True)
        # data_grp = data_grp.droplevel(level=0, axis=1)
        st.dataframe(data_grp)

        fig = go.Figure()
        # on calcule ce que ça donnerait avec le potentiel
        data_grp['total'] = data_grp[f'Efficience_max_{variable}']['Moyenne'] + \
            data_grp[f'potentiel_max_{variable}']['Moyenne']
        fig.add_trace(go.Histogram(
            y=data_grp['total'], x=data_grp.index, histfunc='avg', name=f'potentiel {variable}'))
        fig.add_trace(go.Histogram(
            y=data_grp[f'Efficience_max_{variable}']['Moyenne'], x=data_grp.index, histfunc='avg', name='efficience actuelle'))
        fig.update_layout(
            barmode="overlay",
            title=f'Potentiel {variable}',
            bargap=0.1)

        return fig

    with tab1:
        fig_max_hero = potentiel_max('hero')
        st.plotly_chart(fig_max_hero)

    with tab2:
        fig_max_lgd = potentiel_max('lgd')
        st.plotly_chart(fig_max_lgd)
    with tab3:
        df_rune_filter = filter_dataframe(df_rune, 'df_rune')
        st.dataframe(df_rune_filter)

    with tab4:
        df_count_filter = filter_dataframe(df_count, 'df_count')
        st.dataframe(df_count_filter)
        st.plotly_chart(fig_hero_manquante)
        st.plotly_chart(fig_lgd_manquante)

    with tab5:
        df_inventaire_filter = filter_dataframe(df_inventaire, 'df_inventaire')
        st.dataframe(df_inventaire_filter)


if 'submitted' in st.session_state:
    if st.session_state.submitted:
        st.title('Optimisation Runes')
        optimisation_rune()

    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')


st.caption('Made by Tomlora')