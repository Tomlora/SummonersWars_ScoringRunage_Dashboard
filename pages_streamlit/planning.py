import json
import streamlit as st
from fonctions.workspace import current_settings, save_current, settings, saved_builds, active_locks
from fonctions.planning import grind_plan, constrained_build, SearchLimit

english=st.session_state.get('translations_selected')=='English'
def tr(fr,en): return en if english else fr

def craft_labels(kind,code):
    return {
        'Type':{2:tr('Meule','Grind'),4:tr('Meule immémoriale','Immemorial grind'),6:tr('Meule antique','Ancient grind')}[kind],
        'Set':tr('Universelle','Universal') if kind==4 else runes.set.get(code//10000,str(code//10000)),
        'Stat':runes.property.get((code//100)%100,str((code//100)%100)),
        tr('Qualité','Quality'):{4:tr('Héroïque','Hero'),5:tr('Légendaire','Legendary')}.get(code%100,str(code%100)),
    }

st.title(tr('Planifier mes améliorations','Plan my upgrades'))
value=current_settings()
runes=st.session_state.data_rune
user_id=st.session_state.get('id_joueur')
builds=saved_builds(user_id) if user_id is not None else []

with st.expander(tr('Protéger mes équipes','Protect my teams'),expanded=True):
    st.caption(tr('Les runes verrouillées sont exclues des recommandations, du plan de meules et des recherches de builds. Les verrous de monstres suivent leurs runes au prochain import.', 'Locked runes are excluded from recommendations, grind plans and build searches. Monster locks follow their runes on the next import.'))
    ids=sorted(set(int(v) for v in runes.data.index)|set(value['locked_runes']))
    value['locked_runes']=st.multiselect(tr('Runes verrouillées','Locked runes'),ids,default=value['locked_runes'],format_func=str,key='locks_runes')
    monsters={int(u['unit_id']):st.session_state.identification_monsters.get(u['unit_id'],str(u['unit_id'])) for u in st.session_state.data_json['unit_list']}
    value['locked_monsters']=st.multiselect(tr('Monstres protégés','Protected monsters'),sorted(monsters.keys()|set(value['locked_monsters'])),default=value['locked_monsters'],format_func=lambda i:f'{monsters.get(i,"Absent")} · #{i}',key='locks_monsters')
    labels={int(b['id_build']):f"{b['monstre']} · {b['nom_build']}" for b in builds}
    value['locked_builds']=st.multiselect(tr('Builds enregistrés protégés','Protected saved builds'),sorted(labels.keys()|set(value['locked_builds'])),default=value['locked_builds'],format_func=lambda i:f'{labels.get(i,"Absent")} · #{i}',key='locks_builds')
    if st.button(tr('Enregistrer les verrous','Save locks')):
        save_current()
        st.success(tr('Verrous enregistrés.' if user_id else 'Verrous appliqués à cette session.', 'Locks saved.' if user_id else 'Locks applied to this session.'))
locks=active_locks()
st.caption(tr(f'{len(locks)} runes protégées.', f'{len(locks)} protected runes.'))

stock_tab,build_tab,prefs_tab=st.tabs([tr('Stock de meules','Grind stock'),tr('Build sur critères','Build criteria'),tr('Préférences','Preferences')])
with stock_tab:
    if 'plan_sets' in st.session_state:
        st.session_state.plan_sets=[s for s in st.session_state.plan_sets if s in set(runes.data.rune_set)]
    sets=st.multiselect(tr('Sets prioritaires (vide = tous)','Priority sets (empty = all)'),sorted(runes.data.rune_set.unique()),key='plan_sets')
    st.caption(tr('Allocation par gain d’efficience décroissant, une meule par statistique. Chaque quantité est réservée une seule fois. Les gains sont des maxima aléatoires, sans garantie de résultat ni d’optimalité globale. Les gemmes sont exclues. Rien n’est consommé dans le jeu.', 'Greedy allocation by efficiency gain, one grind per stat. Each item is reserved once. Gains are random-roll maxima, with no guaranteed outcome or global optimum. Gems are excluded. Nothing is consumed in game.'))
    plan,remaining=grind_plan(runes,st.session_state.data_json['rune_craft_item_list'],locks,sets)
    a,b=st.columns(2)
    a.metric(tr('Meules réservées','Reserved grinds'),len(plan))
    b.metric(tr('Gain total maximal (points d’efficience)','Maximum total efficiency points'),round(plan.max_gain.sum(),2))
    if plan.empty:
        st.info(tr('Aucune amélioration compatible avec le stock et les verrous.', 'No upgrade matches your stock and locks.'))
    else:
        import pandas as pd
        shown=pd.DataFrame([{'Rune':row.id_rune,**craft_labels(row.craft_type,row.craft_type_id),
              tr('Meule actuelle','Current grind'):row.current_grind,
              tr('Meule maximale','Maximum grind'):row.max_grind,
              tr('Gain max.','Max gain'):round(row.max_gain,2)} for row in plan.itertuples()])
        st.dataframe(shown,hide_index=True,width='stretch')
        st.download_button(tr('Exporter le plan','Export plan'),shown.to_csv(index=False).encode('utf-8-sig'),'grind-plan.csv','text/csv',on_click='ignore')
        with st.expander(tr('Fiche d’une rune','Rune details')):
            from fonctions.rune_card import rune_card
            rune_card(runes,plan.id_rune,'ui_plan_rune',plan.groupby('id_rune').max_gain.sum().to_dict())
    if remaining:
        import pandas as pd
        with st.expander(tr('Stock restant après réservation','Stock after reservation')):
            st.dataframe(pd.DataFrame([{**craft_labels(kind,code),tr('Restant','Remaining'):amount} for (kind,code),amount in sorted(remaining.items())]),hide_index=True,width='stretch')

with build_tab:
    st.caption(tr('Maximise la vitesse apportée par six runes de niveau ≥12, avec leurs valeurs actuelles. Les seuils SPD et ACC portent sur les statistiques des runes, principales et innées incluses, avant statistiques du monstre, bonus de set, bâtiments et leader.', 'Maximizes speed from six level ≥12 runes using current values. SPD and ACC minima cover rune stats, including main and innate stats, before monster stats, set bonuses, buildings and leader skills.'))
    primary=st.selectbox(tr('Set de 4','Four-piece set'),['Swift','Violent','Despair','Fatal','Rage','Vampire'],key='plan_primary')
    secondary=st.selectbox(tr('Set de 2','Two-piece set'),['any','Will','Focus','Energy','Guard','Blade','Endure','Nemesis','Shield','Revenge','Destroy','Tolerance'],format_func=lambda x:tr('Libre','Any') if x=='any' else x,key='plan_secondary')
    a,b=st.columns(2)
    speed=a.number_input(tr('SPD minimale des runes','Minimum rune SPD'),min_value=0,max_value=400,step=1,key='plan_speed')
    accuracy=b.number_input(tr('ACC minimale des runes (%)','Minimum rune ACC (%)'),min_value=0,max_value=300,step=1,key='plan_accuracy')
    slot2=st.checkbox(tr('Principale SPD en slot 2','SPD main in slot 2'),value=True,key='plan_slot2')
    signature=(st.session_state.import_hash,primary,secondary,speed,accuracy,slot2,tuple(sorted(locks)))
    if st.button(tr('Rechercher le build','Search build'),type='primary'):
        st.session_state.pop('_build_result',None)
        with st.spinner(tr('Recherche…','Searching…')):
            try:
                build=constrained_build(runes.data_set,primary,None if secondary=='any' else secondary,speed,accuracy,locks,slot2)
            except SearchLimit as error:
                st.warning(str(error))
            else:
                st.session_state['_build_result']=(signature,build)
    cached=st.session_state.get('_build_result')
    if cached and cached[0] != signature:
        st.info(tr('Les critères ou les verrous ont changé. Relancez la recherche pour actualiser le build.', 'Criteria or locks changed. Run the search again to update the build.'))
    elif cached:
        build=cached[1]
        if build.empty:
            st.info(tr('Aucun build ne satisfait ces critères et verrous.', 'No build satisfies these criteria and locks.'))
        else:
            st.dataframe(build.assign(id_rune=build.id_rune.astype(str)).rename(columns={'id_rune':'Rune','rune_slot':'Slot','rune_set':'Set','spd':'SPD','acc':'ACC (%)'}),hide_index=True,width='stretch')
            st.success(f"SPD +{build.spd.sum():g} · ACC +{build.acc.sum():g}%")
            with st.expander(tr('Examiner les runes du build','Inspect build runes')):
                from fonctions.rune_card import rune_card
                rune_card(runes,build.id_rune,'ui_build_rune')

with prefs_tab:
    st.caption(tr('Enregistrez les filtres, colonnes, critères et verrous. Les objectifs restent enregistrés depuis leurs pages. Sans historique enregistré, exportez les préférences pour les retrouver plus tard.', 'Save filters, columns, criteria and locks. Goals remain saved from their own pages. Without saved history, export preferences to restore them later.'))
    if st.button(tr('Enregistrer mes préférences','Save my preferences')):
        save_current()
        st.success(tr('Préférences enregistrées.' if user_id else 'Préférences prêtes à exporter.', 'Preferences saved.' if user_id else 'Preferences ready to export.'))
    st.download_button(tr('Exporter les préférences','Export preferences'),json.dumps(value,ensure_ascii=False,indent=2),'sw-preferences.json','application/json',on_click='ignore')
    portable=st.file_uploader(tr('Restaurer des préférences','Restore preferences'),type=['json'],key='preferences_upload')
    if portable is not None and st.button(tr('Restaurer','Restore')):
        try:
            restored=settings(json.loads(portable.getvalue()))
        except (ValueError,TypeError,UnicodeError):
            st.error(tr('Fichier de préférences incompatible.', 'Incompatible preferences file.'))
        else:
            st.session_state['_workspace']=restored
            st.session_state['_restore_preferences']=True
            st.rerun()
