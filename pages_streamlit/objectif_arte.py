import streamlit as st
import pandas as pd
from fonctions.visuel import load_lottieurl, css
from fonctions.artefact import dataframe_replace_to_english, dict_arte_effect_english
from streamlit_extras.switch_page_button import switch_page
from fonctions.gestion_bdd import lire_bdd_perso, requete_perso_bdd
import plotly.graph_objects as go
from streamlit_extras.add_vertical_space import add_vertical_space
import numpy as np


from st_pages import add_indentation
css()

add_indentation()




def objectif():
    data_arte : pd.DataFrame = st.session_state.data_arte.df_top.copy()
    
    

    
    def download_params(id_compte):
        df_params = lire_bdd_perso(f'''SELECT * from sw_objectifs_arte WHERE id = {id_compte} ''', index_col='id').T
        
        if df_params.empty:
            return [10, 10, 10, 10, 10, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True]
        else:
            return df_params.iloc[0].tolist()
            
    liste_params = download_params(st.session_state.id_joueur)
    
    def checkbox_stat(dict_params, value, defaut1, defaut2, defaut3):
        col1, col2, col3 = st.columns(3)
        with col1:
            dict_params[f'{value}_HP'] = st.checkbox('HP', value=defaut1, key=f'{value}_HP')
        with col2:
            dict_params[f'{value}_ATK'] = st.checkbox('ATK', value=defaut2, key=f'{value}_ATK')
        with col3:
            dict_params[f'{value}_DEF'] = st.checkbox('DEF', value=defaut3, key=f'{value}_DEF')
        
        return dict_params
        
        
    param_objectifs = {}
    with st.expander('Paramètres'):
        param_objectifs['REDUCTION'] = st.slider(f'{st.session_state.langue["objectif"]} Reduction', 10, 30, liste_params[0])
        param_objectifs = checkbox_stat(param_objectifs, 'REDUCTION', liste_params[5], liste_params[6], liste_params[7])
        param_objectifs['DMG ELEM'] = st.slider(f'{st.session_state.langue["objectif"]} DMG ELEM', 10, 30, liste_params[1])
        param_objectifs = checkbox_stat(param_objectifs, 'DMG ELEM', liste_params[8], liste_params[9], liste_params[10])
        param_objectifs['CRIT DMG'] = st.slider(f'{st.session_state.langue["objectif"]} CRIT DMG', 10, 30, liste_params[2])
        param_objectifs = checkbox_stat(param_objectifs, 'CRIT DMG', liste_params[11], liste_params[12], liste_params[13])
        param_objectifs['PRECISION'] = st.slider(f'{st.session_state.langue["objectif"]} PRECISION', 10, 30, liste_params[3])
        param_objectifs = checkbox_stat(param_objectifs, 'PRECISION', liste_params[14], liste_params[15], liste_params[16])
        param_objectifs['SOIN'] = st.slider(f'{st.session_state.langue["objectif"]} SOIN', 10, 30, liste_params[4])
        param_objectifs = checkbox_stat(param_objectifs, 'SOIN', liste_params[17], liste_params[18], liste_params[19])
        param_objectifs['SPD'] = st.slider(f'{st.session_state.langue["objectif"]} SPD', 10, 60, liste_params[4])
        param_objectifs = checkbox_stat(param_objectifs, 'SPD', liste_params[17], liste_params[18], liste_params[19])

    
        if st.button(st.session_state.langue['sauvegarder']):
            requete_perso_bdd('''
                              DELETE FROM sw.sw_objectifs_arte
	                          WHERE id = :id;
                              INSERT INTO sw.sw_objectifs_arte(
                            id, reduction, dmg_elem, crit_dmg, "precision", soin, reduction_hp, reduction_atk, reduction_def, dmg_elem_hp, dmg_elem_atk,
                            dmg_elem_def, crit_dmg_hp, crit_dmg_atk, crit_dmg_def, precision_hp, precision_atk, precision_def,
                            soin_hp, soin_atk, soin_def, spd, spd_hp, spd_atk, spd_def)
                            VALUES (:id, :reduction, :dmg_elem, :crit_dmg, :precision, :soin, :reduction_hp, :reduction_atk, :reduction_def, :dmg_elem_hp, :dmg_elem_atk,
                            :dmg_elem_def, :crit_dmg_hp, :crit_dmg_atk, :crit_dmg_def, :precision_hp, :precision_atk, :precision_def,
                            :soin_hp, :soin_atk, :soin_def, :spd, :spd_hp, :spd_atk, :spd_def);  ''',
                                dict_params={'id' : st.session_state.id_joueur,
                                             'reduction' : param_objectifs['REDUCTION'],
                                             'dmg_elem' : param_objectifs['DMG ELEM'],
                                             'crit_dmg' : param_objectifs['CRIT DMG'],
                                             'precision' : param_objectifs['PRECISION'],
                                             'soin' : param_objectifs['SOIN'],
                                             'reduction_hp' : param_objectifs['REDUCTION_HP'],
                                             'reduction_def' : param_objectifs['REDUCTION_DEF'],
                                             'reduction_atk' : param_objectifs['REDUCTION_ATK'],
                                             'dmg_elem_hp' : param_objectifs['DMG ELEM_HP'],
                                             'dmg_elem_atk' : param_objectifs['DMG ELEM_ATK'],
                                             'dmg_elem_def' : param_objectifs['DMG ELEM_DEF'],
                                             'crit_dmg_hp' : param_objectifs['CRIT DMG_HP'],
                                             'crit_dmg_atk' : param_objectifs['CRIT DMG_ATK'],
                                             'crit_dmg_def' : param_objectifs['CRIT DMG_DEF'],
                                             'precision_hp' : param_objectifs['PRECISION_HP'],
                                             'precision_atk' : param_objectifs['PRECISION_ATK'],
                                             'precision_def' : param_objectifs['PRECISION_DEF'],
                                             'soin_hp' : param_objectifs['SOIN_HP'],
                                             'soin_atk' : param_objectifs['SOIN_ATK'],
                                             'soin_def' : param_objectifs['SOIN_DEF'],
                                             'spd' : param_objectifs['SPD'],
                                             'spd_hp' : param_objectifs['SPD_HP'],
                                             'spd_atk' : param_objectifs['SPD_ATK'],
                                             'spd_def' : param_objectifs['SPD_DEF']})
            
            st.success(':v:')
        
    
    if st.session_state.translations_selected == 'English':
        data_arte['arte_attribut'] = data_arte['arte_attribut'].replace(dataframe_replace_to_english)

        data_arte['substat'] = data_arte['substat'].replace(dict_arte_effect_english)
        
        options={ #'DMG INCREASED' : ['DMG INCREASED by % HP',
                        #    "DMG INCREASED by % ATK",
                        #    'DMG INCREASED by % DEF',
                        #    'DMG INCREASED by % SPD'],
             'REDUCTION' : ['REDUCTION DMG FROM FIRE',
                            'REDUCTION DMG FROM WATER',
                            'REDUCTION DMG FROM WIND',
                            'REDUCTION DMG FROM LIGHT',
                            'REDUCTION DMG FROM DARK'],
             'DMG ELEM' : ['DMG TO FIRE',
                          'DMG TO WATER',
                          'DMG TO WIND',
                          'DMG TO LIGHT',
                          'DMG TO DARK'],
             'CRIT DMG' : ['CRIT DMG RECU',
                           'CRIT DMG S1',
                           'CRIT DMG S2',
                           'CRIT DMG S3',
                           'CRIT DMG S4',
                           'CRIT DMG S3/S4',
                           'PREMIER HIT CRIT DMG'],
             'PRECISION' : ['ACC S1',
                            'ACC S2',
                            'ACC S3'],
             'SOIN' : ['HEAL S1', 
                       'HEAL S2',
                       'HEAL S3'],
             'SPD' : ['SPD Increased']} 
        
        data_arte[['substat']] = data_arte[['substat']].replace({'ATK Increased' : 'ATK/DEF Increased', 
                                                                'DEF Increased' : 'ATK/DEF Increased',
                                                                'CRIT DMG S3' : 'CRIT DMG S3/S4',
                                                                'CRIT DMG S4' : 'CRIT DMG S3/S4',
                                                                'REVENGE' : 'REVENGE AND COOP',
                                                                 'COOP DMG' : 'REVENGE AND COOP',})  
        
    else:
    
        options={ #'DMG SUPP' : ['DMG SUPP EN FONCTION DES HP',
                            # "DMG SUPP EN FONCTION DE L'ATQ",
                            # 'DMG SUPP EN FONCTION DE LA DEF',
                            # 'DMG SUPP EN FONCTION DE LA SPD'],
                'REDUCTION' : ['REDUCTION SUR FEU',
                                'REDUCTION SUR EAU',
                                'REDUCTION SUR VENT',
                                'REDUCTION SUR LUMIERE',
                                'REDUCTION SUR DARK'],
                'DMG ELEM' : ['DMG SUR FEU',
                            'DMG SUR EAU',
                            'DMG SUR VENT',
                            'DMG SUR LUMIERE',
                            'DMG SUR DARK'],
                'CRIT DMG' : ['CRIT DMG S1',
                            'CRIT DMG S2',
                            'CRIT DMG S3',
                            'CRIT DMG S4',
                            'CRIT DMG S3/S4',
                            'PREMIER HIT CRIT DMG'],
                'PRECISION' : ['PRECISION S1',
                                'PRECISION S2',
                                'PRECISION S3'],
                'SOIN' : ['SOIN S1',
                          'SOIN S2',
                          'SOIN S3'],
                'SPD' : ['RENFORCEMENT SPD']} 

        data_arte[['substat']] = data_arte[['substat']].replace({'RENFORCEMENT ATK' : 'RENFORCEMENT ATK/DEF', 
                                                                'RENFORCEMENT DEF' : 'RENFORCEMENT ATK/DEF',
                                                                'CRIT DMG S3' : 'CRIT DMG S3/S4',
                                                                'CRIT DMG S4' : 'CRIT DMG S3/S4',
                                                                'REVENGE' : 'REVENGE ET COOP',
                                                                'COOP DMG' : 'REVENGE ET COOP',})
        
    reduction, dmg_sur, crit_dmg, precision, soin, spd = st.tabs(['REDUCTION', 'DMG ELEM', 'CRIT DMG', st.session_state.langue["precision"], st.session_state.langue["soin"], 'SPD'])  
    
    dict_tab = {'REDUCTION' : reduction,
                'DMG ELEM' : dmg_sur,
                'CRIT DMG' : crit_dmg,
                'PRECISION' : precision,
                'SOIN' : soin,
                'SPD' : spd}  
    
    dict_true = {}
    dict_true_max = {} 
    dict_diff = {}
            
    for main_stat in data_arte['main_type'].unique():
        data_filter : pd.DataFrame = data_arte[data_arte['main_type'] == main_stat]
        
        for key, stats in options.items():
            
            if param_objectifs[f'{key}_{main_stat}']:
                with dict_tab[key]:
                    data_filter2 = data_filter[data_filter['substat'].isin(stats)]
                
                
                    data_filter2['count'] = (data_filter2[['1', '2', '3', '4', '5']] > param_objectifs[key]).sum(axis=1)
                    
                    df_to_show = data_filter2.pivot_table(values='count',
                                                        index='substat',
                                                        columns='arte_attribut',
                                                        fill_value=0)
                    
                    df_bool = df_to_show >= 1
                    
                    
                    if not key in dict_true.keys():
                        dict_true[key] = df_bool.sum(axis=0).sum()
                        dict_true_max[key] = df_bool.count(axis=0).sum()
                        dict_diff[key] = 0
                    
                    else:
                        dict_true[key] = dict_true[key] + df_bool.sum(axis=0).sum()
                        dict_true_max[key] = dict_true_max[key] + df_bool.count(axis=0).sum()
                        dict_diff[key] = dict_true_max[key] - dict_true[key]                    
                    
                    st.subheader(f'{main_stat} > {param_objectifs[key]}')
                    
                    st.dataframe(df_bool,
                                use_container_width=True,
                                height=225)
        
    df_final = pd.DataFrame.from_dict([dict_true, dict_true_max, dict_diff])
 
   
    fig = go.Figure()
    
    trace1 = go.Bar(x=df_final.columns, y=df_final.loc[0], name='Réalisé')
    trace2 = go.Bar(x=df_final.columns, y=df_final.loc[1], name=st.session_state.langue["objectif"])
   
    fig.add_traces([trace1, trace2])
    
    # ---- Par Substat
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(fig)
        
    with col2:
        df_final_t = df_final.T.reset_index()
        df_final_t['Progression'] = np.round(df_final_t[0] / df_final_t[1] * 100,2)
        df_final_t['Type'] = np.where(df_final_t['index'].isin(['REDUCTION', 'DMG ELEM']), 'ELEMENT', 'ATTRIBUT')
        
        add_vertical_space(7)
        st.dataframe(df_final_t[['index', 'Progression']].sort_values(by='Progression', ascending=False),
                     use_container_width=True)

    fig.update_layout(
        title="Par Substat",
        xaxis_title="Substat",
        yaxis_title="Quantité",
    )
        

    # ---- Par Type
    df_grp = df_final_t.groupby('Type', as_index=False).sum()
    df_grp['Progression'] = np.round(df_grp[0] / df_grp[1] * 100,2)
        
    
    fig = go.Figure()
    
    trace1 = go.Bar(x=df_grp['Type'], y=df_grp[0], name='Réalisé')
    trace2 = go.Bar(x=df_grp['Type'], y=df_grp[1], name=st.session_state.langue["objectif"])
   
    fig.add_traces([trace1, trace2])
    
    fig.update_layout(
        title="Par Type",
        xaxis_title="Type",
        yaxis_title="Quantité",
    )
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.plotly_chart(fig)
        
    with col4:
        add_vertical_space(7)
        st.dataframe(df_grp[['Type', 'Progression']].sort_values(by='Progression', ascending=False),
                     use_container_width=True)
                
if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title(st.session_state.langue["objectif"])
        objectif()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')
    
    
st.caption('Made by Tomlora :sunglasses:')