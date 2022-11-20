import pandas as pd
import numpy as np

dict_arte_type = {
        1: 'ELEMENT',
        2: 'ARCHETYPE',
    }

dict_arte_effect = {
        200: {'name' : 'EFFECT_ATK_LOST_HP', 'max' : 14},
        201: {'name' : 'EFFECT_DEF_LOST_HP', 'max' : 14},
        202: {'name' : 'EFFECT_SPD_LOST_HP', 'max' : 14},
        203: {'name' : 'EFFECT_SPD_INABILITY', 'max' : 6},
        204: {'name' : 'EFFECT_ATK', 'max' : 5},
        205: {'name' : 'EFFECT_DEF', 'max' : 4},
        206: {'name' : 'EFFECT_SPD', 'max' : 6},
        207: {'name' : 'EFFECT_CRIT_RATE', 'max' : 6},
        208: {'name' : 'EFFECT_COUNTER_DMG', 'max' : 4},
        209: {'name' : 'EFFECT_COOP_ATTACK_DMG', 'max' : 4},
        210: {'name' : 'EFFECT_BOMB_DMG', 'max' : 4},
        211: {'name' : 'EFFECT_REFLECT_DMG', 'max' : 3},
        212: {'name' : 'EFFECT_CRUSHING_HIT_DMG', 'max' : 4},
        213: {'name' : 'EFFECT_DMG_RECEIVED_INABILITY', 'max' : 3},
        214: {'name' : 'EFFECT_CRIT_DMG_RECEIVED', 'max' : 4},
        215: {'name' : 'EFFECT_LIFE_DRAIN', 'max' : 8},
        216: {'name' : 'EFFECT_HP_REVIVE', 'max' : 6},
        217: {'name' : 'EFFECT_ATB_REVIVE', 'max' : 6},
        218: {'name' : 'EFFECT_DMG_PCT_OF_HP', 'max' : 0.3},
        219: {'name' : 'EFFECT_DMG_PCT_OF_ATK', 'max' : 4},
        220: {'name' : 'EFFECT_DMG_PCT_OF_DEF', 'max' : 4},
        221: {'name' : 'EFFECT_DMG_PCT_OF_SPD', 'max' : 40},
        222: {'name' : 'EFFECT_CRIT_DMG_UP_ENEMY_HP_GOOD', 'max' : 6},
        223: {'name' : 'EFFECT_CRIT_DMG_UP_ENEMY_HP_BAD', 'max' : 12},
        224: {'name' : 'EFFECT_CRIT_DMG_SINGLE_TARGET', 'max' : 4},
        300: {'name' : 'EFFECT_DMG_TO_FIRE', 'max' : 5},
        301: {'name' : 'EFFECT_DMG_TO_WATER', 'max' : 5},
        302: {'name' : 'EFFECT_DMG_TO_WIND', 'max' : 5},
        303: {'name' : 'EFFECT_DMG_TO_LIGHT', 'max' : 5},
        304: {'name' : 'EFFECT_DMG_TO_DARK', 'max' : 5},
        305: {'name' : 'EFFECT_DMG_FROM_FIRE', 'max' : 6},
        306: {'name' : 'EFFECT_DMG_FROM_WATER', 'max' : 6},
        307: {'name' : 'EFFECT_DMG_FROM_WIND', 'max' : 6},
        308: {'name' : 'EFFECT_DMG_FROM_LIGHT', 'max' : 6},
        309: {'name' : 'EFFECT_DMG_FROM_DARK', 'max' : 6},
        400: {'name' : 'EFFECT_SK1_CRIT_DMG', 'max' : 6},
        401: {'name' : 'EFFECT_SK2_CRIT_DMG', 'max' : 6},
        402: {'name' : 'EFFECT_SK3_CRIT_DMG', 'max' : 6},
        403: {'name' : 'EFFECT_SK4_CRIT_DMG', 'max' : 6},
        404: {'name' : 'EFFECT_SK1_RECOVERY', 'max' : 6},
        405: {'name' : 'EFFECT_SK2_RECOVERY', 'max' : 6},
        406: {'name' : 'EFFECT_SK3_RECOVERY', 'max' : 6},
        407: {'name' : 'EFFECT_SK1_ACCURACY', 'max' : 6},
        408: {'name' : 'EFFECT_SK2_ACCURACY', 'max' : 6},
        409: {'name' : 'EFFECT_SK3_ACCURACY', 'max' : 6},
    }

