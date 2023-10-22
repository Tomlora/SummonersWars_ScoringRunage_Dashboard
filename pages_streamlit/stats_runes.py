
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from fonctions.visualisation import filter_dataframe
import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
from st_pages import add_indentation
from fonctions.visuel import css
from fonctions.gestion_bdd import lire_bdd_perso
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.add_vertical_space import add_vertical_space
css()

add_indentation()



def stats_runage():
    
    df_points = lire_bdd_perso(f'''SELECT rune_set, sw_detail.id, max(points) as points, max(moyenne) as moyenne, max(mediane) as mediane, sw_user.guilde_id from sw_detail
                                    INNER join sw_user on sw_user.id = sw_detail.id
                                GROUP BY sw_user.guilde_id, sw_detail.id, sw_detail.rune_set''', index_col='rune_set').transpose()
    


    tab_efficience, tab_pts, tab_substat, tab_eff, tab_qual = st.tabs([st.session_state.langue['Efficience'], 'Top 10 stats', 'Substats (Slot)', 'Efficience (Slot)', st.session_state.langue['qualité']])
    
    with tab_efficience:
        
        
        st.session_state.data_rune.calcul_potentiel()
        
         # on récupère les données
        df_efficience : pd.DataFrame = st.session_state.data_rune.data_grind.copy()

        
        # list_set = df_efficience['rune_set'].unique().tolist()
        
        # list_set.sort()
        
        set_select_efficience = selectbox('Set', st.session_state.set_rune , key='efficience')
        
        
        # filtre sur un set ?
        if set_select_efficience != None:
            df_efficience = df_efficience[df_efficience['rune_set'] == set_select_efficience]
            
        
        top = st.slider(st.session_state.langue['nb_rune_to_show'], 10, df_efficience.shape[0], round(df_efficience.shape[0] / 2), 10)     
        
        # on sort par efficience    
        df_efficience = df_efficience.sort_values('efficiency', ascending=False)
        df_efficience_hero = df_efficience.sort_values('efficiency_max_hero', ascending=False)
        df_efficience_lgd = df_efficience.sort_values('efficiency_max_lgd', ascending=False)
        
        
        # top 400
        df_efficience = df_efficience.head(top).reset_index()
        df_efficience_hero = df_efficience_hero.head(top).reset_index()
        df_efficience_lgd = df_efficience_lgd.head(top).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
        
            fig = px.line(df_efficience,
                          x=df_efficience.index,
                          y='efficiency',
                          hover_data=['rune_set', 'rune_equiped'])
            
            st.plotly_chart(fig)
            
                        
        with col2:
        
            if set_select_efficience == None:
                grp_by = 'rune_set'
                
            else:
                grp_by = 'main_type'
                df_efficience['main_type'] = df_efficience['main_type'].replace(
                    {0: 'Aucun',
                    1: 'HP',
                    2: 'HP%',
                    3: 'ATQ',
                    4: 'ATQ%',
                    5: 'DEF',
                    6: 'DEF%',
                    8: "SPD",
                    9: 'CRIT',
                    10: 'DCC',
                    11: 'RES',
                    12: 'ACC'})
                
            fig = px.pie(df_efficience.groupby(grp_by, as_index=False).count(),
                         values='efficiency',
                         names=grp_by,
                         title=st.session_state.langue['repartition'])
            st.plotly_chart(fig)
            
        fig = go.Figure()
            
        fig.add_trace(go.Scatter(x=df_efficience.index, y=df_efficience['efficiency'],
                    mode='lines',
                    name=st.session_state.langue['Efficience']))

        fig.add_trace(go.Scatter(x=df_efficience_hero.index, y=df_efficience_hero['efficiency_max_hero'],
                    mode='lines',
                    name='Efficience potentiel (hero)'))

        fig.add_trace(go.Scatter(x=df_efficience_lgd.index, y=df_efficience_lgd['efficiency_max_lgd'],
                    mode='lines',
                    name='Efficience potentiel (lgd)'))
            
        st.plotly_chart(fig, use_container_width=True)

        
    with tab_pts:
    
        df_points['points'] = df_points['points'].astype('int')
        
        df_max : pd.DataFrame = st.session_state.df_max.copy()
        
        # print(df_max)
        df_max_slot = st.session_state.data_rune.df_max_slot.copy()
        
        
        df_max.reset_index(inplace=True)
        
        st.subheader('Total 10 stats')
        
        value_tcd = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        
        # list_set = df_max['rune_set'].unique().tolist()
        
        # list_set.sort()
        
       
        set_select = st.selectbox('Choisir un set', st.session_state.set_rune , key='stat')
        
        df_max_selected = df_max[df_max['rune_set'] == set_select]
        
        try:
            df_to_show = df_max_selected.pivot_table(values=value_tcd, index=['rune_set', 'substat'], aggfunc='max')[value_tcd].transpose()
        except KeyError:
            pass
        slot_select = selectbox('Choisir un slot de rune', options=[1,2,3,4,5,6])
        
        if slot_select != None:
            df_max_selected = df_max_slot[df_max_slot['rune_set'] == set_select]       
            df_max_selected = df_max_selected[df_max_selected['rune_slot'] == slot_select]
            

            
            try:
                df_to_show = df_max_selected.pivot_table(values=value_tcd, index=['rune_set', 'substat'], aggfunc='max')[value_tcd].transpose()
            except KeyError:
                pass

        checkbox_filtre_guilde = st.checkbox(st.session_state.langue['filter_guilde'], value=False, key='filtre_guilde_stats')

        try:
            
            if checkbox_filtre_guilde:
                df_points = df_points[df_points['guilde_id'] == st.session_state['guildeid']]
            
            # points de l'utilisateur
            df_points_user = df_points[df_points['id'] == st.session_state['id_joueur']]
            
            # son classement
            df_points_set = df_points[df_points.index == set_select]
            df_points_set.set_index('id', inplace=True)
            df_points_set['pts_rank'] = df_points_set['points'].rank(ascending=False, method='min').astype('int')
            df_points_set['mediane_rank'] = df_points_set['mediane'].rank(ascending=False, method='min').astype('int')
            df_points_set['moyenne_rank'] = df_points_set['moyenne'].rank(ascending=False, method='min').astype('int')
            
            st.text('Ton compte :')
            st.markdown(f'Points : :green[{df_points_user.loc[set_select, "points"]}]     |      Efficience(Mediane) : :violet[{round(df_points_user.loc[set_select, "mediane"],2)}]     |    Efficience (Moyenne) : :orange[{round(df_points_user.loc[set_select, "moyenne"],2)}]')

            add_vertical_space(2)
            
            st.text('General (Moyenne):')
            st.markdown(f'Points : :green[{round(df_points.loc[set_select, "points"].mean(),2)}]     |    Efficience(Mediane) : :violet[{round(df_points.loc[set_select, "mediane"].mean(),2)}]     |    Efficience (Moyenne) : :orange[{round(df_points.loc[set_select, "moyenne"].mean(),2)}]')
            
            add_vertical_space(2)
            
            st.text(f'{st.session_state.langue["Classement"]} ({df_points_set.shape[0]} {st.session_state.langue["joueurs"]})')
            st.markdown(f'Points : :green[{df_points_set.loc[st.session_state["id_joueur"], "pts_rank"]}]     |    Efficience(Mediane) : :violet[{df_points_set.loc[st.session_state["id_joueur"], "mediane_rank"]}]     |    Efficience (Moyenne) : :orange[{df_points_set.loc[st.session_state["id_joueur"], "moyenne_rank"]}]')
            st.table(df_to_show)
        except KeyError:
            st.info(st.session_state.langue['no_data'])
        
        
        del df_max_selected, df_max
    
    with tab_substat:
    
        st.subheader('Substats par slot')

        df_rune = st.session_state.data_rune.count_per_slot()
        
        set_selected = selectbox('Set', st.session_state.set_rune, key='set_slot')
        
        sub_selected = st.selectbox('Substat', df_rune['first_sub'].unique().tolist(), key='substat_slot')
        
        value_mini = st.number_input(st.session_state.langue['value_min'], min_value=0, format='%i', value=15, key='value_mini')
        
        df_rune['rune_slot'] = df_rune['rune_slot'].apply(lambda x: f'Slot {x}')
        
        if set_selected == None:

            df_rune_grp = df_rune[(df_rune['first_sub'] == sub_selected) & (df_rune['first_sub_value_total'] >= value_mini)].groupby(['rune_slot']).sum().reset_index()
            fig = px.line_polar(df_rune_grp,
                                r='count', 
                            theta='rune_slot',
                            line_close=True,
                            title=f'{st.session_state.langue["nb_substat"].format(value_mini)}')

            fig.update_layout(polar=dict(radialaxis=dict(gridcolor='lightgrey')))
            st.plotly_chart(fig)
            
        else:

            df_rune_grp = df_rune[(df_rune['first_sub'] == sub_selected) & (df_rune['first_sub_value_total'] >= value_mini) & (df_rune['rune_set'] == set_selected)].groupby(['rune_set', 'rune_slot']).sum().reset_index()
            
            if df_rune_grp.empty:
                st.info(st.session_state.langue['no_data'])
            else:
                fig = px.line_polar(df_rune_grp,
                                    r='count', 
                                    theta='rune_slot',
                                    color='rune_set',
                                    line_close=True,
                                    title=f'{st.session_state.langue["nb_substat_set_selected"].format(set_selected, value_mini, sub_selected.upper())}')
                


                fig.update_layout(polar=dict(radialaxis=dict(gridcolor='lightgrey')))
                st.plotly_chart(fig)
        
    with tab_eff:
    
        st.subheader(f'{st.session_state.langue["Efficience"]} (Slot)')

        df_efficience = st.session_state.data_rune.count_efficience_per_slot()
        
        set_selected = selectbox('Set',st.session_state.set_rune, key='set_slot_eff')
        
        eff_mini = st.number_input(st.session_state.langue['value_min'], min_value=0, format='%i', value=100, key='value_mini_eff')
        
        df_efficience = df_efficience[df_efficience['efficiency'] >= eff_mini]
        
        df_efficience_count = df_efficience.groupby(['rune_set', 'rune_slot']).count().reset_index().rename(columns={'efficiency': 'Nombre'})
        
        df_efficience_count['rune_slot'] = df_efficience_count['rune_slot'].apply(lambda x: f'Slot {x}')
        
        
  
        if set_selected == None:

            df_rune_grp_eff = df_efficience_count.groupby(['rune_slot']).sum().reset_index()
            fig = px.line_polar(df_rune_grp_eff,
                                    r='Nombre', 
                                theta='rune_slot',
                                line_close=True,
                                title=f'{st.session_state.langue["nb_effi"].format(eff_mini)}')
            
            fig.update_layout(polar=dict(radialaxis=dict(gridcolor='lightgrey')))
            st.plotly_chart(fig)
                
        else:

            df_rune_grp_eff = df_efficience_count[df_efficience_count['rune_set'] == set_selected].groupby(['rune_set', 'rune_slot']).sum().reset_index()
            if df_rune_grp_eff.empty:
                st.info(st.session_state.langue['no_data'])
            else:
                fig = px.line_polar(df_rune_grp_eff,
                                        r='Nombre', 
                                        theta='rune_slot',
                                        color='rune_set',
                                        line_close=True,
                                        title=f'Nombre de runes {set_selected} avec une efficience de {eff_mini}% minimum par slot')


                fig.update_layout(polar=dict(radialaxis=dict(gridcolor='lightgrey')))
                st.plotly_chart(fig)
        
    with tab_qual:
               
        trier_par_slot = st.checkbox(st.session_state.langue['tri_slot'], value=False)
        
        if trier_par_slot:
            data_qual = st.session_state.df_quality_per_slot.reset_index()
        
        else:
            data_qual = st.session_state.df_quality.reset_index()
            
        data_qual_filter = filter_dataframe(data_qual)
        st.dataframe(data_qual_filter, use_container_width=True)
        
        st.subheader(f'{st.session_state.langue["repartition"]} 📊')
        select_set = selectbox('Set', data_qual['rune_set'].unique().tolist(), key='set_qual')
        
        if select_set != None:
            data_qual_filter = data_qual[data_qual['rune_set'] == select_set]
            
            if trier_par_slot:
               fig = px.pie(data_qual_filter, values='nombre', names='qualité_original', color='rune_slot', title=f'Qualité des runes {select_set}') 
            else:
                fig = px.pie(data_qual_filter, values='nombre', names='qualité_original', color='qualité_original', title=f'Qualité des runes {select_set}')


            st.plotly_chart(fig)
        
        
        
    
    del data_qual, df_rune_grp, df_rune_grp_eff


if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Runes')
        stats_runage()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')


st.caption('Made by Tomlora :sunglasses:')