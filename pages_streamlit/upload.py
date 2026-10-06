import json
import logging
from pathlib import Path
from os import environ

import pandas as pd
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from fonctions.gestion_bdd import lire_bdd
from fonctions.import_service import validate_export, analyse_export, persist_analysis, publish_analysis, InvalidExport
from fonctions.visuel import css, page_header

css()
language = st.radio('Langue / Language', ['Français','English'], key='translations_selected', horizontal=True)
english = language == 'English'
def tr(fr, en):
    return en if english else fr
st.session_state.langue = json.loads(Path('langue/en.json' if english else 'langue/fr.json').read_text(encoding='utf-8'))
page_header(tr('Analyser mon compte', 'Analyse my account'), tr('Importez votre export Summoners War pour identifier les améliorations utiles.', 'Import your Summoners War export to find useful upgrades.'), icon='📁')
with st.expander(tr('Comment obtenir le JSON ?', 'How do I get the JSON?')):
    st.markdown(tr('Exportez votre compte avec [SW Exporter](https://github.com/Xzandro/sw-exporter), puis déposez le fichier JSON ci-dessous. Vérifiez le compte dans l’aperçu avant de lancer l’analyse.', 'Export your account with [SW Exporter](https://github.com/Xzandro/sw-exporter), then upload the JSON below. Check the account preview before analysing.'))
    st.caption(tr('Le fichier sert à calculer vos statistiques. La sauvegarde de l’historique est optionnelle. La visibilité d’un nouveau compte est privée.', 'The file is used to calculate your statistics. Saving history is optional. New accounts are private.'))
    demo = Path('examples/demo.json').read_bytes()
    st.download_button(tr('Télécharger un exemple fictif', 'Download a fictional example'), demo, file_name='sw-demo.json', mime='application/json', on_click='ignore')

uploaded = st.file_uploader(tr('Export JSON', 'JSON export'), type=['json'], key='upload_file')
use_demo = st.checkbox(tr('Essayer avec le compte fictif', 'Try the fictional account'), key='demo_mode')
raw = demo if use_demo else uploaded.getvalue() if uploaded is not None else None
if st.session_state.get('analysis_ready'):
    st.success(tr('Dernière analyse disponible : ', 'Last analysis available: ') + st.session_state.pseudo)
    if st.button(tr('Ouvrir les résultats', 'Open results'), type='primary'):
        st.switch_page('pages_streamlit/general.py')
    if st.session_state.get('import_notice'):
        st.caption(st.session_state.import_notice)
if raw is not None:
    try:
        data = validate_export(raw)
    except InvalidExport as error:
        st.error(str(error))
        st.info(tr('Choisissez un export SW Exporter complet. Votre dernière analyse reste disponible.', 'Choose a complete SW Exporter export. Your last successful analysis remains available.'))
        st.stop()
    rune_count = len(data['runes']) + sum(len(u['runes']) for u in data['unit_list'])
    artifact_count = len(data['artifacts']) + sum(len(u['artifacts']) for u in data['unit_list'])
    a,b,c = st.columns(3)
    a.metric(tr('Compte', 'Account'), data['wizard_info']['wizard_name'])
    b.metric(tr('Runes', 'Runes'), rune_count)
    c.metric(tr('Artéfacts', 'Artifacts'), artifact_count)
    configured = bool(environ.get('API_SQL'))
    from fonctions.access import can_access
    authorized = configured and not use_demo and can_access(data['wizard_info']['wizard_id'])
    save = st.checkbox(tr('Sauvegarder dans mon historique', 'Save to my history'), value=authorized, disabled=not authorized, key='save_import') and authorized
    if configured and not use_demo and not authorized:
        st.info(tr('L’analyse locale reste disponible. Pour enregistrer, connectez-vous et demandez à l’administrateur de rattacher ce compte à votre identité.', 'Local analysis is available. To save, sign in and ask the administrator to link this account to your identity.'))
    if not configured:
        st.caption(tr('Mode local : l’analyse fonctionne sans base de données.', 'Local mode: analysis works without a database.'))
    if st.button(tr('Analyser ce fichier', 'Analyse this file'), key='upload_submit', type='primary'):
        with st.status(tr('Analyse en cours…', 'Analysing…'), expanded=True) as status:
            try:
                # Names are reference data, independent of saving or account authentication.
                reference = lire_bdd('sw_ref_monsters').T if configured and not use_demo else pd.DataFrame()
                result = analyse_export(data, reference, progress=status.write)
                if save and configured and not use_demo:
                    status.write(tr('Sauvegarde de l’historique', 'Saving history'))
                    metadata, inserted = persist_analysis(result)
                    notice = tr('Historique sauvegardé.', 'History saved.') if inserted else tr('Ce fichier avait déjà été enregistré : aucun doublon créé.', 'This file was already saved: no duplicate created.')
                else:
                    from datetime import datetime
                    from zoneinfo import ZoneInfo
                    metadata = dict(id_joueur=None, visibility=0, rank=0, report_date=datetime.now(ZoneInfo('Europe/Paris')).strftime('%d/%m/%Y'))
                    notice = tr('Analyse locale, sans enregistrement.', 'Local analysis, not saved.')
                publish_analysis(st.session_state, result, metadata)
                st.session_state.import_notice = notice
                if save and configured and not use_demo:
                    st.cache_data.clear()
                status.update(label=tr('Analyse terminée', 'Analysis complete'), state='complete', expanded=False)
            except (SQLAlchemyError, ValueError, KeyError, TypeError, IndexError, RuntimeError, PermissionError) as error:
                logging.getLogger(__name__).error('Import failed (%s)', type(error).__name__)
                status.update(label=tr('Analyse interrompue', 'Analysis interrupted'), state='error')
                st.error(tr('L’import n’a pas pu aboutir. Votre dernière analyse est conservée. Vérifiez le fichier et la connexion à la base avant de réessayer.', 'Import failed. Your last successful analysis is preserved. Check the file and database connection before retrying.'))
                st.caption(tr('Type d’erreur : ', 'Error type: ') + type(error).__name__)
            else:
                st.rerun()
