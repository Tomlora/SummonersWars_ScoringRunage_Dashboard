from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


SUBSTATS = ["HP", "HP%", "ATQ", "ATQ%", "DEF", "DEF%", "SPD", "CRIT", "DCC", "RES", "ACC"]


def _substats(namespace: dict[str, Any], data_class: Any, stats: list[str]) -> pd.DataFrame:
    source = data_class.data_short
    source_id = id(source)
    cache = getattr(data_class, "_optimisation_substat_cache", None)
    if (
        getattr(data_class, "_optimisation_substat_source_id", None) != source_id
        or not isinstance(cache, pd.DataFrame)
        or not cache.index.equals(source.index)
    ):
        cache = pd.DataFrame(index=source.index)
        data_class._optimisation_substat_cache = cache
        data_class._optimisation_substat_source_id = source_id

    extract_stat = namespace["_extract_stat"]
    for stat in stats:
        if stat not in cache.columns:
            cache[stat] = extract_stat(source, data_class, stat).round().astype("int32")
    return cache.loc[:, stats]


def _recommendations(namespace: dict[str, Any], view: pd.DataFrame) -> None:
    tr = namespace["_tr"]
    namespace["section_header"](
        tr("À améliorer", "Upgrade recommendations"),
        tr(
            "Filtrez les runes selon leur potentiel, l’action recommandée et leurs sous-statistiques.",
            "Filter runes by potential, recommended action and substats.",
        ),
    )
    data_class = st.session_state.data_rune
    high = tr("🔴 Haute", "🔴 High")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(tr("Runes analysées", "Runes analysed"), f"{len(view):,}".replace(",", " "))
    k2.metric(tr("Priorité haute", "High priority"), int((view["Priorité"] == high).sum()))
    k3.metric(tr("Gain moyen", "Average gain"), f"+{float(view['Gain potentiel'].mean()) if not view.empty else 0:.1f} pts")
    k4.metric(tr("Runes équipées", "Equipped runes"), int((view["Équipée sur"] != "Inventaire").sum()))

    selected_stats: list[str] = []
    minimums: dict[str, int] = {}
    with st.expander(tr("Filtres et colonnes", "Filters and columns"), expanded=True):
        c1, c2, c3, c4 = st.columns([1.4, 1.2, 1.1, 1])
        sets = c1.multiselect(
            tr("Sets", "Sets"),
            sorted(v for v in view["Set"].dropna().unique() if v and v != "—"),
            placeholder=tr("Tous les sets", "All sets"),
            key="optimisation_filter_sets",
        )
        actions = c2.multiselect(
            tr("Actions", "Actions"),
            sorted(view["Action"].dropna().unique()),
            placeholder=tr("Toutes les actions", "All actions"),
            key="optimisation_filter_actions",
        )
        priority = c3.selectbox(
            tr("Priorité", "Priority"),
            [tr("Toutes", "All"), high, tr("🟠 Moyenne", "🟠 Medium"), tr("🟡 Faible", "🟡 Low")],
            key="optimisation_filter_priority",
        )
        equipped = c4.toggle(
            tr("Équipées uniquement", "Equipped only"),
            value=False,
            key="optimisation_filter_equipped",
        )

        max_gain = max(float(view["Gain potentiel"].max()), 1.0) if not view.empty else 1.0
        min_gain = st.slider(
            tr("Gain potentiel minimum", "Minimum potential gain"),
            0.0,
            float(round(max_gain, 1)),
            0.0,
            0.5,
            key="optimisation_filter_gain",
        )

        if st.toggle(
            tr("Afficher les sous-statistiques", "Show substats"),
            value=False,
            key="optimisation_show_substats",
            help=tr(
                "Les colonnes sont calculées une seule fois, puis réutilisées.",
                "Columns are calculated once, then reused.",
            ),
        ):
            selected_stats = st.multiselect(
                tr("Sous-statistiques affichées", "Displayed substats"),
                SUBSTATS,
                default=SUBSTATS,
                key="optimisation_displayed_substats",
                help=tr(
                    "Valeurs totales, meules déjà appliquées incluses.",
                    "Total values, including existing grinds.",
                ),
            )
            filtered_stats = st.multiselect(
                tr("Sous-statistiques à filtrer", "Substats to filter"),
                selected_stats,
                key="optimisation_filtered_substats",
                help=tr(
                    "Les minimums sont cumulés : la rune doit tous les respecter.",
                    "Minimums are combined: the rune must meet all of them.",
                ),
            )
            if filtered_stats:
                controls = st.columns(min(4, len(filtered_stats)))
                for pos, stat in enumerate(filtered_stats):
                    with controls[pos % len(controls)]:
                        minimums[stat] = int(
                            st.number_input(
                                f"{stat} minimum",
                                min_value=0,
                                value=0,
                                step=1,
                                key=f"optimisation_min_{stat}",
                            )
                        )

    missing_stats = [stat for stat in selected_stats if stat not in view.columns]
    if missing_stats:
        view = view.join(_substats(namespace, data_class, missing_stats), how="left")

    filtered = view
    if sets:
        filtered = filtered[filtered["Set"].isin(sets)]
    if actions:
        filtered = filtered[filtered["Action"].isin(actions)]
    if priority != tr("Toutes", "All"):
        filtered = filtered[filtered["Priorité"] == priority]
    if equipped:
        filtered = filtered[filtered["Équipée sur"] != "Inventaire"]
    filtered = filtered[filtered["Gain potentiel"] >= min_gain]
    for stat, minimum in minimums.items():
        filtered = filtered[filtered[stat] >= minimum]

    limit = st.select_slider(
        tr("Nombre de lignes", "Rows displayed"),
        options=[50, 100, 200, 400],
        value=200,
        key="optimisation_display_limit",
    )
    shown = filtered.head(limit)
    st.caption(
        tr(
            f"{len(filtered)} recommandation(s) · {len(shown)} affichée(s)",
            f"{len(filtered)} recommendation(s) · {len(shown)} displayed",
        )
    )

    columns = ["Priorité", "Set", "Slot", "Équipée sur", "Action", "Efficience", "Potentiel", "Gain potentiel"]
    columns.extend(selected_stats or ["SPD"])
    columns.append("Recommandation")

    config: dict[str, Any] = {
        "Slot": st.column_config.NumberColumn("Slot", format="%d", width="small"),
        "Efficience": st.column_config.NumberColumn(tr("Efficience", "Efficiency"), format="%.2f"),
        "Potentiel": st.column_config.NumberColumn(tr("Potentiel", "Potential"), format="%.2f"),
        "Gain potentiel": st.column_config.ProgressColumn(
            tr("Gain potentiel", "Potential gain"),
            format="+%.2f",
            min_value=0,
            max_value=max(max_gain, 1.0),
        ),
    }
    for stat in set(selected_stats or ["SPD"]):
        config[stat] = st.column_config.NumberColumn(stat, format="%d", width="small")

    st.dataframe(
        shown.loc[:, columns],
        width="stretch",
        height=620,
        hide_index=True,
        column_config=config,
    )

    csv = filtered.loc[:, [c for c in columns if c in filtered.columns]].to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        tr("Exporter les recommandations filtrées", "Export filtered recommendations"),
        csv,
        file_name=f"optimisation_runes_{st.session_state.get('pseudo', 'compte')}.csv",
        mime="text/csv",
        width="stretch",
        key="optimisation_export_filtered",
    )


def _run() -> None:
    page_path = Path(__file__).with_name("grind_runes_theme.py")
    original_fillna = pd.Series.fillna

    def categorical_safe_fillna(series: pd.Series, value: Any = None, *args, **kwargs):
        is_mapping = isinstance(value, (dict, pd.Series, pd.DataFrame))
        if (
            getattr(series.dtype, "name", "") == "category"
            and value is not None
            and not kwargs.get("inplace", False)
            and not is_mapping
            and value not in getattr(series.dtype, "categories", [])
        ):
            series = series.astype("object")
        return original_fillna(series, value=value, *args, **kwargs)

    try:
        pd.Series.fillna = categorical_safe_fillna
        source = page_path.read_text(encoding="utf-8")
        source, separator, _ = source.rpartition("\noptimisation_page()")
        if not separator:
            raise RuntimeError("Impossible de charger la page d'optimisation.")

        namespace: dict[str, Any] = {
            "__file__": str(page_path),
            "__name__": "__grind_runes_theme_safe__",
        }
        exec(compile(source, str(page_path), "exec"), namespace)
        namespace["_render_recommendations"] = lambda view: _recommendations(namespace, view)
        namespace["optimisation_page"]()
    finally:
        pd.Series.fillna = original_fillna


_run()
