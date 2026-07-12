
import streamlit as st
from fonctions.visualisation import filter_dataframe, load_pygwalker
from streamlit_extras.colored_header import colored_header
import pandas as pd
from fonctions.export import export_excel
from fonctions.artefact import dict_arte_effect_english, dataframe_replace_to_english
from streamlit_extras.no_default_selectbox import selectbox

from fonctions.visuel import css
from datetime import timedelta


css()






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
        

        colored_header(
            label=st.session_state.langue['analyse_poussee'],
            description="",
            color_name="blue-70",
        )
        if st.checkbox(st.session_state.langue["construire_tcd"]): 
            vis_spec = r"""{"config":[{"config":{"defaultAggregated":true,"geoms":["auto"],"coordSystem":"generic","limit":-1,"timezoneDisplayOffset":0},
            "encodings":
            {"dimensions":
            [
            {"fid":"Type","name":"Type","basename":"Type","semanticType":"nominal","analyticType":"dimension","offset":0},
            {"fid":"Attribut","name":"Attribut","basename":"Attribut","semanticType":"nominal","analyticType":"dimension","offset":0},
            {"fid":"Equipé","name":"Equipé","basename":"Equipé","semanticType":"nominal","analyticType":"dimension","offset":0},
            {"fid":"level","name":"level","basename":"level","semanticType":"quantitative","analyticType":"dimension","offset":0},
            {"fid":"main_type","name":"main_type","basename":"main_type","semanticType":"nominal","analyticType":"dimension","offset":0},
            {"fid":"gw_mea_key_fid","name":"Measure names","analyticType":"dimension","semanticType":"nominal"}],
            "measures":
            [
            {"fid":"efficience","name":"efficience","basename":"efficience","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"SPD EN CAS D'INCAPACITE","name":"SPD EN CAS D'INCAPACITE","basename":"SPD EN CAS D'INCAPACITE","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"REVENGE ET COOP","name":"REVENGE ET COOP","basename":"REVENGE ET COOP","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"REVENGE","name":"REVENGE","basename":"REVENGE","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"RENFORCEMENT DEF","name":"RENFORCEMENT DEF","basename":"RENFORCEMENT DEF","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"RENFORCEMENT CRITRATE","name":"RENFORCEMENT CRITRATE","basename":"RENFORCEMENT CRITRATE","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"RENFORCEMENT ATK","name":"RENFORCEMENT ATK","basename":"RENFORCEMENT ATK","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"PREMIER HIT CRIT DMG","name":"PREMIER HIT CRIT DMG","basename":"PREMIER HIT CRIT DMG","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"HP REVIVE","name":"HP REVIVE","basename":"HP REVIVE","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"DMG SUR VENT","name":"DMG SUR VENT","basename":"DMG SUR VENT","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"DMG SUR FEU","name":"DMG SUR FEU","basename":"DMG SUR FEU","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"DMG SUR DARK","name":"DMG SUR DARK","basename":"DMG SUR DARK","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"DMG SUPP EN FONCTION DE LA DEF","name":"DMG SUPP EN FONCTION DE LA DEF","basename":"DMG SUPP EN FONCTION DE LA DEF","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"DMG SUPP EN FONCTION DE L'ATQ","name":"DMG SUPP EN FONCTION DE L'ATQ","basename":"DMG SUPP EN FONCTION DE L'ATQ","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"CRUSHING DMG","name":"CRUSHING DMG","basename":"CRUSHING DMG","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"CRIT DMG SUR CIBLE UNIQUE","name":"CRIT DMG SUR CIBLE UNIQUE","basename":"CRIT DMG SUR CIBLE UNIQUE","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"CRIT DMG S4","name":"CRIT DMG S4","basename":"CRIT DMG S4","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"CRIT DMG S3/S4","name":"CRIT DMG S3/S4","basename":"CRIT DMG S3/S4","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"CRIT DMG S3","name":"CRIT DMG S3","basename":"CRIT DMG S3","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"CRIT DMG RECU","name":"CRIT DMG RECU","basename":"CRIT DMG RECU","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"COOP DMG","name":"COOP DMG","basename":"COOP DMG","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"BOMBE DMG","name":"BOMBE DMG","basename":"BOMBE DMG","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"ATK EN FONCTION HP PERDUS","name":"ATK EN FONCTION HP PERDUS","basename":"ATK EN FONCTION HP PERDUS","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"ATB REVIVE","name":"ATB REVIVE","basename":"ATB REVIVE","semanticType":"quantitative","analyticType":"measure","offset":0},
            {"fid":"CRIT DMG EN FONCTION DES HP ELEVES","name":"CRIT DMG EN FONCTION DES HP ELEVES","basename":"CRIT DMG EN FONCTION DES HP ELEVES","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"CRIT DMG EN FONCTION DES HP FAIBLES","name":"CRIT DMG EN FONCTION DES HP FAIBLES","basename":"CRIT DMG EN FONCTION DES HP FAIBLES","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"CRIT DMG S1","name":"CRIT DMG S1","basename":"CRIT DMG S1","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"CRIT DMG S2","name":"CRIT DMG S2","basename":"CRIT DMG S2","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"DEF EN FONCTION HP PERDUS","name":"DEF EN FONCTION HP PERDUS","basename":"DEF EN FONCTION HP PERDUS","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"DMG SUPP EN FONCTION DE LA SPD","name":"DMG SUPP EN FONCTION DE LA SPD","basename":"DMG SUPP EN FONCTION DE LA SPD","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"DMG SUPP EN FONCTION DES HP","name":"DMG SUPP EN FONCTION DES HP","basename":"DMG SUPP EN FONCTION DES HP","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"DMG SUR EAU","name":"DMG SUR EAU","basename":"DMG SUR EAU","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"DMG SUR LUMIERE","name":"DMG SUR LUMIERE","basename":"DMG SUR LUMIERE","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"PRECISION S1","name":"PRECISION S1","basename":"PRECISION S1","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"PRECISION S2","name":"PRECISION S2","basename":"PRECISION S2","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"PRECISION S3","name":"PRECISION S3","basename":"PRECISION S3","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"REDUCTION SUR DARK","name":"REDUCTION SUR DARK","basename":"REDUCTION SUR DARK","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"REDUCTION SUR EAU","name":"REDUCTION SUR EAU","basename":"REDUCTION SUR EAU","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"REDUCTION SUR FEU","name":"REDUCTION SUR FEU","basename":"REDUCTION SUR FEU","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"REDUCTION SUR LUMIERE","name":"REDUCTION SUR LUMIERE","basename":"REDUCTION SUR LUMIERE","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"REDUCTION SUR VENT","name":"REDUCTION SUR VENT","basename":"REDUCTION SUR VENT","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"RENFORCEMENT ATK/DEF","name":"RENFORCEMENT ATK/DEF","basename":"RENFORCEMENT ATK/DEF","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"RENFORCEMENT SPD","name":"RENFORCEMENT SPD","basename":"RENFORCEMENT SPD","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"SOIN S1","name":"SOIN S1","basename":"SOIN S1","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"SOIN S2","name":"SOIN S2","basename":"SOIN S2","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"SOIN S3","name":"SOIN S3","basename":"SOIN S3","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"SPD EN FONCTION HP PERDUS","name":"SPD EN FONCTION HP PERDUS","basename":"SPD EN FONCTION HP PERDUS","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"VOL DE VIE","name":"VOL DE VIE","basename":"VOL DE VIE","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},
            {"fid":"gw_count_fid","name":"Row count","analyticType":"measure","semanticType":"quantitative","aggName":"sum","computed":true,
            "expression":{"op":"one","params":[],"as":"gw_count_fid"}},{"fid":"gw_mea_val_fid","name":"Measure values","analyticType":"measure","semanticType":"quantitative","aggName":"sum"}],"rows":[],"columns":[],"color":[],"opacity":[],"size":[],"shape":[],"radius":[],"theta":[],"longitude":[],"latitude":[],"geoId":[],"details":[],"filters":[],"text":[]},"layout":{"showActions":false,"showTableSummary":false,"stack":"stack","interactiveScale":false,"zeroScale":true,"size":{"mode":"auto","width":320,"height":200},"format":{},"geoKey":"name","resolve":{"x":false,"y":false,"color":false,"opacity":false,"shape":false,"size":false}},"visId":"gw_KJs5","name":"Chart 1"}],"chart_map":{},"workflow_list":[{"workflow":[{"type":"view","query":[{"op":"raw","fields":[]}]}]}],"version":"0.4.9.13"}"""

            pyg = load_pygwalker(df_filter2, vis_spec)
            pyg.explorer()

    
if 'submitted' in st.session_state:
    if st.session_state.submitted:
        st.title('Artefact')
        inventaire_arte()

    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")


st.caption('Made by Tomlora :sunglasses:')
