
import streamlit as st
import pandas as pd
from fonctions.gestion_bdd import lire_bdd_perso, requete_perso_bdd
from streamlit_extras.metric_cards import style_metric_cards
from fonctions.visuel import css
css()

style_metric_cards(background_color='#03152A', border_color='#0083B9', border_left_color='#0083B9', border_size_px=10, box_shadow=False)

def download_params(id_compte):
    df_params = lire_bdd_perso(f'''SELECT * from sw_objectifs_rune WHERE id = {id_compte} ''', index_col='id').T
        
    if df_params.empty:
        return [20, 10, 10, 5, 20, 10, 20, 10, 20, 10, 10, 5]
    else:
        return df_params.iloc[0].tolist()


@st.cache_data
def load_efficience():
    df_eff = st.session_state.data_rune.count_efficience_per_slot()
    # df_eff = df_eff.groupby(['rune_set', 'rune_slot'], as_index=False)

    df_eff['efficience'] = pd.cut(df_eff['efficiency'], 
                                            bins=(100, 110, 140),
                                            right=False)
    

    # si en-dessous de 100, on supprime
    df_eff.dropna(subset=['efficience'], inplace=True)

    df_eff['efficience'] = df_eff['efficience'].astype(str)

    # palier
    palier_1 = df_eff['efficience'].unique()[0]  # '[100.0, 110.0)'
    palier_2 = df_eff['efficience'].unique()[1]  # '[110.0, 120.0)'


    df_eff['efficience'] = df_eff['efficience'].replace({palier_1: 100,
                                                        palier_2: 110})
    
    df_eff = df_eff.groupby(['rune_set', 'rune_slot', 'efficience'], as_index=False).count()

    df_eff.rename(columns={'efficiency' : 'Quantité'}, inplace=True)
    return df_eff

def get_img_runes(df : pd.DataFrame):
    if not "set" in df.columns:
        df.insert(0, 'set', df.index)
        df['img'] = df['set'].apply(lambda x: f'https://raw.githubusercontent.com/swarfarm/swarfarm/master/herders/static/herders/images/runes/{x.lower()}.png')

        return df

def tableau(df, set, efficience, liste_params, n_params):
    df_filter = df[(df['rune_set'] == set) & (df['efficience'] == efficience)]
    df_filter['Objectif'] = liste_params[n_params]
    df_filter['Réalisation'] = (df_filter['Quantité'] / df_filter['Objectif']) * 100
    df_filter['Réalisation'] = df_filter['Réalisation'].apply(lambda x : f'{int(x)}%')



    df_filter.set_index(['rune_set'], inplace=True)
    df_filter = get_img_runes(df_filter)
    real_total = int((df_filter['Quantité'].sum() / df_filter['Objectif'].sum()) * 100)
    real_total = f'{real_total}%'
    df_filter.drop(columns=['set'], inplace=True)
    df_filter.loc[7] = ['', '', df_filter['Quantité'].sum() , df_filter['Objectif'].sum(), real_total, ''] 
    return df_filter, real_total


def checkbox_stat(dict_params, value, defaut1, defaut2, defaut3):
    col1, col2, col3 = st.columns(3)
    with col1:
        dict_params[f'{value}_HP'] = st.checkbox('HP', value=defaut1, key=f'{value}_HP')
    with col2:
        dict_params[f'{value}_ATK'] = st.checkbox('ATK', value=defaut2, key=f'{value}_ATK')
    with col3:
        dict_params[f'{value}_DEF'] = st.checkbox('DEF', value=defaut3, key=f'{value}_DEF')
        
    return dict_params
        
        


