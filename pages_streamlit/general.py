
import streamlit as st
import plotly.graph_objects as go
import plotly_express as px
import pandas as pd
from fonctions.visuel import css, page_header, section_header
from params.coef import coef_set
from fonctions.visualisation import filter_dataframe, table_with_images
from fonctions.gestion_bdd import requete_perso_bdd, sauvegarde_bdd
import traceback




css()




new_index = ['Autre', 'Seal', 'Despair', 'Destroy', 'Violent', 'Will', 'Intangible', 'Total']
new_index_spd = ['Autre', 'Seal', 'Despair', 'Destroy', 'Swift', 'Violent', 'Will', 'Intangible', 'Total']

def show_img_monsters(user_id, data, stars, variable='*', width=70, ):

    data = data[data[variable] == stars]

    st.subheader(f'{stars} etoiles ({data.shape[0]} monstres)')

    if width <= 50:
        return st.image(data['url'].tolist(), width=width)    
    else:
        return st.image(data['url'].tolist(), width=width, caption=data['name'].tolist())


def get_img_runes(df : pd.DataFrame):
    if not "set" in df.columns:
        df.insert(0, 'set', df.index)
        try:
            df['img'] = df['set'].apply(lambda x: f'https://raw.githubusercontent.com/swarfarm/swarfarm/master/herders/static/herders/images/runes/{x.lower()}.png')
        except AttributeError:
            pass
    
    return df

