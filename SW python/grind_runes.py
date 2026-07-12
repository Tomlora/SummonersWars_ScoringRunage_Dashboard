#!/usr/bin/env python
# coding: utf-8
# convertit avec jupyter nbconvert mynotebook.ipynb --to python

# In[112]:


import pandas as pd
import numpy as np
import json
import plotly.express as px
import ast
import requests
from pathlib import Path
from os import system, name

# Friendly
#https://www.mathweb.fr/euclide/2022/02/11/mettre-des-couleurs-en-mode-console-a-un-texte-sous-python/
# https://github.com/Textualize/rich/blob/master/README.fr.md
from rich.console import Console
from rich.progress import track
from rich.markdown import Markdown

# fix plotly express et Visual Studio Code
import plotly.io as pio
pio.renderers.default = "notebook_connected"

# Supprime les Future Warnings sur les copies
pd.options.mode.chained_assignment = None  # default='warn'




# In[113]:


def extraire_variables_imbriquees(df, colonne):
    df[colonne] = [ast.literal_eval(str(item)) for index, item in df[colonne].iteritems()]

    df = pd.concat([df.drop([colonne], axis=1), df[colonne].apply(pd.Series)], axis=1)
    return df

def export_excel(data, data_short, data_property, data_count, data_inventaire):
    
        # https://xlsxwriter.readthedocs.io/working_with_pandas.html
        
        # Pour travailler avec xlswriter et pendas et faire des tableaux, il faut reset l'index
        data.reset_index(inplace=True)
        data.rename(columns={'index' : 'Id_rune'}, inplace=True)
        data_short.reset_index(inplace=True)
        data_short.rename(columns={'index' : 'Set'}, inplace=True)
        data_property.reset_index(inplace=True)
        data_property.rename(columns={'index' : 'Set'}, inplace=True)
        
        
        writer = pd.ExcelWriter("resultat/fichier.xlsx", engine='xlsxwriter')
        data.to_excel(writer, startrow=1, sheet_name='Data_complete', index=False, header=False)
        data_short.to_excel(writer, startrow=1, sheet_name='Par rune et monstre', index=False, header=False)
        data_property.to_excel(writer, startrow=1, sheet_name='Par set', index=False, header=False)
        data_count.to_excel(writer, startrow=1, sheet_name='Par set et propriété', index=False, header=False)
        data_inventaire.to_excel(writer, startrow=1, sheet_name='Inventaire', index=False, header=False)
        
        workbook = writer.book
        worksheet1 = writer.sheets['Data_complete']
        worksheet2 = writer.sheets['Par rune et monstre']
        worksheet3 = writer.sheets['Par set']
        worksheet4 = writer.sheets['Par set et propriété']
        worksheet5 = writer.sheets['Inventaire']

        # Gestion de la taille des colonnes

        cell_format = workbook.add_format({'valign':'vcenter', 'align': 'center'})
        cell_format.set_text_wrap()
        for i, col in enumerate(data.columns):
                worksheet1.set_column(i, i+1, 20, cell_format) # colonne, colonne, len_colonne, format colonne
        for i, col in enumerate(data_short.columns):
                worksheet2.set_column(i, i+1, 20, cell_format) # colonne, colonne, len_colonne, format colonne
        for i, col in enumerate(data_property.columns):
                worksheet3.set_column(i, i+1, 20, cell_format) # colonne, colonne, len_colonne, format colonne
        for i, col in enumerate(data_count.columns):
                worksheet4.set_column(i, i+1, 20, cell_format) # colonne, colonne, len_colonne, format colonne
        for i, col in enumerate(data_inventaire.columns):
                worksheet5.set_column(i, i+1, 20, cell_format) # colonne, colonne, len_colonne, format colonne
                

        # Ajout d'un graphique dans l'onglet 3

        chart = workbook.add_chart({'type' : 'column'})
        (max_row, max_col) = data_property.shape
                       
        chart.add_series({'categories' : ['Par set', 1, 0, max_row, 0 ], 'values' : ['Par set', 1, 1, max_row, 1 ]})
            
        worksheet3.insert_chart(1,3,chart)
            

        
        # Tableau
        
        def tableau(data, worksheet):
            column_settings = [{'header': column} for column in data.columns]
            (max_row, max_col) = data.shape

            worksheet.add_table(0, 0, max_row, max_col-1, {'columns': column_settings})
            
        tableau(data, worksheet1)
        tableau(data_short, worksheet2)
        tableau(data_property, worksheet3)
        tableau(data_count, worksheet4)
        tableau(data_inventaire, worksheet5)
            
        writer.save()
        



