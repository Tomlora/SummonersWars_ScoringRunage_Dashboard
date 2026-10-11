import pandas as pd
import pytest
import streamlit as st

from fonctions.planning import grind_plan
from fonctions.runes import Rune
from fonctions.rune_visual import rune_identity, rune_label, rune_svg


@pytest.mark.parametrize('language', ['Français', 'English'])
@pytest.mark.parametrize('rune_id', [14155954582, 2**55 + 1])
def test_grind_plan_identifies_equipped_rune_with_serialized_id(export, language, rune_id):
    st.session_state['translations_selected'] = language
    export['runes'] = export['runes'][:1]
    export['runes'][0].update(rune_id=rune_id, occupied_id=55)
    runes = Rune(export, {55: 'Fran'})
    plan, _ = grind_plan(runes, [dict(craft_type=2, craft_type_id=30805, amount=1)])
    assert len(plan) == 1
    serialized = plan.iloc[0].id_rune
    assert serialized == str(rune_id)
    identity = rune_identity(runes, serialized)
    assert identity == rune_identity(runes, rune_id)
    assert identity['Set'] == 'Swift' and identity['Slot'] == 1
    assert identity['Équipée sur' if language == 'Français' else 'Equipped on'] == 'Fran'
    assert 'SPD +34' in identity['Sous-statistiques' if language == 'Français' else 'Substats']
    label = rune_label(runes, serialized)
    assert 'Fran' in label and 'Slot 1' in label and str(rune_id) not in label
    assert rune_svg(runes, serialized) == rune_svg(runes, rune_id)
    csv = pd.DataFrame([identity]).to_csv(index=False)
    assert 'Fran' in csv and 'SPD +34' in csv and str(rune_id) not in csv


@pytest.mark.parametrize('language', ['Français', 'English'])
def test_unavailable_rune_does_not_invent_details_or_show_a_technical_id(export, language):
    st.session_state['translations_selected'] = language
    runes = Rune(export, {})
    for unavailable in ('14155954582', '301.0', None, True):
        label = rune_label(runes, unavailable)
        assert label == ('Rune introuvable dans le fichier importé' if language == 'Français'
                         else 'Rune not found in the imported file')
        assert rune_identity(runes, unavailable) == {'Rune': label}
        with pytest.raises(KeyError):
            rune_svg(runes, unavailable)
