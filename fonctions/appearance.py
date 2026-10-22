"""Browser-local appearance choices; never change the server's shared theme."""
from pathlib import Path

import streamlit as st
from streamlit.components.v2 import component

from fonctions.journey import tr


PALETTES = {
    'custom': dict(base=1, primaryColor='#49a4ff', backgroundColor='#07111f',
                   secondaryBackgroundColor='#101f33', textColor='#f4f7fb',
                   borderColor='#304057'),
    'white': dict(base=0, primaryColor='#176bb3', backgroundColor='#ffffff',
                  secondaryBackgroundColor='#f1f5fa', textColor='#172536',
                  borderColor='#c6d1df'),
    'black': dict(base=1, primaryColor='#49a4ff', backgroundColor='#000000',
                  secondaryBackgroundColor='#161616', textColor='#f4f7fb',
                  borderColor='#444444'),
}

def _selector():
    # Register in the active runtime, including each isolated AppTest session.
    return component(
        'sw_appearance',
        js=Path(__file__).with_name('appearance.js').read_text(encoding='utf-8'),
        html='<fieldset><legend></legend><div class="choices"></div></fieldset><p role="status"></p>',
        css='''
            fieldset { border:0; margin:0; padding:0; min-width:0; }
            legend { font-weight:600; margin-bottom:.5rem; }
            .choices { display:flex; flex-direction:column; gap:.45rem; }
            label { display:flex; align-items:center; gap:.55rem; cursor:pointer; padding:.3rem 0; }
            input { accent-color:var(--st-primary-color); width:1rem; height:1rem; }
            input:focus-visible { outline:2px solid var(--st-primary-color); outline-offset:3px; }
            .swatch { width:1rem; height:1rem; border-radius:50%; border:1px solid #8996a6; }
            p { margin:.6rem 0 0; font-size:.85rem; }
        ''',
    )


def appearance_menu():
    with st.sidebar.expander(tr('Apparence', 'Appearance')):
        _selector()(key='ui_appearance', data={
            'palettes': PALETTES,
            'labels': {'custom': tr('Personnalisé · bleu sombre', 'Custom · dark blue'),
                       'white': tr('Blanc', 'White'), 'black': tr('Noir', 'Black')},
            'legend': tr('Thème', 'Theme'),
            'applying': tr('Application du thème…', 'Applying theme…'),
            'saved': tr('Votre choix est mémorisé dans ce navigateur.', 'Your choice is remembered in this browser.'),
            'temporary': tr('Votre navigateur ne permet pas de mémoriser ce choix.', 'Your browser cannot remember this choice.'),
            'error': tr('Le thème n’a pas pu être appliqué. Rechargez la page ; si cela persiste, contactez l’administrateur.',
                        'The theme could not be applied. Reload the page; if this persists, contact the administrator.'),
        })
