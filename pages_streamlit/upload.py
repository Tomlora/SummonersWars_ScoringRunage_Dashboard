import pandas as pd
import numpy as np
import streamlit as st
import json
from datetime import datetime
from streamlit_option_menu import option_menu

from gestion_bdd import sauvegarde_bdd, lire_bdd

def date_du_jour():
    currentMonth = str(datetime.now().month)
    currentYear = str(datetime.now().year)
    currentDay = str(datetime.now().day)
    return f'{currentDay}/{currentMonth}/{currentYear}'


def upload_json(category_selected):
    with st.form('Data du compte'):
        st.session_state.file = st.file_uploader('Choisis un json', type=['json'], help='Json SW Exporter')
        st.session_state['submitted'] = st.form_submit_button('Calcule mon score')
        
        
    if st.session_state['file'] is not None and st.session_state.submitted:

        # On charge le json
        data_json = json.load(st.session_state['file'])


        player_runes = {}


        # pseudo 

        st.session_state.pseudo = data_json['wizard_info']['wizard_name']
        st.session_state.guildeid = data_json['guild']['guild_info']['guild_id']
        st.session_state.guilde = data_json['guild']['guild_info']['name']

        # rune
        # Rune pas équipé
        for rune in data_json['runes']:
            first_sub = 0
            first_sub_value = 0
            first_sub_grinded_value = 0
            second_sub = 0
            second_sub_value = 0
            second_sub_grinded_value = 0
            third_sub = 0
            third_sub_value = 0
            third_sub_grinded_value = 0
            fourth_sub = 0
            fourth_sub_value = 0
            fourth_sub_grinded_value = 0
            first_gemme_bool = 0
            first_sub_grinded_value = 0
            second_gemme_bool = 0
            second_sub_grinded_value = 0
            third_gemme_bool = 0
            third_sub_grinded_value = 0
            fourth_gemme_bool = 0
            fourth_sub_grinded_value = 0

            rune_id = rune['rune_id']
            rune_set = rune['set_id']
            rune_slot = rune['slot_no']
            rune_equiped = rune['occupied_id']
            stars = rune['class']
            level = rune['upgrade_curr']
            efficiency = 0
            max_efficiency = 0
            max_efficiency_reachable = 0
            gain = 0
            main_type = rune['pri_eff'][0]
            main_value = rune['pri_eff'][1]
            innate_type = rune['prefix_eff'][0]
            innate_value = rune['prefix_eff'][1]

            if level > 2:
                first_sub = rune['sec_eff'][0][0]
                first_sub_value = rune['sec_eff'][0][1]
                first_gemme_bool = rune['sec_eff'][0][2]
                first_sub_grinded_value = rune['sec_eff'][0][3]
            if level > 5:
                second_sub = rune['sec_eff'][1][0]
                second_sub_value = rune['sec_eff'][1][1]
                second_gemme_bool = rune['sec_eff'][1][2]
                second_sub_grinded_value = rune['sec_eff'][1][3]
            if level > 8:
                third_sub = rune['sec_eff'][2][0]
                third_sub_value = rune['sec_eff'][2][1]
                third_gemme_bool = rune['sec_eff'][2][2]
                third_sub_grinded_value = rune['sec_eff'][2][3]
            if level > 11:
                fourth_sub = rune['sec_eff'][3][0]
                fourth_sub_value = rune['sec_eff'][3][1]
                fourth_gemme_bool = rune['sec_eff'][3][2]
                fourth_sub_grinded_value = rune['sec_eff'][3][3]

            try:
                player_runes[rune_id] =  [rune_set, rune_slot, rune_equiped, stars, level, efficiency, max_efficiency,
                                    max_efficiency_reachable, gain, main_type, main_value, innate_type, innate_value,
                                    first_sub, first_sub_value, first_gemme_bool,  first_sub_grinded_value, second_sub, second_sub_value, second_gemme_bool,
                                    second_sub_grinded_value, third_sub, third_sub_value, third_gemme_bool, third_sub_grinded_value, fourth_sub,
                                    fourth_sub_value, fourth_gemme_bool, fourth_sub_grinded_value]
            except:
                print(f'Erreur : {rune_id}')

        # Rune équipée
        for unit in data_json['unit_list']:
            for stat in unit:
                if stat == "runes":
                    for rune in unit[stat]:
                        first_sub = 0
                        first_sub_value = 0
                        first_sub_grinded_value = 0
                        second_sub = 0
                        second_sub_value = 0
                        second_sub_grinded_value = 0
                        third_sub = 0
                        third_sub_value = 0
                        third_sub_grinded_value = 0
                        fourth_sub = 0
                        fourth_sub_value = 0
                        fourth_sub_grinded_value = 0

                        rune_id = rune['rune_id']
                        rune_set = rune['set_id']
                        rune_slot = rune['slot_no']
                        rune_equiped = rune['occupied_id']
                        stars = rune['class']
                        level = rune['upgrade_curr']
                        efficiency = 0
                        max_efficiency = 0
                        max_efficiency_reachable = 0
                        gain = 0
                        main_type = rune['pri_eff'][0]
                        main_value = rune['pri_eff'][1]
                        innate_type = rune['prefix_eff'][0]
                        innate_value = rune['prefix_eff'][1]
                        # rank = rune['extra']
                        if level > 2:
                            first_sub = rune['sec_eff'][0][0]
                            first_sub_value = rune['sec_eff'][0][1]
                            first_gemme_bool = rune['sec_eff'][0][2]
                            first_sub_grinded_value = rune['sec_eff'][0][3]
                        if level > 5:
                            second_sub = rune['sec_eff'][1][0]
                            second_sub_value = rune['sec_eff'][1][1]
                            second_gemme_bool = rune['sec_eff'][1][2]
                            second_sub_grinded_value = rune['sec_eff'][1][3]
                        if level > 8:
                            third_sub = rune['sec_eff'][2][0]
                            third_sub_value = rune['sec_eff'][2][1]
                            third_gemme_bool = rune['sec_eff'][2][2]
                            third_sub_grinded_value = rune['sec_eff'][2][3]
                        if level > 11:
                            fourth_sub = rune['sec_eff'][3][0]
                            fourth_sub_value = rune['sec_eff'][3][1]
                            fourth_gemme_bool = rune['sec_eff'][3][2]
                            fourth_sub_grinded_value = rune['sec_eff'][3][3]
                            
                        player_runes[rune_id] =  [rune_set, rune_slot, rune_equiped, stars, level, efficiency, max_efficiency,
                                    max_efficiency_reachable, gain, main_type, main_value, innate_type, innate_value,
                                    first_sub, first_sub_value, first_gemme_bool, first_sub_grinded_value, second_sub, second_sub_value, second_gemme_bool,
                                    second_sub_grinded_value, third_sub, third_sub_value, third_gemme_bool, third_sub_grinded_value, fourth_sub,
                                    fourth_sub_value, fourth_gemme_bool, fourth_sub_grinded_value]


        # on crée un df avec la data

        data = pd.DataFrame.from_dict(player_runes, orient="index", columns=['rune_set', 'rune_slot', 'rune_equiped', 'stars', 'level', 'efficiency', 'max_efficiency', 'max_efficiency_reachable', 'gain', 'main_type', 'main_value', 'innate_type',
                                                                            'innate_value','first_sub', 'first_sub_value', 'first_gemme_bool', 'first_sub_grinded_value', 'second_sub', 'second_sub_value', 'second_gemme_bool',
                                    'second_sub_grinded_value', 'third_sub', 'third_sub_value', 'third_gemme_bool', 'third_sub_grinded_value', 'fourth_sub',
                                    'fourth_sub_value', 'fourth_gemme_bool', 'fourth_sub_grinded_value'])


        # # Map des sets


        set = {1:"Energy", 2:"Guard", 3:"Swift", 4:"Blade", 5:"Rage", 6:"Focus", 7:"Endure", 8:"Fatal", 10:"Despair", 11:"Vampire", 13:"Violent",
                14:"Nemesis", 15:"Will", 16:"Shield", 17:"Revenge", 18:"Destroy", 19:"Fight", 20:"Determination", 21:"Enhance", 22:"Accuracy", 23:"Tolerance", 99:"Immemorial"}

        data['rune_set'] = data['rune_set'].map(set)



        # # Efficiency


        # Valeur max
        sub = {1: (375 * 5) * 2, # PV flat
            2: 8 * 5,  # PV%
            3: (20 * 5) * 2, #ATQ FLAT 
            4: 8 * 5, #ATQ%
            5:(20 * 5) * 2, #DEF FLAT 
            6: 8 * 5,  # DEF %
            8: 6 * 5, # SPD
            9: 6 * 5, # CRIT
            10: 7 * 5, # DCC
            11: 8 * 5, # RES
            12: 8 * 5} # ACC

        # On map les valeurs max
        data['first_sub_value_max'] = data['first_sub'].map(sub)
        data['second_sub_value_max'] = data['second_sub'].map(sub)
        data['third_sub_value_max'] = data['third_sub'].map(sub)
        data['fourth_sub_value_max'] = data['fourth_sub'].map(sub)
        data['innate_value_max'] = data['innate_type'].replace(sub)


        # Value des runes du joueur ( stats de base + meule )

        data['first_sub_value_total'] = (data['first_sub_value'] + data['first_sub_grinded_value'])
        data['second_sub_value_total'] = (data['second_sub_value'] + data['second_sub_grinded_value'])
        data['third_sub_value_total'] = (data['third_sub_value'] + data['third_sub_grinded_value'])
        data['fourth_sub_value_total'] = (data['fourth_sub_value'] + data['fourth_sub_grinded_value'])
        
        # calcul de l'efficiency (stat de la rune / stat max possible)

        data['efficiency'] = np.where(data['innate_type'] != 0, round(((1+data['innate_value'] / data['innate_value_max']
                                                                        + data['first_sub_value_total'] / data['first_sub_value_max']
                                                                        + data['second_sub_value_total'] / data['second_sub_value_max']
                                                                        + data['third_sub_value_total'] / data['third_sub_value_max']
                                                                        + data['fourth_sub_value_total'] / data['fourth_sub_value_max'])
                                                                       / 2.8)*100,2),
                                    round(((1 + data['first_sub_value_total'] / data['first_sub_value_max']
                                            + data['second_sub_value_total'] / data['second_sub_value_max']
                                            + data['third_sub_value_total'] / data['third_sub_value_max']
                                            + data['fourth_sub_value_total'] / data['fourth_sub_value_max'])
                                           / 2.8)*100,2))


        # on retient ce dont on a besoin
        data = data[['rune_set', 'efficiency']]

        data['efficiency_binned'] = pd.cut(data['efficiency'],bins=(100, 110, 119.99, 129.99), right=False)

        # en dessous de 100, renvoie null, on les enlève.

        data.dropna(inplace=True)



        result = data.groupby(['rune_set', 'efficiency_binned']).count()
        # pas besoin d'un multiindex
        result.reset_index(inplace=True)

        # palier
        palier_1 = result['efficiency_binned'].unique()[0] # '[100.0, 110.0)'
        palier_2 = result['efficiency_binned'].unique()[1] # '[110.0, 120.0)'
        palier_3 = result['efficiency_binned'].unique()[2] # '[120.0, 130.0)'

        # poids des paliers

        poids_palier_1 = 1
        poids_palier_2 = 2
        poids_palier_3 = 3

        result['factor'] = 0
        result['factor'] = np.where(result['efficiency_binned'] == palier_1, poids_palier_1, result['factor'])
        result['factor'] = np.where(result['efficiency_binned'] == palier_2, poids_palier_2, result['factor'])
        result['factor'] = np.where(result['efficiency_binned'] == palier_3, poids_palier_3, result['factor'])
        result['points'] = result['efficiency'] * result['factor']

        # on sépare les dataset à mettre en évidence et les autres

        value_selected = result[result['rune_set'].isin(category_selected)]
        value_autres = result[~result['rune_set'].isin(category_selected)]

        value_selected.drop(['factor'], axis=1, inplace=True)

        coef_set = {'Violent' : 3,
                'Will' : 3,
                'Destroy' : 2,
                'Despair' : 2}

        # on ajoute les poids des sets 

        for set in category_selected:
            value_selected['points'] = np.where(value_selected['rune_set'] == set, value_selected['points'] * coef_set[set], value_selected['points'])
            
            
            
        value_autres = value_autres.groupby('efficiency_binned').sum()
        value_autres.reset_index(inplace=True)
        value_autres.insert(0, 'rune_set', 'Autre')
        value_autres.drop(['factor'], axis=1, inplace=True)

        # on regroupe

        df_value = pd.concat([value_selected, value_autres])

        # on replace pour plus de lisibilité

        df_value['efficiency_binned'] = df_value['efficiency_binned'].replace({palier_1 : 100,
                                                                            palier_2 : 110,
                                                                            palier_3 : 120})

        st.session_state.score = df_value['points'].sum()
        
        
        # Calcul du TCD :

        tcd_value = df_value.pivot_table(df_value, 'rune_set', 'efficiency_binned', 'sum')['efficiency']
        # pas besoin du multiindex
        tcd_value.columns.name = "efficiency"
        tcd_value.index.name = 'Set'
        
        total_100 = tcd_value[100].sum()
        total_110 = tcd_value[110].sum()
        total_120 = tcd_value[120].sum()
        
        tcd_value.loc['Total'] = [total_100, total_110, total_120]


        
        # Enregistrement SQL
        
        tcd_value['Joueur'] = st.session_state['pseudo']
        tcd_value['date'] = date_du_jour()
        
        st.session_state.tcd = tcd_value
        
        sauvegarde_bdd(tcd_value, 'sw', 'append')
        
        df_scoring = pd.DataFrame({'Joueur' : [st.session_state['pseudo']], 'score' : [st.session_state['score']], 'date' : [date_du_jour()]})
        df_scoring.set_index('Joueur', inplace=True)
        
        sauvegarde_bdd(df_scoring, 'sw_score', 'append')
        
        st.subheader(f'Validé pour le joueur {st.session_state["pseudo"]} !')
        st.write('Tu peux désormais aller sur les autres onglets disponibles')
        
        st.session_state['submitted'] = True
        