from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from fonctions.artefact import dict_color, dict_color_lv1


def _header_styles(columns: pd.Index) -> list[dict[str, object]]:
    """Build stable Pandas Styler selectors for the two header levels.

    The previous implementation included a generated Streamlit Emotion class in
    every selector. Those class names change between Streamlit versions, which
    silently removed the element and main-stat colours after the 1.59 upgrade.
    Pandas' own ``col_heading`` classes are stable and scoped by the Styler table
    id, so they remain compatible with the dashboard theme.
    """
    styles: list[dict[str, object]] = []

    for position, column in enumerate(columns):
        if not isinstance(column, tuple) or len(column) < 2:
            continue

        attribute, main_type = column[0], column[1]
        attribute_style = dict_color.get(str(attribute).upper())
        main_type_style = dict_color_lv1.get(str(main_type).upper())

        if attribute_style:
            styles.append(
                {
                    "selector": f"th.col_heading.level0.col{position}",
                    "props": attribute_style,
                }
            )
        if main_type_style:
            styles.append(
                {
                    "selector": f"th.col_heading.level1.col{position}",
                    "props": main_type_style,
                }
            )

    return styles


def visualisation_top_arte(
    df: pd.DataFrame,
    column: str,
    use_container_width: bool = True,
    order: list[tuple[str, str]] | None = None,
):
    """Render a Best Artefact table with stable coloured headers."""
    del use_container_width  # kept for backward-compatible callers

    df_filter = df[df["substat"] == column]
    tcd = pd.pivot_table(
        values=["5", "4", "3", "2", "1"],
        columns=["arte_attribut", "main_type"],
        data=df_filter,
        aggfunc="max",
    )

    if tcd.empty:
        return None

    st.write(f"Top 5 {column.capitalize()}")

    if order is not None:
        existing_columns = [candidate for candidate in order if candidate in tcd.columns]
        tcd = tcd.loc[:, existing_columns]

    styles = _header_styles(tcd.columns)
    centered = {"text-align": "center"}

    if column.capitalize() == "Dmg supp en fonction des hp":
        display = np.round(tcd.astype("float", errors="ignore"), 1).astype("str")
    else:
        display = tcd.astype("int", errors="ignore").astype("str")

    styled = display.style.set_properties(**centered).set_table_styles(styles)
    st.table(styled)
    return styled