dict_arte_archetype = {
        0: 'ARCHETYPE_NONE',
        1: 'ARCHETYPE_ATTACK',
        2: 'ARCHETYPE_DEFENSE',
        3: 'ARCHETYPE_HP',
        4: 'ARCHETYPE_SUPPORT',
        5: 'ARCHETYPE_MATERIAL'
    }

dict_arte_main_stat = {
        100: 'HP',
        101: 'ATK',
        102: 'DEF',
    }




class Artefact():
    def __init__(self, data_json):
        self.data_json = data_json
        self.player_arte = {}
        for arte in self.data_json['artifacts']:
            first_sub = 0
            first_sub_value = 0
            second_sub = 0
            second_sub_value = 0
            third_sub = 0
            third_sub_value = 0
            fourth_sub = 0
            fourth_sub_value = 0

            arte_id = arte['rid']
            arte_type = arte['type']
            arte_attribut = arte['attribute']
            arte_equiped = arte['occupied_id']
            level = arte['level']
            efficiency = 0

            main_type = arte['pri_effect'][0]
            main_value = arte['pri_effect'][1]


            if level > 2:
                first_sub = arte['sec_effects'][0][0]
                first_sub_value = arte['sec_effects'][0][1]

            if level > 5:
                second_sub = arte['sec_effects'][1][0]
                second_sub_value = arte['sec_effects'][1][1]

            if level > 8:
                third_sub = arte['sec_effects'][2][0]
                third_sub_value = arte['sec_effects'][2][1]

            if level > 11:
                fourth_sub = arte['sec_effects'][3][0]
                fourth_sub_value = arte['sec_effects'][3][1]

            self.player_arte[arte_id] =  [arte_type, arte_attribut, arte_equiped, level, efficiency,
                                    main_type, main_value, 
                                    first_sub, first_sub_value, second_sub, second_sub_value, third_sub, third_sub_value,
                                    fourth_sub, fourth_sub_value ]

        # arte équipée
        for unit in self.data_json['unit_list']:
            for stat in unit:
                if stat == "artifacts":
                    for arte in unit[stat]:
                        first_sub = 0
                        first_sub_value = 0

                        second_sub = 0
                        second_sub_value = 0

                        third_sub = 0
                        third_sub_value = 0

                        fourth_sub = 0
                        fourth_sub_value = 0


                        arte_id = arte['rid']
        
                        arte_type = arte['type']
                        arte_attribut = arte['attribute']
                        arte_equiped = arte['occupied_id']

                        level = arte['level']
                        efficiency = 0

                        main_type = arte['pri_effect'][0]
                        main_value = arte['pri_effect'][1]

                        # rank = arte['extra']
                        if level > 2:
                            first_sub = arte['sec_effects'][0][0]
                            first_sub_value = arte['sec_effects'][0][1]

                        if level > 5:
                            second_sub = arte['sec_effects'][1][0]
                            second_sub_value = arte['sec_effects'][1][1]

                        if level > 8:
                            third_sub = arte['sec_effects'][2][0]
                            third_sub_value = arte['sec_effects'][2][1]

                        if level > 11:
                            fourth_sub = arte['sec_effects'][3][0]
                            fourth_sub_value = arte['sec_effects'][3][1]

                        self.player_arte[arte_id] =  [arte_type, arte_attribut, arte_equiped, level, efficiency,
                                    main_type, main_value,
                                    first_sub, first_sub_value, second_sub, second_sub_value,
                                    third_sub, third_sub_value, fourth_sub, fourth_sub_value]
                        
        self.data_a = pd.DataFrame.from_dict(self.player_arte, orient="index", columns=['arte_type', 'arte_attribut', 'arte_equiped', 'level', 'efficiency', 'main_type', 'main_value', 
                                                                            'first_sub', 'first_sub_value',  'second_sub', 'second_sub_value',
                                                                            'third_sub', 'third_sub_value', 
                                                                            'fourth_sub','fourth_sub_value'])
        
        # on prend que les arté montés

        self.data_a = self.data_a[self.data_a['level'] == 15]
        
        # on map les identifiants par les mots pour plus de lisibilités

        self.data_a['arte_type'] = self.data_a['arte_type'].map(dict_arte_type)
        self.data_a['arte_attribut'] = self.data_a['arte_attribut'].map(dict_arte_archetype)
        self.data_a['main_type'] = self.data_a['main_type'].map(dict_arte_main_stat)

        def value_max(x):
                return dict_arte_effect[x]['max'] # first proc + 4 upgrades

        def replace_effect(x):
                return dict_arte_effect[x]['name']
                


        for c in ['first_sub', 'second_sub', 'third_sub', 'fourth_sub']:
                self.data_a[f'{c}_value_max'] = self.data_a[c].apply(value_max)
                self.data_a[c] = self.data_a[c].apply(replace_effect)
                
        self.data_a['efficiency'] = round(((self.data_a['first_sub_value'] / self.data_a['first_sub_value_max']
                                            + self.data_a['second_sub_value'] / self.data_a['second_sub_value_max']
                                            + self.data_a['third_sub_value'] / self.data_a['third_sub_value_max']
                                            + self.data_a['fourth_sub_value'] / self.data_a['fourth_sub_value_max'])
                                           / 8)*100,2)
        
    def scoring_arte(self):
        self.data_eff = self.data_a[['efficiency', 'arte_type', 'main_type']]

        self.data_eff['eff_binned'] = pd.cut(self.data_eff['efficiency'],bins=(80, 85, 90, 95, 100, 120), right=False)

        self.data_eff.dropna(inplace=True)

        self.data_eff = self.data_eff.groupby(['eff_binned', 'arte_type', 'main_type']).count()

        self.data_eff.reset_index(inplace=True)

        palier_1 = self.data_eff['eff_binned'].unique()[0] # 80-85
        palier_2 = self.data_eff['eff_binned'].unique()[1] # 85-90
        palier_3 = self.data_eff['eff_binned'].unique()[2] # 90-95
        palier_4 = self.data_eff['eff_binned'].unique()[3] # 95-100
        palier_5 = self.data_eff['eff_binned'].unique()[4] # 100+

        palier_arte = {palier_1 : 1,
                    palier_2 : 2,
                    palier_3 : 3,
                    palier_4 : 4,
                    palier_5 : 5}

        self.data_eff['factor'] = 0
                
        for key, value in palier_arte.items():
            self.data_eff['factor'] = np.where(self.data_eff['eff_binned'] == key, value, self.data_eff['factor'])

        self.data_eff['points'] = self.data_eff['efficiency'] * self.data_eff['factor']

        self.data_eff.drop(['factor'], axis=1, inplace=True)
        
        self.data_eff['eff_binned'] = self.data_eff['eff_binned'].replace({palier_1 : '80',
                                                                            palier_2 : '85',
                                                                            palier_3 : '90',
                                                                            palier_4 : '95',
                                                                            palier_5 : '100+'})

        self.score_a = self.data_eff['points'].sum()
                
                
                # Calcul du TCD :

        self.tcd_arte = self.data_eff.pivot_table(self.data_eff, ['arte_type', 'main_type'], 'eff_binned', 'sum')['efficiency']
                # pas besoin du multiindex
        self.tcd_arte.columns.name = "efficiency"
        self.tcd_arte.index.name = 'Artefact'
        
        self.tcd_arte.reset_index(inplace=True)
        self.tcd_arte.set_index('arte_type', inplace=True)
        
        self.tcd_arte.rename(columns={'main_type' : 'type'}, inplace=True)
                
        total_80 = self.tcd_arte['80'].sum()
        total_85 = self.tcd_arte['85'].sum()
        total_90 = self.tcd_arte['90'].sum()
        total_95 = self.tcd_arte['95'].sum()
        total_100 = self.tcd_arte['100+'].sum()
                
        self.tcd_arte.loc['Total'] = [' ', total_80, total_85, total_90, total_95, total_100]
        
        return self.tcd_arte, self.score_a
            