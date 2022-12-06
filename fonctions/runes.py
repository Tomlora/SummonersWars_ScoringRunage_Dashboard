
import pandas as pd
import numpy as np


class Rune():
    def __init__(self, data_json):
        self.data_json = data_json
        self.player_runes = {}
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

        self.set = {1: "Energy", 2: "Guard", 3: "Swift", 4: "Blade", 5: "Rage",
                    6: "Focus", 7: "Endure", 8: "Fatal", 10: "Despair", 11: "Vampire", 13: "Violent",
                    14: "Nemesis", 15: "Will", 16: "Shield", 17: "Revenge", 18: "Destroy", 19: "Fight",
                    20: "Determination", 21: "Enhance", 22: "Accuracy", 23: "Tolerance", 99: "Immemorial"}

        self.data['rune_set'] = self.data['rune_set'].map(self.set)

        # # Efficiency

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

        self.data_spd = self.data.copy()

    def scoring_rune(self, category_selected, coef_set):
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

        def detect_speed(df):
            for sub in ['first_sub', 'second_sub', 'third_sub', 'fourth_sub']:
                if df[sub] == 8:  # stat speed = 8
                    df['spd'] = df[f'{sub}_value_total']

            return df

        self.data_spd['spd'] = 0

        self.data_spd = self.data_spd.apply(detect_speed, axis=1)

        self.data_spd = self.data_spd[['rune_set', 'spd']]

        self.data_spd['spd_binned'] = pd.cut(
            self.data_spd['spd'], bins=(23, 26, 29, 32, 36, 40), right=False)

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
        self.tcd_value_spd .columns.name = "spd"
        self.tcd_value_spd .index.name = 'Set'

        total_23_spd = self.tcd_value_spd['23-25'].sum()
        total_26_spd = self.tcd_value_spd['26-28'].sum()
        total_29_spd = self.tcd_value_spd['29-31'].sum()
        total_32_spd = self.tcd_value_spd['32-35'].sum()
        total_36_spd = self.tcd_value_spd['36+'].sum()

        self.tcd_value_spd.loc['Total'] = [
            total_23_spd, total_26_spd, total_29_spd, total_32_spd, total_36_spd]

        return self.tcd_value_spd, self.score_spd
