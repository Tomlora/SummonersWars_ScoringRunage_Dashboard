
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from fonctions.visualisation import filter_dataframe
import pandas as pd
import plotly_express as px
from st_pages import add_indentation
from fonctions.visuel import css
from fonctions.gestion_bdd import lire_bdd_perso
from streamlit_extras.no_default_selectbox import selectbox
css()

add_indentation()



def stats_runage():
    
    df_points = lire_bdd_perso(f'''SELECT rune_set, max(points) as points, max(moyenne) as moyenne, max(mediane) as mediane from sw_detail
                               WHERE id = {st.session_state['id_joueur']}
                               GROUP BY rune_set''', index_col='rune_set').transpose()
    
    tab_pts, tab_substat, tab_eff = st.tabs(['Top 10 stats', 'Substats par slot', 'Efficience par slot'])
    
    with tab_pts:
    
        df_points['points'] = df_points['points'].astype('int')
        
        df_max : pd.DataFrame = st.session_state.df_max.copy()
        
        df_max.reset_index(inplace=True)
        
        st.subheader('Total 10 stats')
        
        value_tcd = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        
        list_set = df_max['rune_set'].unique().tolist()
        
        list_set.sort()
        
        set_select = st.selectbox('Choisir un set', list_set , key='stat')
        
        df_max_selected = df_max[df_max['rune_set'] == set_select]
    

        try:
            st.markdown(f'Points : :green[{df_points.loc[set_select, "points"]}] | Efficience(Mediane) : :violet[{round(df_points.loc[set_select, "mediane"],2)}] | Efficience (Moyenne) : :orange[{round(df_points.loc[set_select, "moyenne"],2)}]')
        except KeyError:
            st.info("Pas de statistiques sur ce set")
        
        st.table(df_max_selected.pivot_table(values=value_tcd, index=['rune_set', 'substat'], aggfunc='max')[value_tcd].transpose())
        
        del df_max_selected, df_max
    
    with tab_substat:
    
        st.subheader('Substats par slot')

        df_rune = st.session_state.data_rune.count_per_slot()
        
        set_selected = selectbox('Choisir un set', df_rune['rune_set'].unique().tolist(), key='set_slot')
        
        sub_selected = st.selectbox('Choisir une substat', df_rune['first_sub'].unique().tolist(), key='substat_slot')
        
        value_mini = st.number_input('Valeur minimum', min_value=0, format='%i', value=15, key='value_mini')
        
        df_rune['rune_slot'] = df_rune['rune_slot'].apply(lambda x: f'Slot {x}')
        
        if set_selected == None:

            df_rune_grp = df_rune[(df_rune['first_sub'] == sub_selected) & (df_rune['first_sub_value_total'] >= value_mini)].groupby(['rune_slot']).sum().reset_index()
            fig = px.line_polar(df_rune_grp,
                                r='count', 
                            theta='rune_slot',
                            line_close=True,
                            title=f'Nombre de runes  avec {value_mini} minimum en substat par slot')
            
        else:

            df_rune_grp = df_rune[(df_rune['first_sub'] == sub_selected) & (df_rune['first_sub_value_total'] >= value_mini) & (df_rune['rune_set'] == set_selected)].groupby(['rune_set', 'rune_slot']).sum().reset_index()
            fig = px.line_polar(df_rune_grp,
                                r='count', 
                                theta='rune_slot',
                                color='rune_set',
                                line_close=True,
                                title=f'Nombre de runes {set_selected} avec {value_mini} minimum en {sub_selected.upper()} par slot')


        fig.update_layout(polar=dict(radialaxis=dict(gridcolor='lightgrey')))
        st.plotly_chart(fig)
        
    with tab_eff:
    
        st.subheader('Efficience par slot')

        df_efficience = st.session_state.data_rune.count_efficience_per_slot()
        
        set_selected = selectbox('Choisir un set', df_efficience['rune_set'].unique().tolist(), key='set_slot_eff')
        
        eff_mini = st.number_input('Valeur minimum', min_value=0, format='%i', value=100, key='value_mini_eff')
        
        df_efficience = df_efficience[df_efficience['efficiency'] >= eff_mini]
        
        df_efficience_count = df_efficience.groupby(['rune_set', 'rune_slot']).count().reset_index().rename(columns={'efficiency': 'Nombre'})
        
        df_efficience_count['rune_slot'] = df_efficience_count['rune_slot'].apply(lambda x: f'Slot {x}')
        
        if set_selected == None:

            df_rune_grp_eff = df_efficience_count.groupby(['rune_slot']).sum().reset_index()
            fig = px.line_polar(df_rune_grp_eff,
                                r='Nombre', 
                            theta='rune_slot',
                            line_close=True,
                            title=f'Nombre de runes  avec une efficience de  {eff_mini}% minimum en substat par slot')
            
        else:

            df_rune_grp_eff = df_efficience_count[df_efficience_count['rune_set'] == set_selected].groupby(['rune_set', 'rune_slot']).sum().reset_index()
            fig = px.line_polar(df_rune_grp_eff,
                                r='Nombre', 
                                theta='rune_slot',
                                color='rune_set',
                                line_close=True,
                                title=f'Nombre de runes {set_selected} avec une efficience de {eff_mini}% minimum par slot')


        fig.update_layout(polar=dict(radialaxis=dict(gridcolor='lightgrey')))
        st.plotly_chart(fig)


if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Runes')
        stats_runage()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')


st.caption('Made by Tomlora')