def swarfarm_monstres():
        # database swarfarm
    url = "https://swarfarm.com/api/v2/monsters/?page=1"
    r = requests.get(url=url)
    data = r.json()
    df = pd.DataFrame(data)

    for i in track(range(2,21), description="Chargement de la Database Swarfarm..."):
        url = f"https://swarfarm.com/api/v2/monsters/?page={i}"
        r = requests.get(url=url)
        data = r.json()
        df2 = pd.DataFrame(data)
        df = pd.concat([df, df2])
        
        
    # on extrait les variables du dict dans la colonne ['results'] et on supprime ce qui m'intéresse pas
    df = extraire_variables_imbriquees(df, 'results')
    df.drop(['next', 'previous'], axis=1, inplace=True)
    # On garde ce qui nous intéresse
    df_mobs_swarfarm = df[['id', 'url', 'com2us_id', 'family_id', 'name']]

    df_mobs_swarfarm.to_excel('swarfarm.xlsx', index=False)


# # Import data

# In[114]:

MARKDOWN = """
# Application Grind_runes pour Summoners Wars
# Version developpée par Tomlora


## Utilisation :

- Il faut tout d'abord un json, qu'il est possible d'obtenir via SWEX. L'application va demander le chemin vers ce fichier.
- Enfin, l'application a besoin d'une base de données pour identifier les monstres. Pour cela, cela nécessite que l'application se connecte à Swarfarm. 
Si vous souhaitez créer ou mettre à jour la base de données des monstres, il faudra répondre oui à la question. Sinon, il faudra écrire non.
Le oui est **obligatoire à la première utilisation**, sinon vous n'avez pas la base de données nécessaire au fonctionnement de l'application

## Resultats :

L'application va analyser les runes et identifier les substats non-maximisées pour améliorer l'efficience d'une rune.

Après analyse, un rapport est généré dans un dossier resultat sous format Excel avec 5 onglets :
- Un onglet avec toute la data détaillée (stats des runes, équipée, efficience, stats maximales à grind  + les grind à utiliser (heroique ou légendaire)
- Un second onglet qui résume toute la data
- Un troisième onglet qui récapitule par set
- Un quatrième onglet qui résume par set et propriété
- L'inventaire actuel

Cette analyse est complétée par quelques graphiques qui sont situés dans le même dossier.
"""


console_readme = Console()
md = Markdown(MARKDOWN)
console_readme.print(md)
print('------------------------------------------------------')
url_json = input('\nLien du json ? ')
f = open(url_json, encoding="utf8")

maj_swarfarm = input("\nCréation ou maj de la database Swarfarm ? (Oui/Non) ")
maj_swarfarm = maj_swarfarm.lower()


# On clear la cmd

 # for windows
if name == 'nt':
    system('cls')

   # for mac and linux
else:
   system('clear')

# In[115]:


# On charge le json
data_json = json.load(f)


player_runes = {}

# Rune pas équipé
for rune in track(data_json['runes'], description="Chargement des runes non-équipées..."):
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
                              first_sub, first_sub_value, first_gemme_bool,  first_sub_grinded_value, second_sub, second_sub_value, second_gemme_bool,
                              second_sub_grinded_value, third_sub, third_sub_value, third_gemme_bool, third_sub_grinded_value, fourth_sub,
                              fourth_sub_value, fourth_gemme_bool, fourth_sub_grinded_value]


# Rune équipée
for unit in track(data_json['unit_list'], description="Chargement des runes équipées..."):
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


# In[118]:


