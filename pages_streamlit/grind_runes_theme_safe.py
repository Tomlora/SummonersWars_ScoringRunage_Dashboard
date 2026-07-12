from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

import pandas as pd



def _run_optimisation_page() -> None:
    """Run the themed optimisation page with categorical-safe fillna.

    Pandas categorical columns reject a replacement value that is not already
    registered as a category. The themed page uses display fallbacks such as
    an em dash, so categorical series are converted to object only for that
    specific non-inplace fill operation.
    """
    page_path = Path(__file__).with_name("grind_runes_theme.py")
    original_fillna = pd.Series.fillna

    def fillna(series: pd.Series, value: Any = None, *args, **kwargs):
        dtype_name = getattr(series.dtype, "name", "")
        inplace = bool(kwargs.get("inplace", False))
        is_mapping = isinstance(value, (dict, pd.Series, pd.DataFrame))

        if dtype_name == "category" and value is not None and not inplace and not is_mapping:
            categories = getattr(series.dtype, "categories", [])
            if value not in categories:
                series = series.astype("object")

        return original_fillna(series, value=value, *args, **kwargs)

    try:
        pd.Series.fillna = fillna
        runpy.run_path(str(page_path), run_name="__grind_runes_theme_safe__")
    finally:
        pd.Series.fillna = original_fillna


_run_optimisation_page()
