import streamlit as st
import os
import plotly.graph_objects as go
import plotly_express as px
import pandas as pd
from datetime import timedelta

from fonctions.gestion_bdd import lire_bdd_perso, get_user
from fonctions.visualisation import transformation_stats_visu, plotline_evol_rune_visu, table_with_images
from fonctions.artefact import visualisation_top_arte
from params.coef import order

from fonctions.compare import comparaison
from streamlit_extras.metric_cards import style_metric_cards
from st_pages import add_indentation
from streamlit_extras.add_vertical_space import add_vertical_space
from fonctions.visuel import css

css()
add_indentation()
style_metric_cards(background_color='#03152A', border_color='#0083B9', border_left_color='#0083B9', border_size_px=0, box_shadow=False)

@st.cache_data
def filter_data(df, selected_options):
    """Filtre la data en fonction des dates sélectionnés

    Parameters
    ----------
    df : DataFrame
        Dataframe avec les scores et dates
    selected_options : List
        Liste de dates à inclure dans le DataFrame

    Returns
    -------
    DataFrame
        DataFrame triée sur les dates sélectionnées
    """
    df_filtered = df[df['date'].isin(selected_options)]
    return df_filtered

@st.cache_data(ttl=timedelta(minutes=5))
def chargement_data_joueur(df_guilde, guilde_target):
    if guilde_target == '*':
        df = lire_bdd_perso(
                'SELECT * from sw_user, sw_score WHERE sw_user.id = sw_score.id_joueur').transpose()
        df_complet = lire_bdd_perso(
                'SELECT sw_user.*, sw_detail.rune_set, sw_detail."100", sw_detail."110", sw_detail."120" from sw_user, sw_detail WHERE sw_user.id = sw_detail.id').transpose()
        
    
    # sinon on trie sur la guilde spécifiée        
    else:
        df = lire_bdd_perso(
                f'''SELECT * from sw_user, sw_score
                WHERE sw_user.id = sw_score.id_joueur
                AND sw_user.guilde_id = {df_guilde.loc[df_guilde['guilde'] == guilde_target].index.values[0]}''').transpose()
            
        df_complet = lire_bdd_perso(
                f'''SELECT sw_user.*, sw_detail.rune_set, sw_detail."100", sw_detail."110", sw_detail."120" from sw_user, sw_detail
                WHERE sw_user.id = sw_detail.id
                AND sw_user.guilde_id = {df_guilde.loc[df_guilde['guilde'] == guilde_target].index.values[0]}''').transpose()
        
    
    df_arte = lire_bdd_perso(
                '''SELECT sw_user.joueur, sw_arte_top.* from sw_user, sw_arte_top
                WHERE sw_user.id = sw_arte_top.id''').transpose()    

        
    try:
        df.drop(['id', 'guilde_id'], axis=1, inplace=True)
            # sort l'index : Majuscule -> Minuscule -> caractères spéciaux
    except:
        pass
    
    try:
        df_complet.drop(['id', 'guilde_id'], axis=1, inplace=True)
            # sort l'index : Majuscule -> Minuscule -> caractères spéciaux
    except:
        pass
    
    df.sort_index(axis=0, inplace=True)
    
    df_complet_grp = df_complet.groupby(['joueur', 'rune_set']).max()
        
    return df, df_complet_grp, df_arte
        
@st.cache_data
def chargement_guilde():
    df_guilde = lire_bdd_perso(f'''SELECT * from sw_guilde''', index_col='guilde_id').transpose()
    return df_guilde

