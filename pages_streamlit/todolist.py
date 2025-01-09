import pandas as pd
import streamlit as st
from fonctions.visualisation import filter_dataframe
from fonctions.export import export_excel
from fonctions.gestion_bdd import lire_bdd_perso, requete_perso_bdd, sauvegarde_bdd




from fonctions.visuel import css
css()






st.title('To do list')


def todo():
    
    st.info(st.session_state.langue['warning_detail_runes'], icon="⚠️")

    def charger_notes(id_joueur):
        return lire_bdd_perso(f"SELECT * FROM sw_todolist WHERE id_joueur = {id_joueur}", index_col='id_rune').T
    
    notes = charger_notes(st.session_state.id_joueur)
    
        # # swarfarm
    @st.cache_data(ttl='10m', show_spinner=st.session_state.langue['loading_rune'])
    def charger_data(joueur):
        swarfarm = st.session_state.swarfarm[[
            'com2us_id', 'name', 'image_filename', 'url']].set_index('com2us_id')
        # df_mobs['name_monstre'] = df_mobs['id_monstre'].map(
        #     swarfarm.to_dict(orient="dict")['name'])

        # On peut faire le mapping...

        st.session_state.data_rune.data_build = st.session_state.data_rune.data.copy()

        st.session_state.data_rune.data_build = st.session_state.data_rune.data_build[st.session_state.data_rune.data_build['level'] >= 12]

        rename_column = {'rune_set': 'Set rune',
                        'rune_slot': 'Slot',
                        'rune_equiped': 'Equipé',
                        'main_type': 'Stat principal',
                        'main_value': 'Valeur stat principal',
                        'first_sub': 'Substat 1',
                        'second_sub': 'Substat 2',
                        'third_sub': 'Substat 3',
                        'fourth_sub': 'Substat 4',
                        'first_sub_value_total': 'Substat 1 total',
                        'second_sub_value_total': 'Substat 2 total',
                        'third_sub_value_total': 'Substat 3 total',
                        'fourth_sub_value_total': 'Substat 4 total',
                        }

        st.session_state.data_rune.data_build.rename(
            columns=rename_column, inplace=True)
        st.session_state.data_rune.data_build['Equipé'] = st.session_state.data_rune.data_build['Equipé'].astype(
            'str')
        st.session_state.data_rune.data_build['Equipé'].replace(
            {'0': st.session_state.langue['Inventaire']}, inplace=True)
        
        st.session_state.data_rune.data_build[['Set rune', 'Stat principal', 'innate_type']] = st.session_state.data_rune.data_build[['Set rune', 'Stat principal', 'innate_type']].astype('category')
        


        st.session_state.data_rune.data_build = st.session_state.data_rune.data_build[['Set rune', 'Slot', 'Equipé', 'Stat principal', 'Valeur stat principal',
                                                                                    'innate_type', 'innate_value', 'level',
                                                                                    'Substat 1', 'Substat 1 total',
                                                                                    'Substat 2', 'Substat 2 total',
                                                                                    'Substat 3', 'Substat 3 total',
                                                                                    'Substat 4', 'Substat 4 total']]

        st.session_state.data_rune.data_build = st.session_state.data_rune.map_stats(st.session_state.data_rune.data_build, [
            'Stat principal', 'innate_type', 'Substat 1', 'Substat 2', 'Substat 3', 'Substat 4']).reset_index()

        st.session_state.data_rune.data_build.rename(
            columns={'index': 'id_rune'}, inplace=True)

        # on peut préparer la page
        st.warning('Runes +12 ou +15 seulement', icon="⚠️")
        

                
        melt = st.session_state.data_rune.data_build.melt(id_vars=['id_rune', 'Set rune', 'Slot', 'level', 'Substat 1', 'Substat 2', 'Substat 3', 'Substat 4'],
                            value_vars=['Substat 1 total', 'Substat 2 total', 'Substat 3 total', 'Substat 4 total'])



        def changement_variable(x):
            number = x.variable[-7]
            type = x[f'Substat {number}']
                        
            return type

        melt['variable'] = melt.apply(changement_variable, axis=1)
                

        pivot = melt.pivot_table(index=['id_rune', 'Set rune', 'Slot'],
                                        columns='variable',
                                        values='value',
                                        aggfunc='first',
                                        fill_value=0).reset_index()
                

        st.session_state.data_rune.data_build  = st.session_state.data_rune.data_build.merge(pivot, on=['id_rune', 'Set rune', 'Slot'])
        
        df_mobs = st.session_state.df_mobs.set_index('id_unit')
        
        return st.session_state.data_rune.data_build, swarfarm, df_mobs
    
    st.session_state.data_rune.data_build, swarfarm, df_mobs = charger_data(st.session_state.compteid)
    

    try:
        data_build_filter = filter_dataframe(
                st.session_state.data_rune.data_build.drop(['Substat 1', 'Substat 1 total', 'Substat 2', 'Substat 2 total', 'Substat 3', 'Substat 3 total', 'Substat 4', 'Substat 4 total', 'Aucun'], axis=1), 'data_build', type_number='int')
    except KeyError:
        data_build_filter = filter_dataframe(
                st.session_state.data_rune.data_build.drop(['Substat 1', 'Substat 1 total', 'Substat 2', 'Substat 2 total', 'Substat 3', 'Substat 3 total', 'Substat 4', 'Substat 4 total'], axis=1), 'data_build', type_number='int')        
        
    if not 'img' in data_build_filter.columns:
        img = data_build_filter['Set rune'].apply(lambda x: f'https://raw.githubusercontent.com/swarfarm/swarfarm/master/herders/static/herders/images/runes/{x.lower()}.png')
        data_build_filter.insert(0, 'img', img, True)
    
    # Modification
   
    colonne_to_disabled = data_build_filter.columns.tolist()
    
    data_build_filter.set_index('id_rune', inplace=True)
    
    def ajout_colonne(df):
        df['notes'] = "" 
        df['stat_to_replace'] = "" 
        df['stat_objectif'] = ""      
        df['fait'] = False
        return df
        
    data_build_filter = ajout_colonne(data_build_filter)
    data_build_filter.update(notes)    
    


    def charger_df_edited(data_build_filter, joueur_id):    
        edited_df = st.data_editor(data_build_filter, 
                        use_container_width=True,
                        column_config={'img' : st.column_config.ImageColumn('Rune', help='Rune'),
                                    'stat_to_replace' : st.column_config.SelectboxColumn("Stat to replace", options=data_build_filter['Stat principal'].unique().tolist()),
                                    'stat_objectif' : st.column_config.SelectboxColumn("Stat objectif", options=data_build_filter['Stat principal'].unique().tolist())},
                        disabled=colonne_to_disabled)
        
        return edited_df
    
    edited_df = charger_df_edited(data_build_filter, st.session_state.compteid)
    
    
    def save(edited_df):
        df_filter = edited_df[(edited_df['fait'] == True) | (edited_df['notes'] != "") | (edited_df['stat_to_replace'] != "") | (edited_df['stat_objectif'] != "")].copy()
        df_filter['id_joueur'] = st.session_state.id_joueur
        df_filter_to_save = df_filter[['id_joueur', 'notes', 'stat_to_replace', 'stat_objectif', 'fait']]
        requete_perso_bdd('DELETE FROM sw_todolist WHERE id_joueur = :id_joueur', {'id_joueur' : st.session_state.id_joueur})
        sauvegarde_bdd(df_filter_to_save, 'sw_todolist', 'append')
        if df_filter.empty:
            st.warning('Vide', icon="⚠️")
        else:
            st.success('Sauvegardé', icon="✅")
        return df_filter
    
    def reset():
        requete_perso_bdd('DELETE FROM sw_todolist WHERE id_joueur = :id_joueur', {'id_joueur' : st.session_state.id_joueur})
        st.success('Réinitialisé')
        

    
    # save(edited_df)



    data_xlsx = export_excel(edited_df.drop('img', axis=1), 'Id_rune', 'Runes')

    col1, col2, col3 = st.columns([0.7,0.15,0.15])
    
    with col1:
        st.download_button(st.session_state.langue['download_excel'], data_xlsx, file_name='runes.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    with col2:
        st.button('Sauvegarder', on_click=save, args=(edited_df,), help=' ⚠️ Il faut sauvegarder avant chaque modification de filtre')
        st.button('Reset', on_click=reset)
        

        
        
        
    st.subheader('ToDoList')
    st.dataframe(edited_df[(edited_df['fait'] == True) | (edited_df['notes'] != "") | (edited_df['stat_to_replace'] != "") | (edited_df['stat_objectif'] != "")].copy(),
                use_container_width=True,
                column_config={'img' : st.column_config.ImageColumn('Rune', help='Rune')})

    

if 'submitted' in st.session_state:
    if st.session_state.submitted:
        try:
            todo()
        except KeyError:
            st.warning('Cet onglet est réservé aux joueurs ayant un meilleur niveau de runes')

    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")

st.caption('Made by Tomlora :sunglasses:')