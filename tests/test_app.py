from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from fonctions.import_service import analyse_export, publish_analysis, validate_export
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
PAGES=['general','optimisation','stats_runes','inventaire_artefact','top_artefact','stats_artefact','upgrade_runes','upgrade_artefact','calculator','calculator_arte','dmg_add','use_arte','planning']

def check(at):
    assert not at.exception, [error.message for error in at.exception]

def seeded(export,language='Français'):
    at=AppTest.from_file(str(ROOT/'scoring_runage.py'),default_timeout=30)
    state={}
    publish_analysis(state,analyse_export(validate_export(export),pd.DataFrame()),{'id_joueur':None,'report_date':'05/10/2026'})
    for key,value in state.items(): at.session_state[key]=value
    at.session_state['translations_selected']=language
    return at.run()

@pytest.mark.parametrize('language',['Français','English'])
@pytest.mark.parametrize('count',[0,1,24])
def test_local_navigation(export,monkeypatch,language,count):
    monkeypatch.chdir(ROOT)
    monkeypatch.delenv('API_SQL',raising=False)
    export['runes']=export['runes'][:count]
    at=seeded(export,language)
    for page in PAGES:
        at.switch_page('pages_streamlit/'+page+'.py').run()
        check(at)
        assert at.session_state['translations_selected']==language

def test_demo_import_ignores_configured_database(monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv('API_SQL','postgresql://invalid.invalid/not-used')
    at=AppTest.from_file(str(ROOT/'scoring_runage.py'),default_timeout=30).run()
    at.checkbox(key='demo_mode').check().run()
    at.button(key='upload_submit').click().run()
    check(at)
    assert not at.error
    assert at.session_state['analysis_ready']
    assert at.session_state['id_joueur'] is None

@pytest.mark.parametrize('language',['Français','English'])
def test_optimisation_interactions(export,monkeypatch,language):
    monkeypatch.chdir(ROOT);monkeypatch.delenv('API_SQL',raising=False)
    at=seeded(export,language).switch_page('pages_streamlit/optimisation.py').run()
    at.button[0].click().run();check(at)
    at.toggle(key='optimisation_show_substats').set_value(True).run();check(at)
    at.multiselect(key='optimisation_filtered_substats').select('SPD').run();check(at)
    at.number_input(key='optimisation_min_SPD').set_value(999).run();check(at)
    assert any(('Aucun' in info.value or 'No ' in info.value) for info in at.info)
    for button in at.button:
        if button.label in ['Réinitialiser les filtres','Reset filters']:
            button.click().run();break
    check(at)

def test_statistic_views(export,monkeypatch):
    monkeypatch.chdir(ROOT);monkeypatch.delenv('API_SQL',raising=False)
    at=seeded(export).switch_page('pages_streamlit/stats_runes.py').run()
    for view in ['Top 10','Substats / Slot','Efficience / Slot','Qualité']:
        at.segmented_control[0].set_value(view).run();check(at)
