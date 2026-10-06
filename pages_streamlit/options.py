from fonctions.access import require_saved_page
require_saved_page()
import streamlit as st
import pandas as pd
from fonctions.gestion_bdd import lire_bdd_perso, supprimer_data, supprimer_data_all, connection
from fonctions.journey import deletion_preview, score_labels
from fonctions.visuel import css, page_header
css()
en=st.session_state.get('translations_selected')=='English'
def tr(fr,english): return english if en else fr
page_header(tr('Mes données','My data'),icon='📱')
user=st.session_state.get('id_joueur')
if user is None:
    st.info(tr('Analyse locale : aucun historique enregistré.','Local analysis: no saved history.'))
    st.stop()
if st.session_state.get('_deleted_report'):
    st.success(tr('Relevé supprimé : ','Deleted report: ')+st.session_state.pop('_deleted_report'))
dates=lire_bdd_perso('SELECT date,score_general,score_spd,score_arte,score_qual FROM sw_score WHERE id_joueur=:id',index_col=None,params={'id':user}).T
dates=dates.sort_values('date', key=lambda values: pd.to_datetime(values, format='mixed', dayfirst=True, errors='coerce'), ascending=False, na_position='last')
choices=dates['date'].drop_duplicates().tolist()
if st.session_state.get('ui_delete_date') not in choices:
    st.session_state.pop('ui_delete_date',None)
date=st.selectbox(tr('Relevé à supprimer','Snapshot to delete'),choices,key='ui_delete_date')
if date is not None:
    st.subheader(tr('Aperçu du relevé : ','Report preview: ')+date)
    selected=dates[dates.date.eq(date)].iloc[0]
    for col,(key,label) in zip(st.columns(4),score_labels().items()):
        col.metric(label,f'{selected[key]:g} pts')
    with connection() as conn:
        counts=deletion_preview(conn,user,date)
    st.caption(tr('Seront supprimés : les scores et statistiques de cette date, ainsi que tous ses détails d’import.', 'This deletes the scores and statistics for this date, together with all its import details.'))
    st.write(tr('Imports détaillés concernés','Affected detailed imports')+f" : {counts.get('sw_rune_snapshots',0)}")
    st.caption(tr('Les autres dates, objectifs, builds, tâches et préférences sont conservés.', 'Other dates, goals, builds, tasks and preferences are kept.'))
else:
    st.info(tr('Aucun relevé à supprimer.','No reports to delete.'))
with st.form('delete_snapshot_'+str(date)):
    confirm=st.checkbox(tr('Je confirme la suppression de ce relevé.','I confirm deletion of this snapshot.'))
    delete=st.form_submit_button(tr('Supprimer le relevé','Delete snapshot'),disabled=dates.empty)
if delete:
    if not confirm:
        st.warning(tr('Confirmez la suppression.','Confirm deletion first.'))
    else:
        supprimer_data(user,date)
        st.cache_data.clear()
        st.session_state['_deleted_report']=date
        st.session_state.pop('ui_delete_date',None)
        st.session_state.pop('import_summary',None)
        if date==st.session_state.get('report_date'):
            st.session_state.analysis_ready=False
            st.session_state.submitted=False
            st.switch_page('pages_streamlit/upload.py')
        st.rerun()
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
