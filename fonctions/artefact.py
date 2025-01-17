import pandas as pd
import numpy as np
import re
import streamlit as st

dict_arte_type = {
    1: 'ELEMENT',
    2: 'ARCHETYPE',
}

dict_arte_element = {
    1 : 'EAU',
    2 : 'FEU',
    3 : 'VENT',
    4 : 'LUMIERE',
    5 : 'TENEBRE',
    98 : 'INTANGIBLE',
}

dict_arte_effect = {
    200: {'name': 'ATK EN FONCTION HP PERDUS', 'max': 14}, #ancien
    201: {'name': 'DEF EN FONCTION HP PERDUS', 'max': 14}, # ancien
    202: {'name': 'SPD EN FONCTION HP PERDUS', 'max': 14}, # ancien
    203: {'name': "SPD EN CAS D'INCAPACITE", 'max': 6},
    204: {'name': 'RENFORCEMENT ATK', 'max': 5}, #ancien
    205: {'name': 'RENFORCEMENT DEF', 'max': 4}, # ancien
    206: {'name': 'RENFORCEMENT SPD', 'max': 6},
    207: {'name': 'RENFORCEMENT CRITRATE', 'max': 6},
    208: {'name': 'REVENGE', 'max': 4},
    209: {'name': 'COOP DMG', 'max': 4},
    210: {'name': 'BOMBE DMG', 'max': 4},
    211: {'name': 'DMG RENVOYE', 'max': 3},
    212: {'name': 'CRUSHING DMG', 'max': 4},
    213: {'name': "DMG RECU EN CAS D'INCAPACITE", 'max': 3},
    214: {'name': 'CRIT DMG RECU', 'max': 4},
    215: {'name': 'VOL DE VIE', 'max': 8},
    216: {'name': 'HP REVIVE', 'max': 6},
    217: {'name': 'ATB REVIVE', 'max': 6},
    218: {'name': 'DMG SUPP EN FONCTION DES HP', 'max': 0.3},
    219: {'name': "DMG SUPP EN FONCTION DE L'ATQ", 'max': 4},
    220: {'name': 'DMG SUPP EN FONCTION DE LA DEF', 'max': 4},
    221: {'name': 'DMG SUPP EN FONCTION DE LA SPD', 'max': 40},
    222: {'name': 'CRIT DMG EN FONCTION DES HP ELEVES', 'max': 6},
    223: {'name': 'CRIT DMG EN FONCTION DES HP FAIBLES', 'max': 12},
    224: {'name': 'CRIT DMG SUR CIBLE UNIQUE', 'max': 4},
    225: {'name' : 'REVENGE ET COOP', 'max': 4},
    226: {'name' : 'RENFORCEMENT ATK/DEF', 'max': 5},
    300: {'name': 'DMG SUR FEU', 'max': 5},
    301: {'name': 'DMG SUR EAU', 'max': 5},
    302: {'name': 'DMG SUR VENT', 'max': 5},
    303: {'name': 'DMG SUR LUMIERE', 'max': 5},
    304: {'name': 'DMG SUR DARK', 'max': 5},
    305: {'name': 'REDUCTION SUR FEU', 'max': 6},
    306: {'name': 'REDUCTION SUR EAU', 'max': 6},
    307: {'name': 'REDUCTION SUR VENT', 'max': 6},
    308: {'name': 'REDUCTION SUR LUMIERE', 'max': 6},
    309: {'name': 'REDUCTION SUR DARK', 'max': 6},
    400: {'name': 'CRIT DMG S1', 'max': 6},
    401: {'name': 'CRIT DMG S2', 'max': 6},
    402: {'name': 'CRIT DMG S3', 'max': 6}, # ancien
    403: {'name': 'CRIT DMG S4', 'max': 6}, # ancien
    404: {'name': 'SOIN S1', 'max': 6},
    405: {'name': 'SOIN S2', 'max': 6},
    406: {'name': 'SOIN S3', 'max': 6},
    407: {'name': 'PRECISION S1', 'max': 6},
    408: {'name': 'PRECISION S2', 'max': 6},
    409: {'name': 'PRECISION S3', 'max': 6},
    410: {'name' : 'CRIT DMG S3/S4', 'max' : 6},
    411: {'name' : 'PREMIER HIT CRIT DMG', 'max': 6},
}

