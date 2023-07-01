
import pandas as pd
import numpy as np
from time import time
from fonctions.gestion_bdd import optimisation_int


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


class Rune():
    def __init__(self, data_json):
        self.data_json = data_json
        self.player_runes = {}
        self.property = {0: 'Aucun',
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
        
        # Valeur max
        sub = {1: (375 * 5) * 2,  # PV flat
               2: 8 * 5,  # PV%
               3: (20 * 5) * 2,  # ATQ FLAT
               4: 8 * 5,  # ATQ%
               5: (20 * 5) * 2,  # DEF FLAT
               6: 8 * 5,  # DEF %
               8: 6 * 5,  # SPD
               9: 6 * 5,  # CRIT
               10: 7 * 5,  # DCC
               11: 8 * 5,  # RES
               12: 8 * 5}  # ACC
        
        self.sub_max_lgd = {1: 550,
                            2: 10,
                            3: 30,
                            4: 10,
                            5: 30,
                            6: 10,
                            8: 5}
        
        self.sub_max_heroique = {1: 450,
                                 2: 7,
                                 3: 22,
                                 4: 7,
                                 5: 22,
                                 6: 7,
                                 8: 4}
        
        self.set = {1: "Energy",
                    2: "Guard",
                    3: "Swift",
                    4: "Blade",
                    5: "Rage",
                    6: "Focus",
                    7: "Endure",
                    8: "Fatal",
                    10: "Despair",
                    11: "Vampire",
                    13: "Violent",
                    14: "Nemesis",
                    15: "Will",
                    16: "Shield",
                    17: "Revenge",
                    18: "Destroy",
                    19: "Fight",
                    20: "Determination",
                    21: "Enhance",
                    22: "Accuracy",
                    23: "Tolerance",
                    24 : "Seal",
                    25 : 'Intangible',
                    99: "Immemorial"}
        
        self.set_to_show = {1: "Energy",
                    2: "Guard",
                    3: "Swift",
                    4: "Blade",
                    5: "Rage",
                    6: "Focus",
                    7: "Endure",
                    8: "Fatal",
                    10: "Despair",
                    11: "Vampire",
                    13: "Violent",
                    14: "Nemesis",
                    15: "Will",
                    16: "Shield",
                    17: "Revenge",
                    18: "Destroy",
                    19: "Fight",
                    20: "Determination",
                    21: "Enhance",
                    22: "Accuracy",
                    23: "Tolerance",
                    24 : "Seal",
                    25 : 'Intangible'}
        
        self.property_grind = {1: 'Meule : HP', # 141
                          2: 'Meule : HP%', # 125
                          3: 'Meule : ATQ',
                          4: 'Meule : ATQ%',
                          5: 'Meule : DEF',
                          6: 'Meule : DEF%',
                          8: "Meule : SPD"}
        
        self.property_grind_gemme = {1: 'Gemme : HP',
                                2: 'Gemme : HP%',
                                3: 'Gemme : ATQ',
                                4: 'Gemme : ATQ%',
                                5: 'Gemme : DEF',
                                6: 'Gemme : DEF%',
                                8: "Gemme : SPD"}
        

        self.gemme_max_lgd = {'HP': 580, 'HP%': 13, 'ATQ': 40, 'ATQ%': 13, 'DEF': 40,
                                'DEF%': 13, 'SPD': 10, 'CRIT': 9, 'DCC': 10, 'RES': 11, 'ACC': 11}
        self.gemme_max_hero = {'HP': 420, 'HP%': 11, 'ATQ': 30, 'ATQ%': 11, 'DEF': 30,
                                'DEF%': 11, 'SPD': 8, 'CRIT': 7, 'DCC': 8, 'RES': 9, 'ACC': 9}
        
        # Inventaire
        for rune in self.data_json['runes']:
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
                self.player_runes[rune_id] = [rune_set, rune_slot, rune_equiped, stars, level, efficiency, max_efficiency,
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

                        self.player_runes[rune_id] = [rune_set, rune_slot, rune_equiped, stars, level, efficiency, max_efficiency,
                                                      max_efficiency_reachable, gain, main_type, main_value, innate_type, innate_value,
                                                      first_sub, first_sub_value, first_gemme_bool, first_sub_grinded_value, second_sub, second_sub_value, second_gemme_bool,
                                                      second_sub_grinded_value, third_sub, third_sub_value, third_gemme_bool, third_sub_grinded_value, fourth_sub,
                                                      fourth_sub_value, fourth_gemme_bool, fourth_sub_grinded_value]

                # on crée un df avec la data

        self.data = pd.DataFrame.from_dict(self.player_runes, orient="index", columns=['rune_set', 'rune_slot', 'rune_equiped', 'stars', 'level', 'efficiency', 'max_efficiency', 'max_efficiency_reachable', 'gain', 'main_type', 'main_value', 'innate_type',
                                                                                       'innate_value', 'first_sub', 'first_sub_value', 'first_gemme_bool', 'first_sub_grinded_value', 'second_sub', 'second_sub_value', 'second_gemme_bool',
                                                                                       'second_sub_grinded_value', 'third_sub', 'third_sub_value', 'third_gemme_bool', 'third_sub_grinded_value', 'fourth_sub',
                                                                                       'fourth_sub_value', 'fourth_gemme_bool', 'fourth_sub_grinded_value'])

        # # Map des sets



        self.data['rune_set'] = self.data['rune_set'].map(self.set)

        # On map les valeurs max
        self.data['first_sub_value_max'] = self.data['first_sub'].map(sub)
        self.data['second_sub_value_max'] = self.data['second_sub'].map(sub)
        self.data['third_sub_value_max'] = self.data['third_sub'].map(sub)
        self.data['fourth_sub_value_max'] = self.data['fourth_sub'].map(sub)
        self.data['innate_value_max'] = self.data['innate_type'].replace(sub)

        # Value des runes du joueur ( stats de base + meule )

        self.data['first_sub_value_total'] = (
            self.data['first_sub_value'] + self.data['first_sub_grinded_value'])
        self.data['second_sub_value_total'] = (
            self.data['second_sub_value'] + self.data['second_sub_grinded_value'])
        self.data['third_sub_value_total'] = (
            self.data['third_sub_value'] + self.data['third_sub_grinded_value'])
        self.data['fourth_sub_value_total'] = (
            self.data['fourth_sub_value'] + self.data['fourth_sub_grinded_value'])

        # calcul de l'efficiency (stat de la rune / stat max possible)

        self.data['efficiency'] = np.where(self.data['innate_type'] != 0, round(((1+self.data['innate_value'] / self.data['innate_value_max']
                                                                                + self.data['first_sub_value_total'] / self.data['first_sub_value_max']
                                                                                + self.data['second_sub_value_total'] / self.data['second_sub_value_max']
                                                                                + self.data['third_sub_value_total'] / self.data['third_sub_value_max']
                                                                                + self.data['fourth_sub_value_total'] / self.data['fourth_sub_value_max'])
                                                                                 / 2.8)*100, 2),
                                           round(((1 + self.data['first_sub_value_total'] / self.data['first_sub_value_max']
                                                   + self.data['second_sub_value_total'] / self.data['second_sub_value_max']
                                                   + self.data['third_sub_value_total'] / self.data['third_sub_value_max']
                                                   + self.data['fourth_sub_value_total'] / self.data['fourth_sub_value_max'])
                                                  / 2.8)*100, 2))
        

        self.data = optimisation_int(self.data, ['int64'])
        # self.data = optimisation_int(self.data, ['float64'], 'float16')
        
        self.set_rune = self.data['rune_set'].unique().tolist()
        self.set_rune.sort()

        self.data_spd = self.data.copy()
        

        def map_stats(df : pd.DataFrame, columns : list):
            '''Transforme les substats numériques en string'''

            df[columns] = df[columns].applymap(lambda x : self.property[x])
                    
            return df
        
        self.data_set = self.data[self.data['level'] >= 12]
        
        self.data_set = map_stats(self.data_set, ['innate_type', 'first_sub', 'second_sub', 'third_sub', 'fourth_sub', 'main_type'])
        
            

    def scoring_rune(self, category_selected, coef_set):
        """Calcule le score général du compte

        Parameters
        ----------
        category_selected : List
            Liste des sets de rune à mettre en évidence
        coef_set : List
            Liste des coefficients à utiliser pour les sets à mettre en évidence

        Returns
        -------
        TCD : DataFrame
            DataFrame des résultats
        Score : Integer
            Scoring
        """
        self.data_r = self.data[['rune_set', 'efficiency']]

        self.data_r['efficiency_binned'] = pd.cut(
            self.data_r['efficiency'], bins=(100, 110, 119.99, 139.99), right=False)

        # en dessous de 100, renvoie null, on les enlève.

        self.data_r.dropna(inplace=True)

        result = self.data_r.groupby(['rune_set', 'efficiency_binned']).count()
        # pas besoin d'un multiindex
        result.reset_index(inplace=True)

        # palier
        palier_1 = result['efficiency_binned'].unique()[0]  # '[100.0, 110.0)'
        palier_2 = result['efficiency_binned'].unique()[1]  # '[110.0, 120.0)'
        palier_3 = result['efficiency_binned'].unique()[2]  # '[120.0, 130.0)'

        # poids des paliers

        palier = {palier_1: 1,
                  palier_2: 2,
                  palier_3: 3}

        result['factor'] = 0

        for key, value in palier.items():
            result['factor'] = np.where(
                result['efficiency_binned'] == key, value, result['factor'])

        result['points'] = result['efficiency'] * result['factor']
        
        # Dans le détail :
        
        self.df_efficiency = result.copy()
        
        self.df_efficiency['efficiency_binned'] = self.df_efficiency['efficiency_binned'].replace({palier_1: 100,
                                                                               palier_2: 110,
                                                                               palier_3: 120})
        
        self.tcd_df_efficiency = self.df_efficiency.pivot_table(
            self.df_efficiency, 'rune_set', 'efficiency_binned', 'sum')['efficiency']
        
        self.tcd_df_efficiency['points'] = self.tcd_df_efficiency.apply(lambda x: (x[100] * 1 + x[110] * 2 + x[120] * 3) * coef_set.get(x.name, 1), axis=1)
        
        total_100 = self.tcd_df_efficiency[100].sum()
        total_110 = self.tcd_df_efficiency[110].sum()
        total_120 = self.tcd_df_efficiency[120].sum()
        total = self.tcd_df_efficiency['points'].sum()

        self.tcd_df_efficiency.loc['Total'] = [total_100, total_110, total_120, total]
        

        

        # on sépare les dataset à mettre en évidence et les autres

        self.value_selected = result[result['rune_set'].isin(
            category_selected)]
        self.value_autres = result[~result['rune_set'].isin(category_selected)]

        self.value_selected.drop(['factor'], axis=1, inplace=True)

        # on ajoute les poids des sets

        for set in category_selected:
            self.value_selected['points'] = np.where(
                self.value_selected['rune_set'] == set, self.value_selected['points'] * coef_set[set], self.value_selected['points'])

        self.value_autres = self.value_autres.groupby(
            'efficiency_binned').sum()
        self.value_autres.reset_index(inplace=True)
        self.value_autres.insert(0, 'rune_set', 'Autre')
        self.value_autres.drop(['factor'], axis=1, inplace=True)

        # on regroupe

        df_value = pd.concat([self.value_selected, self.value_autres])

        # on replace pour plus de lisibilité

        df_value['efficiency_binned'] = df_value['efficiency_binned'].replace({palier_1: 100,
                                                                               palier_2: 110,
                                                                               palier_3: 120})

        self.score_r = df_value['points'].sum()

        # Calcul du TCD :

        self.tcd_value = df_value.pivot_table(
            df_value, 'rune_set', 'efficiency_binned', 'sum')['efficiency']
        # pas besoin du multiindex
        self.tcd_value.columns.name = "efficiency"
        self.tcd_value.index.name = 'Set'

        total_100 = self.tcd_value[100].sum()
        total_110 = self.tcd_value[110].sum()
        total_120 = self.tcd_value[120].sum()

        self.tcd_value.loc['Total'] = [total_100, total_110, total_120]

        return self.tcd_value, self.score_r

    def scoring_spd(self, category_selected_spd, coef_set_spd):
        """Calcule le score speed du compte

        Parameters
        ----------
        category_selected_spd : List
            Liste des sets de rune à mettre en évidence
        coef_set_spd : List
            Liste des coefficients à utiliser pour les sets à mettre en évidence

        Returns
        -------
        TCD : DataFrame
            DataFrame des résultats
        Score : Integer
            Scoring speed
        """

        def detect_speed(df):
            for sub in ['first_sub', 'second_sub', 'third_sub', 'fourth_sub']:
                if df[sub] == 8:  # stat speed = 8
                    df['spd'] = df[f'{sub}_value_total']

            return df

        self.data_spd['spd'] = 0

        self.data_spd = self.data_spd.apply(detect_speed, axis=1)

        self.data_spd = self.data_spd[['rune_set', 'spd']]

        self.data_spd['spd_binned'] = pd.cut(self.data_spd['spd'], 
                                            bins=(23, 26, 29, 32, 36, 40),
                                            right=False)

        self.data_spd.dropna(inplace=True)

        self.result_spd = self.data_spd.groupby(
            ['rune_set', 'spd_binned']).count()

        self.result_spd.reset_index(inplace=True)

        palier_1 = self.result_spd['spd_binned'].unique()[0]  # 23-26
        palier_2 = self.result_spd['spd_binned'].unique()[1]  # 26-29
        palier_3 = self.result_spd['spd_binned'].unique()[2]  # 29-32
        palier_4 = self.result_spd['spd_binned'].unique()[3]  # 32-36
        palier_5 = self.result_spd['spd_binned'].unique()[4]  # 36+

        palier_spd = {palier_1: 1,
                      palier_2: 2,
                      palier_3: 3,
                      palier_4: 4,
                      palier_5: 5}

        self.result_spd['factor_spd'] = 0

        for key, value in palier_spd.items():
            self.result_spd['factor_spd'] = np.where(
                self.result_spd['spd_binned'] == key, value, self.result_spd['factor_spd'])

        self.result_spd['points_spd'] = self.result_spd['spd'] * \
            self.result_spd['factor_spd']

        # on sépare les dataset à mettre en évidence et les autres

        self.value_selected_spd = self.result_spd[self.result_spd['rune_set'].isin(
            category_selected_spd)]
        self.value_autres_spd = self.result_spd[~self.result_spd['rune_set'].isin(
            category_selected_spd)]

        self.value_selected_spd.drop(['factor_spd'], axis=1, inplace=True)

        for set in category_selected_spd:
            self.value_selected_spd['points_spd'] = np.where(
                self.value_selected_spd['rune_set'] == set, self.value_selected_spd['points_spd'] * coef_set_spd[set], self.value_selected_spd['points_spd'])

        self.value_autres_spd = self.value_autres_spd.groupby(
            'spd_binned').sum()
        self.value_autres_spd.reset_index(inplace=True)
        self.value_autres_spd.insert(0, 'rune_set', 'Autre')
        self.value_autres_spd.drop(['factor_spd'], axis=1, inplace=True)

        self.df_value_spd = pd.concat(
            [self.value_selected_spd, self.value_autres_spd])

        # on replace pour plus de lisibilité

        self.df_value_spd['spd_binned'] = self.df_value_spd['spd_binned'].replace({palier_1: '23-25',
                                                                                   palier_2: '26-28',
                                                                                   palier_3: '29-31',
                                                                                   palier_4: '32-35',
                                                                                   palier_5: '36+'})

        self.score_spd = self.df_value_spd['points_spd'].sum()

        self.tcd_value_spd = self.df_value_spd.pivot_table(
            self.df_value_spd, 'rune_set', 'spd_binned', 'sum')['spd']

        # pas besoin du multiindex
        self.tcd_value_spd.columns.name = "spd"
        self.tcd_value_spd.index.name = 'Set'

        total_23_spd = self.tcd_value_spd['23-25'].sum()
        total_26_spd = self.tcd_value_spd['26-28'].sum()
        total_29_spd = self.tcd_value_spd['29-31'].sum()
        total_32_spd = self.tcd_value_spd['32-35'].sum()
        total_36_spd = self.tcd_value_spd['36+'].sum()

        self.tcd_value_spd.loc['Total'] = [
            total_23_spd, total_26_spd, total_29_spd, total_32_spd, total_36_spd]
        
        return self.tcd_value_spd, self.score_spd
    
    def map_stats(self, df : pd.DataFrame, columns : list):
        '''Transforme les substats numériques en string'''

        df[columns] = df[columns].applymap(lambda x : self.property[x])
                
        return df
        
    
    def calcul_value_max(self):

        self.data_max = self.data.copy()
        
        self.data_max = self.data_max[self.data_max['level'] >= 12]
        

        self.data_max = self.map_stats(self.data_max, ['innate_type', 'first_sub', 'second_sub', 'third_sub', 'fourth_sub', 'main_type'])
    
                
        self.data_max['first_sub_value_total'] = (
            self.data_max['first_sub_value'] + self.data_max['first_sub_grinded_value'])
        self.data_max['second_sub_value_total'] = (
            self.data_max['second_sub_value'] + self.data_max['second_sub_grinded_value'])
        self.data_max['third_sub_value_total'] = (
            self.data_max['third_sub_value'] + self.data_max['third_sub_grinded_value'])
        self.data_max['fourth_sub_value_total'] = (
            self.data_max['fourth_sub_value'] + self.data_max['fourth_sub_grinded_value'])

        
                
        def prepare_data(data_max, aggfunc):        
            df_first = pd.pivot_table(data_max, index=['first_sub', 'rune_set'], values='first_sub_value_total', aggfunc=aggfunc).reset_index()
            df_second = pd.pivot_table(data_max, index=['second_sub', 'rune_set'], values='second_sub_value_total', aggfunc=aggfunc).reset_index()
            df_third = pd.pivot_table(data_max, index=['third_sub', 'rune_set'], values='third_sub_value_total', aggfunc=aggfunc).reset_index()
            df_fourth = pd.pivot_table(data_max, index=['fourth_sub', 'rune_set'], values='fourth_sub_value_total', aggfunc=aggfunc).reset_index()

            df_max = df_first.merge(df_second, left_on=['first_sub', 'rune_set'], right_on=['second_sub', 'rune_set'])
            df_max = df_max.merge(df_third, left_on=['first_sub', 'rune_set'], right_on=['third_sub', 'rune_set'])
            df_max = df_max.merge(df_fourth, left_on=['first_sub', 'rune_set'], right_on=['fourth_sub', 'rune_set'])
            
            df_max = df_max[df_max['first_sub'] != 'Aucun']
            

            return df_max
        

        
        # MAX
        
        
        self.df_max = prepare_data(self.data_max, 'max')

            
        self.df_max.drop(['second_sub', 'third_sub', 'fourth_sub'], axis=1, inplace=True)
        
        self.df_max['max_value'] = self.df_max[['first_sub_value_total', 'second_sub_value_total', 'third_sub_value_total', 'fourth_sub_value_total']].max(axis=1)
        self.df_max.rename(columns={'first_sub' : 'substat'}, inplace=True)
        self.df_max.set_index('substat', inplace=True)
        
        self.df_max = self.df_max[['rune_set', 'max_value']]
        



        # AVG

        # NOTE : Cette partie prend trop de temps
        def calcul_avg(data_max, n):
            df_avg = prepare_data(data_max, lambda x: x.nlargest(n).tolist())
            df_avg['value'] = df_avg[['first_sub_value_total', 'second_sub_value_total', 'third_sub_value_total', 'fourth_sub_value_total']].sum(axis=1)
            df_avg[f'top{n}'] = df_avg['value'].apply(lambda liste: np.sort(np.array(liste))[-n:].mean())
            
            if n == 10:
                return df_avg[f'top{n}'].values, df_avg
            
            return df_avg[f'top{n}'].values
        
        
        for i in [5,10,15,25]:
            if i != 10:
                self.df_max[f'top{i}'] = calcul_avg(self.data_max, i)
            else:
                self.df_max[f'top{i}'], self.df_best_value = calcul_avg(self.data_max, i)
        
        
        self.df_max = optimisation_int(self.df_max, ['int64'])
        
        self.df_best_value = self.df_best_value[['first_sub', 'rune_set', 'value']]
        
        def fill_value(x):
            long = len(x)
            if long < 10:
                for i in range(10-long): 
                    x.append(0) 
            return x
        
        self.df_best_value['value'] = self.df_best_value['value'].apply(fill_value)
        self.df_best_value[f'value'] = self.df_best_value['value'].apply(lambda liste: np.sort(np.array(liste))[-10:])
        

        self.df_best_value[['10', '9', '8', '7', '6', '5', '4', '3', '2', '1']] = self.df_best_value['value'].apply(lambda x: pd.Series(list(x))) 
        
        
        
        self.df_best_value.drop(['value'], axis=1, inplace=True)
        self.df_best_value.rename(columns={'first_sub' : 'substat'}, inplace=True)

        
        self.df_best_value = optimisation_int(self.df_best_value, ['int64'])
        
       
        self.df_max = self.df_max.reset_index().merge(self.df_best_value, on=['substat', 'rune_set'])

        self.df_max.set_index('substat', inplace=True)

        
        return self.df_max
    
    
    def calcul_potentiel(self):
        '''Calcul du potentiel max de chaque rune'''
        self.data_grind = self.data.copy()
        
        self.data_grind = self.data_grind[self.data_grind['level'] > 11]
        self.data_grind = self.data_grind[self.data_grind['stars'] > 5]
        


    # Certaines stats ne sont pas meulables. On remplace donc le potentiel de meule par 0

        dict = {'first_grind_value_max': 'first_sub', 'second_grind_value_max': 'second_sub',
                'third_grind_value_max': 'third_sub', 'fourth_grind_value_max': 'fourth_sub'}
        
        for key, value in dict.items():

            self.data_grind[key + '_lgd'] = self.data_grind[value].replace(self.sub_max_lgd)
            self.data_grind[key + '_hero'] = self.data_grind[value].replace(self.sub_max_heroique)

            # Certaines stats ne sont pas meulables. On remplace donc le potentiel de meule par 0

            self.data_grind[key + "_lgd"] = np.where(self.data_grind[value]
                                          > 8, 0,  self.data_grind[key + "_lgd"])
            self.data_grind[key + "_hero"] = np.where(self.data_grind[value]
                                           > 8, 0, self.data_grind[key + "_hero"])
            
            
        # Value stats de base + meule (max)

        self.data_grind['first_sub_value_total_max_lgd'] = (
            self.data_grind['first_sub_value'] + self.data_grind['first_grind_value_max_lgd'])
        self.data_grind['second_sub_value_total_max_lgd'] = (
            self.data_grind['second_sub_value'] + self.data_grind['second_grind_value_max_lgd'])
        self.data_grind['third_sub_value_total_max_lgd'] = (
            self.data_grind['third_sub_value'] + self.data_grind['third_grind_value_max_lgd'])
        self.data_grind['fourth_sub_value_total_max_lgd'] = (
            self.data_grind['fourth_sub_value'] + self.data_grind['fourth_grind_value_max_lgd'])

        self.data_grind['first_sub_value_total_max_hero'] = (
            self.data_grind['first_sub_value'] + self.data_grind['first_grind_value_max_hero'])
        self.data_grind['second_sub_value_total_max_hero'] = (
            self.data_grind['second_sub_value'] + self.data_grind['second_grind_value_max_hero'])
        self.data_grind['third_sub_value_total_max_hero'] = (
            self.data_grind['third_sub_value'] + self.data_grind['third_grind_value_max_hero'])
        self.data_grind['fourth_sub_value_total_max_hero'] = (
            self.data_grind['fourth_sub_value'] + self.data_grind['fourth_grind_value_max_hero'])

        self.data_grind['efficiency_max_lgd'] = np.where(self.data_grind['innate_type'] != 0,
                                            round(((1+self.data_grind['innate_value'] / self.data_grind['innate_value_max']
                                                    + self.data_grind['first_sub_value_total_max_lgd'] / self.data_grind['first_sub_value_max']
                                                    + self.data_grind['second_sub_value_total_max_lgd'] / self.data_grind['second_sub_value_max']
                                                    + self.data_grind['third_sub_value_total_max_lgd'] / self.data_grind['third_sub_value_max']
                                                    + self.data_grind['fourth_sub_value_total_max_lgd'] / self.data_grind['fourth_sub_value_max'])
                                                    / 2.8)*100, 2),
                                            round(((1 + self.data_grind['first_sub_value_total_max_lgd'] / self.data_grind['first_sub_value_max']
                                                    + self.data_grind['second_sub_value_total_max_lgd'] / self.data_grind['second_sub_value_max']
                                                    + self.data_grind['third_sub_value_total_max_lgd'] / self.data_grind['third_sub_value_max']
                                                    + self.data_grind['fourth_sub_value_total_max_lgd'] / self.data_grind['fourth_sub_value_max'])
                                                    / 2.8)*100, 2))


        self.data_grind['efficiency_max_hero'] = np.where(self.data_grind['innate_type'] != 0,
                                            round(((1+self.data_grind['innate_value'] / self.data_grind['innate_value_max']
                                                    + self.data_grind['first_sub_value_total_max_hero'] / self.data_grind['first_sub_value_max']
                                                    + self.data_grind['second_sub_value_total_max_hero'] / self.data_grind['second_sub_value_max']
                                                    + self.data_grind['third_sub_value_total_max_hero'] / self.data_grind['third_sub_value_max']
                                                    + self.data_grind['fourth_sub_value_total_max_hero'] / self.data_grind['fourth_sub_value_max'])
                                                    / 2.8)*100, 2),
                                            round(((1 + self.data_grind['first_sub_value_total_max_hero'] / self.data_grind['first_sub_value_max']
                                                    + self.data_grind['second_sub_value_total_max_hero'] / self.data_grind['second_sub_value_max']
                                                    + self.data_grind['third_sub_value_total_max_hero'] / self.data_grind['third_sub_value_max']
                                                    + self.data_grind['fourth_sub_value_total_max_hero'] / self.data_grind['fourth_sub_value_max'])
                                                    / 2.8)*100, 2))

        self.data_grind['potentiel_max_lgd'] = self.data_grind['efficiency_max_lgd'] - self.data_grind['efficiency']

        self.data_grind['potentiel_max_hero'] = self.data_grind['efficiency_max_hero'] - self.data_grind['efficiency']
        


        self.data_grind.drop(['max_efficiency', 'max_efficiency_reachable',
                'gain'], axis=1, inplace=True)

        # # Map
        # ## Propriété
        # Plus simple ici qu'avant



        for c in ['innate_type', 'first_sub', 'second_sub', 'third_sub', 'fourth_sub', 'main_type']:
            self.data_grind[c] = self.data_grind[c].map(self.property)
            
        self.data_grind = optimisation_int(self.data_grind, ['int64'])
        # self.data_grind = optimisation_int(self.data_grind, ['float64'], 'float16')
            
            
    def identify_monsters(self, monsters:dict, data='data_grind'):
        '''Compatible avec data_grind
        
        data est le nom du df à modifier : [data, data_grind]
        
        Remplace les id des monstres par leurs noms'''

        if data == 'data_grind':
            self.data_grind['rune_equiped'] = self.data_grind['rune_equiped'].replace(monsters)
        elif data == 'data':
            self.data['rune_equiped'] = self.data['rune_equiped'].replace(monsters)
        
        
    def grind(self):
        '''Compatible avec data_grind
        
        Identifie les grinds potentiels et les commentaires'''    
        
        self.data_grind['indicateurs_level'] = (self.data_grind['level'] == 15).astype(
                'int')  # Si 15 -> 1. Sinon 0

            # # Amélioration des Grind

        dict = {'amelioration_first_grind': ['first_sub_grinded_value', 'first_grind_value'],
                    'amelioration_second_grind': ['second_sub_grinded_value', 'second_grind_value'],
                    'amelioration_third_grind': ['third_sub_grinded_value', 'third_grind_value'],
                    'amelioration_fourth_grind': ['fourth_sub_grinded_value', 'fourth_grind_value']}


        for key, value in dict.items():
                    # Améliorable ? (valeur)
            self.data_grind[key + '_lgd_value'] = self.data_grind[value[1] +
                                                    '_max_lgd'] - self.data_grind[value[0]]
            self.data_grind[key + '_hero_value'] = self.data_grind[value[1] +
                                                    '_max_hero'] - self.data_grind[value[0]]
                    # Améliorable ? (bool)
            self.data_grind[key +
                        '_lgd_ameliorable?'] = (self.data_grind[key + '_lgd_value'] > 0).astype('int')
            self.data_grind[key +
                        '_hero_ameliorable?'] = (self.data_grind[key + '_hero_value'] > 0).astype('int')


        # # Commentaires

   
                # Level
        self.data_grind['Commentaires'] = np.where(
                    self.data_grind['level'] != 15, "A monter +15 \n", "")
        calcul_gemme = self.data_grind['first_gemme_bool'] + self.data_grind['second_gemme_bool'] + \
                    self.data_grind['third_gemme_bool'] + self.data_grind['fourth_gemme_bool']
        self.data_grind['Commentaires'] = np.where(
                    calcul_gemme == 0, self.data_grind['Commentaires'] + "Pas de gemme utilisée", self.data_grind['Commentaires'])
        
        
        # Grind
        self.data_grind['Grind_lgd'] = ""
        self.data_grind['Grind_hero'] = ""

        dict = {'amelioration_first_grind': 'first_sub',
                        'amelioration_second_grind': 'second_sub',
                        'amelioration_third_grind': 'third_sub',
                        'amelioration_fourth_grind': 'fourth_sub'}

        # meule

        for key, value in dict.items():
            nom = key + "_lgd_value"
            self.data_grind['Grind_lgd'] = np.where(self.data_grind[key + '_lgd_ameliorable?'] == 1, self.data_grind['Grind_lgd'] +
                                                "Meule : " + self.data_grind[value] + "(" + self.data_grind[nom].astype('str') + ") \n", self.data_grind['Grind_lgd'])

            nom = key + "_hero_value"
            self.data_grind['Grind_hero'] = np.where(self.data_grind[key + '_hero_ameliorable?'] == 1, self.data_grind['Grind_hero'] +
                                                "Meule : " + self.data_grind[value] + "(" + self.data_grind[nom].astype('str') + ") \n", self.data_grind['Grind_hero'])

        # gemme

        # sub des gemmes



        # On les inclut au dataframe

        self.data_grind['first_gemme_max_lgd'] = self.data_grind['first_sub'].map(self.gemme_max_lgd)
        self.data_grind['second_gemme_max_lgd'] = self.data_grind['second_sub'].map(self.gemme_max_lgd)
        self.data_grind['third_gemme_max_lgd'] = self.data_grind['third_sub'].map(self.gemme_max_lgd)
        self.data_grind['fourth_gemme_max_lgd'] = self.data_grind['fourth_sub'].map(self.gemme_max_lgd)

        self.data_grind['first_gemme_max_hero'] = self.data_grind['first_sub'].map(self.gemme_max_hero)
        self.data_grind['second_gemme_max_hero'] = self.data_grind['second_sub'].map(self.gemme_max_hero)
        self.data_grind['third_gemme_max_hero'] = self.data_grind['third_sub'].map(self.gemme_max_hero)
        self.data_grind['fourth_gemme_max_hero'] = self.data_grind['fourth_sub'].map(self.gemme_max_hero)

        dict2 = {'first_gemme': 'first_sub',
                        'second_gemme': 'second_sub',
                        'third_gemme': 'third_sub',
                        'fourth_gemme': 'fourth_sub'}

                # On fait le calcul :

        for key, sub in dict2.items():

            condition = self.data_grind[key + '_bool'] == 1  # si 1 -> gemme utilisée
                # différence entre le max et la gemme
            calcul_lgd = self.data_grind[key + '_max_lgd'] - self.data_grind[sub + '_value']
                # différence entre le max et la gemme
            calcul_hero = self.data_grind[key + '_max_hero'] - self.data_grind[sub + '_value']
            condition_lgd = calcul_lgd > 0  # s'il y a un écart, ce n'est pas la stat max
            condition_hero = calcul_hero > 0

            self.data_grind['Grind_lgd'] = np.where(condition,
                                                np.where(condition_lgd,
                                                        self.data_grind['Grind_lgd'] + "Gemme : " + self.data_grind[sub] +
                                                        "(" + calcul_lgd.astype('str') + ")",
                                                        self.data_grind['Grind_lgd']),
                                                self.data_grind['Grind_lgd'])
            self.data_grind['Grind_hero'] = np.where(condition,
                                                np.where(condition_hero,
                                                        self.data_grind['Grind_hero'] + "Gemme : " + self.data_grind[sub] +
                                                        "(" + calcul_hero.astype('str') + ")",
                                                        self.data_grind['Grind_hero']),
                                                self.data_grind['Grind_hero'])
            
        self.data_grind.drop(['stars', 'level'], axis=1, inplace=True)

        self.data_short = self.data_grind[['rune_set', 'rune_slot', 'rune_equiped', 'efficiency', 'efficiency_max_hero',
                       'efficiency_max_lgd', 'potentiel_max_lgd', 'potentiel_max_hero', 'Commentaires', 'Grind_lgd', 'Grind_hero']]
        
        self.data_grind = optimisation_int(self.data_grind, ['int64'])
        self.data_short = optimisation_int(self.data_short, ['int64'])
        
        
    def count_meules_manquantes(self):
        '''Calcule le nombre de meules manquantes'''


        list_property_type = []
        list_property_count = []

        for propriete in self.property_grind.values():

            count = self.data_grind['Grind_hero'].str.count(propriete).sum()


            list_property_type.append(propriete)
            list_property_count.append(count)


        for propriete in self.property_grind_gemme.values():
            count = self.data_grind['Grind_hero'].str.count(propriete).sum()

            list_property_type.append(propriete)
            list_property_count.append(count)

        self.df_meule_manquante = pd.DataFrame(
            [list_property_type, list_property_count]).transpose()
        self.df_meule_manquante = self.df_meule_manquante.rename(columns={
                                         0: 'Propriété', 1: 'Meules/Gemmes (hero) manquantes pour atteindre la stat max'})
        
    def count_rune_with_potentiel_left(self):
        '''Compte le nombre de runes qui peut encore être améliorés'''
        
        dict_rune = {}
        list_type = []
        list_count = []
        list_propriete = []
        list_propriete_gemmes = []
        list_count_gemmes = []

        self.set = {1: "Energy", 2: "Guard", 3: "Swift", 4: "Blade", 5: "Rage", 6: "Focus", 7: "Endure", 8: "Fatal", 10: "Despair", 11: "Vampire", 13: "Violent",
            14: "Nemesis", 15: "Will", 16: "Shield", 17: "Revenge", 18: "Destroy", 19: "Fight", 20: "Determination", 21: "Enhance", 22: "Accuracy", 23: "Tolerance", 99: "Immemorial"}

        for type_rune in self.set.values():
            for propriete in self.property_grind.values():
                data_type_rune = self.data_grind[self.data_grind['rune_set'] == type_rune]
                nb_rune = self.data_grind[self.data_grind['rune_set'] == type_rune].count().max()
                count = data_type_rune['Grind_hero'].str.count(propriete).sum()
                

                dict_rune[type_rune] = nb_rune

                list_type.append(type_rune)
                list_count.append(count)
                list_propriete.append(propriete)

                self.df_rune = pd.DataFrame.from_dict(
                    dict_rune, orient='index', columns=['Nombre de runes'])

            for propriete in self.property_grind_gemme.values():
                data_type_rune = self.data_grind[self.data_grind['rune_set'] == type_rune]
                nb_rune = self.data_grind[self.data_grind['rune_set'] == type_rune].count().max()
                count = data_type_rune['Grind_hero'].str.count(propriete).sum()

                # list_type.append(type_rune)
                list_count_gemmes.append(count)
                list_propriete_gemmes.append(propriete)

        self.df_count = pd.DataFrame([list_type, list_propriete, list_count,
                                list_propriete_gemmes, list_count_gemmes]).transpose()
        self.df_count = self.df_count.rename(columns={0: 'Set', 1: 'Propriété Meules',
                                   2: 'Meules (hero) manquantes pour la stat max', 3: 'Propriété Gemmes', 4: 'Gemmes (hero) manquantes'})
        
        
        self.df_count = optimisation_int(self.df_count, ['int64'])
        
        
    def calcul_efficiency_describe(self):
        self.data_avg_efficiency : pd.DataFrame = self.data.groupby('rune_set').agg({'efficiency' : ['mean', 'max', 'median', 'count']})
        self.data_avg_efficiency = self.data_avg_efficiency.droplevel(level=0, axis=1)
        self.data_avg_efficiency = self.data_avg_efficiency.rename(columns={'mean' : 'moyenne',
                                                            'median' : 'mediane',
                                                            'count' : 'Nombre runes'})
        
        self.data_avg_efficiency = optimisation_int(self.data_avg_efficiency, ['int64'])
        # self.data_avg_efficiency = optimisation_int(self.data_avg_efficiency, ['float64'], 'float16')
        return self.data_avg_efficiency
        

    def calcul_efficiency_describe_top(self, top : int=25): # TODO : A tester
        self.data_avg_asc : pd.DataFrame = self.data.sort_values(by='efficiency', ascending=False)
        
        a = time()
        data_avg_top = self.data_avg_asc.groupby('type_rune')['efficience'].nlargest(top).reset_index()
        
        print(data_avg_top)
        
        data_avg_top_avg = data_avg_top.groupby('type_rune')['efficience'].mean().reset_index()
        
        print(data_avg_top_avg)
        
        print(time()-a)
        
        

        
    def count_per_slot(self):
        """On compte par set et par slot le nombre de runes ayant la même valeur en substat"""

        self.data_per_slot = self.data.copy()
        
        self.data_per_slot = self.data_per_slot[self.data_per_slot['level'] >= 12]
        
        self.data_per_slot = self.map_stats(self.data_per_slot, ['first_sub', 'second_sub', 'third_sub', 'fourth_sub'])
                   
        self.data_per_slot['first_sub_value_total'] = (
            self.data_per_slot['first_sub_value'] + self.data_per_slot['first_sub_grinded_value'])
        self.data_per_slot['second_sub_value_total'] = (
            self.data_per_slot['second_sub_value'] + self.data_per_slot['second_sub_grinded_value'])
        self.data_per_slot['third_sub_value_total'] = (
            self.data_per_slot['third_sub_value'] + self.data_per_slot['third_sub_grinded_value'])
        self.data_per_slot['fourth_sub_value_total'] = (
            self.data_per_slot['fourth_sub_value'] + self.data_per_slot['fourth_sub_grinded_value'])

                
        def prepare_data(data_max, aggfunc):        
            df_first = pd.pivot_table(data_max, index=['first_sub', 'rune_set', 'rune_slot', 'first_sub_value_total'], values='first_sub_value', aggfunc=aggfunc).reset_index()
            df_second = pd.pivot_table(data_max, index=['second_sub', 'rune_set', 'rune_slot', 'second_sub_value_total'], values='second_sub_value', aggfunc=aggfunc).reset_index()
            df_third = pd.pivot_table(data_max, index=['third_sub', 'rune_set', 'rune_slot', 'third_sub_value_total'], values='third_sub_value', aggfunc=aggfunc).reset_index()
            df_fourth = pd.pivot_table(data_max, index=['fourth_sub', 'rune_set', 'rune_slot', 'fourth_sub_value_total'], values='fourth_sub_value', aggfunc=aggfunc).reset_index()

            df_per_slot = df_first.merge(df_second, left_on=['first_sub', 'rune_set', 'rune_slot', 'first_sub_value_total'], right_on=['second_sub', 'rune_set', 'rune_slot', 'second_sub_value_total'], how='outer')

            df_per_slot = df_per_slot.merge(df_third, left_on=['first_sub', 'rune_set', 'rune_slot', 'first_sub_value_total'], right_on=['third_sub', 'rune_set', 'rune_slot', 'third_sub_value_total'], how='outer')

            df_per_slot = df_per_slot.merge(df_fourth, left_on=['first_sub', 'rune_set', 'rune_slot', 'first_sub_value_total'], right_on=['fourth_sub', 'rune_set', 'rune_slot', 'fourth_sub_value_total'], how='outer')

            df_per_slot = df_per_slot[df_per_slot['first_sub'] != 'Aucun']
            

            return df_per_slot
        
        
        self.data_per_slot = prepare_data(self.data_per_slot, 'count')
        
        self.data_per_slot.drop(['second_sub', 'third_sub', 'fourth_sub', 'second_sub_value_total', 'third_sub_value_total', 'fourth_sub_value_total'], axis=1, inplace=True)
        
        # Si on a pas de rune avec la valeur pour le slot et le set, on met 0
        
        self.data_per_slot.fillna(0, inplace=True)
        
        # on fait le total
        
        self.data_per_slot['count'] = self.data_per_slot['first_sub_value'] + self.data_per_slot['second_sub_value'] + self.data_per_slot['third_sub_value'] + self.data_per_slot['fourth_sub_value']
        
        # Maintenant qu'on a le total, on peut supprimer les colonnes inutiles
        
        self.data_per_slot.drop(['first_sub_value', 'second_sub_value', 'third_sub_value', 'fourth_sub_value'], axis=1, inplace=True)
        
        return self.data_per_slot
        
    def count_efficience_per_slot(self):
        """On compte par set et par slot le nombre de runes ayant la même valeur en substat"""

        self.eff_per_slot = self.data.copy()
        
        self.eff_per_slot['efficiency'].fillna(0, inplace=True) # les runes pas montées n'ont pas été calculés
        
        
        return self.eff_per_slot[['rune_set', 'rune_slot', 'efficiency']]
        
        