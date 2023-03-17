import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from st_pages import add_indentation

add_indentation()

def find_monsters():

    st.header('Bestiaire')

    @st.cache(suppress_st_warning=True)
    def chargement_bestiaire():
        data_monsters = pd.read_csv('swarfarm_monstres.csv')
        data_spells = pd.read_csv('swarfarm_spells.csv')
        return data_monsters, data_spells

    data_monsters_original, data_spell_original = chargement_bestiaire()

    liste_effet = data_spell_original['name_1'].unique()

    liste_lead = data_monsters_original['area_leader'].unique().tolist()
    liste_lead.append('*')

    elementaire = data_monsters_original['element'].unique().tolist()
    elementaire.append('*')
    elementaire.remove('Pure')  # ne peut pas être drop

    data_monsters = data_monsters_original.copy()
    data_spells = data_spell_original.copy()

    col1, col2 = st.columns(2)

    with col1:
        element_selected = st.radio('Element', elementaire, len(elementaire)-1)

    with col2:
        buff_selected = st.selectbox('Buff/Debuff', liste_effet)
        lead_selected = st.selectbox('Lead', liste_lead, len(liste_lead)-1)

    if element_selected != '*':
        data_monsters = data_monsters[data_monsters['element']
                                      == element_selected]

    if lead_selected != '*':
        data_monsters = data_monsters[data_monsters['area_leader']
                                      == lead_selected]

    def verif_effet(df, effet):
        df['verif1'] = df['name_1'].str.contains(effet).astype('int')
        df['verif2'] = df['name_2'].str.contains(effet).astype('int')
        df['verif3'] = df['name_3'].str.contains(effet).astype('int')
        df['verif4'] = df['name_4'].str.contains(effet).astype('int')
        df['verif5'] = df['name_5'].str.contains(effet).astype('int')
        df['verif_g'] = df['verif1'] + df['verif2'] + \
            df['verif3'] + df['verif4'] + df['verif5']

        def return_bool(x):
            return x >= 1


        df['verif_g'] = df['verif_g'].apply(return_bool)

        df.drop(['verif1', 'verif2', 'verif3', 'verif4',
                'verif5'], axis=1, inplace=True)

        return df

    column_monsters = ['name', 'element', 'archetype', 'attribute_leader',
                       'amount_leader', 'area_leader', 'element_leader']
    if buff_selected == '-1':
        st.dataframe(data_monsters[column_monsters])
    else:
        df_spells = verif_effet(data_spells, buff_selected)
        df_filtre = df_spells[df_spells['verif_g'] == True]

        list_mob = []
        for index, element in df_filtre['used_on'].items():
            element = element.replace('[', '').replace(']', '')
            element = element.split(', ')
            for id_mob in element:
                try:
                    id_mob = int(id_mob)
                    list_mob.append(id_mob)
                except ValueError:
                    pass

        st.dataframe(
            data_monsters[data_monsters['id'].isin(list_mob)][column_monsters])


if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Bestiaire')
        find_monsters()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')