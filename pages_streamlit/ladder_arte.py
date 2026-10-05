import streamlit as st
from fonctions.gestion_bdd import lire_bdd_perso
from fonctions.analysis import select_snapshots
from fonctions.leaderboards import show_ranking
from fonctions.artefact import dict_arte_effect_english, dataframe_replace_to_english
from fonctions.visuel import css,page_header

@st.cache_data(ttl=300)
def load_data():
    return lire_bdd_perso('SELECT u.id,u.joueur,u.visibility,u.guilde_id,g.guilde,d.date,d.arte_type,d.arte_attribut,d.substat,d.max_value FROM sw_arte_max d JOIN sw_user u ON u.id=d.id LEFT JOIN sw_guilde g ON g.guilde_id=u.guilde_id',index_col=None).T

css()
page_header('Classement des artéfacts / Artifact leaderboard',icon='🏆')
data=load_data()
if data.empty:
    st.info('Aucun relevé disponible / No snapshots available.')
else:
    if st.session_state.translations_selected=='English':
        data['arte_attribut']=data['arte_attribut'].replace(dataframe_replace_to_english)
        data['substat']=data['substat'].replace(dict_arte_effect_english)
    stat=st.selectbox('Substat',sorted(data.substat.unique()))
    attribute=st.selectbox('Attribut / Attribute',sorted(data.arte_attribut.unique()),index=None)
    kind=st.selectbox('Type',sorted(data.arte_type.unique()),index=None)
    data=data[data.substat.eq(stat)]
    if attribute: data=data[data.arte_attribut.eq(attribute)]
    if kind: data=data[data.arte_type.eq(kind)]
    show_ranking(select_snapshots(data,'max_value','record'),'max_value',['max_value','arte_attribut','arte_type'])