dataframe_replace_to_english = {'EAU' : 'WATER',
                                'FEU' : 'FIRE',
                                'VENT' : 'WIND',
                                'LUMIERE' : 'LIGHT',
                                'TENEBRE' : 'DARK',
                                'INTANGIBLE' : 'INTANGIBLE',
                                'ATTACK' : 'ATTACK',
                                'DEFENSE' : 'DEFENSE',
                                'HP' : 'HP',
                                'SUPPORT' : 'SUPPORT',
                                'AUCUN' : 'NONE',
                                'Tous' : 'ALL'}

dict_arte_effect_english = {
    'ATK EN FONCTION HP PERDUS': 'ATK+ Proportional to lost HP', #ancien
    'DEF EN FONCTION HP PERDUS' : 'DEF+ Proportional to lost HP', # ancien
    'SPD EN FONCTION HP PERDUS' : 'SPD+ Proportional to lost HP', # ancien
    "SPD EN CAS D'INCAPACITE" : 'SPD Under Inability',
    'RENFORCEMENT ATK' : 'ATK Increased', #ancien
    'RENFORCEMENT DEF' : 'DEF Increased', # ancien
    'RENFORCEMENT SPD' : 'SPD Increased',
    'RENFORCEMENT CRITRATE' : 'CRITRATE Increased',
    'REVENGE' : 'REVENGE',
    'COOP DMG' : 'COOP DMG',
    'BOMBE DMG': 'BOMB DMG',
    'DMG RENVOYE' : 'REFLECTED DMG',
    'CRUSHING DMG' : 'CRUSHING DMG',
    "DMG RECU EN CAS D'INCAPACITE" : 'DMG Received under Inability decreased',
    'CRIT DMG RECU' : 'CRIT DMG Received decreased',
    'VOL DE VIE' : 'Life Drain',
    'HP REVIVE' : 'HP REVIVE',
    'ATB REVIVE' : 'ATB REVIVE',
    'DMG SUPP EN FONCTION DES HP' : 'DMG INCREASED by % HP',
    "DMG SUPP EN FONCTION DE L'ATQ": 'DMG INCREASED by % ATK',
    'DMG SUPP EN FONCTION DE LA DEF': 'DMG INCREASED by % DEF',
    'DMG SUPP EN FONCTION DE LA SPD': 'DMG INC by % SPD',
    'CRIT DMG EN FONCTION DES HP ELEVES': "CRIT DMG+ up as the enemy's HP condition is good",
    'CRIT DMG EN FONCTION DES HP FAIBLES': "CRIT DMG+ up as the enemy's HP condition is bad",
    'CRIT DMG SUR CIBLE UNIQUE': "Single-target skill CRIT DMG",
    'REVENGE ET COOP': 'REVENGE AND COOP',
    'RENFORCEMENT ATK/DEF': 'ATK/DEF Increased',
    'DMG SUR FEU': 'DMG TO FIRE',
    'DMG SUR EAU': 'DMG TO WATER',
    'DMG SUR VENT': 'DMG TO WIND',
    'DMG SUR LUMIERE': 'DMG TO LIGHT',
    'DMG SUR DARK': 'DMG TO DARK',
    'REDUCTION SUR FEU': 'REDUCTION DMG FROM FIRE',
    'REDUCTION SUR EAU': 'REDUCTION DMG FROM WATER',
    'REDUCTION SUR VENT': 'REDUCTION DMG FROM WIND',
    'REDUCTION SUR LUMIERE': 'REDUCTION DMG FROM LIGHT',
    'REDUCTION SUR DARK': 'REDUCTION DMG FROM DARK',
    'CRIT DMG S1': 'CRIT DMG S1',
    'CRIT DMG S2': 'CRIT DMG S2',
    'CRIT DMG S3' : 'CRIT DMG S3', # ancien
    'CRIT DMG S4' : 'CRIT DMG S4', # ancien
    'SOIN S1' : 'HEAL S1',
    'SOIN S2' : 'HEAL S2',
    'SOIN S3' : 'HEAL S3',
    'PRECISION S1' : 'ACC S1',
    'PRECISION S2' : 'ACC S2',
    'PRECISION S3' : 'ACC S3',
    'CRIT DMG S3/S4' : 'CRIT DMG S3/S4',
    'PREMIER HIT CRIT DMG' : 'FIRST HIT CRIT DMG' }

