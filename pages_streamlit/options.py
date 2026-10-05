from fonctions.access import require_saved_page
require_saved_page()
import streamlit as st
from fonctions.gestion_bdd import lire_bdd_perso, supprimer_data, supprimer_data_all
from fonctions.visuel import css, page_header
css()
en=st.session_state.get('translations_selected')=='English'
def tr(fr,english): return english if en else fr
page_header(tr('Mes données','My data'),icon='📱')
user=st.session_state.get('id_joueur')
if user is None:
    st.info(tr('Analyse locale : aucun historique enregistré.','Local analysis: no saved history.'))
    st.stop()
dates=lire_bdd_perso('SELECT DISTINCT date FROM sw_score WHERE id_joueur=:id',index_col=None,params={'id':user}).T
with st.form('delete_snapshot'):
    date=st.selectbox(tr('Relevé à supprimer','Snapshot to delete'),dates['date'].tolist())
    confirm=st.checkbox(tr('Je confirme la suppression de ce relevé.','I confirm deletion of this snapshot.'))
    delete=st.form_submit_button(tr('Supprimer le relevé','Delete snapshot'),disabled=dates.empty)
if delete:
    if not confirm:
        st.warning(tr('Confirmez la suppression.','Confirm deletion first.'))
    else:
        supprimer_data(user,date)
        st.cache_data.clear()
        st.success(tr('Relevé supprimé.','Snapshot deleted.'))
        if date==st.session_state.get('report_date'):
            st.session_state.analysis_ready=False
            st.session_state.submitted=False
            st.switch_page('pages_streamlit/upload.py')
with st.form('delete_account'):
    st.warning(tr('Supprimer tous les relevés, objectifs, builds et tâches de ce compte.','Delete all snapshots, goals, builds and tasks for this account.'))
    name=st.text_input(tr('Saisissez le nom du compte pour confirmer','Type the account name to confirm'))
    delete_all=st.form_submit_button(tr('Supprimer toutes mes données','Delete all my data'))
if delete_all:
    if name!=st.session_state.pseudo:
        st.warning(tr('Le nom ne correspond pas au compte.','The name does not match this account.'))
    else:
        supprimer_data_all(user)
        st.cache_data.clear()
        for key in list(st.session_state):
            del st.session_state[key]
        st.switch_page('pages_streamlit/upload.py')
