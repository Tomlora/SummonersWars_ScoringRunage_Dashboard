from pathlib import Path
import tomllib

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from fonctions.appearance import PALETTES

ROOT = Path(__file__).resolve().parents[1]


def test_custom_palette_remains_the_server_default():
    config = tomllib.loads((ROOT / '.streamlit/config.toml').read_text(encoding='utf-8'))
    assert config['theme']['base'] == 'dark'
    for key in ('primaryColor', 'backgroundColor', 'secondaryBackgroundColor', 'textColor'):
        assert PALETTES['custom'][key] == config['theme'][key]
    assert PALETTES['white']['backgroundColor'] == '#ffffff'
    assert PALETTES['black']['backgroundColor'] == '#000000'
    assert config['client']['allowedOrigins'] == [
        'https://scoringsw.eu', 'http://localhost', 'http://127.0.0.1:*']


@pytest.mark.parametrize('language', ['Français', 'English'])
def test_appearance_menu_does_not_mutate_shared_configuration(language, monkeypatch):
    monkeypatch.chdir(ROOT)
    before = {key: st.get_option('theme.' + key) for key in ('base', 'backgroundColor', 'textColor')}
    at = AppTest.from_string('''
import streamlit as st
from fonctions.appearance import appearance_menu
appearance_menu()
st.button('Rerun')
''')
    at.session_state['translations_selected'] = language
    at.run()
    assert not at.exception
    assert at.sidebar.expander[0].label == ('Apparence' if language == 'Français' else 'Appearance')
    at.button[0].click().run()
    assert not at.exception
    assert before == {key: st.get_option('theme.' + key) for key in before}
