import pandas as pd
import plotly.express as px
import streamlit as st
from fonctions.visuel import css,page_header,apply_plotly_theme
from params.coef import coef_set

def general_page():
    css()
    en=st.session_state.get('translations_selected')=='English'
    def tr(fr,english):return english if en else fr
    if not st.session_state.get('analysis_ready'):
        st.info(tr('Importez un JSON pour commencer.','Import a JSON to get started.'))
        return
    page_header(st.session_state.pseudo,st.session_state.guilde,icon='📚')
    cols=st.columns(4)
    for col,key,label in zip(cols,['score','score_spd','score_arte','score_qual'],[tr('Score runes','Rune score'),tr('Score vitesse','Speed score'),tr('Score artéfacts','Artifact score'),tr('Score qualité','Quality score')]):
        col.metric(label,f"{int(st.session_state[key]):,} pts".replace(',', ' '))
    st.caption(f"{st.session_state.report_date} · {st.session_state.scoring_version} · {st.session_state.analysis_seconds:.2f} s")
    with st.expander(tr('Comprendre les scores','Understand the scores')):
        st.write(tr('Runes : 1, 2 ou 3 points pour les paliers [100,110[, [110,120[ et ≥120, multipliés par le coefficient du set. Le gain potentiel est une limite théorique, pas une promesse de résultat.', 'Runes: 1, 2 or 3 points for tiers [100,110), [110,120) and ≥120, multiplied by the set coefficient. Potential gain is a theoretical limit, not a guaranteed outcome.'))
        st.dataframe(pd.DataFrame(coef_set.items(),columns=['Set',tr('Coefficient','Weight')]),hide_index=True,width='stretch')
        st.caption(tr('Les historiques existants ne sont pas recalculés. Les corrections de méthode peuvent créer une rupture avec les anciens relevés.', 'Existing history is not recalculated. Method corrections can create a discontinuity with older snapshots.'))
    choice=st.segmented_control(tr('Analyse','Analysis'),['Scores',tr('Statistiques','Statistics'),tr('Monstres','Monsters')],default='Scores',key='overview_view')
    if choice=='Scores':
        st.dataframe(st.session_state.tcd.drop(columns=['id','date'],errors='ignore'),width='stretch')
        names={'runes':'Runes','speed':tr('Vitesse','Speed'),'artifacts':tr('Artéfacts','Artifacts'),'quality':tr('Qualité','Quality'),'com2us':'Com2us'}
        detail=st.selectbox(tr('Détail','Detail'),list(names),format_func=names.get,key='ui_overview_detail')
        key={'runes':'tcd_detail_score','speed':'tcd_spd','artifacts':'tcd_arte','quality':'df_scoring_quality','com2us':'df_scoring_com2us_summary'}[detail]
        st.dataframe(st.session_state[key].rename(columns=str),width='stretch')
    elif choice==tr('Statistiques','Statistics'):
        avg=st.session_state.data_avg
        st.dataframe(avg,width='stretch')
        if not avg.empty:
            st.plotly_chart(apply_plotly_theme(px.bar(avg,y=['moyenne','max'],barmode='group')),width='stretch')
            st.plotly_chart(apply_plotly_theme(px.pie(avg,names=avg.index,values='Nombre runes')),width='stretch')
    else:
        monsters=st.session_state.df_mobs.copy()
        reference=st.session_state.swarfarm
        if not reference.empty:
            monsters=monsters.merge(reference,left_on='id_monstre',right_on='com2us_id',how='left')
        mode=st.selectbox(tr('Collection','Collection'),['Box','2A','LD',tr('Autel de scellement','Sealed shrine')])
        if mode==tr('Autel de scellement','Sealed shrine'):
            monsters=pd.DataFrame(st.session_state.data_json.get('unit_storage_list',[]))
            if not monsters.empty and not reference.empty:
                monsters=monsters.merge(reference,left_on='unit_master_id',right_on='com2us_id',how='left')
        elif mode=='2A' and 'awaken_level' in monsters:
            monsters=monsters[monsters.awaken_level==2]
        elif mode=='LD' and 'element' in monsters:
            monsters=monsters[monsters.element.isin(['Light','Dark'])]
        query=st.text_input(tr('Rechercher un monstre','Find a monster'))
        name='name' if 'name' in monsters else 'name_monstre'
        if query and name in monsters:
            monsters=monsters[monsters[name].astype(str).str.contains(query,case=False,regex=False)]
        star_column='natural_stars' if mode=='LD' else '*' if '*' in monsters else 'class'
        if star_column in monsters:
            stars=st.multiselect(tr('Étoiles','Stars'),sorted(monsters[star_column].dropna().unique()))
            if stars:monsters=monsters[monsters[star_column].isin(stars)]
        if monsters.empty:
            st.info(tr('Aucun monstre pour cette sélection.','No monsters for this selection.'))
        else:
            number=st.number_input('Page',1,max(1,(len(monsters)+23)//24),1,key='monsters_page')
            shown=monsters.iloc[(number-1)*24:number*24].copy()
            columns=[c for c in [name,star_column,'level','quantity','Date_invocation'] if c in shown]
            if 'image_filename' in shown:
                shown['Image']='https://swarfarm.com/static/herders/images/monsters/'+shown.image_filename.fillna('')
                columns.insert(0,'Image')
            st.dataframe(shown[columns],hide_index=True,width='stretch',column_config={'Image':st.column_config.ImageColumn()})

if __name__=='__main__':
    general_page()