def general_page():
    
    if 'submitted' in st.session_state:
        if st.session_state.submitted:
            

            page_header(
                f'{st.session_state.pseudo} · {st.session_state.guilde}',
                'Vue synthétique de la qualité des runes, de la vitesse et des artéfacts du compte.',
                icon='📚',
                eyebrow='Vue d’ensemble',
            )

            # self.data_set = map_stats(self.data_set, ['innate_type', 'first_sub', 'second_sub', 'third_sub', 'fourth_sub', 'main_type'])

            # -------------- Scoring du compte
            try:
                analysis_date = (
                    st.session_state.tcd.iloc[0].get('date', '—')
                    if not st.session_state.tcd.empty
                    else '—'
                )

                kpi_rune, kpi_speed, kpi_arte, kpi_date = st.columns(4)
                kpi_rune.metric(
                    st.session_state.langue['Score_Rune'],
                    st.session_state['score'],
                )
                kpi_speed.metric(
                    st.session_state.langue['Score_Speed'],
                    st.session_state['score_spd'],
                )
                kpi_arte.metric(
                    st.session_state.langue['Score_Arte'],
                    st.session_state['score_arte'],
                )
                kpi_date.metric('Dernière analyse', analysis_date)

                section_header(
                    'Répartition des runes',
                    'Nombre de runes par palier d’efficience et par set prioritaire.',
                )

                st.session_state.tcd = get_img_runes(st.session_state.tcd)
                st.session_state.tcd.rename(
                    columns={100: '100', 110: '110', 120: '120'},
                    inplace=True,
                )
                st.dataframe(
                    st.session_state.tcd[['set', '100', '110', '120', 'img']]
                    .reindex(new_index)
                    .set_index('img')
                    .dropna(how='all'),
                    use_container_width=True,
                    column_config={
                        'img': st.column_config.ImageColumn('Rune', help='Set de rune')
                    },
                )


                tab1, tab2, tab3, tab4= st.tabs(
                    [st.session_state.langue['Autres_scoring'], st.session_state.langue['Detail_scoring'], st.session_state.langue['Efficience_avg_set'], st.session_state.langue['monstres']])
                
                
                
                with tab1:
                    with st.expander(st.session_state.langue['Autres_scoring'], expanded=True):

                        # ---------------- Scoring arte + speed

                        tcd_column_spd, _, score_column_arte = st.columns([0.4,0.1,0.4])

                        with tcd_column_spd:
                            st.metric(st.session_state.langue['Score_Speed'], st.session_state['score_spd'])

                        with score_column_arte:
                            st.metric(F'{st.session_state.langue["Score_Arte"]} ({st.session_state.langue["Efficience_avg"]} : {round(st.session_state.data_arte.data_a["efficiency"].mean(),2)})', st.session_state['score_arte'],
                                      help=st.session_state.langue['explication_scoring_artefact'])

                            # ---------------- Df arte + speed

                        tcd_column_df_spd, _, score_column_df_arte = st.columns([0.4,0.1,0.4])
                        #  df.style.highlight_max(axis=0)
                        with tcd_column_df_spd:
                            st.session_state.tcd_spd = get_img_runes(st.session_state.tcd_spd)
                            st.dataframe(
                                st.session_state.tcd_spd.reindex(new_index_spd).set_index('img').dropna(how='all'),
                                use_container_width=True,
                                column_config={'img' : st.column_config.ImageColumn('Rune', help='Rune')},
                                height=330)
                            


                        with score_column_df_arte:
                            st.dataframe(st.session_state.tcd_arte, use_container_width=True, height=298)

                        st.metric('Score com2us', int(st.session_state.df_scoring_com2us_summary['mean_SCORE'].mean()), help=st.session_state.langue["scoring_com2us_artefact"])

                        st.session_state.df_scoring_com2us_summary = get_img_runes(st.session_state.df_scoring_com2us_summary)

                        st.dataframe(st.session_state.df_scoring_com2us_summary.set_index('img').dropna(how='all').drop(columns=['id', 'date']),
                                     use_container_width=True,
                                     column_config={'img' : st.column_config.ImageColumn('Rune', help='Rune')})
                            

                        st.metric(st.session_state.langue['Score_quality_rune'],st.session_state.score_qual,
                                  help=st.session_state.langue['explication_scoring_qualite'])
                        st.session_state.df_scoring_quality = get_img_runes(st.session_state.df_scoring_quality)
                        st.dataframe(st.session_state.df_scoring_quality.set_index('img').dropna(how='all'),
                                     use_container_width=True,
                                     column_config={'img' : st.column_config.ImageColumn('Rune', help='Rune')})
                            


                with tab2:
                    with st.expander(st.session_state.langue['Detail_scoring']):

                        column_detail_scoring1, _, column_detail_scoring2 = st.columns([0.4,0.1,0.4])

                        with column_detail_scoring1:
                            st.session_state.tcd_detail_score = get_img_runes(st.session_state.tcd_detail_score)
                            try:
                                st.dataframe(st.session_state.tcd_detail_score.set_index('img'),
                                            use_container_width=True,
                                            column_config={'img' : st.column_config.ImageColumn('Rune', help='Rune')})
                            except KeyError:
                                st.dataframe(st.session_state.tcd_detail_score)

                        with column_detail_scoring2:
                            txt = st.session_state.langue['Explication_scoring']

                            for rune, score in coef_set.items():
                                txt += f'{rune.upper()} : {score} \n'

                            st.text(txt)

                with tab3:
                    with st.expander(st.session_state.langue['Efficience_set']):
                        col1_tab3, _, col2_tab3 = st.columns([0.4,0.05,0.4])
                        
                        with col1_tab3:
                            st.session_state.data_avg = get_img_runes(st.session_state.data_avg)
                            st.session_state.data_avg.rename(columns={100 : '100', 110 : '110', 120 : '120'}, inplace=True)
                            st.dataframe(st.session_state.data_avg.set_index('img'), 
                                        use_container_width=True,
                                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Rune')})

                        with col2_tab3:
                            fig = go.Figure()
                            fig.add_trace(go.Histogram(
                                y=st.session_state.data_avg['max'], x=st.session_state.data_avg.index, histfunc='avg', name=st.session_state.langue['max']))
                            fig.add_trace(go.Histogram(
                                y=st.session_state.data_avg['moyenne'], x=st.session_state.data_avg.index, histfunc='avg', name=st.session_state.langue['avg']))
                            fig.update_layout(
                                barmode="overlay",
                                bargap=0.1)
                            st.plotly_chart(fig)
                            
                        
                        fig_count = px.pie(st.session_state.data_avg,
                                           names=st.session_state.data_avg.index,
                                           values='Nombre runes',
                                           color=st.session_state.data_avg.index,
                                           title='Comptage de Runes')
                        
                        st.plotly_chart(fig_count)
                            


                with tab4:
                    with st.expander(st.session_state.langue['list_monsters']):

                        st.warning(
                            body=st.session_state.langue['performance_storage'], icon="🚨")

                        # @st.cache_data(show_spinner=False)
                        # def chargement_mobs(user_id):
                        #     data_mobs = pd.DataFrame.from_dict(
                        #         st.session_state['data_json'], orient="index").transpose()

                        #     data_mobs = data_mobs['unit_list']

                        #     # data_mobs = data_mobs[data_mobs['class'] > 3]

                        #     # On va boucler et retenir ce qui nous intéresse..
                        #     list_mobs = []

                        #     for monstre in data_mobs[0]:
                        #         unit = monstre['unit_id']
                        #         master_id = monstre['unit_master_id']
                        #         stars = monstre['class']
                        #         level = monstre['unit_level']
                        #         list_mobs.append([unit, master_id, stars, level])

                        #     # On met ça en dataframe
                        #     df_mobs = pd.DataFrame(list_mobs, columns=[
                        #                         'id_unit', 'id_monstre', '*', 'level'])

                        #     return df_mobs

                        # df_mobs = chargement_mobs(st.session_state.compteid)

                        # on merge
                        df_mobs_complet = pd.merge(
                            st.session_state.df_mobs, st.session_state.swarfarm, left_on='id_monstre', right_on='com2us_id')
                        
                        

                        # on retient ce dont on a besoin
                        df_mobs_name = df_mobs_complet[[
                            'name', '*', 'level', 'image_filename', 'element', 'natural_stars', 'awaken_level', 'Date_invocation']]

                        def _key_element(x):
                            '''Transforme les valeurs catégoriques en valeurs numériques'''
                            if x == 'Fire':
                                return 0
                            elif x == 'Water':
                                return 1
                            elif x == 'Wind':
                                return 2
                            elif x == 'Light':
                                return 3
                            elif x == 'Dark':
                                return 4
                            else:
                                return x

                        df_mobs_name['element_number'] = df_mobs_name['element'].apply(
                            lambda x: _key_element(x))

                        df_mobs_name.sort_values(by=['element_number', 'natural_stars', '*', 'level', 'name'],
                                                ascending=[True, False,
                                                            False, False, True],
                                                inplace=True)

                        df_mobs_name['url'] = df_mobs_name.apply(
                            lambda x:  f'https://swarfarm.com/static/herders/images/monsters/{x["image_filename"]}', axis=1)
                        

                        st.session_state.df_mobs_name_all = df_mobs_name

                        taille_image = st.slider(
                            st.session_state.langue['taille_image'], min_value=30, max_value=100, value=70, step=10)
                        
                        # filtre monstre

                        df_mobs_name_filter = filter_dataframe(df_mobs_name)

                        
                        

                        

                        tab_6, tab_5, tab_4, tab_3, tab_2, tab_1 = st.tabs(
                            ['6*', '5*', '4*', '3*', '2*', '1*'])

                        with tab_6:
                            show_img_monsters(st.session_state['id_joueur'],
                                df_mobs_name_filter, 6, width=taille_image)

                        with tab_5:
                            show_img_monsters(st.session_state['id_joueur'],
                                df_mobs_name_filter, 5, width=taille_image)

                        with tab_4:
                            show_img_monsters(st.session_state['id_joueur'],
                                df_mobs_name_filter, 4, width=taille_image)

                        with tab_3:
                            show_img_monsters(st.session_state['id_joueur'],
                                df_mobs_name_filter, 3, width=taille_image)

                        with tab_2:
                            show_img_monsters(st.session_state['id_joueur'],
                                df_mobs_name_filter, 2, width=taille_image)

                        with tab_1:
                            show_img_monsters(st.session_state['id_joueur'],
                                df_mobs_name_filter, 1, width=taille_image)





                # tableau avec image

                # ## à revoir en tableau croisé

                # check_tableau = st.checkbox('Tableau résumé')

                # if check_tableau:
                #     df_mobs_name = st.session_state.df_mobs_name_all
                #     # df_mobs_name = df_mobs_name[[
                #     #     'name', '*', 'level', 'element', 'natural_stars', 'awaken_level', 'Date_invocation']]

                #     df_mobs_name.drop(['image_filename'], axis=1, inplace=True)
                #     # df_mobs_name['avatar'] = df_mobs_name.apply(
                #     #     lambda x:  f'<img src="{x.url}" width="60" >', axis=1)

                #     # df_mobs_name.drop('url', axis=1, inplace=True)

                #     # st.markdown(df_mobs_name.to_html(escape=False, index=False), unsafe_allow_html=True)

                #     table_with_images(df_mobs_name)
                
                
                try:
                    df_global = pd.merge(
                        st.session_state.df_mobs, st.session_state.swarfarm, left_on='id_monstre', right_on='com2us_id')

                    df_global = df_global[['id_unit', 'id_monstre', '*', 'level', 'storage', 'Date_invocation']]

                    df_global.rename(columns={'*' : 'etoiles'}, inplace=True)
                    
                    df_global['id'] = st.session_state['id_joueur']
                    
                    df_global = df_global.groupby(['id', 'id_monstre', 'storage']).agg({'etoiles': 'max', 'level': 'max', 'id_unit': 'count', 'Date_invocation' : 'min'})
                    df_global.rename(columns={'id_unit' : 'quantité'}, inplace=True)

                    df_global.reset_index(inplace=True)
                    # on supprime les informations qu'on avait déjà
                    requete_perso_bdd('''DELETE FROM sw_monsters WHERE "id" = :id''', dict_params={
                                    'id': st.session_state['id_joueur']})
                    # # on insert les nouvelles

                    sauvegarde_bdd(df_global, 'sw_monsters', 'append', index=False)
                except:
                    pass
                




            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.subheader('Erreur')
                st.write('Pas de JSON chargé')

        else:
            st.switch_page("pages_streamlit/upload.py")

    else:
        st.switch_page("pages_streamlit/upload.py")
        
       
general_page()



st.caption('Made by Tomlora :sunglasses:')
