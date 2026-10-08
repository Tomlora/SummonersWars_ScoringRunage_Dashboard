from fonctions.access import require_saved_page
require_saved_page()
import streamlit as st
from fonctions.gestion_bdd import lire_bdd_perso
from fonctions.analysis import select_snapshots
from fonctions.leaderboards import show_ranking
from fonctions.artefact import dict_arte_effect_english, dataframe_replace_to_english
from fonctions.visuel import css,page_header
from fonctions.journey import tr

@st.cache_data(ttl=300)
def load_data():
    return lire_bdd_perso('SELECT u.id,u.joueur,u.visibility,u.guilde_id,g.guilde,d.date,d.arte_type,d.arte_attribut,d.substat,d.max_value FROM sw_arte_max d JOIN sw_user u ON u.id=d.id LEFT JOIN sw_guilde g ON g.guilde_id=u.guilde_id',index_col=None).T

css()
page_header(tr('Classement des artéfacts','Artifact leaderboard'),icon='🏆')
data=load_data()
if data.empty:
    st.info(tr('Aucun relevé disponible.','No snapshots available.'))
else:
    english=st.session_state.get('translations_selected')=='English'
    stat=st.selectbox(tr('Sous-statistique','Substat'),sorted(data.substat.unique()),format_func=lambda v:dict_arte_effect_english.get(v,v) if english else v,key='ui_arte_stat')
    attribute=st.selectbox(tr('Attribut','Attribute'),sorted(data.arte_attribut.unique()),index=None,format_func=lambda v:dataframe_replace_to_english.get(v,v) if english else v,key='ui_arte_attribute')
    kind=st.selectbox('Type',sorted(data.arte_type.unique()),index=None,key='ui_arte_kind')
    data=data[data.substat.eq(stat)]
    if attribute: data=data[data.arte_attribut.eq(attribute)]
    if kind: data=data[data.arte_type.eq(kind)]
    if english:
        data['arte_attribut']=data.arte_attribut.replace(dataframe_replace_to_english)
    show_ranking(select_snapshots(data,'max_value','record'),'max_value',['max_value','arte_attribut','arte_type'],key_prefix='ui_arte_',column_config={'max_value':st.column_config.NumberColumn(tr('Valeur','Value'),format='%.2f'),'arte_attribut':tr('Attribut','Attribute'),'arte_type':'Type'})
