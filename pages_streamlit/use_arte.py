import streamlit as st
import pandas as pd
import numpy as np
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.no_default_selectbox import selectbox
from st_pages import add_indentation
from fonctions.visualisation import filter_dataframe

from fonctions.visuel import css


css()

add_indentation()


def data_columns(data):
    return data.columns

def lignes_en_doublon(data):
    #Compte le nombre de doublons (lignes)
    return len(data)-len(data.drop_duplicates())

def cellules_manquantes_pourcentage(data):
    #Permet d'avoir un % de cellules manquantes
    return data.isna().sum().sum()/(data.size)

def supprimer_variables_peu_utilisables(data, condition): # 'nom' à améliorer
# Permet de supprimer les variables qui ont un nombre de données manquantes important. On calcule en fonction d'un % (condition)
    data_filtree = pd.DataFrame()
    data_filtree = data
    for column in data.columns: #on boucle sur chaque colonne de la Dataframe
        var_type = data[column].dtypes #on check le type de la colonne
        pourcentage_valeur_manquantes = cellules_manquantes_pourcentage(data[column])  #% de données manquant
        if var_type == 'float64' and float(pourcentage_valeur_manquantes) > condition: # si le type n'est pas float, ça ne peut pas marcher.
            data_filtree.drop(column, axis=1, inplace=True) #on drop l'intégralité de la colonne si le % manquant dépasse la condition...
    return data_filtree   



st.title('Où utiliser ?')
st.info("**Note** : Cet onglet étant nouveau, il peut y avoir des incohérences", icon="ℹ️")

add_vertical_space(1)

@st.cache_data
def charger_data_artefact():
    df = pd.read_excel('artifact_tool.xlsm', sheet_name='User monsters', header=3)
    df = supprimer_variables_peu_utilisables(df, 0.95,) # colonnes inutiles
    df.drop(['All\nOK?', 3, 2, 1, 'Owned'], axis=1, inplace=True) # colonnes inutiles
    df.dropna(thresh=10, inplace=True) # on retire les mobs qui ont pas assez d'info
    
    swarfarm = pd.read_excel('swarfarm.xlsx').drop('id', axis=1)
    
    swarfarm['url'] = swarfarm.apply(
                        lambda x:  f'https://swarfarm.com/static/herders/images/monsters/{x["image_filename"]}', axis=1)
    
    df = df.merge(swarfarm[['name', 'url', 'natural_stars']], how='left', left_on='Awakened', right_on='name').drop_duplicates(subset=['Awakened'])
    return df



dict_priority = {'Faible': 1, 'Moyen': 2, 'Elevé': 3}
def choose_stats(stats, key):
    stats = selectbox('Choisissez la stat à afficher', stats, key=f"{key}", no_selection_label='Aucun')
    priority = st.selectbox('Choisissez la priorité', ['Faible', 'Moyen', 'Elevé'], key=f"{key}2")
    priority = dict_priority[priority]
    
    return stats, priority
    
    
    
    


df_where_to_use = charger_data_artefact()

tab1, tab2 = st.tabs(['Recherche par Artefact', 'Recherche par Monstre'])

stats = df_where_to_use.columns.drop(['Family', 'Element', 'Awakened', 'Attribute', 'Preferred stats', 'Include', 'name', 'url', 'natural_stars'])

with tab1:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        stat1, priority1 = choose_stats(stats, 'stats1')
    with col2:
        stat2, priority2 = choose_stats(stats, 'stats2')

    add_vertical_space(1)    

    # col3, col4 = st.columns(2)
    with col3:
        stat3, priority3 = choose_stats(stats, 'stats3')
    with col4:
        stat4, priority4 = choose_stats(stats, 'stats4')

    df_final = df_where_to_use.copy()
    for stat, priority in zip([stat1, stat2, stat3, stat4], [priority1, priority2, priority3, priority4]):
        if stat != None:
            df_final = df_final[df_final[stat] >= priority]

    if stat1 == None and stat2 == None and stat3 == None and stat4 == None:
        st.warning('Veuillez sélectionner au moins une stat')
    else:
        # Modif DF
        df_final = df_final[['Awakened', 'Attribute', 'Element', 'Family', 'Preferred stats', 'url', 'natural_stars']]  
        
        df_final.columns = ['Monstre', 'Attribut', 'Element', 'Famille', 'Stats préférées', 'url', 'Etoiles']
        
        df_final['Stats préférées'] = df_final['Stats préférées'].str.replace('Any', 'Toutes')  
        
        # Filtre dispo    
        index_filter = filter_dataframe(
                df_final.drop(['url', 'Etoiles'], axis=1), 'data_build', type_number='int').index
        
        data_filter = df_final.loc[index_filter].dropna(subset='url').sort_values(by=['Etoiles', 'Famille'], ascending=[False, False])
        
        
        st.image(data_filter['url'].tolist(), width=50, caption=data_filter['Monstre'].tolist()) 
        
with tab2:
      
    monster = st.multiselect('Monstre', df_where_to_use['Awakened'].unique(), key='monster')
    
    df_monster = df_where_to_use[df_where_to_use['Awakened'].isin(monster)]\
        .drop(['Family', 'Element', 'Attribute', 'Preferred stats', 'Include', 'name', 'url', 'natural_stars'], axis=1)\
        .set_index('Awakened')
        
    df_monster.replace({0: '/', 1: 'Faible', 2: 'Moyen', 3 : 'Elevé' }, inplace=True)
    
    st.dataframe(df_monster, use_container_width=True)
    
    


st.caption('Made by Tomlora')