dict_arte_archetype = {
    0: 'NONE',
    1: 'ATTACK',
    2: 'DEFENSE',
    3: 'HP',
    4: 'SUPPORT',
    5: 'MATERIAL',
    98: 'INTANGIBLE'
}

dict_arte_main_stat = {
    100: 'HP',
    101: 'ATK',
    102: 'DEF',
}


@st.cache_data
def max_sub_by_proc(proc, langue):
    "Calcule la sub max en fonction du nombre de proc"

    proc += 1  # le proc à +0

    
    sub_max = {
        'ATK EN FONCTION HP PERDUS' : 14 * proc, #ancien
        'DEF EN FONCTION HP PERDUS' : 14 * proc, # ancien
        'SPD EN FONCTION HP PERDUS' : 14 * proc, # ancien
        "SPD EN CAS D'INCAPACITE" : 6 * proc,
        'RENFORCEMENT ATK' : 5 * proc, #ancien
        'RENFORCEMENT DEF' : 4 * proc, # ancien
        'RENFORCEMENT SPD' : 6 * proc,
        'RENFORCEMENT CRITRATE' : 6 * proc,
        'REVENGE' : 4 * proc,
        'COOP DMG' : 4 * proc,
        'BOMBE DMG' : 4 * proc,
        'DMG RENVOYE' : 3 * proc,
        'CRUSHING DMG' : 4 * proc,
        "DMG RECU EN CAS D'INCAPACITE" : 3 * proc,
        'CRIT DMG RECU' : 4 * proc,
        'VOL DE VIE' : 8 * proc,
        'HP REVIVE' : 6 * proc,
        'ATB REVIVE' : 6 * proc,
        'DMG SUPP EN FONCTION DES HP' : 0.3 * proc,
        "DMG SUPP EN FONCTION DE L'ATQ" : 4 * proc,
        'DMG SUPP EN FONCTION DE LA DEF' : 4 * proc,
        'DMG SUPP EN FONCTION DE LA SPD' : 40 * proc,
        'CRIT DMG EN FONCTION DES HP ELEVES' : 6 * proc,
        'CRIT DMG EN FONCTION DES HP FAIBLES' : 12 * proc,
        'CRIT DMG SUR CIBLE UNIQUE' : 4 * proc,
        'REVENGE ET COOP' : 4 * proc,
        'RENFORCEMENT ATK/DEF' : 5 * proc,
        'DMG SUR FEU' : 5 * proc,
        'DMG SUR EAU' : 5 * proc,
        'DMG SUR VENT' : 5 * proc,
        'DMG SUR LUMIERE' : 5 * proc,
        'DMG SUR DARK' : 5 * proc,
        'REDUCTION SUR FEU' : 6 * proc,
        'REDUCTION SUR EAU' : 6 * proc,
        'REDUCTION SUR VENT' : 6 * proc,
        'REDUCTION SUR LUMIERE' : 6 * proc,
        'REDUCTION SUR DARK' : 6 * proc,
        'CRIT DMG S1' : 6 * proc,
        'CRIT DMG S2' : 6 * proc,
        'CRIT DMG S3' : 6 * proc, # ancien
        'CRIT DMG S4' : 6 * proc, # ancien
        'SOIN S1' : 6 * proc,
        'SOIN S2' : 6 * proc,
        'SOIN S3' : 6 * proc,
        'PRECISION S1' : 6 * proc,
        'PRECISION S2' : 6 * proc,
        'PRECISION S3' : 6 * proc,
        'CRIT DMG S3/S4'  : 6 * proc,
        'PREMIER HIT CRIT DMG' : 6 * proc
    }
    
    if langue == 'English':
        sub_max = {dict_arte_effect_english[key] : value for key, value in sub_max.items()}
        
    return sub_max

