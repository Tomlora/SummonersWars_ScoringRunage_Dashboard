from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st


ELEMENT_PALETTE: dict[str, tuple[str, str]] = {
    "EAU": ("#1F4F73", "#F4F7FB"),
    "FEU": ("#7A343B", "#F4F7FB"),
    "VENT": ("#7B572A", "#F4F7FB"),
    "LUMIERE": ("#CBD5DF", "#102033"),
    "TENEBRE": ("#4E3B68", "#F4F7FB"),
    "INTANGIBLE": ("#2F6958", "#F4F7FB"),
    "ATTACK": ("#365B7D", "#F4F7FB"),
    "DEFENSE": ("#76404B", "#F4F7FB"),
    "HP": ("#376957", "#F4F7FB"),
    "SUPPORT": ("#684A35", "#F4F7FB"),
}

MAIN_STAT_PALETTE: dict[str, tuple[str, str]] = {
    "ATK": ("#416B8F", "#F4F7FB"),
    "DEF": ("#87485B", "#F4F7FB"),
    "HP": ("#3E745F", "#F4F7FB"),
}


def _header_props(background: str, foreground: str) -> list[tuple[str, str]]:
    return [
        ("background-color", background),
        ("color", foreground),
        ("font-weight", "600"),
        ("text-align", "center"),
        ("border-color", "#29405D"),
    ]


def _header_styles(columns: pd.Index) -> list[dict[str, object]]:
    """Build muted, high-contrast styles for both artefact header levels."""
    styles: list[dict[str, object]] = [
        {
            "selector": "th",
            "props": [
                ("border-color", "#29405D"),
                ("padding", "0.45rem 0.55rem"),
            ],
        },
        {
            "selector": "th.row_heading",
            "props": [
                ("background-color", "#101D2F"),
                ("color", "#9CB6D7"),
                ("font-weight", "600"),
                ("border-color", "#29405D"),
            ],
        },
        {
            "selector": "td",
            "props": [
                ("background-color", "#0B1727"),
                ("color", "#DDE7F5"),
                ("border-color", "#20344F"),
            ],
        },
    ]

    for position, column in enumerate(columns):
        if not isinstance(column, tuple) or len(column) < 2:
            continue

        attribute, main_type = str(column[0]).upper(), str(column[1]).upper()
        attribute_colors = ELEMENT_PALETTE.get(attribute)
        main_type_colors = MAIN_STAT_PALETTE.get(main_type)

        if attribute_colors:
            background, foreground = attribute_colors
            styles.append(
                {
                    "selector": f"th.col_heading.level0.col{position}",
                    "props": _header_props(background, foreground),
                }
            )
        if main_type_colors:
            background, foreground = main_type_colors
            styles.append(
                {
                    "selector": f"th.col_heading.level1.col{position}",
                    "props": _header_props(background, foreground),
                }
            )

    return styles


def visualisation_top_arte(
    df: pd.DataFrame,
    column: str,
    use_container_width: bool = True,
    order: list[tuple[str, str]] | None = None,
):
    """Render a Best Artefact table with muted, readable coloured headers."""
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

    if column.capitalize() == "Dmg supp en fonction des hp":
        display = np.round(tcd.astype("float", errors="ignore"), 1).astype("str")
    else:
        display = tcd.astype("int", errors="ignore").astype("str")

    styled = (
        display.style
        .set_properties(**{"text-align": "center"})
        .set_table_styles(_header_styles(tcd.columns))
    )
    st.table(styled)
    return styled