data = pd.DataFrame.from_dict(player_runes, orient="index", columns=['rune_set', 'rune_slot', 'rune_equiped', 'stars', 'level', 'efficiency', 'max_efficiency', 'max_efficiency_reachable', 'gain', 'main_type', 'main_value', 'innate_type',
                                                                     'innate_value','first_sub', 'first_sub_value', 'first_gemme_bool', 'first_sub_grinded_value', 'second_sub', 'second_sub_value', 'second_gemme_bool',
                              'second_sub_grinded_value', 'third_sub', 'third_sub_value', 'third_gemme_bool', 'third_sub_grinded_value', 'fourth_sub',
                              'fourth_sub_value', 'fourth_gemme_bool', 'fourth_sub_grinded_value'])
# data


# # On supprime toute rune inférieure au level 11 ou 5 etoiles

# In[119]:


data = data[data['level'] > 11]
data = data[data['stars'] > 5]


# # Map des sets

# In[120]:


set = {1:"Energy", 2:"Guard", 3:"Swift", 4:"Blade", 5:"Rage", 6:"Focus", 7:"Endure", 8:"Fatal", 10:"Despair", 11:"Vampire", 13:"Violent",
        14:"Nemesis", 15:"Will", 16:"Shield", 17:"Revenge", 18:"Destroy", 19:"Fight", 20:"Determination", 21:"Enhance", 22:"Accuracy", 23:"Tolerance", 99:"Immemorial"}

data['rune_set'] = data['rune_set'].map(set)



# # Efficiency

# In[121]:


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

# Value max :
data['first_sub_value_max'] = data['first_sub'].map(sub)
data['second_sub_value_max'] = data['second_sub'].map(sub)
data['third_sub_value_max'] = data['third_sub'].map(sub)
data['fourth_sub_value_max'] = data['fourth_sub'].map(sub)
data['innate_value_max'] = data['innate_type'].replace(sub)


# Value stats de base + meule

data['first_sub_value_total'] = (data['first_sub_value'] + data['first_sub_grinded_value'])
data['second_sub_value_total'] = (data['second_sub_value'] + data['second_sub_grinded_value'])
data['third_sub_value_total'] = (data['third_sub_value'] + data['third_sub_grinded_value'])
data['fourth_sub_value_total'] = (data['fourth_sub_value'] + data['fourth_sub_grinded_value'])

data['efficiency'] = np.where(data['innate_type'] != 0, round(((1+data['innate_value'] / data['innate_value_max'] + data['first_sub_value_total'] / data['first_sub_value_max'] + data['second_sub_value_total'] / data['second_sub_value_max'] + data['third_sub_value_total'] / data['third_sub_value_max'] + data['fourth_sub_value_total'] / data['fourth_sub_value_max']) / 2.8)*100,2),
                              round(((1 + data['first_sub_value_total'] / data['first_sub_value_max'] + data['second_sub_value_total'] / data['second_sub_value_max'] + data['third_sub_value_total'] / data['third_sub_value_max'] + data['fourth_sub_value_total'] / data['fourth_sub_value_max']) / 2.8)*100,2))



# In[122]:


sub_max_lgd = {1:550, 2:10, 3:30, 4:10, 5:30, 6:10, 8:5}
sub_max_heroique = {1:450, 2:7, 3:22, 4:7, 5:22, 6:7, 8:4}


# Certaines stats ne sont pas meulables. On remplace donc le potentiel de meule par 0

dict = {'first_grind_value_max' : 'first_sub', 'second_grind_value_max' : 'second_sub', 'third_grind_value_max' : 'third_sub', 'fourth_grind_value_max' : 'fourth_sub'}

for key, value in dict.items():
       data[key + '_lgd'] = data[value].replace(sub_max_lgd)
       data[key + '_hero'] = data[value].replace(sub_max_heroique)
       
       # Certaines stats ne sont pas meulables. On remplace donc le potentiel de meule par 0
       
       data[key + "_lgd"] = np.where(data[value] > 8, 0,  data[key + "_lgd"])
       data[key + "_hero"] = np.where(data[value] > 8, 0, data[key + "_hero"]) 


# Value stats de base + meule (max)

