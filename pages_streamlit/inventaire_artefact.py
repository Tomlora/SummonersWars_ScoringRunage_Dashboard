
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from fonctions.visualisation import filter_dataframe
from streamlit_extras.colored_header import colored_header
import pandas as pd
from fonctions.export import export_excel
from fonctions.artefact import dict_arte_effect_english, dataframe_replace_to_english
from streamlit_extras.no_default_selectbox import selectbox
from st_pages import add_indentation
from fonctions.visuel import css
from datetime import timedelta


css()

add_indentation()




def inventaire_arte():


    data_inventaire : pd.DataFrame = st.session_state.data_arte.data_a.copy()

    data_inventaire.rename(columns={
        'arte_type': 'Type',
        'arte_attribut': 'Attribut',
        'arte_equiped': 'Equipé',
        'efficiency': 'efficience'
    }, inplace=True)
    
    if st.session_state.translations_selected == 'English':
        data_inventaire['Attribut'] = data_inventaire['Attribut'].replace(dataframe_replace_to_english)
        
        for column in ['first_sub', 'second_sub', 'third_sub', 'fourth_sub']:
            data_inventaire[column] = data_inventaire[column].replace(dict_arte_effect_english)
        
        options={'DMG INCREASED' : ['DMG INCREASED by % HP',
                           "DMG INCREASED by % ATK",
                           'DMG INCREASED by % DEF',
                           'DMG INCREASED by % SPD'],
             'REDUCTION' : ['REDUCTION DMG FROM FIRE',
                            'REDUCTION DMG FROM WATER',
                            'REDUCTION DMG FROM WIND',
                            'REDUCTION DMG FROM LIGHT',
                            'REDUCTION DMG FROM DARK'],
             'DMG TO' : ['DMG TO FIRE',
                          'DMG TO WATER',
                          'DMG TO WIND',
                          'DMG TO LIGHT',
                          'DMG TO DARK'],
             'HP LOST' : ['lost HP'],
             'CRIT DMG' : ['CRIT DMG RECU',
                           'CRIT DMG S1',
                           'CRIT DMG S2',
                           'CRIT DMG S3',
                           'CRIT DMG S4',
                           'CRIT DMG S3/S4',
                           'PREMIER HIT CRIT DMG'],
             'ACC' : ['ACC S1',
                            'ACC S2',
                            'ACC S3']} 
        
    else:
    
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


    check_v8 = st.checkbox(st.session_state.langue['fusion_substat_arte_v8'], help=st.session_state.langue['fusion_substat_arte_v8_help'])
    
    if check_v8:
        if st.session_state.translations_selected == 'Français':
            data_inventaire[['first_sub', 'second_sub', 'third_sub', 'fourth_sub']] = data_inventaire[['first_sub', 'second_sub', 'third_sub', 'fourth_sub']].replace({'RENFORCEMENT ATK' : 'RENFORCEMENT ATK/DEF', 
                                                                                                                                                'RENFORCEMENT DEF' : 'RENFORCEMENT ATK/DEF',
                                                                                                                                                'CRIT DMG S3' : 'CRIT DMG S3/S4',
                                                                                                                                                'CRIT DMG S4' : 'CRIT DMG S3/S4',
                                                                                                                                                'REVENGE' : 'REVENGE ET COOP',
                                                                                                                                                'COOP DMG' : 'REVENGE ET COOP',})
        
        elif st.session_state.translations_selected == 'English':
            data_inventaire[['first_sub', 'second_sub', 'third_sub', 'fourth_sub']] = data_inventaire[['first_sub', 'second_sub', 'third_sub', 'fourth_sub']].replace({'ATK Increased' : 'ATK/DEF Increased', 
                                                                                                                                                    'DEF Increased' : 'ATK/DEF Increased',
                                                                                                                                                    'CRIT DMG S3' : 'CRIT DMG S3/S4',
                                                                                                                                                    'CRIT DMG S4' : 'CRIT DMG S3/S4',
                                                                                                                                                    'REVENGE' : 'REVENGE AND COOP',
                                                                                                                                                    'COOP DMG' : 'REVENGE AND COOP',})
    rec_spec = selectbox(st.session_state.langue['recherche_spec'], options=list(options.keys()),
                 help=st.session_state.langue['recherche_spec_help_arte'],
                 index=0)
    
    if rec_spec != None:
        if rec_spec == 'DMG ELEMENTAIRE':
            rec_spec = st.session_state.langue['dmg_sur']
            
            
        nb_spec = st.slider(st.session_state.langue['nb_substat_mini'], min_value=1, max_value=4, value=1, step=1)
        
        
        data_inventaire['totalsub'] = data_inventaire['first_sub'] + data_inventaire['second_sub'] + data_inventaire['third_sub'] + data_inventaire['fourth_sub']
        
        data_grp = data_inventaire.groupby(['index']).agg({'totalsub':lambda x: ', '.join(tuple(x.tolist()))})
        data_grp['critere'] = data_grp['totalsub'].str.count(rec_spec)
                    
        
        data_inventaire = data_inventaire.merge(data_grp, on='index')
        
        data_inventaire = data_inventaire[data_inventaire['critere'] >= nb_spec]
        

        filter_detail = selectbox(st.session_state.langue['filter_one_substat'], options=options[rec_spec])
        if filter_detail != None:
            data_inventaire = data_inventaire[(data_inventaire['first_sub'].str.contains(filter_detail)) | (data_inventaire['second_sub'].str.contains(filter_detail)) | (data_inventaire['third_sub'].str.contains(filter_detail)) | (data_inventaire['fourth_sub'].str.contains(filter_detail))]
        
        st.text(st.session_state.langue['artefact_substat_mini'].format(nb_spec, rec_spec, data_inventaire.shape[0]))
        
        data_inventaire.drop(['totalsub_x', 'totalsub_y'], axis=1, inplace=True)
        
    data_inventaire.drop(['index'], axis=1, inplace=True)   
    df_filter = filter_dataframe(data_inventaire)

    st.dataframe(df_filter.sort_values('efficience', ascending=False))
    
    data_xlsx = export_excel(df_filter.sort_values('efficience', ascending=False), 'Id_Artefacts', 'Artefacts')

    st.download_button(st.session_state.langue['download_excel'], data_xlsx, file_name=f'artefacts {st.session_state["pseudo"]}.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    
    colored_header(
            label=st.session_state.langue['detail'],
            description="",
            color_name="blue-70",
        )
    
    check_detail_arte = st.checkbox(st.session_state.langue['show_detail'], value=False, key='detail_arte')
    
    if check_detail_arte:
        
        @st.cache_data(ttl=timedelta(minutes=30), show_spinner=st.session_state.langue['calcul_inventaire_arte'])
        def chargement_detail_inventaire(joueur_id, data_inventaire : pd.DataFrame):
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

            # NOTE : Cette étape est très lente  sans "observed"             
            pivot = melt.pivot_table(index=['Type', 'Attribut', 'Equipé', 'efficience', 'main_type'],
                                                columns='variable',
                                                values='value',
                                                aggfunc='first',
                                                observed=True,
                                                fill_value=0).reset_index()
                


            data_inventaire_final = data_inventaire.merge(pivot, on=['Type', 'Attribut', 'Equipé', 'efficience', 'main_type']).drop(columns=['Substat 1', 'Substat 2', 'Substat 3', 'Substat 4', 'Substat valeur 1', 'Substat valeur 2', 'Substat valeur 3', 'Substat valeur 4'])


            return data_inventaire_final
                
        data_inventaire_final = chargement_detail_inventaire(st.session_state.compteid, data_inventaire)
        
        df_filter2 = filter_dataframe(data_inventaire_final, key='filtrer_data')
                
        st.dataframe(df_filter2.sort_values('efficience', ascending=False))
        data_xlsx2 = export_excel(df_filter2.sort_values('efficience', ascending=False), 'Id_Artefacts', 'Artefacts')
                
        st.download_button('Télécharger la data (Excel)', data_xlsx2, file_name=f'artefacts_details {st.session_state["pseudo"]}.xlsx',
                                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
if 'submitted' in st.session_state:
    if st.session_state.submitted:
        st.title('Artefact')
        inventaire_arte()

    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')


st.caption('Made by Tomlora :sunglasses:')