class Artefact():
    def __init__(self, data_json, monsters):
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
            arte_unit_style = arte['unit_style']
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

            self.player_arte[arte_id] = [arte_type, arte_attribut, arte_equiped, arte_unit_style, level, efficiency,
                                         main_type, main_value,
                                         first_sub, first_sub_value, second_sub, second_sub_value, third_sub, third_sub_value,
                                         fourth_sub, fourth_sub_value]

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
                        arte_unit_style = arte['unit_style']

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

                        self.player_arte[arte_id] = [arte_type, arte_attribut, arte_equiped, arte_unit_style, level, efficiency,
                                                     main_type, main_value,
                                                     first_sub, first_sub_value, second_sub, second_sub_value,
                                                     third_sub, third_sub_value, fourth_sub, fourth_sub_value]

        self.data_a = pd.DataFrame.from_dict(self.player_arte, orient="index", columns=['arte_type', 'arte_attribut', 'arte_equiped', 'unit_style', 'level', 'efficiency', 'main_type', 'main_value',
                                                                                        'first_sub', 'first_sub_value',  'second_sub', 'second_sub_value',
                                                                                        'third_sub', 'third_sub_value',
                                                                                        'fourth_sub', 'fourth_sub_value'])

        # on prend que les arté montés

        self.data_a = self.data_a[self.data_a['level'] >= 12]

        # on map les identifiants par les mots pour plus de lisibilités

        self.data_a['arte_type'] = self.data_a['arte_type'].map(dict_arte_type)
        
        self.data_a['main_type'] = self.data_a['main_type'].map(
            dict_arte_main_stat)
        
        def identification_attribut(x):
            if x['arte_type'] == 'ARCHETYPE':
                return dict_arte_archetype[x['unit_style']]
            elif x['arte_type'] == 'ELEMENT':
                return dict_arte_element[x['arte_attribut']]
            
        self.data_a['arte_attribut'] = self.data_a.apply(lambda x : identification_attribut(x), axis=1)

        def value_max(x):
            return dict_arte_effect[x]['max']  # first proc + 4 upgrades

        def replace_effect(x):
            return dict_arte_effect[x]['name']

        for c in ['first_sub', 'second_sub', 'third_sub', 'fourth_sub']:
            self.data_a[f'{c}_value_max'] = self.data_a[c].apply(value_max)
            self.data_a[c] = self.data_a[c].apply(replace_effect)

        self.data_a['efficiency'] = round(((self.data_a['first_sub_value'] / self.data_a['first_sub_value_max']
                                            + self.data_a['second_sub_value'] /
                                            self.data_a['second_sub_value_max']
                                            + self.data_a['third_sub_value'] /
                                            self.data_a['third_sub_value_max']
                                            + self.data_a['fourth_sub_value'] / self.data_a['fourth_sub_value_max'])
                                           / 8)*100, 2)
        
        self.data_a.reset_index(inplace=True)
        
        self.data_a[['arte_type', 'arte_attribut']] = self.data_a[['arte_type', 'arte_attribut']].astype('category')
        
        self.data_a['arte_equiped'] = self.data_a['arte_equiped'].replace({0 : st.session_state.langue['Inventaire']})
        self.data_a['arte_equiped'] = self.data_a['arte_equiped'].replace(monsters)
        self.data_a['arte_equiped'] = self.data_a['arte_equiped'].astype('category')
        
    def scoring_arte(self):
        self.data_eff = self.data_a[['efficiency', 'arte_type', 'main_type']]

        self.data_eff['eff_binned'] = pd.cut(
            self.data_eff['efficiency'], bins=(80, 85, 90, 95, 100, 120), right=False)

        self.data_eff.dropna(inplace=True)

        self.data_eff = self.data_eff.groupby(
            ['eff_binned', 'arte_type', 'main_type']).count()

        self.data_eff.reset_index(inplace=True)

        palier_1 = self.data_eff['eff_binned'].unique()[0]  # 80-85
        palier_2 = self.data_eff['eff_binned'].unique()[1]  # 85-90
        palier_3 = self.data_eff['eff_binned'].unique()[2]  # 90-95
        palier_4 = self.data_eff['eff_binned'].unique()[3]  # 95-100
        palier_5 = self.data_eff['eff_binned'].unique()[4]  # 100+

        palier_arte = {palier_1: 1,
                       palier_2: 2,
                       palier_3: 3,
                       palier_4: 4,
                       palier_5: 5}

        self.data_eff['factor'] = 0

        for key, value in palier_arte.items():
            self.data_eff['factor'] = np.where(
                self.data_eff['eff_binned'] == key, value, self.data_eff['factor'])

        self.data_eff['points'] = self.data_eff['efficiency'] * self.data_eff['factor']

        self.data_eff.drop(['factor'], axis=1, inplace=True)

        self.data_eff['eff_binned'] = self.data_eff['eff_binned'].replace({palier_1: '80',
                                                                           palier_2: '85',
                                                                           palier_3: '90',
                                                                           palier_4: '95',
                                                                           palier_5: '100+'})

        self.score_a = self.data_eff['points'].sum()

        # Calcul du TCD :

        self.tcd_arte = self.data_eff.pivot_table(
            self.data_eff, ['arte_type', 'main_type'], 'eff_binned', 'sum')['efficiency']
        # pas besoin du multiindex
        self.tcd_arte.columns.name = "efficiency"
        self.tcd_arte.index.name = 'Artefact'

        self.tcd_arte.reset_index(inplace=True)
        self.tcd_arte.set_index('arte_type', inplace=True)

        self.tcd_arte.rename(columns={'main_type': 'type'}, inplace=True)

        total_80 = self.tcd_arte['80'].sum()
        total_85 = self.tcd_arte['85'].sum()
        total_90 = self.tcd_arte['90'].sum()
        total_95 = self.tcd_arte['95'].sum()
        total_100 = self.tcd_arte['100+'].sum()

        self.tcd_arte.loc['Total'] = [' ', total_80,
                                      total_85, total_90, total_95, total_100]

        return self.tcd_arte, self.score_a
    
    

        

    def calcul_value_max(self):

        self.data_max = self.data_a.copy()
        
               
        def prepare_data(data_max, aggfunc):        
            df_first = pd.pivot_table(data_max,
                                      index=['first_sub', 'arte_type', 'arte_attribut'],
                                      values='first_sub_value',
                                      aggfunc=aggfunc).reset_index()
            df_second = pd.pivot_table(data_max,
                                       index=['second_sub', 'arte_type', 'arte_attribut'],
                                       values='second_sub_value',
                                       aggfunc=aggfunc).reset_index()
            df_third = pd.pivot_table(data_max,
                                      index=['third_sub', 'arte_type', 'arte_attribut'],
                                      values='third_sub_value',
                                      aggfunc=aggfunc).reset_index()
            df_fourth = pd.pivot_table(data_max,
                                       index=['fourth_sub', 'arte_type', 'arte_attribut'],
                                       values='fourth_sub_value',
                                       aggfunc=aggfunc).reset_index()

            df_max = df_first.merge(df_second,
                                    how='outer',
                                    left_on=['first_sub', 'arte_type', 'arte_attribut'],
                                    right_on=['second_sub', 'arte_type', 'arte_attribut'])
            df_max = df_max.merge(df_third,
                                  how='outer',
                                  left_on=['first_sub', 'arte_type', 'arte_attribut'],
                                  right_on=['third_sub', 'arte_type', 'arte_attribut'])
            df_max = df_max.merge(df_fourth,
                                  how='outer',
                                  left_on=['first_sub', 'arte_type', 'arte_attribut'],
                                  right_on=['fourth_sub', 'arte_type', 'arte_attribut'])
            
            df_max = df_max[df_max['first_sub'] != 'Aucun']
            

            return df_max
        

        
        # MAX
        

        self.df_max = prepare_data(self.data_max, 'max')
        
        # En regroupant, il y a des positions où il n'y a pas la substat qu'on cherche.
        self.df_max['third_sub'] = self.df_max['third_sub'].fillna(self.df_max['fourth_sub'])
        self.df_max['second_sub'] = self.df_max['second_sub'].fillna(self.df_max['third_sub'])
        self.df_max['first_sub'] = self.df_max['first_sub'].fillna(self.df_max['second_sub'])
        
            
        self.df_max.drop(['second_sub', 'third_sub', 'fourth_sub'], axis=1, inplace=True)
    
        # on remplace les valeurs nulles par 0
        self.df_max.select_dtypes(include='number').fillna(0, inplace=True)    
        
        self.df_max['max_value'] = self.df_max[['first_sub_value', 'second_sub_value', 'third_sub_value', 'fourth_sub_value']].max(axis=1)
        self.df_max.rename(columns={'first_sub' : 'substat'}, inplace=True)
        self.df_max.set_index('substat', inplace=True)
        

               
        self.df_max = self.df_max[['arte_type', 'arte_attribut', 'max_value']]
        

        self.df_max_arte_type = self.df_max.groupby(['arte_type', 'substat']).agg({'max_value' : 'max'})
        self.df_max_element = self.df_max.groupby(['arte_attribut', 'substat']).agg({'max_value' : 'max'})
        self.df_max_substat = self.df_max.groupby(['substat']).agg({'max_value' : 'max'})
        

    
    def count_substat(self, mot_cle, nb_mot_cle):
        data = self.data_a.copy()
        data['totalsub'] = data['first_sub'] + data['second_sub'] + data['third_sub'] + data['fourth_sub']
        data_grp = data.groupby(['index']).agg({'totalsub':lambda x: ', '.join(tuple(x.tolist()))})
        data_grp['critere'] = data_grp['totalsub'].apply(lambda x: len(re.findall(mot_cle, x)))
        data_count = data_grp[data_grp['critere'] >= nb_mot_cle]
        return data_count, data_count.shape[0]
    
    
    def top(self):
        
        def prepare_data(data_max, aggfunc):        
            df_first = pd.pivot_table(data_max, index=['first_sub', 'arte_attribut', 'main_type'], values='first_sub_value', aggfunc=aggfunc).reset_index()
            df_second = pd.pivot_table(data_max, index=['second_sub', 'arte_attribut', 'main_type'], values='second_sub_value', aggfunc=aggfunc).reset_index()
            df_third = pd.pivot_table(data_max, index=['third_sub', 'arte_attribut', 'main_type'], values='third_sub_value', aggfunc=aggfunc).reset_index()
            df_fourth = pd.pivot_table(data_max, index=['fourth_sub', 'arte_attribut', 'main_type'], values='fourth_sub_value', aggfunc=aggfunc).reset_index()

            df_max = df_first.merge(df_second, how='outer', left_on=['first_sub', 'arte_attribut', 'main_type'], right_on=['second_sub', 'arte_attribut', 'main_type'])
            df_max['first_sub'].fillna(df_max['second_sub'], inplace=True)
            df_max = df_max.merge(df_third, how='outer', left_on=['first_sub', 'arte_attribut', 'main_type'], right_on=['third_sub', 'arte_attribut', 'main_type'])
            df_max['first_sub'].fillna(df_max['third_sub'], inplace=True)
            df_max = df_max.merge(df_fourth, how='outer', left_on=['first_sub', 'arte_attribut', 'main_type'], right_on=['fourth_sub', 'arte_attribut', 'main_type'])
            df_max['first_sub'].fillna(df_max['fourth_sub'], inplace=True)
            
            df_max = df_max[df_max['first_sub'] != 'Aucun']
            
            df_max['third_sub'] = df_max['third_sub'].fillna(df_max['fourth_sub'])
            df_max['second_sub'] = df_max['second_sub'].fillna(df_max['third_sub'])
            df_max['first_sub'] = df_max['first_sub'].fillna(df_max['second_sub'])
            
            df_max[['first_sub_value', 'second_sub_value', 'third_sub_value', 'fourth_sub_value']] = df_max[['first_sub_value', 'second_sub_value', 'third_sub_value', 'fourth_sub_value']].fillna(0)
            
            

            return df_max
        
        
        def fill_avg(x):
            long = len(x)
            if long < 5:
                for i in range(5-long): 
                    x.append(0) 
            return x
        
        def calcul_avg(data_max, n):
            
            df_avg = prepare_data(data_max, lambda x: x.nlargest(n).tolist())
            df_avg = df_avg.applymap(lambda x: [0] if x == 0 else x)
            df_avg['value'] = df_avg[['first_sub_value', 'second_sub_value', 'third_sub_value', 'fourth_sub_value']].sum(axis=1)
            df_avg['value'] = df_avg['value'].apply(lambda x: fill_avg(x))
            df_avg[f'top{n}'] = df_avg['value'].apply(lambda liste: np.sort(np.array(liste))[-n:])
            
            
            return df_avg

        self.df_top = calcul_avg(self.data_max, 5)
         
        self.df_top[['5', '4', '3', '2', '1']] = self.df_top['top5'].apply(lambda x: pd.Series(list(x))) 
        
        self.df_top = self.df_top[['first_sub', 'arte_attribut', 'main_type', '1', '2', '3', '4', '5']]
                    
        self.df_top.rename(columns={'first_sub' : 'substat'}, inplace=True)
        
        self.df_top.sort_values(by=['arte_attribut', 'substat'], inplace=True)
   
        
        self.df_top.reset_index(inplace=True, drop=True)
        


        return self.df_top
  
