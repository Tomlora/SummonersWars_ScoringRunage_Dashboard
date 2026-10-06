from fonctions.access import require_saved_page
require_saved_page()
import streamlit as st
from fonctions.gestion_bdd import lire_bdd_perso
from fonctions.analysis import select_snapshots
from fonctions.leaderboards import show_ranking
from fonctions.visuel import css,page_header
from fonctions.journey import tr

@st.cache_data(ttl=300)
def load_data():
    return lire_bdd_perso('SELECT u.id,u.joueur,u.visibility,u.guilde_id,g.guilde,d.* FROM sw_max d JOIN sw_user u ON u.id=d.id LEFT JOIN sw_guilde g ON g.guilde_id=u.guilde_id',index_col=None).T.loc[:,lambda frame:~frame.columns.duplicated()]

css()
page_header(tr('Classement des runes','Rune leaderboard'),icon='🏆')
data=load_data()
if data.empty:
    st.info(tr('Aucun relevé disponible.','No snapshots available.'))
else:
    metrics={v:tr('Maximum','Maximum') if v=='max_value' else tr('Moyenne top ','Top average ')+v[3:] for v in ['max_value','top5','top10','top15','top25']}
    score=st.radio(tr('Indicateur','Metric'),list(metrics),format_func=metrics.get,horizontal=True,key='ui_value_metric')
    stat=st.selectbox(tr('Sous-statistique','Substat'),sorted(data.substat.unique()),key='ui_value_stat')
    rune=st.selectbox('Set',sorted(data.rune_set.unique()),index=None,key='ui_value_set')
    data=data[data.substat.eq(stat)]
    if rune: data=data[data.rune_set.eq(rune)]
    data=select_snapshots(data,score,'record')
    show_ranking(data,score,key_prefix='ui_value_',column_config={score:st.column_config.NumberColumn(stat,format='%.2f')})
