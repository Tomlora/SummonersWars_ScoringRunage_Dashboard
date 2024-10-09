
import streamlit as st
import pandas as pd
from fonctions.visuel import css
from params.coef import coef_set, order
from fonctions.artefact import visualisation_top_arte
from io import BytesIO




css()




def top_arte():
    liste_substat = st.session_state.data_arte.df_top['substat'].unique()
    df_arte = st.session_state.data_arte.df_top.copy()
                    
    liste_elementaire = ['FEU', 'EAU', 'VENT', 'LUMIERE', 'TENEBRE', 'INTANGIBLE']
    liste_attribut = ['ATTACK', 'DEFENSE', 'HP', 'SUPPORT', 'INTANGIBLE']
                    
                    
    col_elem, col_att = st.columns(2)
                    
    with col_elem:
        elem_only = st.checkbox('Elementaire seulement')
        download_data_arte = st.checkbox(f"{st.session_state.langue['download_excel']} ?",
                                                         help=st.session_state.langue['download_data_arte'])
    with col_att:
        attribut_only = st.checkbox('Attribut seulement')
                    
    if elem_only:
        df_arte = df_arte[df_arte['arte_attribut'].isin(liste_elementaire)]
                    
    if attribut_only:
        df_arte = df_arte[df_arte['arte_attribut'].isin(liste_attribut)]
                        
    if elem_only and attribut_only:
        st.warning(st.session_state.langue['combo_arte_error'])
                    
                    
                    
    def show_arte_table(keyword, substat, joueur_id, download_data: bool, exclure='None',):
                        
                       
                        i = 0
                        index_keyword = []
                        liste_df = {}
                        
                        for i in range(len(substat)):
                            if keyword in substat[i] and not exclure in substat[i]:
                                index_keyword.append(i)
                                
                        if len(index_keyword) >= 1:
                            
                            for n in range(0,len(index_keyword), 2):
                                element = index_keyword[n]
                                col_arte1, _, col_arte2 = st.columns([0.4,0.1,0.4])
                                with col_arte1:
                                    df_arte_filter = visualisation_top_arte(df_arte[['substat', 'arte_attribut', 'main_type', '1', '2', '3', '4', '5']], substat[element],
                                                        order=order)
                                    liste_df[substat[element][:30].replace('/', '|')] = df_arte_filter
                                try:
                                    if keyword in substat[element+1]:
                                        with col_arte2:
                                            df_arte_filter2 = visualisation_top_arte(df_arte[['substat', 'arte_attribut', 'main_type', '1', '2', '3', '4', '5']], substat[element+1],
                                                                order=order)
                                            liste_df[substat[element+1][:30].replace('/', '|')] = df_arte_filter2
                                            
                                except IndexError: # il n'y en a plus
                                    pass
                
                            if download_data:
                                output = BytesIO()

                                writer = pd.ExcelWriter(output, engine='xlsxwriter')
                                
                                for name, df_data in liste_df.items():
                                    
                                    df_data.to_excel(
                                        writer, startrow=1, sheet_name=name, index=True, header=True)

                                writer.close()

                                processed_data = output.getvalue()

                                st.download_button(st.session_state.langue['download_excel'], processed_data, file_name=f'artefact_{keyword}.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', key=element)         

    tab_reduc, tab_dmg, tab_dmg_supp, tab_precision, tab_crit, tab_soin, tab_renforcement, tab_perdus, tab_autres = st.tabs(['Réduction',
                                                                                        'Dégâts élémentaire',
                                                                                        'Degats supp',
                                                                                        'Précision',
                                                                                        'CRIT',
                                                                                        'SOIN',
                                                                                        'RENFORCEMENT',
                                                                                        'EN FONCTION PERDUS',
                                                                                        'AUTRES'])    

                        
    with tab_reduc:

                        show_arte_table('REDUCTION', liste_substat, st.session_state.compteid, download_data_arte)
                            
    with tab_dmg:

                        show_arte_table('DMG SUR', liste_substat, st.session_state.compteid, download_data_arte, 'CRIT')
                        
                        
    with tab_dmg_supp:

                        show_arte_table('DMG SUPP', liste_substat, st.session_state.compteid, download_data_arte)

                        
    with tab_precision:

                        show_arte_table('PRECISION', liste_substat, st.session_state.compteid, download_data_arte)

                        
    with tab_crit:

                        show_arte_table('CRIT', liste_substat, st.session_state.compteid, download_data_arte)
                        show_arte_table('PREMIER HIT CRIT DMG', liste_substat, st.session_state.compteid, download_data_arte)


    with tab_renforcement:

                        show_arte_table('RENFORCEMENT', liste_substat, st.session_state.compteid, download_data_arte)

    with tab_soin:

                        show_arte_table('SOIN', liste_substat, st.session_state.compteid, download_data_arte)
                        
    with tab_perdus:
                        show_arte_table('PERDUS', liste_substat, st.session_state.compteid, download_data_arte)
                        show_arte_table('DEF EN FONCTION', liste_substat, st.session_state.compteid, download_data_arte)


    with tab_autres:

                        col1, col2 = st.columns(2)
                        with col1:
                            show_arte_table('REVIVE', liste_substat, st.session_state.compteid, download_data_arte)
                            show_arte_table('BOMBE', liste_substat, st.session_state.compteid, download_data_arte)
                            show_arte_table('COOP', liste_substat, st.session_state.compteid, download_data_arte)
                            show_arte_table('REVENGE ET COOP', liste_substat, st.session_state.compteid, download_data_arte)
                        with col2:
                            show_arte_table('REVENGE', liste_substat, st.session_state.compteid, download_data_arte)
                            show_arte_table('VOL', liste_substat, st.session_state.compteid, download_data_arte)
                            show_arte_table('INCAPACITE', liste_substat, st.session_state.compteid, download_data_arte)


if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Top Artefact')
        top_arte()
    
    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")
    
    
st.caption('Made by Tomlora :sunglasses:')