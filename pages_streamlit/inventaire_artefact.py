
import streamlit as st
from fonctions.gestion_bdd import requete_perso_bdd
from fonctions.artefact import Artefact
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.dataframe_explorer import dataframe_explorer
from fonctions.visualisation import filter_dataframe
import pandas as pd
from fonctions.export import export_excel

from st_pages import add_indentation

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
    
    data_inventaire.drop(['unit_style', 'main_value', 'first_sub_value_max', 'second_sub_value_max', 'third_sub_value_max', 'fourth_sub_value_max'], axis=1, inplace=True)

    rec_spec = st.selectbox('Recherche spécifique', options=['AUCUN', 'DMG SUPP', 'REDUCTION', 'DMG ELEMENTAIRE', 'HP PERDUS', 'CRIT DMG'],
                 help='Permet de filtrer les artefacts en fonction de leur substat sur plusieurs lignes',
                 index=0)
    
    if rec_spec != 'AUCUN':
        if rec_spec == 'DMG ELEMENTAIRE':
            rec_spec = 'DMG SUR'
            
        nb_spec = st.slider('Nombre de substats minimum', min_value=1, max_value=4, value=1, step=1)
        
        data_inventaire['totalsub'] = data_inventaire['first_sub'] + data_inventaire['second_sub'] + data_inventaire['third_sub'] + data_inventaire['fourth_sub']
        
        data_grp = data_inventaire.groupby(['index']).agg({'totalsub':lambda x: ', '.join(tuple(x.tolist()))})
        data_grp['critere'] = data_grp['totalsub'].str.count(rec_spec)
        
        data_inventaire = data_inventaire.merge(data_grp, on='index')
        
        data_inventaire = data_inventaire[data_inventaire['critere'] >= nb_spec]
        
        st.text('Artefacts avec au moins {} substats {} : {}'.format(nb_spec, rec_spec, data_inventaire.shape[0]))
        
        data_inventaire.drop(['totalsub_x', 'totalsub_y'], axis=1, inplace=True)
        
    data_inventaire.drop(['index'], axis=1, inplace=True)   
    df_filter = filter_dataframe(data_inventaire)

    st.dataframe(df_filter)
    
    data_xlsx = export_excel(df_filter, 'Id_Artefacts', 'Artefacts')

    st.download_button('Télécharger la data (Excel)', data_xlsx, file_name='artefacts.xlsx',
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
