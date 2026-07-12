
import pandas as pd
import numpy as np
import ast
import streamlit as st
from io import BytesIO
from fonctions.visualisation import filter_dataframe, load_pygwalker
from fonctions.runes import Rune, CRAFT_TYPE_MAP, COM2US_QUALITY_MAP
# fix plotly express et Visual Studio Code
import plotly.io as pio
pio.renderers.default = "notebook_connected"

from streamlit_extras.colored_header import colored_header


from fonctions.visuel import css

css()



# Supprime les Future Warnings sur les copies
pd.options.mode.chained_assignment = None  # default='warn'






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
    with st.status(st.session_state.langue['calcul_potentiel_rune'], expanded=True) as status:

        data_class.calcul_potentiel()

        st.success(st.session_state.langue['calcul_potentiel_rune_success'])


    # # Indicateurs
    # ## Runes +15

        
        data_class.grind()



        data = data_class.data_grind
        
        data_short = data_class.data_short

    # ## Meules manquantes par stat (total)
        
        df_property = data_class.count_meules_manquantes()

        st.success(st.session_state.langue['calcul_rune_miss_success'])

    # Même calcul mais par set
        

        data_class.count_rune_with_potentiel_left()

        df_rune = data_class.df_rune

        df_count = data_class.df_count

        # Inventaire

        # On va gérer l'inventaire maintenant...

        df_inventaire = pd.DataFrame.from_dict(
            st.session_state['data_json'], orient='index').transpose()

        df_inventaire = df_inventaire['rune_craft_item_list']


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

        st.success(st.session_state.langue['calcul_add_info_success'])

    #     Exemple découpage : item : 150814
    #     rune : 15
    #     stat : 8
    #     quality : 14

        @st.cache_data(show_spinner=False)
        def charge_data(data, data_short, df_rune, df_count, df_inventaire, user_id, meule:bool, all_data:bool, set_selected = None, efficiency_selected = None, spd_selected = None):
            with st.spinner(st.session_state.langue['calcul_loading_rune']):

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
                                'fourth_sub': 'Substat 4',
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
                                'first_sub_value_total': 'Substat total 1',
                                'second_sub_value_total': 'Substat total 2',
                                'third_sub_value_total': 'Substat total 3',
                                'fourth_sub_value_total': 'Substat total 4',
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
                
                data.reset_index(inplace=True)
                data.rename(columns={'index': 'Id_rune'}, inplace=True)
                data_short.reset_index(inplace=True)
                data_short.rename(columns={'index': 'Set'}, inplace=True)
                df_rune.reset_index(inplace=True)
                df_rune.rename(columns={'index': 'Set'}, inplace=True)

                # Mise en forme :

                data['Equipé'] = data['Equipé'].astype('str')
                data_short['Equipé'] = data['Equipé'].astype('str')
                data_short['Equipé'] = data_short['Equipé'].replace(
                    {'0': 'Inventaire'})

                data_short['Efficience'] = np.round(data_short['Efficience'], 2)
                
                data_short.rename(columns={'Set': 'Id_rune'}, inplace=True)
                
                # Gestion des substats
                
                
                
                if all_data:
                    st.dataframe(data)
                
                if meule:
                
                    melt = data.melt(id_vars=['Id_rune', 'Set rune', 'Slot', 'Substat 1', 'Substat 2', 'Substat 3', 'Substat 4'],
                            value_vars=['Substat total 1', 'Substat total 2', 'Substat total 3', 'Substat total 4'])
                else:
                    
                    melt = data.melt(id_vars=['Id_rune', 'Set rune', 'Slot', 'Substat 1', 'Substat 2', 'Substat 3', 'Substat 4'],
                            value_vars=['Substat valeur 1', 'Substat valeur 2', 'Substat valeur 3', 'Substat valeur 4'])

                def changement_variable(x):
                        number = x.variable[-1]
                        type = x[f'Substat {number}']
                        
                        return type

                melt['variable'] = melt.apply(changement_variable, axis=1)
                

                pivot = melt.pivot_table(index=['Id_rune', 'Set rune', 'Slot'],
                                        columns='variable',
                                        values='value',
                                        aggfunc='first',
                                        observed=True,
                                        fill_value=0).reset_index()
                
                if meule:
                    data = data.merge(pivot, on=['Id_rune', 'Set rune', 'Slot']).drop(columns=['Substat 1', 'Substat 2', 'Substat 3', 'Substat 4', 'Substat total 1', 'Substat total 2', 'Substat total 3', 'Substat total 4'])
                else:
                    data = data.merge(pivot, on=['Id_rune', 'Set rune', 'Slot']).drop(columns=['Substat 1', 'Substat 2', 'Substat 3', 'Substat 4', 'Substat valeur 1', 'Substat valeur 2', 'Substat valeur 3', 'Substat valeur 4'])
                data_short = data_short.merge(pivot, on=['Id_rune', 'Set rune', 'Slot'])
                
                data['Commentaires'] = np.where(
                    data['SPD'] == 0, data['Commentaires'] + "\n Pas de SPD", data['Commentaires'])

                data_short['Commentaires'] = np.where(
                    data_short['SPD'] == 0, data_short['Commentaires'] + "\n Pas de SPD", data_short['Commentaires'])
                
                data_xlsx = export_excel(
                    data, data_short, df_rune, df_count, df_inventaire)
                try:
                    data_short.drop('Set', axis=1,  inplace=True)
                except KeyError:  # déjà fait
                    pass

                return data_xlsx, data, data_short, df_rune, df_count, df_inventaire
            
        status.update(label='Complet !', state='complete', expanded=False)    
        
    show_stat = st.checkbox(st.session_state.langue['show_include_meule'], value=True, key='checkbox_data', help=st.session_state.langue['show_include_meule_help'])
    show_all = st.checkbox(st.session_state.langue['data_complete'], key='data_complete', help=st.session_state.langue['data_complete_help'])
    
    reapp = st.checkbox(st.session_state.langue['reap_tag'])
    
    data_xlsx, data, data_short, df_rune, df_count, df_inventaire = charge_data(
            data, data_short, df_rune, df_count, df_inventaire, st.session_state.compteid, show_stat, show_all)
    
    if reapp:
        set_selected = st.multiselect('Set Rune', st.session_state.set_rune, help=st.session_state.langue['obligatoire'], default=['Violent', 'Will', 'Swift'])
        efficiency_max_potentiel = st.slider(f'{st.session_state.langue["Efficience"]} max lgd', 0, 150, 50)
        spd_selected = st.slider('SPD', 0, 32, 0)
        

        data['Commentaires'] = np.where(
                               ((data['Set rune'].isin(set_selected) &
                                 ((data['Efficience_max_lgd'] <= efficiency_max_potentiel) |
                                  (data['SPD'] <= spd_selected)))),
                               data['Commentaires'] + "\n Reapp",
                               data['Commentaires'])
        data_short['Commentaires'] = np.where(
                               ((data_short['Set rune'].isin(set_selected) & 
                                 ((data_short['Efficience_max_lgd'] < efficiency_max_potentiel)  | 
                                  (data['SPD'] <= spd_selected)))),
                               data_short['Commentaires'] + "\n Reapp",
                               data_short['Commentaires'])
        
        data_xlsx = export_excel(
                    data, data_short, df_rune, df_count, df_inventaire)


    st.subheader('Summary')
    st.info(st.session_state.langue['info_conservation_data'])
    
    data_short_filter = filter_dataframe(data_short, 'data_short')
    st.dataframe(data_short_filter.drop('Id_rune', axis=1))
    
            
    st.download_button(st.session_state.langue['download_excel'], data_xlsx, file_name=f'optimisation runes {st.session_state["pseudo"]}.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    

    colored_header(
            label=st.session_state.langue['analyse_poussee'],
            description="",
            color_name="blue-70",
        )    
    if st.checkbox(st.session_state.langue['construire_tcd']):
        vis_spec = r"""{"config":[{"config":{"defaultAggregated":true,"geoms":["auto"],"coordSystem":"generic","limit":-1,"timezoneDisplayOffset":0},
        "encodings":{"dimensions":
        [{"fid":"Set rune","name":"Set rune","basename":"Set rune","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"Id_rune","name":"Id_rune","basename":"Id_rune","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"Slot","name":"Slot","basename":"Slot","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"Equipé","name":"Equipé","basename":"Equipé","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"qualité","name":"qualité","basename":"qualité","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"qualité_original","name":"qualité_original","basename":"qualité_original","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"Stat principal","name":"Stat principal","basename":"Stat principal","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"Valeur stat principal","name":"Valeur stat principal","basename":"Valeur stat principal","semanticType":"quantitative","analyticType":"dimension","offset":0},
        {"fid":"innate_type","name":"innate_type","basename":"innate_type","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"Gemmé 1 ?","name":"Gemmé 1 ?","basename":"Gemmé 1 ?","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"Gemmé 2 ?","name":"Gemmé 2 ?","basename":"Gemmé 2 ?","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"Gemmé 3 ?","name":"Gemmé 3 ?","basename":"Gemmé 3 ?","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"Gemmé 4 ?","name":"Gemmé 4 ?","basename":"Gemmé 4 ?","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"indicateurs_level","name":"indicateurs_level","basename":"indicateurs_level","semanticType":"quantitative","analyticType":"dimension","offset":0},
        {"fid":"Commentaires","name":"Commentaires","basename":"Commentaires","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"Grind_lgd","name":"Grind_lgd","basename":"Grind_lgd","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"Grind_hero","name":"Grind_hero","basename":"Grind_hero","semanticType":"nominal","analyticType":"dimension","offset":0},
        {"fid":"gw_mea_key_fid","name":"Measure names","analyticType":"dimension","semanticType":"nominal"}],
        "measures":[
        

        {"fid":"Efficience","name":"Efficience","basename":"Efficience","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"innate_value","name":"innate_value","basename":"innate_value","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Substat valeur 1","name":"Substat valeur 1","basename":"Substat valeur 1","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Valeur meule 1","name":"Valeur meule 1","basename":"Valeur meule 1","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Substat valeur 2","name":"Substat valeur 2","basename":"Substat valeur 2","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Valeur meule 2","name":"Valeur meule 2","basename":"Valeur meule 2","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Substat valeur 3","name":"Substat valeur 3","basename":"Substat valeur 3","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Valeur meule 3","name":"Valeur meule 3","basename":"Valeur meule 3","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Substat valeur 4","name":"Substat valeur 4","basename":"Substat valeur 4","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Valeur meule 4","name":"Valeur meule 4","basename":"Valeur meule 4","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Substat 1 max","name":"Substat 1 max","basename":"Substat 1 max","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Substat 2 max","name":"Substat 2 max","basename":"Substat 2 max","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Substat 3 max","name":"Substat 3 max","basename":"Substat 3 max","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Substat 4 max","name":"Substat 4 max","basename":"Substat 4 max","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Meule 1 lgd Max","name":"Meule 1 lgd Max","basename":"Meule 1 lgd Max","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Meule 1 hero Max","name":"Meule 1 hero Max","basename":"Meule 1 hero Max","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Meule 2 lgd Max","name":"Meule 2 lgd Max","basename":"Meule 2 lgd Max","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Meule 2 hero Max","name":"Meule 2 hero Max","basename":"Meule 2 hero Max","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Meule 3 lgd Max","name":"Meule 3 lgd Max","basename":"Meule 3 lgd Max","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Meule 3 hero Max","name":"Meule 3 hero Max","basename":"Meule 3 hero Max","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Meule 4 lgd Max","name":"Meule 4 lgd Max","basename":"Meule 4 lgd Max","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Meule 4 hero Max","name":"Meule 4 hero Max","basename":"Meule 4 hero Max","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"first_sub_value_total_max_lgd","name":"first_sub_value_total_max_lgd","basename":"first_sub_value_total_max_lgd","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"second_sub_value_total_max_lgd","name":"second_sub_value_total_max_lgd","basename":"second_sub_value_total_max_lgd","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"third_sub_value_total_max_lgd","name":"third_sub_value_total_max_lgd","basename":"third_sub_value_total_max_lgd","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"fourth_sub_value_total_max_lgd","name":"fourth_sub_value_total_max_lgd","basename":"fourth_sub_value_total_max_lgd","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"first_sub_value_total_max_hero","name":"first_sub_value_total_max_hero","basename":"first_sub_value_total_max_hero","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"second_sub_value_total_max_hero","name":"second_sub_value_total_max_hero","basename":"second_sub_value_total_max_hero","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"third_sub_value_total_max_hero","name":"third_sub_value_total_max_hero","basename":"third_sub_value_total_max_hero","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"fourth_sub_value_total_max_hero","name":"fourth_sub_value_total_max_hero","basename":"fourth_sub_value_total_max_hero","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Efficience_max_lgd","name":"Efficience_max_lgd","basename":"Efficience_max_lgd","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"Efficience_max_hero","name":"Efficience_max_hero","basename":"Efficience_max_hero","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"potentiel_max_lgd","name":"potentiel_max_lgd","basename":"potentiel_max_lgd","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"potentiel_max_hero","name":"potentiel_max_hero","basename":"potentiel_max_hero","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"amelioration_first_grind_lgd_value","name":"amelioration_first_grind_lgd_value","basename":"amelioration_first_grind_lgd_value","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"amelioration_first_grind_hero_value","name":"amelioration_first_grind_hero_value","basename":"amelioration_first_grind_hero_value","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"amelioration_second_grind_lgd_value","name":"amelioration_second_grind_lgd_value","basename":"amelioration_second_grind_lgd_value","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"amelioration_second_grind_hero_value","name":"amelioration_second_grind_hero_value","basename":"amelioration_second_grind_hero_value","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"amelioration_third_grind_lgd_value","name":"amelioration_third_grind_lgd_value","basename":"amelioration_third_grind_lgd_value","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"amelioration_third_grind_hero_value","name":"amelioration_third_grind_hero_value","basename":"amelioration_third_grind_hero_value","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"amelioration_fourth_grind_lgd_value","name":"amelioration_fourth_grind_lgd_value","basename":"amelioration_fourth_grind_lgd_value","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"amelioration_fourth_grind_hero_value","name":"amelioration_fourth_grind_hero_value","basename":"amelioration_fourth_grind_hero_value","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"ACC","name":"ACC","basename":"ACC","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"ATQ","name":"ATQ","basename":"ATQ","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"ATQ%","name":"ATQ%","basename":"ATQ%","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"CRIT","name":"CRIT","basename":"CRIT","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"DCC","name":"DCC","basename":"DCC","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"DEF","name":"DEF","basename":"DEF","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"DEF%","name":"DEF%","basename":"DEF%","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"HP","name":"HP","basename":"HP","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"HP%","name":"HP%","basename":"HP%","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"RES","name":"RES","basename":"RES","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"SPD","name":"SPD","basename":"SPD","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
        {"fid":"amelioration_fourth_grind_hero_ameliorable?","name":"amelioration_fourth_grind_hero_ameliorable?","basename":"amelioration_fourth_grind_hero_ameliorable?","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"amelioration_fourth_grind_lgd_ameliorable?","name":"amelioration_fourth_grind_lgd_ameliorable?","basename":"amelioration_fourth_grind_lgd_ameliorable?","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"amelioration_third_grind_hero_ameliorable?","name":"amelioration_third_grind_hero_ameliorable?","basename":"amelioration_third_grind_hero_ameliorable?","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"amelioration_third_grind_lgd_ameliorable?","name":"amelioration_third_grind_lgd_ameliorable?","basename":"amelioration_third_grind_lgd_ameliorable?","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"amelioration_second_grind_hero_ameliorable?","name":"amelioration_second_grind_hero_ameliorable?","basename":"amelioration_second_grind_hero_ameliorable?","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"amelioration_second_grind_lgd_ameliorable?","name":"amelioration_second_grind_lgd_ameliorable?","basename":"amelioration_second_grind_lgd_ameliorable?","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"amelioration_first_grind_hero_ameliorable?","name":"amelioration_first_grind_hero_ameliorable?","basename":"amelioration_first_grind_hero_ameliorable?","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"amelioration_first_grind_lgd_ameliorable?","name":"amelioration_first_grind_lgd_ameliorable?","basename":"amelioration_first_grind_lgd_ameliorable?","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"fourth_gemme_max_hero","name":"fourth_gemme_max_hero","basename":"fourth_gemme_max_hero","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"third_gemme_max_hero","name":"third_gemme_max_hero","basename":"third_gemme_max_hero","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"second_gemme_max_hero","name":"second_gemme_max_hero","basename":"second_gemme_max_hero","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"first_gemme_max_hero","name":"first_gemme_max_hero","basename":"first_gemme_max_hero","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"fourth_gemme_max_lgd","name":"fourth_gemme_max_lgd","basename":"fourth_gemme_max_lgd","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"third_gemme_max_lgd","name":"third_gemme_max_lgd","basename":"third_gemme_max_lgd","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"second_gemme_max_lgd","name":"second_gemme_max_lgd","basename":"second_gemme_max_lgd","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"first_gemme_max_lgd","name":"first_gemme_max_lgd","basename":"first_gemme_max_lgd","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"innate_value_max","name":"innate_value_max","basename":"innate_value_max","semanticType":"quantitative","analyticType":"measure","offset":0},
        {"fid":"gw_count_fid","name":"Row count","analyticType":"measure","semanticType":"quantitative","aggName":"sum","computed":true,
        "expression":{"op":"one","params":[],"as":"gw_count_fid"}},{"fid":"gw_mea_val_fid","name":"Measure values","analyticType":"measure","semanticType":"quantitative","aggName":"sum"}],"rows":[],"columns":[],"color":[],"opacity":[],"size":[],"shape":[],"radius":[],"theta":[],"longitude":[],"latitude":[],"geoId":[],"details":[],"filters":[],"text":[]},"layout":{"showActions":false,"showTableSummary":false,"stack":"stack","interactiveScale":false,"zeroScale":true,"size":{"mode":"auto","width":320,"height":200},"format":{},"geoKey":"name","resolve":{"x":false,"y":false,"color":false,"opacity":false,"shape":false,"size":false}},"visId":"gw_ETxn","name":"Chart 1"}],"chart_map":{},"workflow_list":[{"workflow":[{"type":"view","query":[{"op":"raw","fields":[]}]}]}],"version":"0.4.9.13"}"""

        pig = load_pygwalker(data, vis_spec)
        pig.explorer()
    
    

    del data, data_short, df_rune, df_count, df_inventaire, data_xlsx, data_short_filter

if 'submitted' in st.session_state:
    if st.session_state.submitted:
        st.title('Optimisation Runes')
        optimisation_rune()

    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")


st.caption('Made by Tomlora :sunglasses:')