data['first_sub_value_total_max_lgd'] = (data['first_sub_value'] + data['first_grind_value_max_lgd'])
data['second_sub_value_total_max_lgd'] = (data['second_sub_value'] + data['second_grind_value_max_lgd'])
data['third_sub_value_total_max_lgd'] = (data['third_sub_value'] + data['third_grind_value_max_lgd'])
data['fourth_sub_value_total_max_lgd'] = (data['fourth_sub_value'] + data['fourth_grind_value_max_lgd'])

data['first_sub_value_total_max_hero'] = (data['first_sub_value'] + data['first_grind_value_max_hero'])
data['second_sub_value_total_max_hero'] = (data['second_sub_value'] + data['second_grind_value_max_hero'])
data['third_sub_value_total_max_hero'] = (data['third_sub_value'] + data['third_grind_value_max_hero'])
data['fourth_sub_value_total_max_hero'] = (data['fourth_sub_value'] + data['fourth_grind_value_max_hero'])


# In[123]:


data['efficiency_max_lgd'] = np.where(data['innate_type'] != 0, round(((1+data['innate_value'] / data['innate_value_max'] + data['first_sub_value_total_max_lgd'] / data['first_sub_value_max'] + data['second_sub_value_total_max_lgd'] / data['second_sub_value_max'] + data['third_sub_value_total_max_lgd'] / data['third_sub_value_max'] + data['fourth_sub_value_total_max_lgd'] / data['fourth_sub_value_max']) / 2.8)*100,2),
                              round(((1 + data['first_sub_value_total_max_lgd'] / data['first_sub_value_max'] + data['second_sub_value_total_max_lgd'] / data['second_sub_value_max'] + data['third_sub_value_total_max_lgd'] / data['third_sub_value_max'] + data['fourth_sub_value_total_max_lgd'] / data['fourth_sub_value_max']) / 2.8)*100,2))

data['efficiency_max_hero'] = np.where(data['innate_type'] != 0, round(((1+data['innate_value'] / data['innate_value_max'] + data['first_sub_value_total_max_hero'] / data['first_sub_value_max'] + data['second_sub_value_total_max_hero'] / data['second_sub_value_max'] + data['third_sub_value_total_max_hero'] / data['third_sub_value_max'] + data['fourth_sub_value_total_max_hero'] / data['fourth_sub_value_max']) / 2.8)*100,2),
                              round(((1 + data['first_sub_value_total_max_hero'] / data['first_sub_value_max'] + data['second_sub_value_total_max_hero'] / data['second_sub_value_max'] + data['third_sub_value_total_max_hero'] / data['third_sub_value_max'] + data['fourth_sub_value_total_max_hero'] / data['fourth_sub_value_max']) / 2.8)*100,2))

data['potentiel_max'] = data['efficiency_max_lgd'] - data['efficiency']


# # On supprime les variables inutiles

# In[126]:


data.drop(['max_efficiency', 'max_efficiency_reachable', 'gain'], axis=1, inplace=True)


# # Map 
# ## Propriété
# Plus simple ici qu'avant

# In[127]:


property = {0:'Aucun', 
            1:'HP', 
            2:'HP%', 
            3:'ATQ', 
            4:'ATQ%', 
            5:'DEF', 
            6:'DEF%', 
            8:"SPD", 
            9:'CRIT', 
            10:'DCC', 
            11:'RES', 
            12:'ACC'}

for c in ['innate_type', 'first_sub', 'second_sub', 'third_sub', 'fourth_sub', 'main_type']:
    data[c] = data[c].map(property)
    
    


# ## Monstres

# In[128]:


data_mobs = pd.DataFrame.from_dict(data_json, orient="index").transpose()


# In[129]:


data_mobs = data_mobs['unit_list']


# In[130]:


# On va boucler et retenir ce qui nous intéresse..
list_mobs = []
data_mobs[0]
for monstre in track(data_mobs[0], description="Identification des monstres..."):
    unit = monstre['unit_id']
    master_id = monstre['unit_master_id']
    list_mobs.append([unit, master_id])
    
# On met ça en dataframe    
df_mobs = pd.DataFrame(list_mobs, columns=['id_unit', 'id_monstre'])


# In[131]:


# df_mobs