def return_style(color, background_color):
            
    style_perso = [
        ('font-size', '14px'),
        ('text-align', 'center'),
        ('font-weight', 'bold'),
        ('color', color),
        ('background-color', background_color)
        ]
            
    return style_perso
        
water = return_style('#FFFFFF', '#0000FF')
feu = return_style('#FFFFFF', '#FF0000')
vent = return_style('#FFFFFF', '#FF7F00')
light = return_style('#000000', '#FFFFFF')
dark = return_style('#FFFFFF', '#6F2DA8')
intangible = return_style('#FFFFFF', '#3CB371')
attack = return_style('#FFFFFF', '#2E86C1')
defense = return_style('#FFFFFF', '#C0392B')
hp = return_style('#FFFFFF', '#45B39D')
support = return_style('#FFFFFF', '#6E2C00')

atk_lv1 = return_style('#FFFFFF', '#77B5FE')
def_lv1 = return_style('#FFFFFF', '#FB335B')
supp_lv1 = return_style('#FFFFFF', '#008000')

dict_color = {'EAU' : water,
              'FEU' : feu,
              'VENT' : vent,
              'LUMIERE' : light,
              'TENEBRE' : dark,
              'INTANGIBLE' : intangible,
              'ATTACK' : attack,
              'DEFENSE' : defense,
              'HP' : hp,
              'SUPPORT' : support}

