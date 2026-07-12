from __future__ import annotations

import runpy
from pathlib import Path

import streamlit as st



def _run_ladder_page() -> None:
    """Render the leaderboard HTML directly instead of through Markdown."""
    ladder_path = Path(__file__).with_name("ladder.py")
    original_markdown = st.markdown

    def markdown(body, *args, **kwargs):
        is_leaderboard = (
            kwargs.get("unsafe_allow_html", False)
            and isinstance(body, str)
            and "sw-leaderboard-wrap" in body
        )
        if not is_leaderboard:
            return original_markdown(body, *args, **kwargs)

        # st.markdown interprets the indentation of generated table rows as a
        # code block. st.html bypasses Markdown parsing entirely. The fallback
        # also strips line indentation for older Streamlit versions.
        html_body = "".join(line.strip() for line in body.splitlines())
        if hasattr(st, "html"):
            return st.html(html_body)
        return original_markdown(html_body, unsafe_allow_html=True)

    try:
        st.markdown = markdown
        runpy.run_path(str(ladder_path), run_name="__ladder_page__")
    finally:
        st.markdown = original_markdown


_run_ladder_page()
