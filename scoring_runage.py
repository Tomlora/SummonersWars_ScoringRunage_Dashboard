"""Application entry point. Navigation depends on a successfully published analysis."""
import json
from pathlib import Path
import streamlit as st
from fonctions.visuel import css
from params.coef import coef_set, coef_set_spd

st.set_page_config(page_title='Summoners War · Scoring & Runage',page_icon='⚔️',layout='wide',initial_sidebar_state='expanded')
css()
from fonctions.access import login_panel, require_user, AccessDenied
login_panel()
if st.session_state.get('id_joueur') is not None:
    try:
        require_user(st.session_state.id_joueur)
    except AccessDenied:
        st.session_state.clear()
        st.warning('Accès au compte retiré / Account access revoked.')
if 'translations_selected' in st.session_state:
    st.session_state.translations_selected = st.session_state.translations_selected
english=st.session_state.get('translations_selected')=='English'
def tr(fr,en): return en if english else fr
st.session_state.langue=json.loads(Path('langue/en.json' if english else 'langue/fr.json').read_text(encoding='utf-8'))
st.session_state.category_selected=list(coef_set)
st.session_state.category_selected_spd=list(coef_set_spd)
st.session_state.coef_set=coef_set
st.session_state.coef_set_spd=coef_set_spd
ready=st.session_state.get('analysis_ready',False)
st.session_state.submitted=ready
saved=ready and st.session_state.get('id_joueur') is not None
if ready:
    from fonctions.workspace import current_settings, PREFIXES
    from copy import deepcopy
    preferences=current_settings()
    if st.session_state.pop('_restore_preferences',False):
        for key in list(st.session_state):
            if key.startswith(PREFIXES) or key.startswith('locks_'):
                del st.session_state[key]
        st.session_state.update(deepcopy(preferences['filters']))
        st.session_state.saved_filter_presets=deepcopy(preferences['presets'])
    # Keep widget values when Streamlit cleans up widgets from inactive pages.
    for key in list(st.session_state):
        if key.startswith((*PREFIXES, 'ui_', 'evol_')):
            st.session_state[key]=st.session_state[key]
def page(file,fr,en,icon): return st.Page('pages_streamlit/'+file+'.py',title=tr(fr,en),icon=icon)
pages={tr('Accueil','Home'):[page('upload','Importer un JSON','Import JSON','📁'),page('update','Nouveautés','Updates','🔈')]}
if ready:
    pages[tr('Mon compte','My account')]=[page('general','Vue générale','Overview','📚')]
    pages[tr('Runes','Runes')]=[page('optimisation','Optimisation','Optimisation','🔍'),page('stats_runes','Statistiques','Statistics','📊'),page('upgrade_runes','Améliorations','Upgrades','⬆️')]
    pages[tr('Artéfacts','Artifacts')]=[page('inventaire_artefact','Inventaire','Inventory','📂'),page('top_artefact','Meilleurs artéfacts','Best artifacts','🏆'),page('stats_artefact','Statistiques','Statistics','📊'),page('upgrade_artefact','Améliorations','Upgrades','⬆️')]
    pages[tr('Runes','Runes')]+=[page('planning','Planification','Planning','🛠️')]
    if saved:
        pages[tr('Mon compte','My account')]+=[page('import_changes','Changements entre imports','Import changes','🔄')]
        pages[tr('Mon compte','My account')]+=[page('evolution','Évolution','History','📈'),page('comparaison','Comparaison','Comparison','💹'),page('timeline_summon','Invocations','Summons','👻')]
        pages[tr('Runes','Runes')]+=[page('objectif_rune','Objectifs','Goals','💪'),page('todolist','Liste de tâches','To-do list','📋'),page('build_manager','Builds','Builds','🔨'),page('optimisation_spd','Meilleure vitesse','Best speed','⚡')]
        pages[tr('Artéfacts','Artifacts')]+=[page('objectif_arte','Objectifs','Goals','💪')]
        pages[tr('Classements','Leaderboards')]=[page('ladder','Scores','Scores','🥇'),page('ladder_value','Runes','Runes','🏆'),page('ladder_arte','Artéfacts','Artifacts','🏆'),page('ladder_others','PvP et World Boss','PvP and World Boss','🏆')]
        pages['Live']=[page('donjons','Donjons','Dungeons','🏯'),page('raid','Raid','Raid','🐲')]
        pages[tr('Paramètres','Settings')]=[page('visibility','Visibilité','Visibility','👀'),page('options','Mes données','My data','📱')]
    st.sidebar.caption(f"{st.session_state.pseudo} · {st.session_state.get('report_date','')}\n\n{tr('Calcul','Scoring')} {st.session_state.get('scoring_version','')}")
pages[tr('Calculateurs','Calculators')]=[page('calculator','Efficience des runes','Rune efficiency','🔢'),page('calculator_arte','Efficience des artéfacts','Artifact efficiency','💎'),page('dmg_add','Dégâts additionnels','Additional damage','💥'),page('use_arte','Utilisation des artéfacts','Artifact usage','🧠')]
with st.sidebar.expander(tr('Apparence','Appearance')):
    st.caption(tr('Retrouvez le thème d’origine avec Dark (sombre), ou choisissez Light pour un fond blanc : ouvrez ⋮ en haut à droite, puis Theme. System suit les préférences de votre appareil.', 'Choose Dark for the original theme, or Light for a white background: open ⋮ at the top right, then Theme. System follows your device preferences.'))
st.navigation(pages,position='sidebar',expanded=True).run()