# Maintenant, on a besoin d'identifier les id.
# Pour cela, on va utiliser l'api de swarfarm

# In[ ]:





# In[132]:

if maj_swarfarm == "oui":
    swarfarm_monstres() # à activer/désactiver pour maj 
swarfarm = pd.read_excel('swarfarm.xlsx')
# swarfarm


# In[133]:


swarfarm = swarfarm[['com2us_id', 'name']].set_index('com2us_id')
df_mobs['name_monstre'] = df_mobs['id_monstre'].map(swarfarm.to_dict(orient="dict")['name'])

# On peut faire le mapping...

# In[135]:


df_mobs = df_mobs[['id_unit', 'name_monstre']].set_index('id_unit')


# In[136]:


data['rune_equiped'] = data['rune_equiped'].replace(df_mobs.to_dict(orient="dict")['name_monstre'])


# # Indicateurs
# ## Runes +15

# In[137]:


data['indicateurs_level'] = (data['level'] == 15).astype('int') # Si 15 -> 1. Sinon 0


# # Amélioration des Grind

# In[138]:


dict = {'amelioration_first_grind' : ['first_sub_grinded_value', 'first_grind_value'],
        'amelioration_second_grind' : ['second_sub_grinded_value', 'second_grind_value'],
        'amelioration_third_grind' : ['third_sub_grinded_value', 'third_grind_value'],
        'amelioration_fourth_grind' : ['fourth_sub_grinded_value', 'fourth_grind_value']}

for key, value in dict.items():
    # Améliorable ? (valeur)
    data[key + '_lgd_value'] = data[value[1] + '_max_lgd'] - data[value[0]]
    data[key + '_hero_value'] = data[value[1] + '_max_hero'] - data[value[0]]
    # Améliorable ? (bool)
    data[key + '_lgd_ameliorable?'] = (data[key + '_lgd_value'] > 0).astype('int')
    data[key + '_hero_ameliorable?'] = (data[key + '_hero_value'] > 0).astype('int')


# # Commentaires

# In[139]:


# Level
data['Commentaires'] = np.where(data['level'] != 15, "A monter +15 \n", "")
calcul_gemme = data['first_gemme_bool'] + data['second_gemme_bool'] + data['third_gemme_bool'] + data['fourth_gemme_bool']
data['Commentaires'] = np.where(calcul_gemme == 0, data['Commentaires'] + "Pas de gemme utilisée", data['Commentaires'])
data['Grind_lgd'] = ""
data['Grind_hero'] = ""


dict = {'amelioration_first_grind' : 'first_sub',
        'amelioration_second_grind' : 'second_sub',
        'amelioration_third_grind' : 'third_sub',
        'amelioration_fourth_grind' : 'fourth_sub'}

# meule

for key, value in dict.items():
    nom = key + "_lgd_value"
    data['Grind_lgd'] = np.where(data[key + '_lgd_ameliorable?'] == 1, data['Grind_lgd'] +  "Meule : " + data[value] + "(" + data[nom].astype('str') + ") \n", data['Grind_lgd'])
    
    nom = key + "_hero_value"
    data['Grind_hero'] = np.where(data[key + '_hero_ameliorable?'] == 1, data['Grind_hero'] +  "Meule : " + data[value] + "(" + data[nom].astype('str') + ") \n", data['Grind_hero'])
    
# gemme



# sub des gemmes

gemme_max_lgd = {'HP':580, 'HP%':13, 'ATQ':40, 'ATQ%':13, 'DEF':40, 'DEF%':13, 'SPD':10, 'CRIT':9, 'DCC':10, 'RES':11, 'ACC':11}
gemme_max_hero = {'HP':420, 'HP%':11, 'ATQ':30, 'ATQ%':11, 'DEF':30, 'DEF%':11, 'SPD':8, 'CRIT':7, 'DCC':8, 'RES':9, 'ACC':9}



# On les inclut au dataframe

data['first_gemme_max_lgd'] = data['first_sub'].map(gemme_max_lgd)
data['second_gemme_max_lgd'] = data['second_sub'].map(gemme_max_lgd)
data['third_gemme_max_lgd'] = data['third_sub'].map(gemme_max_lgd)
data['fourth_gemme_max_lgd'] = data['fourth_sub'].map(gemme_max_lgd)

