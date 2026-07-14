from __future__ import annotations

import runpy
from pathlib import Path

import streamlit as st
import streamlit_lottie
import streamlit_extras.button_selector as button_selector_module

import fonctions.visuel as visuel
from fonctions.streamlit_compat import ensure_pygwalker_streamlit_compatibility
from fonctions.visuel import apply_plotly_theme, css, page_header, section_header


css()
ensure_pygwalker_streamlit_compatibility()


def _segmented_selector(options, key=None, **_kwargs) -> int:
    values = list(options)
    if not values:
        return 0
    selected = st.segmented_control(
        "Indicateur",
        values,
        default=values[0],
        key=key or "evolution_indicator",
        width="stretch",
        label_visibility="collapsed",
    )
    return values.index(selected) if selected in values else 0


def _run_legacy_page() -> None:
    legacy_path = Path(__file__).with_name("evolution.py")

    original_title = st.title
    original_subheader = st.subheader
    original_dataframe = st.dataframe
    original_plotly_chart = st.plotly_chart
    original_selector = button_selector_module.button_selector
    original_lottie_loader = visuel.load_lottieurl
    original_lottie = streamlit_lottie.st_lottie

    def subheader(label, *args, **kwargs):
        if str(label).strip().lower() == "evolution":
            return None
        return original_subheader(label, *args, **kwargs)

    def dataframe(data, *args, **kwargs):
        kwargs.pop("use_container_width", None)
        kwargs.setdefault("width", "stretch")
        return original_dataframe(data, *args, **kwargs)

    def plotly_chart(figure, *args, **kwargs):
        kwargs.pop("use_container_width", None)
        kwargs["width"] = "stretch"
        return original_plotly_chart(
            apply_plotly_theme(figure), *args, **kwargs
        )

    try:
        st.title = lambda *_args, **_kwargs: None
        st.subheader = subheader
        st.dataframe = dataframe
        st.plotly_chart = plotly_chart
        button_selector_module.button_selector = _segmented_selector
        visuel.load_lottieurl = lambda *_args, **_kwargs: None
        streamlit_lottie.st_lottie = lambda *_args, **_kwargs: None
        runpy.run_path(str(legacy_path), run_name="__evolution_legacy__")
    finally:
        st.title = original_title
        st.subheader = original_subheader
        st.dataframe = original_dataframe
        st.plotly_chart = original_plotly_chart
        button_selector_module.button_selector = original_selector
        visuel.load_lottieurl = original_lottie_loader
        streamlit_lottie.st_lottie = original_lottie


if st.session_state.get("submitted", False):
    page_header(
        "Évolution des scores",
        "Suivez la progression du compte dans le temps et comparez les différents paliers.",
        icon="📈",
        eyebrow="Historique",
    )
    section_header(
        "Tendances",
        "Choisissez les dates et l’indicateur à analyser ; les graphiques partagent désormais le même thème.",
    )

_run_legacy_page()