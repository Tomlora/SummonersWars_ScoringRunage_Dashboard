import pandas as pd
import streamlit as st
from fonctions.gestion_bdd import lire_bdd_perso
from fonctions.analysis import select_snapshots
from fonctions.visuel import css,page_header
from params.coef import coef_set,coef_set_spd

@st.cache_data(ttl=300,show_spinner=False)
def leaderboard_data(kind,set_name=None):
    metadata='u.id,u.joueur,u.visibility,u.guilde_id,u.joueur_id,g.guilde'
    join=' JOIN sw_user u ON u.id=d.{key} LEFT JOIN sw_guilde g ON g.guilde_id=u.guilde_id '
    if kind in ('score_general','score_spd','score_arte','score_qual'):
        sql=f'SELECT {metadata},d.date,d.{kind} AS score FROM sw_score d'+join.format(key='id_joueur')
        return lire_bdd_perso(sql,index_col=None).T
    if kind=='com2us_global':
        sql = f'SELECT {metadata},d.date,SUM(d."sum_SCORE") AS "sum_SCORE",MAX(d."max_SCORE") AS "max_SCORE" FROM sw_scoring_com2us d' + join.format(key='id') + 'GROUP BY u.id,u.joueur,u.visibility,u.guilde_id,u.joueur_id,g.guilde,d.date'
        return lire_bdd_perso(sql,index_col=None).T
    if kind=='rune_set':
        fields=['100','110','120']; table='sw_detail'; column='rune_set'; weights=[1,2,3]; coefficient=coef_set.get(set_name,1)
    elif kind=='speed_set':
        fields=['23-25','26-28','29-31','32-35','36+']; table='sw_spd'; column='Set'; weights=[1,2,3,4,5]; coefficient=coef_set_spd.get(set_name,1)
    else:
        fields=['mean_SCORE','max_SCORE'];table='sw_scoring_com2us';column='rune_set';weights=[];coefficient=1
    selected=','.join(f'd."{field}"' for field in fields)
    sql=f'SELECT {metadata},d.date,{selected} FROM {table} d'+join.format(key='id')+f'WHERE d."{column}"=:set_name'
    data=lire_bdd_perso(sql,index_col=None,params={'set_name':set_name}).T
    if weights:data['score']=data[fields].mul(weights).sum(axis=1)*coefficient
    return data

def classement():
    css()
    en=st.session_state.get('translations_selected')=='English'
    def tr(fr,english):return english if en else fr
    page_header(tr('Classements','Leaderboards'),tr('Chaque score provient d’un relevé complet.','Every score comes from one complete snapshot.'),icon='🏆')
    kinds={'Runes':'score_general','Speed':'score_spd','Artefacts':'score_arte',tr('Qualité','Quality'):'score_qual',tr('Runes par set','Runes by set'):'rune_set',tr('Vitesse par set','Speed by set'):'speed_set','Com2us':'com2us_global','Com2us (Set)':'com2us'}
    kind=kinds[st.selectbox(tr('Indicateur','Metric'),list(kinds))]
    mode=st.radio(tr('Relevé utilisé','Snapshot used'),['latest','record'],format_func=lambda x:tr('Dernier relevé','Latest snapshot') if x=='latest' else tr('Record personnel','Personal best'),horizontal=True)
    set_name=None
    if kind in ('rune_set','speed_set','com2us'):
        set_name=st.selectbox('Set',st.session_state.set_rune)
    data=leaderboard_data(kind,set_name)
    if kind in ('com2us','com2us_global'):
        metric=st.radio(tr('Valeur','Value'),(['mean_SCORE','max_SCORE'] if kind=='com2us' else ['sum_SCORE','max_SCORE']),horizontal=True)
        data['score']=data[metric]
    data=select_snapshots(data,'score',mode)
    from fonctions.leaderboards import visible_players
    data=visible_players(data,st.session_state.id_joueur,st.session_state.guildeid)
    if st.toggle(tr('Ma guilde uniquement','My guild only')):
        data=data[data.guilde_id.eq(st.session_state.guildeid)]
    if data.empty:
        st.info(tr('Aucun relevé disponible.','No snapshots available.'));return
    data.insert(0,tr('Rang','Rank'),data.score.rank(method='min',ascending=False).astype('int64'))
    limit=st.selectbox(tr('Lignes par page','Rows per page'),[25,50,100])
    number=st.number_input('Page',1,max(1,(len(data)+limit-1)//limit),1)
    st.caption(tr('Les anciens relevés conservent leur méthode de calcul.','Older snapshots retain their original scoring method.'))
    st.dataframe(data.iloc[(number-1)*limit:number*limit][[tr('Rang','Rank'),'joueur','guilde','score','date']],hide_index=True,width='stretch',column_config={'score':st.column_config.ProgressColumn('Score',min_value=0,max_value=max(float(data.score.max()),1))})

if __name__=='__main__':classement()