data['first_gemme_max_hero'] = data['first_sub'].map(gemme_max_hero)
data['second_gemme_max_hero'] = data['second_sub'].map(gemme_max_hero)
data['third_gemme_max_hero'] = data['third_sub'].map(gemme_max_hero)
data['fourth_gemme_max_hero'] = data['fourth_sub'].map(gemme_max_hero)


dict2 = {'first_gemme' : 'first_sub',
        'second_gemme': 'second_sub',
        'third_gemme': 'third_sub',
        'fourth_gemme': 'fourth_sub'}


# On fait le calcul : 

for key, sub in track(dict2.items(), description="Identification des gemmes à grind...."):

    condition = data[key + '_bool'] == 1 #si 1 -> gemme utilisée
    calcul_lgd = data[key + '_max_lgd'] - data[sub + '_value'] # différence entre le max et la gemme
    calcul_hero = data[key + '_max_hero'] - data[sub + '_value'] # différence entre le max et la gemme
    condition_lgd =  calcul_lgd > 0 # s'il y a un écart, ce n'est pas la stat max
    condition_hero = calcul_hero > 0

    data['Grind_lgd'] = np.where(condition, np.where(condition_lgd, data['Grind_lgd'] + "Gemme : " + data[sub] + "(" + calcul_lgd.astype('str') + ")", data['Grind_lgd']), data['Grind_lgd'] )
    data['Grind_hero'] = np.where(condition, np.where(condition_hero, data['Grind_hero'] + "Gemme : " + data[sub] + "(" + calcul_hero.astype('str') + ")", data['Grind_hero']), data['Grind_hero'] )  



# # Clean du xl


data.drop(['stars', 'level'], axis=1, inplace=True)

data_short = data[['rune_set', 'rune_slot', 'rune_equiped', 'efficiency', 'efficiency_max_hero', 'efficiency_max_lgd', 'potentiel_max', 'Commentaires', 'Grind_lgd', 'Grind_hero']]


# ## Meules manquantes par stat

property_grind = {1:'Meule : HP', 
            2:'Meule : HP%', 
            3:'Meule : ATQ', 
            4:'Meule : ATQ%', 
            5:'Meule : DEF', 
            6:'Meule : DEF%', 
            8:"Meule : SPD"}

list_property_type = []
list_property_count = []

for propriete in track(property_grind.values(), description="Comptage des meules nécessaires..."):
    count = data['Grind_hero'].str.count(propriete).sum()
    
    list_property_type.append(propriete)
    list_property_count.append(count)
    
property_grind_gemme = {1:'Gemme : HP', 
            2:'Gemme : HP%', 
            3:'Gemme : ATQ', 
            4:'Gemme : ATQ%', 
            5:'Gemme : DEF', 
            6:'Gemme : DEF%', 
            8:"Gemme : SPD"}

for propriete in track(property_grind_gemme.values(), description="Comptage des gemmes nécessaires..."):
    count = data['Grind_hero'].str.count(propriete).sum()
    
    list_property_type.append(propriete)
    list_property_count.append(count)

    
df_property = pd.DataFrame([list_property_type, list_property_count]).transpose()
df_property = df_property.rename(columns={0:'Propriété', 1:'Meules/Gemmes (hero) manquantes pour atteindre la stat max'})
    


# In[142]:

# Création du dossier

path = Path("./resultat")
path.mkdir(parents=True, exist_ok=True)

# Graphique

fig = px.histogram(df_property, x='Propriété', y='Meules/Gemmes (hero) manquantes pour atteindre la stat max', color='Propriété', title="Meules heroiques manquantes pour atteindre la stat max", text_auto=True)
fig.write_image('resultat/MeulesGemmes_manquantes_par_stat.png')


# ## Meules manquantes par set

# In[143]:


dict_rune = {}
list_type = []
list_count = []
list_propriete = []
list_propriete_gemmes = []
list_count_gemmes = []