dict_color_lv1 = {'ATK' : atk_lv1,
              'DEF' : def_lv1,
              'HP' : supp_lv1}


        

def visualisation_top_arte(df, column, use_container_width=True, order=None):
        
    df_filter = df[df['substat'] == column]
        
    tcd = pd.pivot_table(values=['5','4','3','2','1'], columns=['arte_attribut', 'main_type'], data=df_filter, aggfunc='max')
    
    if not tcd.empty:
        
        st.write(f'Top 5 {column.capitalize()}')
        
        if order != None:
        # Sélectionner les colonnes existantes dans l'ordre souhaité
            existing_cols = [col for col in order if col in tcd.columns]
            tcd = tcd.loc[:, existing_cols]
        
        # style_table = [dict(selector=f"thead tr th.col_heading.level0.col{i}.css-3d58hu.e1q9reml1", props=dict_color[column[0].upper()]) for i, column in enumerate(tcd.columns)] + [dict(selector=f"thead tr th.col_heading.level1.col{i}.css-3d58hu.e1q9reml1", props=dict_color_lv1[column[1].upper()]) for i, column in enumerate(tcd.columns)]
        style_table = [dict(selector=f"thead tr th.col_heading.level0.col{i}.st-emotion-cache-3d58hu.e1q9reml1", props=dict_color[column[0].upper()]) for i, column in enumerate(tcd.columns)] + [dict(selector=f"thead tr th.col_heading.level1.col{i}.st-emotion-cache-3d58hu.e1q9reml1", props=dict_color_lv1[column[1].upper()]) for i, column in enumerate(tcd.columns)]
        # table
        if column.capitalize() == 'Dmg supp en fonction des hp':
            df2=tcd.astype('float', errors='ignore')
            df2 = np.round(df2,1)
            df2 = df2.astype('str').style.set_properties(**{'text-align': 'center'}).set_table_styles(style_table)
        else:
            df2=tcd.astype('int', errors='ignore').astype('str').style.set_properties(**{'text-align': 'center'}).set_table_styles(style_table)
        # df2=tcd.astype(type_data, errors='ignore').astype('str').style.set_properties(**{'text-align': 'center'}).set_table_styles(style_table)
        st.table(df2)    

        return df2