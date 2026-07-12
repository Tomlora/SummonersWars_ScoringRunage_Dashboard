from __future__ import annotations

import runpy
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit_lottie
import streamlit_extras.metric_cards as metric_cards

import fonctions.visuel as visuel
from fonctions.streamlit_compat import ensure_pygwalker_streamlit_compatibility
from fonctions.visuel import apply_plotly_theme, css, page_header, section_header


css()
ensure_pygwalker_streamlit_compatibility()


def _integer_score(key: str) -> int:
    try:
        return int(round(float(st.session_state.get(key, 0))))
    except (TypeError, ValueError):
        return 0


def _report_date() -> str:
    tcd = st.session_state.get("tcd")
    if isinstance(tcd, pd.DataFrame) and not tcd.empty and "date" in tcd.columns:
        return str(tcd.iloc[0]["date"])
    return "—"


def _artefact_efficiency() -> str:
    try:
        return f"{float(st.session_state.data_arte.data_a['efficiency'].mean()):.2f} %"
    except (AttributeError, KeyError, TypeError, ValueError):
        return "—"


def _rune_summary() -> pd.DataFrame | None:
    tcd = st.session_state.get("tcd")
    if not isinstance(tcd, pd.DataFrame) or tcd.empty:
        return None

    data = tcd.copy()
    if "set" not in data.columns:
        data.insert(0, "set", data.index)
    data.rename(columns={100: "100", 110: "110", 120: "120"}, inplace=True)
    data["img"] = data["set"].apply(
        lambda value: (
            "https://raw.githubusercontent.com/swarfarm/swarfarm/master/"
            f"herders/static/herders/images/runes/{str(value).lower()}.png"
        )
    )
    preferred_order = [
        "Autre", "Seal", "Despair", "Destroy", "Violent", "Will",
        "Intangible", "Total",
    ]
    return (
        data.set_index("set")
        .reindex(preferred_order)
        .reset_index()
        [["img", "set", "100", "110", "120"]]
        .dropna(how="all", subset=["100", "110", "120"])
    )


def _render_overview() -> None:
    page_header(
        str(st.session_state.get("pseudo", "Compte Summoners War")),
        f"Vue synthétique du compte · Guilde : {st.session_state.get('guilde', '—')}",
        icon="📚",
        eyebrow="Scoring général",
    )
    section_header(
        "Vue d’ensemble",
        "Les principaux indicateurs du dernier JSON analysé.",
    )
    rune, speed, artefact, quality, report = st.columns(5)
    rune.metric("Score Rune", f"{_integer_score('score')} pts")
    speed.metric("Score Speed", f"{_integer_score('score_spd')} pts")
    artefact.metric(
        "Score Artefact",
        f"{_integer_score('score_arte')} pts",
        help=f"Efficience moyenne : {_artefact_efficiency()}",
    )
    quality.metric("Score Qualité", f"{_integer_score('score_qual')} pts")
    report.metric("Dernière analyse", _report_date())

    rune_summary = _rune_summary()
    if rune_summary is not None:
        section_header(
            "Répartition des runes",
            "Nombre de runes par palier d’efficience et par set prioritaire.",
        )
        st.dataframe(
            rune_summary,
            width="stretch",
            hide_index=True,
            column_config={
                "img": st.column_config.ImageColumn("Rune", width="small"),
                "set": st.column_config.TextColumn("Set"),
            },
        )

    section_header(
        "Analyses détaillées",
        "Scores secondaires, détails par set et collection de monstres.",
    )


def _run_legacy_page() -> None:
    legacy_path = Path(__file__).with_name("general.py")

    original_subheader = st.subheader
    original_metric = st.metric
    original_dataframe = st.dataframe
    original_plotly_chart = st.plotly_chart
    original_lottie_loader = visuel.load_lottieurl
    original_lottie = streamlit_lottie.st_lottie
    original_metric_cards = metric_cards.style_metric_cards

    calls = {"subheader": 0, "metric": 0, "dataframe": 0}

    def subheader(label, *args, **kwargs):
        calls["subheader"] += 1
        if calls["subheader"] == 1:
            return None
        return original_subheader(label, *args, **kwargs)

    def metric(label, value, *args, **kwargs):
        calls["metric"] += 1
        if calls["metric"] <= 2:
            return None
        return original_metric(label, value, *args, **kwargs)

    def dataframe(data, *args, **kwargs):
        calls["dataframe"] += 1
        if calls["dataframe"] == 1:
            return None
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
        st.subheader = subheader
        st.metric = metric
        st.dataframe = dataframe
        st.plotly_chart = plotly_chart
        visuel.load_lottieurl = lambda *_args, **_kwargs: None
        streamlit_lottie.st_lottie = lambda *_args, **_kwargs: None
        metric_cards.style_metric_cards = lambda *_args, **_kwargs: None
        runpy.run_path(str(legacy_path), run_name="__general_legacy__")
    finally:
        st.subheader = original_subheader
        st.metric = original_metric
        st.dataframe = original_dataframe
        st.plotly_chart = original_plotly_chart
        visuel.load_lottieurl = original_lottie_loader
        streamlit_lottie.st_lottie = original_lottie
        metric_cards.style_metric_cards = original_metric_cards


if st.session_state.get("submitted", False):
    _render_overview()

_run_legacy_page()