for type_rune in set.values():
    for propriete in property_grind.values():
        data_type_rune = data[data['rune_set'] == type_rune]
        nb_rune = data[data['rune_set'] == type_rune].count().max()
        count = data_type_rune['Grind_hero'].str.count(propriete).sum()
        
        dict_rune[type_rune] = nb_rune
        
        list_type.append(type_rune)
        list_count.append(count)
        list_propriete.append(propriete)
        
        df_rune = pd.DataFrame.from_dict(dict_rune, orient='index', columns=['Nombre de runes'])
        
    for propriete in property_grind_gemme.values():
        data_type_rune = data[data['rune_set'] == type_rune]
        nb_rune = data[data['rune_set'] == type_rune].count().max()
        count = data_type_rune['Grind_hero'].str.count(propriete).sum()
        
       
        # list_type.append(type_rune)
        list_count_gemmes.append(count)
        list_propriete_gemmes.append(propriete)


# In[144]:


df_count = pd.DataFrame([list_type, list_propriete, list_count, list_propriete_gemmes, list_count_gemmes]).transpose()
df_count = df_count.rename(columns={0:'Set', 1:'Propriété Meules', 2:'Meules (hero) manquantes pour la stat max', 3: 'Propriété Gemmes', 4:'Gemmes (hero) manquantes'})


# Graphique
fig = px.histogram(df_count, x='Set', y='Meules (hero) manquantes pour la stat max', color='Propriété Meules', title="Meules heroiques manquantes pour la stat max", text_auto=True)
fig.write_image('resultat/Meules_manquantes par rune et propriété.png')

fig = px.histogram(df_count, x='Set', y='Gemmes (hero) manquantes', color='Propriété Gemmes', title="Gemmes heroiques manquantes pour la stat max", text_auto=True)
fig.write_image('resultat/Gemmes_manquantes par rune et propriété.png')





# Inventaire

# On va gérer l'inventaire maintenant...

df_inventaire = pd.DataFrame.from_dict(data_json, orient='index').transpose()

df_inventaire = df_inventaire['rune_craft_item_list']

# id des crafts

CRAFT_TYPE_MAP = {
    1:'Enchant_gem',
    2:'Grindstone',
    3:'Gemme_immemoriale',
    4:'Grindstone_immemoriale',
    5:'Ancienne_gemme',
    6:'Ancienne_grindstone',
}

# id des runes

# on reprend le dict set

# stat

# on reprend property

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

for i in track(range(0, nb_boucle), description="Déchiffrage des gemmes/runes..."):
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
    
#     Exemple découpage : item : 150814
#     rune : 15
#     stat : 8
#     quality : 14

df_inventaire = pd.DataFrame(df_inventaire)


# découpe le dictionnaire imbriqué en un dict = une variable
df_inventaire = extraire_variables_imbriquees(df_inventaire, 'rune_craft_item_list')

# on refait pour sortir toutes les variables de chaque dict.... et on concatène pour n'avoir qu'un seul dataframe
df_combine = extraire_variables_imbriquees(df_inventaire,0)
df_combine = df_combine[['craft_item_id', 'wizard_id', 'craft_type', 'craft_type_id', 'sell_value', 'amount' ,'type', 'rune', 'stat', 'quality']]

for i in track(range(1, len(df_inventaire.columns)), description="Création de l'inventaire..."):
    df_combine2 = extraire_variables_imbriquees(df_inventaire, i)
    df_combine2 = df_combine2[['craft_item_id', 'wizard_id', 'craft_type', 'craft_type_id', 'sell_value', 'amount' ,'type', 'rune', 'stat', 'quality']]
    df_combine = pd.concat([df_combine,df_combine2])
    
# On retient les variables utiles

df_inventaire = df_combine[['type', 'rune', 'stat', 'quality', 'amount']]

# on sort values

df_inventaire.sort_values(by=['rune'],  inplace=True)

fig = px.histogram(df_inventaire, x="rune", y="amount", color='type', title="Inventaire")
fig.write_image('resultat/Inventaire.png')




# # Export

# In[147]:


export_excel(data, data_short, df_rune, df_count, df_inventaire)



console = Console()

console.print("Terminé ! Tu peux fermer cette cmd et consulter le dossier resultat :smiley: ", style="green")

input()