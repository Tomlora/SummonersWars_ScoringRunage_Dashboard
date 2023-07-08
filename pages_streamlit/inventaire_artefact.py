
import streamlit as st
from fonctions.gestion_bdd import requete_perso_bdd
from fonctions.artefact import Artefact
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.dataframe_explorer import dataframe_explorer
from fonctions.visualisation import filter_dataframe
from streamlit_extras.colored_header import colored_header
import pandas as pd
from fonctions.export import export_excel
from streamlit_extras.no_default_selectbox import selectbox

from st_pages import add_indentation
from fonctions.visuel import css
css()

add_indentation()




def inventaire_arte():

    st.session_state.data_arte.identify_monsters(
        st.session_state.identification_monsters)

    data_inventaire : pd.DataFrame = st.session_state.data_arte.data_a.copy()

    data_inventaire.rename(columns={
        'arte_type': 'Type',
        'arte_attribut': 'Attribut',
        'arte_equiped': 'Equipé',
        'efficiency': 'efficience'
    }, inplace=True)
    
    options={'DMG SUPP' : ['DMG SUPP EN FONCTION DES HP',
                           "DMG SUPP EN FONCTION DE L'ATQ",
                           'DMG SUPP EN FONCTION DE LA DEF',
                           'DMG SUPP EN FONCTION DE LA SPD'],
             'REDUCTION' : ['REDUCTION SUR FEU',
                            'REDUCTION SUR EAU',
                            'REDUCTION SUR VENT',
                            'REDUCTION SUR LUMIERE',
                            'REDUCTION SUR DARK'],
             'DMG SUR' : ['DMG SUR FEU',
                          'DMG SUR EAU',
                          'DMG SUR VENT',
                          'DMG SUR LUMIERE',
                          'DMG SUR DARK'],
             'HP PERDUS' : ['HP PERDUS'],
             'CRIT DMG' : ['CRIT DMG RECU',
                           'CRIT DMG S1',
                           'CRIT DMG S2',
                           'CRIT DMG S3',
                           'CRIT DMG S4',
                           'CRIT DMG S3/S4',
                           'PREMIER HIT CRIT DMG'],
             'PRECISION' : ['PRECISION S1',
                            'PRECISION S2',
                            'PRECISION S3']} 

    data_inventaire.drop(['unit_style', 'main_value', 'first_sub_value_max', 'second_sub_value_max', 'third_sub_value_max', 'fourth_sub_value_max'], axis=1, inplace=True)


    check_v8 = st.checkbox('Fusionner les anciens substats avec ceux de la v8 ?', help='Si coché, il peut donc y avoir des doublons dans les substats')
    
    if check_v8:
        data_inventaire[['first_sub', 'second_sub', 'third_sub', 'fourth_sub']] = data_inventaire[['first_sub', 'second_sub', 'third_sub', 'fourth_sub']].replace({'RENFORCEMENT ATK' : 'RENFORCEMENT ATK/DEF', 
                                                                                                                                                'RENFORCEMENT DEF' : 'RENFORCEMENT ATK/DEF',
                                                                                                                                                'CRIT DMG S3' : 'CRIT DMG S3/S4',
                                                                                                                                                'CRIT DMG S4' : 'CRIT DMG S3/S4',
                                                                                                                                                'REVENGE' : 'REVENGE ET COOP',
                                                                                                                                                'COOP DMG' : 'REVENGE ET COOP',})
    rec_spec = selectbox('Recherche spécifique', options=list(options.keys()),
                 help='Permet de filtrer les artefacts en fonction de leur substat sur plusieurs lignes',
                 index=0)
    
    if rec_spec != None:
        if rec_spec == 'DMG ELEMENTAIRE':
            rec_spec = 'DMG SUR'
            
            
        nb_spec = st.slider('Nombre de substats minimum', min_value=1, max_value=4, value=1, step=1)
        
        
        data_inventaire['totalsub'] = data_inventaire['first_sub'] + data_inventaire['second_sub'] + data_inventaire['third_sub'] + data_inventaire['fourth_sub']
        
        data_grp = data_inventaire.groupby(['index']).agg({'totalsub':lambda x: ', '.join(tuple(x.tolist()))})
        data_grp['critere'] = data_grp['totalsub'].str.count(rec_spec)
                    
        
        data_inventaire = data_inventaire.merge(data_grp, on='index')
        
        data_inventaire = data_inventaire[data_inventaire['critere'] >= nb_spec]
        

        filter_detail = selectbox('Filtrer sur une substat', options=options[rec_spec])
        if filter_detail != None:
            data_inventaire = data_inventaire[(data_inventaire['first_sub'].str.contains(filter_detail)) | (data_inventaire['second_sub'].str.contains(filter_detail)) | (data_inventaire['third_sub'].str.contains(filter_detail)) | (data_inventaire['fourth_sub'].str.contains(filter_detail))]
        
        st.text('Artefacts avec au moins {} substats {} : {}'.format(nb_spec, rec_spec, data_inventaire.shape[0]))
        
        data_inventaire.drop(['totalsub_x', 'totalsub_y'], axis=1, inplace=True)
        
    data_inventaire.drop(['index'], axis=1, inplace=True)   
    df_filter = filter_dataframe(data_inventaire)

    st.dataframe(df_filter.sort_values('efficience', ascending=False))
    
    data_xlsx = export_excel(df_filter.sort_values('efficience', ascending=False), 'Id_Artefacts', 'Artefacts')

    st.download_button('Télécharger la data (Excel)', data_xlsx, file_name='artefacts.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    
    colored_header(
            label="Detaillé",
            description="",
            color_name="blue-70",
        )
    
    
    data_inventaire.rename(columns={'first_sub' : 'Substat 1', 'second_sub' : 'Substat 2', 'third_sub' : 'Substat 3', 'fourth_sub' : 'Substat 4',
                                    'first_sub_value' : 'Substat valeur 1', 'second_sub_value' : 'Substat valeur 2', 'third_sub_value' : 'Substat valeur 3', 'fourth_sub_value' : 'Substat valeur 4'},
                           inplace=True)
    
    


    melt = data_inventaire.melt(id_vars=['Type', 'Attribut', 'Equipé', 'efficience', 'main_type', 'Substat 1', 'Substat 2', 'Substat 3', 'Substat 4'],
                        value_vars=['Substat valeur 1', 'Substat valeur 2', 'Substat valeur 3', 'Substat valeur 4'])

    def changement_variable(x):
        number = x.variable[-1]
        type = x[f'Substat {number}']
                    
        return type
    
    melt['variable'] = melt.apply(changement_variable, axis=1)
                
    pivot = melt.pivot_table(index=['Type', 'Attribut', 'Equipé', 'efficience', 'main_type'],
                                    columns='variable',
                                    values='value',
                                    aggfunc='first',
                                    fill_value=0).reset_index()
    

    data_inventaire = data_inventaire.merge(pivot, on=['Type', 'Attribut', 'Equipé', 'efficience', 'main_type']).drop(columns=['Substat 1', 'Substat 2', 'Substat 3', 'Substat 4', 'Substat valeur 1', 'Substat valeur 2', 'Substat valeur 3', 'Substat valeur 4'])

    st.dataframe(data_inventaire.sort_values('efficience', ascending=False))
    
    
    df_filter2 = filter_dataframe(data_inventaire, key='filtrer_data')
    data_xlsx2 = export_excel(df_filter2.sort_values('efficience', ascending=False), 'Id_Artefacts', 'Artefacts')
    
    st.download_button('Télécharger la data (Excel)', data_xlsx2, file_name='artefacts_details.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
if 'submitted' in st.session_state:
    if st.session_state.submitted:
        st.title('Artefact')
        inventaire_arte()

    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')


st.caption('Made by Tomlora')