def visu_page():
    
    st.info('Actualisé toutes les 5 minutes')

    df_guilde = chargement_guilde()
    
    df_guilde.sort_values(by=['guilde'], ascending=True, inplace=True)
        
    liste_guildes = df_guilde['guilde'].tolist()
    liste_guildes.append('*')
        
    guilde_target = st.selectbox('Guilde (peut être vide)', liste_guildes, index=len(liste_guildes)-1)
    
    # si pas de guilde spécifiée, on prend tout

    df, df_complet, df_arte = chargement_data_joueur(df_guilde, guilde_target)            

    

    liste_joueurs = df.index.unique().values.tolist()
    joueur_target = st.selectbox('Joueur', liste_joueurs)
    id_joueur, visibility, guildeid, rank = get_user(joueur_target)
    
    df_arte = df_arte[df_arte['id'] == id_joueur]

    submitted_joueur = True
    
    size_general, avg_score_general, max_general, size_guilde, avg_score_guilde, max_guilde, df_max, df_guilde_compare = comparaison(
                    guildeid)

    if submitted_joueur:
        
        # on charge les infos dont on va avoir besoin
        guilde = df_guilde.loc[guildeid]['guilde']
        
        data_detail = transformation_stats_visu(
                'sw', id_joueur, distinct=True)
        data_scoring = transformation_stats_visu(
                'sw_score', id_joueur, distinct=True)
        
        dict_visibility = {0: 'Non-visible',
                           1: 'Caché',
                           2: 'Visible à ma guilde',
                           3: 'Visible à tous',
                           4 : 'Caché au public mais visible à ma guilde'}
        
        new_index = ['Autre', 'Despair', 'Destroy', 'Violent', 'Will', 'Total']
        
        
        
        date = pd.to_datetime(data_scoring['date'], format="%d/%m/%Y").max().strftime('%d/%m/%Y')
        st.caption(f'Guilde : :blue[{guilde}] ({size_guilde} membres)')
        st.caption(f"Dernière analyse : :blue[{date}]")
        st.caption(f'Visibilité dans les onglets : :blue[{dict_visibility[visibility]}] ')
        
        
        tab_stats, tab_arte, tab_evo, tab_box, tab_storage = st.tabs(['Stats', 'Artefact', 'Evolution', 'Box', 'Storage'])
        
        
        with tab_stats:
            col1, _, col2 = st.columns([0.5, 0.1, 0.4]) 
            with col1:                     
                st.dataframe(data_detail.pivot_table(values='Nombre', index='Set', columns='Palier', aggfunc='max').reindex(new_index), use_container_width=True)
            with col2:
                st.metric('Score Rune', data_scoring['score_general'].max())
                st.metric(f'Moyenne Guilde ({size_guilde} joueurs)', avg_score_guilde)
                
            
            with st.expander('Details'):
                try:
                    st.dataframe(df_complet.loc[joueur_target, ['100', '110', '120']].drop('Total', axis=0), use_container_width=True)
                except KeyError:
                    st.warning('Pas de détails pour ce joueur')
            
            
        with tab_arte:

               
            liste_substat = df_arte['substat'].unique()
                
            liste_elementaire = ['FEU', 'EAU', 'VENT', 'LUMIERE', 'TENEBRE']
            liste_attribut = ['ATTACK', 'DEFENSE', 'HP', 'SUPPORT']
                
            col_elem, col_att = st.columns(2)
                
            with col_elem:
                elem_only = st.checkbox('Elementaire seulement')
            with col_att:
                attribut_only = st.checkbox('Attribut seulement')
                
            if elem_only:
                df_arte = df_arte[df_arte['arte_attribut'].isin(liste_elementaire)]
                
            if attribut_only:
                df_arte = df_arte[df_arte['arte_attribut'].isin(liste_attribut)]
                    
            if elem_only and attribut_only:
                st.warning('Cette combinaison est impossible')
                
                
                
                
            def show_arte_table(keyword, substat, exclure='None'):
                    
                i = 0
                index_keyword = []
                    
                for i in range(len(substat)):
                    if keyword in substat[i] and not exclure in substat[i]:
                        index_keyword.append(i)
                            
                if len(index_keyword) >= 1:
                        
                    for n in range(0,len(index_keyword), 2):
                        element = index_keyword[n]
                        col_arte1, _, col_arte2 = st.columns([0.4,0.1,0.4])
                        with col_arte1:
                            visualisation_top_arte(df_arte[['substat', 'arte_attribut', '1', '2', '3', '4', '5']], substat[element],
                                                       order=order)
                        try:
                            if keyword in substat[element+1]:
                                with col_arte2:
                                    visualisation_top_arte(df_arte[['substat', 'arte_attribut', '1', '2', '3', '4', '5']], substat[element+1],
                                                               order=order)
                        except IndexError: # il n'y en a plus
                            pass
            

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

                show_arte_table('REDUCTION', liste_substat)
                        
            with tab_dmg:

                show_arte_table('DMG SUR', liste_substat, 'CRIT')
                    
                    
            with tab_dmg_supp:

                show_arte_table('DMG SUPP', liste_substat)

                    
            with tab_precision:

                show_arte_table('PRECISION', liste_substat)

                    
            with tab_crit:

                show_arte_table('CRIT', liste_substat)


            with tab_renforcement:

                show_arte_table('RENFORCEMENT', liste_substat)

            with tab_soin:

                show_arte_table('SOIN', liste_substat)
                    
            with tab_perdus:
                show_arte_table('PERDUS', liste_substat)
                show_arte_table('DEF EN FONCTION', liste_substat)


            with tab_autres:

                col1, col2 = st.columns(2)
                with col1:
                    show_arte_table('REVIVE', liste_substat)
                    show_arte_table('BOMBE', liste_substat)
                    show_arte_table('COOP', liste_substat)
                with col2:
                    show_arte_table('REVENGE', liste_substat)
                    show_arte_table('VOL', liste_substat)
                    show_arte_table('INCAPACITE', liste_substat)
        
            
            
            
        with tab_evo:


            col1, col2 = st.columns(2)

            with col2:
                options_date = data_scoring['date'].unique().tolist()
                options_select = st.multiselect(
                    'Selectionner les dates à afficher :', options_date, options_date)

                data_detail = filter_data(data_detail, options_select)
                data_scoring = filter_data(data_scoring, options_select)

            with col1:  # on met la col1 après, pour bien prendre en compte les modifs dans data_scoring
                st.subheader('Evolution')
                st.dataframe(data_scoring.set_index('date').rename(columns={'score_general' : 'General',
                                                                            'score_spd' : 'Speed',
                                                                            'score_arte' : 'Artefact'}))
                

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data_scoring['date'], y=data_scoring['score_general'], mode='lines+markers'))

                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
                fig.update_yaxes(showgrid=False)
                
                # sauter des lignes
                st.text("")
                st.text("")
                
                st.subheader('Score general')

                data_100 = data_detail[data_detail['Palier'] == '100']
                data_110 = data_detail[data_detail['Palier'] == '110']
                data_120 = data_detail[data_detail['Palier'] == '120']

                tab1, tab2, tab3, tab4 = st.tabs(
                    ['General', 'Palier 100', 'Palier 110', 'Palier 120'])

                with tab1:
                    st.plotly_chart(fig)

                with tab2:
                    fig_rune_100 = plotline_evol_rune_visu(data_100)
                    st.plotly_chart(fig_rune_100)

                with tab3:
                    fig_rune_110 = plotline_evol_rune_visu(data_110)
                    st.plotly_chart(fig_rune_110)

                with tab4:
                    fig_rune_120 = plotline_evol_rune_visu(data_120)
                    st.plotly_chart(fig_rune_120)

                st.subheader('Speed')

                data_detail_spd = transformation_stats_visu(
                    'sw_spd', id_joueur, distinct=True)
                data_scoring_spd = transformation_stats_visu(
                    'sw_score', id_joueur, distinct=True, score='score_spd')

                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=data_scoring_spd['date'], y=data_scoring_spd['score_spd'], mode='lines+markers'))

                fig2.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
                fig2.update_yaxes(showgrid=False)

                data_25 = data_detail_spd[data_detail_spd['Palier'] == '23-25']
                data_28 = data_detail_spd[data_detail_spd['Palier'] == '26-28']
                data_31 = data_detail_spd[data_detail_spd['Palier'] == '29-31']
                data_35 = data_detail_spd[data_detail_spd['Palier'] == '32-35']
                data_36 = data_detail_spd[data_detail_spd['Palier'] == '36+']

                tab_spd_general, tab2325, tab2628, tab2931, tab3235, tab36 = st.tabs(
                    ['General', '23-25', '26-28', '29-31', '32-35', '36+'])

                with tab_spd_general:
                    st.plotly_chart(fig2)

                with tab2325:
                    fig25 = plotline_evol_rune_visu(data_25)
                    st.plotly_chart(fig25)

                with tab2628:
                    fig28 = plotline_evol_rune_visu(data_28)
                    st.plotly_chart(fig28)
                with tab2931:
                    fig31 = plotline_evol_rune_visu(data_31)
                    st.plotly_chart(fig31)
                with tab3235:
                    fig35 = plotline_evol_rune_visu(data_35)
                    st.plotly_chart(fig35)
                with tab36:
                    fig36 = plotline_evol_rune_visu(data_36)
                    st.plotly_chart(fig36)

                st.subheader('Artefact')
                data_detail_arte = transformation_stats_visu(
                    'sw_arte', id_joueur, distinct=True)
                data_scoring_arte = transformation_stats_visu(
                    'sw_score', id_joueur, distinct=True, score='score_arte')

                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(
                    x=data_scoring_arte['date'], y=data_scoring_arte['score_arte'], mode='lines+markers'))

                tab_arte_general, tab80, tab85, tab90, tab95, tab100 = st.tabs(
                    ['General', '80', '85', '90', '95', '100+'])

                data_80 = data_detail_arte[data_detail_arte['Palier'] == '80']
                data_85 = data_detail_arte[data_detail_arte['Palier'] == '85']
                data_90 = data_detail_arte[data_detail_arte['Palier'] == '90']
                data_95 = data_detail_arte[data_detail_arte['Palier'] == '95']
                data_100 = data_detail_arte[data_detail_arte['Palier'] == '100+']

                with tab_arte_general:
                    st.plotly_chart(fig3)
                with tab80:
                    fig80 = px.line(data_80, x="date", y="Nombre",
                                    color='arte_type', symbol='type')
                    st.plotly_chart(fig80)
                with tab85:
                    fig85 = px.line(data_85, x="date", y="Nombre",
                                    color='arte_type', symbol='type')
                    st.plotly_chart(fig85)
                with tab90:
                    fig90 = px.line(data_90, x="date", y="Nombre",
                                    color='arte_type', symbol='type')
                    st.plotly_chart(fig90)
                with tab95:
                    fig95 = px.line(data_95, x="date", y="Nombre",
                                    color='arte_type', symbol='type')
                    st.plotly_chart(fig95)
                with tab100:
                    fig100 = px.line(data_100, x="date", y="Nombre",
                                    color='arte_type', symbol='type')
                    st.plotly_chart(fig100)
        
                        
            df : pd.DataFrame = lire_bdd_perso(f'''SELECT sw_monsters.*, sw_user.joueur from sw_monsters
                    INNER JOIN sw_user ON sw_user.id = sw_monsters.id
                    WHERE sw_user.id = {id_joueur}
                    ''', index_col='id').transpose().reset_index()
            
            if not df.empty:
            
                swarfarm = pd.read_excel('swarfarm.xlsx')
                swarfarm.drop('id', axis=1, inplace=True) # inutile ici
                
                df_mob = pd.merge(df, swarfarm, left_on='id_monstre', right_on='com2us_id')
                
                df_mob['url_image'] = df_mob.apply(lambda x:  f'https://swarfarm.com/static/herders/images/monsters/{x["image_filename"]}', axis=1)
                
                def key_element(x):
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
                        
                df_mob['element_number'] = df_mob['element'].apply(lambda x : key_element(x))
                    
                
                df_mob.sort_values(by=['element_number', 'natural_stars', 'name'],
                                            ascending=[True, False, True,],
                                            inplace=True)
                
                df_mob_actif = df_mob[df_mob['storage'] == False]
                
                df_mob_actif['monsters_q'] = df_mob_actif['name'] + ' x' + df_mob_actif['quantité'].astype('str')
                
                df_storage = df_mob[df_mob['storage'] == True]
                
                       
                with tab_box:
                    
                    
                    taille_image = st.slider('Taille des images', 30, 200, 70, step=5)
                    
                    awaken_column, star_columns = st.columns(2)
                    
                    with awaken_column:
                        awaken_level = st.checkbox('Exclure les monstres non-évolués', value=True)
                        ld_only = st.checkbox('LD seulement')
                    
                    with star_columns:
                        stars_naturel = st.slider('Exclure les nats naturels', 0, 5, 1, step=1)
                    
                                            
                    if awaken_level:
                        df_mob_actif = df_mob_actif[df_mob_actif['awaken_level'] > 0]
                        
                    if ld_only:
                        df_mob_actif = df_mob_actif[df_mob_actif['element_number'].isin([3,4])]
                        

                    df_mob_actif = df_mob_actif[df_mob_actif['natural_stars'] > stars_naturel]

                        
                    add_vertical_space(2)        
                        
                    if taille_image <= 50:
                    
                        st.image(image=df_mob_actif['url_image'].tolist(), width=taille_image)

                    
                    else:
                        
                        st.image(image=df_mob_actif['url_image'].tolist(), width=taille_image, caption=df_mob_actif['monsters_q'].tolist())

                    
                with tab_storage:
                    
                    
                    df_storage['quantité'] = df_storage['quantité'].astype('int')
                    
                    
                    tab1, tab2 = st.tabs(['Texte', 'Image'])
                            
                    with tab1:    
                                 
                        st.dataframe(df_storage[['name', 'quantité', 'element']])
                            
                    with tab2:
                        df_html = table_with_images(df=df_storage[['url_image', 'name', 'quantité']], url_columns=("url_image",))
                        try:    
                            st.markdown(df_html, unsafe_allow_html=True)
                        except:
                            st.info('Non-disponible')
                            
                            
                            

        
        try:
            del df_storage
        except:
            pass    
        
        try:
            del df_mob_actif, df_mob, df            
        except:
            pass
        
        try:
            del df, tab80, tab85, tab90, tab95, tab100, data_80, data_85, data_90, data_95, data_100, fig3, fig80, fig85, fig90, fig95, fig100
        except UnboundLocalError:
            pass
        
        try:
            del df_html
        except:
            pass
        

                        

st.title('Visualisation')

mdp = st.text_input('mot de passe', '', type='password')
if mdp == os.environ.get('pass_visual'):
    visu_page()
elif mdp == '':
    st.write('')
else:
    st.warning('Mot de passe incorrect')

    
    
st.caption('Made by Tomlora')
    
    
    
    
