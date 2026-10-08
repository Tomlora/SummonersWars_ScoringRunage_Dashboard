from pathlib import Path
import pytest
import pandas as pd
from streamlit.testing.v1 import AppTest
from fonctions.import_service import analyse_export, validate_export, persist_analysis, publish_analysis
from fonctions.workspace import load_settings, settings

ROOT=Path(__file__).resolve().parents[1]


def seed(result,metadata,language='Français'):
    state={};publish_analysis(state,result,metadata)
    at=AppTest.from_file(str(ROOT/'scoring_runage.py'),default_timeout=30)
    for key,value in state.items():at.session_state[key]=value
    at.session_state['translations_selected']=language
    return at.run()


@pytest.mark.parametrize('language',['Français','English'])
def test_plan_search_and_lock_interactions(export,monkeypatch,language):
    monkeypatch.chdir(ROOT);monkeypatch.delenv('API_SQL',raising=False)
    export['rune_craft_item_list']=[dict(craft_type=2,craft_type_id=30805,amount=1)]
    result=analyse_export(validate_export(export),pd.DataFrame())
    at=seed(result,dict(id_joueur=None,report_date='06/10/2026'),language)
    at.switch_page('pages_streamlit/planning.py').run()
    assert not at.exception
    search=next(b for b in at.button if b.label in ['Rechercher le build','Search build'])
    search.click().run()
    assert not at.exception
    assert any('SPD +' in s.value for s in at.success)
    at.multiselect(key='locks_runes').set_value(list(result['data_rune'].data.index)).run()
    search=next(b for b in at.button if b.label in ['Rechercher le build','Search build'])
    search.click().run()
    assert not at.exception
    assert any('Aucun build' in s.value or 'No build' in s.value for s in at.info)


def test_preferences_survive_new_session_and_language(engine,export,monkeypatch):
    monkeypatch.chdir(ROOT)
    result=analyse_export(validate_export(export),pd.DataFrame())
    metadata,_=persist_analysis(result)
    at=seed(result,metadata).switch_page('pages_streamlit/optimisation.py').run()
    at.button[0].click().run()
    at.multiselect(key='optimisation_filter_actions').set_value(['gem']).run()
    at.selectbox(key='optimisation_filter_priority').set_value('high').run()
    at.toggle(key='optimisation_show_substats').set_value(True).run()
    at.multiselect(key='optimisation_displayed_substats').set_value(['SPD','ACC']).run()
    at.switch_page('pages_streamlit/planning.py').run()
    at.number_input(key='plan_accuracy').set_value(40).run()
    at.multiselect(key='locks_runes').set_value([301]).run()
    next(b for b in at.button if b.label=='Enregistrer mes préférences').click().run()
    assert not at.exception
    saved=load_settings(metadata['id_joueur'])
    assert saved['filters']['optimisation_filter_actions']==['gem']
    assert saved['locked_runes']==[301]
    fresh=seed(result,metadata,'English').switch_page('pages_streamlit/optimisation.py').run()
    fresh.button[0].click().run()
    assert not fresh.exception
    assert fresh.multiselect(key='optimisation_filter_actions').value==['gem']
    assert fresh.selectbox(key='optimisation_filter_priority').value=='high'
    assert fresh.multiselect(key='optimisation_displayed_substats').value==['SPD','ACC']
    fresh.switch_page('pages_streamlit/planning.py').run()
    assert not fresh.exception
    assert fresh.number_input(key='plan_accuracy').value==40
    assert fresh.multiselect(key='locks_runes').value==[301]


def test_account_switch_clears_local_preferences(export):
    result=analyse_export(validate_export(export),pd.DataFrame())
    state={'compteid':1,'_workspace':settings(),'saved_filter_presets':{'mine':{}},'plan_accuracy':30}
    metadata=dict(id_joueur=None,report_date='06/10/2026')
    publish_analysis(state,result,metadata)
    assert state['plan_accuracy']==30
    result['compteid']=2
    publish_analysis(state,result,metadata)
    assert '_workspace' not in state and 'saved_filter_presets' not in state and 'plan_accuracy' not in state
