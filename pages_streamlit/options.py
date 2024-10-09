import pandas as pd
import streamlit as st
from fonctions.gestion_bdd import lire_bdd, supprimer_data, supprimer_data_all


from fonctions.visuel import css
css()



def params():
    # On lit la BDD
    df_actuel = lire_bdd('sw_score')
    df_actuel = df_actuel.transpose()
    df_actuel.reset_index(inplace=True)


    df_actuel = df_actuel[df_actuel['id_joueur'] == st.session_state['id_joueur']]
    df_actuel.drop(['id_joueur'], axis=1, inplace=True)

    # Datetime
    df_actuel['datetime'] = pd.to_datetime(
        df_actuel['date'], format='%d/%m/%Y')
    df_actuel.sort_values(by=['datetime'], inplace=True)

    # Liste des dates
    liste_date = df_actuel['date'].unique().tolist()

    with st.form('Supprimer des données'):
        st.subheader(st.session_state.langue['delete_one_save'])
        date_retenu = st.selectbox('Date', liste_date)
        validation_suppression = st.form_submit_button(
            st.session_state.langue['valider'])

    if validation_suppression:
        supprimer_data(st.session_state['id_joueur'], date_retenu)
        st.text(st.session_state.langue['supprimer'])

    with st.form('Supprimer toutes mes données'):
        st.subheader(st.session_state.langue['delete_all'])
        validation_suppression_definitive = st.form_submit_button(
            st.session_state.langue['supprimer'])

    if validation_suppression_definitive:

        supprimer_data_all(st.session_state['id_joueur'])
        st.text(st.session_state.langue['supprimer'])



if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Options')
        params()
    
    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")
    
    
st.caption('Made by Tomlora :sunglasses:')