def objectif_rune():

    df_efficience = load_efficience()

    liste_params = download_params(st.session_state.id_joueur)



    param_objectifs = {}
    with st.expander('Paramètres'):
        param_objectifs['Violent (100)'] = st.slider(f'{st.session_state.langue["objectif"]} Violent (100)', 2, 60, liste_params[0])
        param_objectifs['Violent (110)'] = st.slider(f'{st.session_state.langue["objectif"]} Violent (110)', 2, 60, liste_params[1])

        param_objectifs['Destroy (100)'] = st.slider(f'{st.session_state.langue["objectif"]} Destroy (100)', 2, 60, liste_params[2])
        param_objectifs['Destroy (110)'] = st.slider(f'{st.session_state.langue["objectif"]} Destroy (110)', 2, 60, liste_params[3])

        param_objectifs['Will (100)'] = st.slider(f'{st.session_state.langue["objectif"]} Will (100)', 2, 60, liste_params[4])
        param_objectifs['Will (110)'] = st.slider(f'{st.session_state.langue["objectif"]} Will (110)', 2, 60, liste_params[5])

        param_objectifs['Despair (100)'] = st.slider(f'{st.session_state.langue["objectif"]} Despair (100)', 2, 60, liste_params[6])
        param_objectifs['Despair (110)'] = st.slider(f'{st.session_state.langue["objectif"]} Despair (110)', 2, 60, liste_params[7])

        param_objectifs['Swift (100)'] = st.slider(f'{st.session_state.langue["objectif"]} Swift (100)', 2, 60, liste_params[8])
        param_objectifs['Swift (110)'] = st.slider(f'{st.session_state.langue["objectif"]} Swift (110)', 2, 60, liste_params[9])

        param_objectifs['Nemesis (100)'] = st.slider(f'{st.session_state.langue["objectif"]} Nemesis (100)', 2, 60, liste_params[10])
        param_objectifs['Nemesis (110)'] = st.slider(f'{st.session_state.langue["objectif"]} Nemesis (110)', 2, 60, liste_params[11])



    
        if st.button(st.session_state.langue['sauvegarder']):
            requete_perso_bdd('''
                              DELETE FROM sw.sw_objectifs_rune
	                          WHERE id = :id;
                            INSERT INTO sw.sw_objectifs_rune(
                                id, vio100, vio110, destroy100, destroy110, will100, will110, despair100, despair110, swift100, swift110, nemesis100, nemesis110)
                                VALUES (:id, :vio100, :vio110, :destroy100, :destroy110, :will100, :will110, :despair100, :despair110, :swift100, :swift110, :nemesis100, :nemesis110); ''',
                                dict_params={'id' : st.session_state.id_joueur,
                                             'vio100' : param_objectifs['Violent (100)'],
                                             'vio110' : param_objectifs['Violent (110)'],
                                             'destroy100' : param_objectifs['Destroy (100)'],
                                             'destroy110' : param_objectifs['Destroy (110)'],
                                             'will100' : param_objectifs['Will (100)'],
                                             'will110' : param_objectifs['Will (110)'],
                                             'despair100' : param_objectifs['Despair (100)'],
                                             'despair110' : param_objectifs['Despair (110)'],
                                             'swift100' : param_objectifs['Swift (100)'],
                                             'swift110' : param_objectifs['Swift (110)'],
                                             'nemesis100' : param_objectifs['Nemesis (100)'],
                                             'nemesis110' : param_objectifs['Nemesis (110)']})
            
            st.success(':v:')

    tab100, tab110 = st.tabs(['Efficience 100', 'Efficience 110'])



    with tab100:
        df_vio100, objectif_vio100 = tableau(df_efficience, 'Violent', 100, liste_params, 0)
        df_destroy100, objectif_destroy100 = tableau(df_efficience, 'Destroy', 100, liste_params, 2)
        df_despair100, objectif_despair100 = tableau(df_efficience, 'Despair', 100, liste_params, 6)
        df_will100, objectif_will100 = tableau(df_efficience, 'Will', 100, liste_params, 4)
        df_swift100, objectif_swift100 = tableau(df_efficience, 'Swift', 100, liste_params, 8)
        df_nem100, objectif_nem100 = tableau(df_efficience, 'Nemesis', 100, liste_params, 10)

        df_vio110, objectif_vio110 = tableau(df_efficience, 'Violent', 110, liste_params, 1)
        df_destroy110, objectif_destroy110 = tableau(df_efficience, 'Destroy', 110, liste_params, 3)
        df_despair110, objectif_despair110 = tableau(df_efficience, 'Despair', 110, liste_params, 7)
        df_will110, objectif_will110 = tableau(df_efficience, 'Will', 110, liste_params, 5)
        df_swift110, objectif_swift110 = tableau(df_efficience, 'Swift', 110, liste_params, 9)
        df_nem110, objectif_nem110 = tableau(df_efficience, 'Nemesis', 110, liste_params, 11)

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        col1.metric('Violent (100)',objectif_vio100)
        col2.metric('Destroy (100)',objectif_destroy100)
        col3.metric('Despair (100)',objectif_despair100)
        col4.metric('Will (100)',objectif_will100)
        col5.metric('Swift (100)',objectif_swift100)
        col6.metric('Nemesis (100)',objectif_nem100)

        col1_1, col1_2 = st.columns(2)

        with col1_1:

            st.subheader('Violent')
            st.dataframe(
                        df_vio100.set_index('img'), 
                        use_container_width=True, 
                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Set de rune')}
                        )

            st.subheader('Destroy')
            st.dataframe(
                        df_despair100.set_index('img'), 
                        use_container_width=True, 
                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Set de rune')}
                        )

            st.subheader('Despair')
            st.dataframe(
                        df_despair100.set_index('img'), 
                        use_container_width=True, 
                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Set de rune')}
                        )

        with col1_2:

            st.subheader('Will')
            st.dataframe(
                        df_will100.set_index('img'), 
                        use_container_width=True, 
                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Set de rune')}
                        )


            st.subheader('Swift')
            st.dataframe(
                        df_swift100.set_index('img'), 
                        use_container_width=True, 
                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Set de rune')}
                        )

            st.subheader('Nemesis')
            st.dataframe(
                        df_nem100.set_index('img'), 
                        use_container_width=True, 
                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Set de rune')}
                        )



    
    with tab110:

        col11, col12, col13, col14, col15, col16 = st.columns(6)

        col11.metric('Violent (110)',objectif_vio110)
        col12.metric('Destroy (110)',objectif_destroy110)
        col13.metric('Despair (110)',objectif_despair110)
        col14.metric('Will (110)',objectif_will110)
        col15.metric('Swift (110)',objectif_swift110)
        col16.metric('Nemesis (110)',objectif_nem110)

        col2_1, col2_2 = st.columns(2)

        with col2_1:

            st.subheader('Violent')
            st.dataframe(
                        df_vio110.set_index('img'), 
                        use_container_width=True, 
                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Set de rune')}
                        )

            st.subheader('Destroy')
            st.dataframe(
                        df_destroy110.set_index('img'), 
                        use_container_width=True, 
                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Set de rune')}
                        )

            st.subheader('Despair')
            st.dataframe(
                        df_despair110.set_index('img'), 
                        use_container_width=True, 
                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Set de rune')}
                        )

        with col2_2:

            st.subheader('Will')
            st.dataframe(
                        df_will110.set_index('img'), 
                        use_container_width=True, 
                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Set de rune')}
                        )

            st.subheader('Swift')
            st.dataframe(
                        df_swift110.set_index('img'), 
                        use_container_width=True, 
                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Set de rune')}
                        )

            st.subheader('Nemesis')
            st.dataframe(
                        df_nem110.set_index('img'), 
                        use_container_width=True, 
                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Set de rune')}
                        )
    


        

if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Objectif Rune')
        try:
            objectif_rune()
        except IndexError:
            st.warning('Cet onglet est réservé aux joueurs ayant un meilleur niveau de runes')
    
    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")
    
    
st.caption('Made by Tomlora :sunglasses:')