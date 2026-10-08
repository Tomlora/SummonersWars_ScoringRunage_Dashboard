import streamlit as st
from fonctions.access import require_saved_page
from fonctions.snapshots import list_snapshots, load_snapshot, compare_snapshots
require_saved_page()
english=st.session_state.get('translations_selected')=='English'
def tr(fr,en): return en if english else fr
st.title(tr('Changements entre imports','Changes between imports'))
st.caption(tr('Les instantanés détaillés commencent avec cette version. Les anciens scores agrégés ne permettent pas de reconstruire les runes. Deux imports différents d’une même journée sont conservés.', 'Detailed snapshots start with this version. Old aggregate scores cannot reconstruct runes. Distinct same-day imports are retained.'))
user_id=st.session_state.id_joueur
snapshots=list_snapshots(user_id)
if len(snapshots)<2:
    st.info(tr('Enregistrez deux exports différents pour comparer les runes.', 'Save two different exports to compare runes.'))
    st.stop()
def label(i):
    s=snapshots[i]
    return f"{s['imported_at']} · {s['payload_sha'][:8]} · {s['scoring_version']}"
a,b=st.columns(2)
old=a.selectbox(tr('Avant','Before'),range(len(snapshots)),index=len(snapshots)-2,format_func=label)
new=b.selectbox(tr('Après','After'),range(len(snapshots)),index=len(snapshots)-1,format_func=label)
def load(i): return load_snapshot(user_id,snapshots[i]['payload_sha'],snapshots[i]['scoring_version'])
before,after=load(old),load(new)
try:
    changes=compare_snapshots(before,after)
except ValueError as error:
    st.warning(str(error)); st.stop()
st.metric(tr('Score runage','Rune score'),after['score'],delta=after['score']-before['score'])
st.caption(tr('Une efficience vide signifie que le calcul est indisponible pour cette rune. Elle ne contribue pas au score et ne permet pas de conclure à une amélioration.', 'An empty efficiency means the calculation is unavailable for that rune. It contributes no score and cannot establish an improvement.'))
st.caption(tr('La contribution de chaque rune dépend de son palier d’efficience (100/110/120) et du coefficient de son set. Une amélioration peut donc ne pas changer le score. « Disparue » signifie absente de l’export, pas nécessairement vendue.', 'Each rune contributes according to its efficiency tier (100/110/120) and set coefficient. An improvement may therefore leave the score unchanged. Removed means absent from the export, not necessarily sold.'))
names={'added':tr('Nouvelle','New'),'removed':tr('Disparue','Removed'),'improved':tr('Améliorée','Improved'),'changed':tr('Modifiée','Changed')}
selected=st.multiselect(tr('Changements','Changes'),list(names),default=list(names),format_func=names.get)
shown=changes[changes.status.isin(selected)].copy()
shown['status']=shown.status.map(names)
fields={'set_id':'Set','slot_no':'Slot','occupied_id':tr('Équipement','Equipment'),
        'class':tr('Étoiles','Stars'),'rank':tr('Qualité','Quality'),'extra':tr('Qualité initiale','Original quality'),
        'upgrade_curr':tr('Niveau','Level'),'pri_eff':tr('Principale','Main stat'),
        'prefix_eff':tr('Innée','Innate stat'),'sec_eff':tr('Sous-statistiques','Substats')}
shown['changes']=shown.changes.map(lambda value:', '.join(fields.get(v,v) for v in value.split(', ') if v))
shown=shown.rename(columns={'id_rune':'Rune','status':tr('État','Status'),'changes':tr('Changements','Changes'),
     'efficiency_before':tr('Efficience avant','Efficiency before'),'efficiency_after':tr('Efficience après','Efficiency after'),
     'score_delta':tr('Écart de score','Score change')})
st.dataframe(shown,hide_index=True,width='stretch')
st.download_button(tr('Exporter les différences','Export changes'),shown.to_csv(index=False).encode('utf-8-sig'),'rune-changes.csv','text/csv',on_click='ignore')
