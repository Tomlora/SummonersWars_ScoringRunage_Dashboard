from fonctions.access import require_saved_page
require_saved_page()
import pandas as pd
import streamlit as st
from fonctions.journey import tr
from fonctions.tasks import load_tasks, save_tasks
from fonctions.export import export_excel
from fonctions.rune_card import rune_card
from fonctions.rune_visual import rune_label, rune_identity, stat_text, substats
from fonctions.visuel import css, page_header
css()
page_header(tr('Mes tâches','My tasks'),tr('Préparez les modifications à effectuer dans le jeu.','Prepare the changes to make in game.'),icon='📋')
runes=st.session_state.data_rune
notes=load_tasks(st.session_state.id_joueur)
data=runes.data[['rune_set','rune_slot','rune_equiped','level','efficiency']].copy()
data.index.name='id_rune'
data['main_stat']=[stat_text(runes,row.main_type,row.main_value) for _,row in runes.data.iterrows()]
data['substats']=[substats(runes,row) for _,row in runes.data.iterrows()]
data['rune_equiped']=data.rune_equiped.replace({0:tr('Inventaire','Inventory'),'0':tr('Inventaire','Inventory')})
for key,default in [('notes',''),('stat_to_replace',''),('stat_objectif',''),('fait',False)]:
    data[key]=notes[key].reindex(data.index).fillna(default)
focus=st.session_state.get('ui_task_rune')
if focus is not None:
    st.info(tr('Rune sélectionnée : ','Selected rune: ')+rune_label(runes,focus))
    if st.button(tr('Afficher toutes les runes','Show all runes')):
        st.session_state.pop('ui_task_rune',None)
        st.rerun()
    data=data[data.index==focus]
query=st.text_input(tr('Rechercher un monstre ou un set','Find a monster or set'),key='ui_task_query')
if query:
    mask=data.rune_set.astype(str).str.contains(query,case=False,regex=False)|data.rune_equiped.astype(str).str.contains(query,case=False,regex=False)|data.index.astype(str).str.contains(query,regex=False)
    data=data[mask]
only=st.checkbox(tr('Uniquement mes tâches','Only my tasks'),key='ui_task_only')
if only:
    data=data[data.fait|data.notes.ne('')|data.stat_to_replace.ne('')|data.stat_objectif.ne('')]
with st.expander(tr('Filtres avancés sur les statistiques','Advanced stat filters')):
    if st.toggle(tr('Activer les filtres avancés','Enable advanced filters'),key='ui_task_advanced'):
        from fonctions.visualisation import filter_dataframe
        fields={'rune_set':'Set','rune_slot':'Slot','stars':tr('Étoiles','Stars'),'level':tr('Niveau','Level'),
                'efficiency':tr('Efficience (%)','Efficiency (%)'),'main_type':tr('Principale','Main stat'),
                'main_value':tr('Valeur principale','Main value'),'innate_type':tr('Innée','Innate stat'),
                'innate_value':tr('Valeur innée','Innate value')}
        for i,sub in enumerate(('first','second','third','fourth'),1):
            fields[sub+'_sub']=tr('Sous-statistique ','Substat ')+str(i)
            fields[sub+'_sub_value_total']=tr('Total sous-statistique ','Substat total ')+str(i)
        stats=runes.data.loc[data.index,list(fields)].copy()
        for column in ['main_type','innate_type','first_sub','second_sub','third_sub','fourth_sub']:
            stats[column]=stats[column].map(lambda value:runes.property.get(value,value))
        filtered=filter_dataframe(stats.rename(columns=fields),key='task_advanced_query')
        data=data.loc[filtered.index]
if data.empty:
    st.info(tr('Aucune rune pour cette sélection. Effacez la recherche ou les filtres.','No runes match. Clear the search or filters.'))
else:
    size=st.selectbox(tr('Runes par page','Runes per page'),[25,50,100],key='ui_task_size')
    pages=max(1,(len(data)+size-1)//size)
    st.session_state.ui_task_page=min(max(st.session_state.get('ui_task_page',1),1),pages)
    page=st.number_input('Page',1,pages,key='ui_task_page')
    st.caption(tr(f'{len(data)} runes · page {page}/{pages}',f'{len(data)} runes · page {page}/{pages}'))
    data=data.iloc[(page-1)*size:page*size]
    st.caption(tr('Enregistrez vos modifications avant de changer les filtres. Les tâches masquées sont conservées.','Save changes before changing filters. Hidden tasks are kept.'))
    with st.form('rune_tasks'):
        edited=st.data_editor(data,width='stretch',height='content',hide_index=True,disabled=['rune_set','rune_slot','rune_equiped','level','efficiency','main_stat','substats'],column_config={
            '_index':st.column_config.NumberColumn(tr('ID rune','Rune ID'),format='%d',disabled=True),
            'rune_set':'Set','rune_slot':'Slot','rune_equiped':tr('Monstre','Monster'),'level':tr('Niveau','Level'),
            'main_stat':tr('Principale','Main stat'),'substats':st.column_config.TextColumn(tr('Sous-statistiques','Substats'),width='large'),
            'efficiency':st.column_config.NumberColumn(tr('Efficience (%)','Efficiency (%)'),format='%.2f'),
            'notes':tr('Notes','Notes'),'stat_to_replace':tr('Statistique à remplacer','Stat to replace'),
            'stat_objectif':tr('Statistique souhaitée','Target stat'),'fait':tr('Terminé','Done')})
        save=st.form_submit_button(tr('Enregistrer les tâches affichées','Save displayed tasks'))
    if save:
        save_tasks(st.session_state.id_joueur,edited)
        notes=load_tasks(st.session_state.id_joueur)
        st.success(tr('Tâches enregistrées.','Tasks saved.'))
    st.download_button(tr('Exporter les tâches affichées','Export displayed tasks'),export_excel(edited,'id_rune','Runes'),'rune-tasks.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',on_click='ignore')
    with st.expander(tr('Fiche d’une rune','Rune details')):
        rune_card(runes,data.index,'ui_tasks_card',actions=False)
if not notes.empty:
    st.subheader(tr('Toutes mes tâches enregistrées','All saved tasks'))
    saved_display=pd.DataFrame([{**rune_identity(runes,rune_id),**row.to_dict()} for rune_id,row in notes.iterrows()])
    st.dataframe(saved_display.rename(columns={'notes':tr('Notes','Notes'),'stat_to_replace':tr('Statistique à remplacer','Stat to replace'),'stat_objectif':tr('Statistique souhaitée','Target stat'),'fait':tr('Terminé','Done')}),hide_index=True,width='stretch')
    if st.button(tr('Réinitialiser toutes mes tâches','Reset all my tasks')):
        st.session_state['_confirm_reset_tasks']=True
    if st.session_state.get('_confirm_reset_tasks'):
        st.warning(tr('Toutes les tâches de ce compte seront supprimées.','All tasks for this account will be deleted.'))
        if st.button(tr('Confirmer la réinitialisation','Confirm reset')):
            cleared=notes.copy()
            for key in ['notes','stat_to_replace','stat_objectif']: cleared[key]=''
            cleared['fait']=False
            save_tasks(st.session_state.id_joueur,cleared)
            st.session_state.pop('_confirm_reset_tasks',None)
            st.rerun()
