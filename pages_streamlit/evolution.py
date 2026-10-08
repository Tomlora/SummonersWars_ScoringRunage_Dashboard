from fonctions.access import require_saved_page
require_saved_page()
import pandas as pd
import plotly.express as px
import streamlit as st
from fonctions.gestion_bdd import lire_bdd_perso, connection
from fonctions.visualisation import transformation_stats_visu
from fonctions.visuel import css, page_header, apply_plotly_theme
from fonctions.journey import tr, dated, period_rows, score_labels
from sqlalchemy import inspect, text

css()
page_header(tr('Évolution','History'),tr('Suivez votre progression sur une période commune à tous les graphiques.','Track your progress over the same period in every chart.'),icon='📈')
user=st.session_state.id_joueur
scores=lire_bdd_perso('SELECT date,score_general,score_spd,score_arte,score_qual FROM sw_score WHERE id_joueur=:id',index_col=None,params={'id':user}).T
if scores.empty:
    st.info(tr('Aucun relevé disponible.','No reports available.'))
    st.stop()
labels=score_labels()
periods={'30':tr('30 jours','30 days'),'90':tr('90 jours','90 days'),'365':tr('Un an','One year'),'all':tr('Tout','All')}
def reset_dates():
    st.session_state.pop('ui_history_dates',None)
period=st.radio(tr('Période','Period'),list(periods),index=3,format_func=periods.get,horizontal=True,key='ui_history_period',on_change=reset_dates)
end=dated(scores)._date.max()
selected=period_rows(scores,None if period=='all' else int(period),end)
st.caption(tr('Période se terminant au dernier relevé : ','Period ending at the latest report: ')+end.strftime('%d/%m/%Y'))
options=selected.date.tolist()
if 'ui_history_dates' in st.session_state:
    st.session_state.ui_history_dates=[d for d in st.session_state.ui_history_dates if d in options]
with st.expander(tr('Choisir les relevés affichés','Choose displayed reports')):
    dates=st.multiselect(tr('Relevés','Reports'),options,default=options,key='ui_history_dates')
selected=selected[selected.date.isin(dates)]
if selected.empty:
    st.info(tr('Sélectionnez au moins un relevé.','Select at least one report.'))
    st.stop()
versions={}
with connection() as conn:
    if inspect(conn).has_table('sw_imports'):
        for day,version in conn.execute(text('SELECT DISTINCT date,scoring_version FROM sw_imports WHERE id_joueur=:id'),{'id':int(user)}):
            versions.setdefault(day,set()).add(version)
known=[versions.get(d,set()) for d in selected.date]
comparable=all(len(v)==1 for v in known) and len(set.union(*known))==1
first,last=selected.iloc[0],selected.iloc[-1]
for col,(key,label) in zip(st.columns(4),labels.items()):
    delta=float(last[key])-float(first[key]) if len(selected)>1 and comparable else None
    col.metric(label,f'{last[key]:g} pts',None if delta is None else f'{delta:+g} pts')
st.caption(tr('Progression absolue entre ','Absolute change between ')+f'{first.date} → {last.date} · {len(selected)} '+tr('relevés','reports'))
if len(selected)<2:
    st.info(tr('Deux relevés sont nécessaires pour mesurer une progression.','Two reports are needed to measure progress.'))
elif not comparable:
    st.warning(tr('Méthodes de calcul différentes ou inconnues : les écarts ne sont pas calculés. Les valeurs historiques restent affichées.','Scoring methods differ or are unknown: changes are not calculated. Historical values are still displayed.'))
st.dataframe(selected.iloc[::-1].rename(columns=labels).set_index('date'),width='stretch',height='content')

def plot(frame,y,color=None,dash=None,unit=None,key=None):
    if frame.empty:
        st.info(tr('Aucune donnée pour cette sélection.','No data for this selection.'))
        return
    frame=dated(frame)
    fig=px.line(frame,x='_date',y=y,color=color,line_dash=dash,markers=True,labels={'_date':tr('Date','Date'),y:unit or tr('Nombre','Count'),'Set':'Set','Palier':tr('Palier','Tier'),'arte_type':tr('Type','Type'),'type':tr('Attribut','Attribute')})
    st.plotly_chart(apply_plotly_theme(fig),width='stretch',key='history_chart_'+(key or y))

detail=st.checkbox(tr('Détail par set','Details by set'),key='ui_history_detail')
if detail:
    runes=lire_bdd_perso('SELECT rune_set AS "Set","100","110","120",points,date FROM sw_detail WHERE id=:id',index_col=None,params={'id':user}).T
    quality=lire_bdd_perso('SELECT rune_set AS "Set","LGD","ANTIQUE_LGD",score,date FROM sw_score_qual WHERE id=:id',index_col=None,params={'id':user}).T
    sets=sorted(set(runes.Set.dropna())-{'Total'})
    if 'ui_history_sets' in st.session_state:
        st.session_state.ui_history_sets=[s for s in st.session_state.ui_history_sets if s in sets]
    chosen=st.multiselect(tr('Sets','Sets'),sets,default=sets[:1],key='ui_history_sets')
    runes=runes[runes.date.isin(dates)&runes.Set.isin(chosen)]
    quality=quality[quality.date.isin(dates)&quality.Set.isin(chosen)]
    a,b=st.tabs([tr('Runes','Runes'),tr('Qualité','Quality')])
    with a:
        st.dataframe(runes,width='stretch',hide_index=True)
        for tab,field in zip(st.tabs([tr('Score (points)','Score (points)'),'100 ≤ E < 110','110 ≤ E < 120','E ≥ 120']),['points','100','110','120']):
            with tab:
                plot(runes,field,'Set',unit=tr('Points','Points') if field=='points' else None)
    with b:
        st.dataframe(quality.rename(columns={'LGD':tr('Légendaires','Legendary'),'ANTIQUE_LGD':tr('Légendaires antiques','Ancient legendary')}),width='stretch',hide_index=True)
        for tab,field in zip(st.tabs([tr('Score (points)','Score (points)'),tr('Légendaires','Legendary'),tr('Légendaires antiques','Ancient legendary')]),['score','LGD','ANTIQUE_LGD']):
            with tab:
                plot(quality,field,'Set',unit=tr('Points','Points') if field=='score' else None)
else:
    metric=st.radio(tr('Indicateur','Metric'),list(labels),format_func=labels.get,horizontal=True,key='ui_history_metric')
    plot(selected,metric,unit=tr('Score (points)','Score (points)'))
    table={'score_general':'sw','score_spd':'sw_spd','score_arte':'sw_arte'}.get(metric)
    if table:
        details=transformation_stats_visu(table,user,distinct=True,ascending=True)
        details=details[details.date.isin(dates)]
        tiers={'sw':['100','110','120'],'sw_spd':['23-25','26-28','29-31','32-35','36+'],'sw_arte':['80','85','90','95','100+']}[table]
        names=[tr('Palier ','Tier ')+value for value in tiers]
        for tab,tier in zip(st.tabs(names),tiers):
            with tab:
                group=details[details.Palier.eq(tier)]
                plot(group,'Nombre','arte_type' if table=='sw_arte' else 'Set','type' if table=='sw_arte' else None,key=table+tier)
