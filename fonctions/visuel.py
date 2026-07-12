from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Optional

import plotly.graph_objects as go
import plotly.io as pio
import requests
import streamlit as st


THEME = {
    "background": "#07111f",
    "surface": "#101f33",
    "grid": "rgba(191, 211, 236, 0.10)",
    "text": "#f4f7fb",
    "muted": "#9fb0c6",
    "primary": "#49a4ff",
    "secondary": "#8b7bff",
    "gold": "#e7b85c",
    "success": "#45ce91",
    "warning": "#f1b75d",
    "danger": "#ef6b78",
}


def _register_plotly_template() -> None:
    """Register the shared dark Plotly template once per process."""
    template_name = "summoners_war_dashboard"
    if template_name not in pio.templates:
        pio.templates[template_name] = go.layout.Template(
            layout=go.Layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"family": "Inter, Segoe UI, sans-serif", "color": THEME["text"]},
                colorway=[
                    THEME["primary"],
                    THEME["secondary"],
                    THEME["gold"],
                    THEME["success"],
                    THEME["warning"],
                    THEME["danger"],
                ],
                margin={"l": 24, "r": 24, "t": 58, "b": 34},
                hoverlabel={
                    "bgcolor": THEME["surface"],
                    "font": {"color": THEME["text"]},
                },
                legend={
                    "orientation": "h",
                    "yanchor": "bottom",
                    "y": 1.02,
                    "xanchor": "right",
                    "x": 1,
                },
                xaxis={
                    "gridcolor": THEME["grid"],
                    "linecolor": THEME["grid"],
                    "zeroline": False,
                    "title_font": {"color": THEME["muted"]},
                    "tickfont": {"color": THEME["muted"]},
                },
                yaxis={
                    "gridcolor": THEME["grid"],
                    "linecolor": THEME["grid"],
                    "zeroline": False,
                    "title_font": {"color": THEME["muted"]},
                    "tickfont": {"color": THEME["muted"]},
                },
            )
        )
    pio.templates.default = template_name


@st.cache_data(ttl="6h", show_spinner=False)
def load_lottieurl(url: str):
    """Load an optional Lottie animation without blocking the UI indefinitely."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return None
    return response.json()


@st.cache_resource
def css() -> None:
    """Load the shared CSS and configure a consistent Plotly theme."""
    _register_plotly_template()
    css_path = Path(__file__).resolve().parent.parent / "style.css"
    with css_path.open(encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


def apply_plotly_theme(
    fig: go.Figure,
    *,
    title: Optional[str] = None,
    height: Optional[int] = None,
    show_legend: bool = True,
) -> go.Figure:
    """Apply the dashboard layout to a Plotly figure created before ``css()``."""
    updates = {
        "template": "summoners_war_dashboard",
        "showlegend": show_legend,
        "hovermode": "closest",
    }
    if title is not None:
        updates["title"] = {"text": title, "x": 0.02, "xanchor": "left"}
    if height is not None:
        updates["height"] = height
    fig.update_layout(**updates)
    return fig


def page_header(
    title: str,
    subtitle: Optional[str] = None,
    *,
    icon: Optional[str] = None,
    eyebrow: Optional[str] = None,
) -> None:
    """Render a consistent page heading without coupling pages to custom components."""
    eyebrow_html = (
        f'<div class="sw-page-header__eyebrow">{escape(eyebrow)}</div>'
        if eyebrow
        else ""
    )
    subtitle_html = (
        f'<p class="sw-page-header__subtitle">{escape(subtitle)}</p>'
        if subtitle
        else ""
    )
    icon_html = (
        f'<div class="sw-page-header__icon">{escape(icon)}</div>' if icon else ""
    )
    st.markdown(
        f"""
        <div class="sw-page-header">
            <div>
                {eyebrow_html}
                <h1 class="sw-page-header__title">{escape(title)}</h1>
                {subtitle_html}
            </div>
            {icon_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: Optional[str] = None) -> None:
    subtitle_html = f"<p>{escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f'<div class="sw-section-header"><h2>{escape(title)}</h2>{subtitle_html}</div>',
        unsafe_allow_html=True,
    )


@st.cache_data
def icon(emoji: str) -> None:
    """Show an emoji as a page icon."""
    st.write(
        f'<span style="font-size: 50px; line-height: 1">{escape(emoji)}</span>',
        unsafe_allow_html=True,
    )


def load_logo() -> None:
    """Render the existing project logo with a constrained responsive size."""
    st.markdown(
        """
        <div style="display:flex;justify-content:center;margin:0.25rem 0 1rem;">
            <img src="https://i.imgur.com/AUwdzno.png" alt="Summoners War scoring dashboard"
                 style="max-width:100%;width:330px;height:auto;" />
        </div>
        """,
        unsafe_allow_html=True,
    )
