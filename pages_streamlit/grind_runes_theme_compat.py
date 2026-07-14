from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

import fonctions.visualisation as visualisation_module


class _StreamlitExplorerFallback:
    """Lightweight explorer used when PyGWalker cannot attach to Streamlit."""

    def __init__(self, frame: pd.DataFrame, error: Exception):
        self.frame = frame
        self.error = error

    def explorer(self) -> None:
        st.warning(
            "PyGWalker n'est pas compatible avec cette version de Streamlit. "
            "Un explorateur léger est affiché à la place.",
            icon="⚠️",
        )
        st.caption(f"Erreur PyGWalker interceptée : {type(self.error).__name__}")

        labels: list[str] = []
        positions: dict[str, int] = {}
        occurrences: dict[str, int] = {}
        for position, column in enumerate(self.frame.columns):
            base_label = str(column)
            occurrences[base_label] = occurrences.get(base_label, 0) + 1
            occurrence = occurrences[base_label]
            label = base_label if occurrence == 1 else f"{base_label} ({occurrence})"
            labels.append(label)
            positions[label] = position

        default_columns = labels[: min(12, len(labels))]
        selected_labels = st.multiselect(
            "Colonnes à explorer",
            labels,
            default=default_columns,
            key="optimisation_fallback_explorer_columns",
        )
        row_limit = st.select_slider(
            "Nombre maximal de lignes",
            options=[100, 250, 500, 1000, 2000],
            value=500,
            key="optimisation_fallback_explorer_rows",
        )

        selected_positions = [positions[label] for label in selected_labels]
        if not selected_positions:
            st.info("Sélectionnez au moins une colonne.")
            return

        preview = self.frame.iloc[:row_limit, selected_positions]
        st.dataframe(preview, width="stretch", height=620)
        if len(self.frame) > row_limit:
            st.caption(
                f"Aperçu limité à {row_limit} lignes sur {len(self.frame)} afin de préserver les performances."
            )


def _safe_pygwalker_loader(original_loader):
    """Return PyGWalker when possible, otherwise a non-crashing explorer."""

    def load(frame: pd.DataFrame, config: str = ""):
        try:
            return original_loader(frame, config)
        except Exception as error:
            return _StreamlitExplorerFallback(frame, error)

    return load


def _unique_headers(columns: pd.Index) -> list[str]:
    """Return unique Excel table headers while preserving their display order."""
    counts: dict[str, int] = {}
    headers: list[str] = []
    for column in columns:
        label = str(column)
        counts[label] = counts.get(label, 0) + 1
        occurrence = counts[label]
        headers.append(label if occurrence == 1 else f"{label} ({occurrence})")
    return headers


def _worksheet_table(writer: pd.ExcelWriter, sheet_name: str, frame: pd.DataFrame) -> None:
    """Format an Excel sheet safely, including DataFrames with duplicate columns."""
    worksheet = writer.sheets[sheet_name]
    worksheet.freeze_panes(1, 1)
    sample = frame.head(100)

    for position, column in enumerate(frame.columns):
        # Selecting by position guarantees a Series even when column names repeat.
        values = sample.iloc[:, position].astype(str)
        maximum_length = values.str.len().max()
        if pd.isna(maximum_length):
            maximum_length = 0
        width = min(
            38,
            max(12, len(str(column)) + 2, int(maximum_length) + 2),
        )
        worksheet.set_column(position, position, width)

    if not frame.empty and len(frame.columns) > 0:
        worksheet.add_table(
            0,
            0,
            len(frame),
            len(frame.columns) - 1,
            {
                "columns": [
                    {"header": header}
                    for header in _unique_headers(frame.columns)
                ],
                "style": "Table Style Medium 2",
            },
        )


def _run_optimisation_page() -> None:
    page_path = Path(__file__).with_name("grind_runes_theme_safe.py")
    source = page_path.read_text(encoding="utf-8")
    source, separator, _ = source.rpartition("\n_run()")
    if not separator:
        raise RuntimeError("Impossible de charger l'adaptateur Optimisation.")

    namespace: dict[str, Any] = {
        "__file__": str(page_path),
        "__name__": "__grind_runes_theme_compat__",
    }
    exec(compile(source, str(page_path), "exec"), namespace)

    # Replace only the two failing integration points. All calculations and
    # page behaviour remain implemented by grind_runes_theme_safe.py.
    namespace["_worksheet_table"] = _worksheet_table

    original_loader = visualisation_module.load_pygwalker
    visualisation_module.load_pygwalker = _safe_pygwalker_loader(original_loader)
    try:
        namespace["_run"]()
    finally:
        visualisation_module.load_pygwalker = original_loader


_run_optimisation_page()
