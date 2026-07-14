from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


SUBSTATS = ["HP", "HP%", "ATQ", "ATQ%", "DEF", "DEF%", "SPD", "CRIT", "DCC", "RES", "ACC"]
PERCENT_SUBSTATS = {"HP%", "ATQ%", "DEF%", "CRIT", "DCC", "RES", "ACC"}
SUBSTAT_POSITIONS = ("first", "second", "third", "fourth")

EXPORT_RENAME = {
    "rune_set": "Set rune",
    "rune_slot": "Slot",
    "rune_equiped": "Equipé",
    "efficiency": "Efficience",
    "efficiency_max_hero": "Efficience max héroïque",
    "efficiency_max_lgd": "Efficience max légendaire",
    "quality": "Qualité",
    "main_type": "Stat principale",
    "main_value": "Valeur stat principale",
    "first_sub": "Sous-stat 1",
    "second_sub": "Sous-stat 2",
    "third_sub": "Sous-stat 3",
    "fourth_sub": "Sous-stat 4",
    "first_sub_value": "Valeur de base 1",
    "second_sub_value": "Valeur de base 2",
    "third_sub_value": "Valeur de base 3",
    "fourth_sub_value": "Valeur de base 4",
    "first_gemme_bool": "Gemmée 1 ?",
    "second_gemme_bool": "Gemmée 2 ?",
    "third_gemme_bool": "Gemmée 3 ?",
    "fourth_gemme_bool": "Gemmée 4 ?",
    "first_sub_grinded_value": "Meule appliquée 1",
    "second_sub_grinded_value": "Meule appliquée 2",
    "third_sub_grinded_value": "Meule appliquée 3",
    "fourth_sub_grinded_value": "Meule appliquée 4",
    "first_sub_value_max": "Sous-stat 1 max",
    "second_sub_value_max": "Sous-stat 2 max",
    "third_sub_value_max": "Sous-stat 3 max",
    "fourth_sub_value_max": "Sous-stat 4 max",
    "first_sub_value_total": "Total actuel 1",
    "second_sub_value_total": "Total actuel 2",
    "third_sub_value_total": "Total actuel 3",
    "fourth_sub_value_total": "Total actuel 4",
    "first_grind_value_max_lgd": "Meule 1 légendaire max",
    "second_grind_value_max_lgd": "Meule 2 légendaire max",
    "third_grind_value_max_lgd": "Meule 3 légendaire max",
    "fourth_grind_value_max_lgd": "Meule 4 légendaire max",
    "first_grind_value_max_hero": "Meule 1 héroïque max",
    "second_grind_value_max_hero": "Meule 2 héroïque max",
    "third_grind_value_max_hero": "Meule 3 héroïque max",
    "fourth_grind_value_max_hero": "Meule 4 héroïque max",
}


def _substat_values(data_class: Any, stats: list[str]) -> pd.DataFrame:
    source = data_class.data_grind
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

    for stat in stats:
        total_column = f"{stat}__total"
        grind_column = f"{stat}__grind"
        if total_column in cache.columns and grind_column in cache.columns:
            continue
        base_values = pd.Series(0, index=source.index, dtype="int32")
        grind_values = pd.Series(0, index=source.index, dtype="int32")
        for position in SUBSTAT_POSITIONS:
            name_column = f"{position}_sub"
            base_column = f"{position}_sub_value"
            grind_source_column = f"{position}_sub_grinded_value"
            if name_column not in source.columns or base_column not in source.columns:
                continue
            mask = source[name_column].astype(str).eq(stat)
            if not mask.any():
                continue
            base = pd.to_numeric(source[base_column], errors="coerce").fillna(0)
            grind = (
                pd.to_numeric(source[grind_source_column], errors="coerce").fillna(0)
                if grind_source_column in source.columns
                else pd.Series(0, index=source.index)
            )
            base_values = base_values.add(base.where(mask, 0).astype("int32"), fill_value=0)
            grind_values = grind_values.add(grind.where(mask, 0).astype("int32"), fill_value=0)
        cache[grind_column] = grind_values.astype("int32")
        cache[total_column] = (base_values + grind_values).astype("int32")

    requested = [column for stat in stats for column in (f"{stat}__total", f"{stat}__grind")]
    return cache.loc[:, requested]


def _format_total_with_grind(total: Any, grind: Any, *, percent: bool) -> str:
    total_value = int(total or 0)
    grind_value = int(grind or 0)
    suffix = " %" if percent else ""
    if grind_value:
        return f"{total_value}{suffix} (+{grind_value}{suffix})"
    return f"{total_value}{suffix}"


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
    mean_gain = float(view["Gain potentiel"].mean()) if not view.empty else 0.0
    k3.metric(tr("Gain moyen", "Average gain"), f"+{mean_gain:.1f} pts")
    k4.metric(tr("Runes équipées", "Equipped runes"), int((view["Équipée sur"] != "Inventaire").sum()))

    selected_stats: list[str] = []
    minimums: dict[str, int] = {}
    display_mode = tr("Total", "Total")
    with st.expander(tr("Filtres et colonnes", "Filters and columns"), expanded=True):
        c1, c2, c3, c4 = st.columns([1.4, 1.2, 1.1, 1])
        sets = c1.multiselect(
            tr("Sets", "Sets"),
            sorted(value for value in view["Set"].dropna().unique() if value and value != "—"),
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
                "Les colonnes sont calculées une seule fois depuis les données détaillées, puis réutilisées.",
                "Columns are calculated once from detailed data, then reused.",
            ),
        ):
            display_mode = st.segmented_control(
                tr("Affichage des valeurs", "Value display"),
                [tr("Total", "Total"), tr("Total + meule", "Total + grind")],
                default=tr("Total", "Total"),
                key="optimisation_substat_display_mode",
                help=tr(
                    "Le second mode affiche par exemple 49 % (+7 %) : total 49, dont 7 apportés par la meule.",
                    "The second mode displays, for example, 49% (+7%): total 49, including 7 from the grind.",
                ),
            ) or tr("Total", "Total")
            selected_stats = st.multiselect(
                tr("Sous-statistiques affichées", "Displayed substats"),
                SUBSTATS,
                default=SUBSTATS,
                key="optimisation_displayed_substats",
            )
            filtered_stats = st.multiselect(
                tr("Sous-statistiques à filtrer", "Substats to filter"),
                selected_stats,
                key="optimisation_filtered_substats",
                help=tr(
                    "Les filtres utilisent toujours le total et se cumulent.",
                    "Filters always use the total and are combined.",
                ),
            )
            if filtered_stats:
                controls = st.columns(min(4, len(filtered_stats)))
                for position, stat in enumerate(filtered_stats):
                    with controls[position % len(controls)]:
                        minimums[stat] = int(
                            st.number_input(
                                f"{stat} minimum",
                                min_value=0,
                                value=0,
                                step=1,
                                key=f"optimisation_min_{stat}",
                            )
                        )

    if selected_stats:
        details = _substat_values(data_class, selected_stats)
        view = view.join(details, how="left")
        for stat in selected_stats:
            total_column = f"{stat}__total"
            grind_column = f"{stat}__grind"
            if display_mode == tr("Total + meule", "Total + grind"):
                view[stat] = [
                    _format_total_with_grind(total, grind, percent=stat in PERCENT_SUBSTATS)
                    for total, grind in zip(view[total_column], view[grind_column])
                ]
            else:
                view[stat] = view[total_column].astype("int32")
    else:
        speed = _substat_values(data_class, ["SPD"])
        view["SPD"] = speed["SPD__total"].reindex(view.index).fillna(0).astype("int32")

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
        filtered = filtered[filtered[f"{stat}__total"] >= minimum]

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
    if display_mode == tr("Total", "Total"):
        for stat in set(selected_stats or ["SPD"]):
            config[stat] = st.column_config.NumberColumn(
                stat,
                format="%d %%" if stat in PERCENT_SUBSTATS else "%d",
                width="small",
            )
    else:
        for stat in selected_stats:
            config[stat] = st.column_config.TextColumn(stat, width="small")
    st.dataframe(
        shown.loc[:, columns],
        width="stretch",
        height=620,
        hide_index=True,
        column_config=config,
    )
    csv = filtered.loc[:, [column for column in columns if column in filtered.columns]].to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        tr("Exporter les recommandations filtrées", "Export filtered recommendations"),
        csv,
        file_name=f"optimisation_runes_{st.session_state.get('pseudo', 'compte')}.csv",
        mime="text/csv",
        width="stretch",
        key="optimisation_export_filtered",
    )


def _wide_substats(data_class: Any, frame: pd.DataFrame) -> pd.DataFrame:
    details = _substat_values(data_class, SUBSTATS).reindex(frame.index)
    output = frame.copy()
    source = data_class.data_grind.reindex(frame.index)
    for stat in SUBSTATS:
        base_values = pd.Series(0, index=frame.index, dtype="int32")
        for position in SUBSTAT_POSITIONS:
            name_column = f"{position}_sub"
            value_column = f"{position}_sub_value"
            if name_column not in source.columns or value_column not in source.columns:
                continue
            mask = source[name_column].astype(str).eq(stat)
            values = pd.to_numeric(source[value_column], errors="coerce").fillna(0)
            base_values = base_values.add(values.where(mask, 0).astype("int32"), fill_value=0)
        output[f"{stat} base"] = base_values.astype("int32")
        output[f"{stat} meule"] = details[f"{stat}__grind"].fillna(0).astype("int32")
        output[f"{stat} total"] = details[f"{stat}__total"].fillna(0).astype("int32")
    return output


def _excel_safe(frame: pd.DataFrame, *, index_name: str | None = None) -> pd.DataFrame:
    output = frame.rename(columns=EXPORT_RENAME).copy()
    if index_name is not None:
        original_index_name = output.index.name or "index"
        output = output.reset_index().rename(columns={original_index_name: index_name})
    for column in output.select_dtypes(include="category").columns:
        output[column] = output[column].astype("object")
    for column in [name for name in output.columns if str(name).startswith("Gemmée")]:
        output[column] = output[column].map({0: "Non", 1: "Oui", False: "Non", True: "Oui"}).fillna(output[column])
    return output


def _worksheet_table(writer: pd.ExcelWriter, sheet_name: str, frame: pd.DataFrame) -> None:
    worksheet = writer.sheets[sheet_name]
    worksheet.freeze_panes(1, 1)
    sample = frame.head(100)
    for index, column in enumerate(frame.columns):
        values = sample[column].astype(str) if column in sample else pd.Series(dtype=str)
        width = min(38, max(12, len(str(column)) + 2, int(values.str.len().max() or 0) + 2))
        worksheet.set_column(index, index, width)
    if not frame.empty and len(frame.columns) > 0:
        worksheet.add_table(
            0,
            0,
            len(frame),
            len(frame.columns) - 1,
            {
                "columns": [{"header": str(column)} for column in frame.columns],
                "style": "Table Style Medium 2",
            },
        )


def _build_detailed_workbook(data_class: Any, inventory: pd.DataFrame) -> bytes:
    if not hasattr(data_class, "df_rune") or not hasattr(data_class, "df_count"):
        data_class.count_meules_manquantes()
        data_class.count_rune_with_potentiel_left()

    complete = _excel_safe(_wide_substats(data_class, data_class.data_grind), index_name="Id_rune")
    summary_source = data_class.data_short.copy()
    summary_details = _substat_values(data_class, SUBSTATS).reindex(summary_source.index)
    for stat in SUBSTATS:
        summary_source[f"{stat} meule"] = summary_details[f"{stat}__grind"]
        summary_source[f"{stat} total"] = summary_details[f"{stat}__total"]
    summary = _excel_safe(summary_source, index_name="Id_rune")
    by_set = _excel_safe(getattr(data_class, "df_rune", pd.DataFrame()), index_name="Set")
    by_property = _excel_safe(getattr(data_class, "df_count", pd.DataFrame()), index_name="Set")
    inventory_export = _excel_safe(inventory)
    guide = pd.DataFrame(
        {
            "Feuille": [
                "Par rune et monstre",
                "Data_complete",
                "Par set",
                "Par set et propriete",
                "Inventaire",
            ],
            "Contenu": [
                "Résumé par rune avec efficience, potentiel, recommandations et sous-statistiques totales.",
                "Toutes les colonnes techniques et tous les calculs, avec base, meule et total par sous-statistique.",
                "Agrégats des améliorations restantes par set.",
                "Agrégats détaillés par set et propriété.",
                "Gemmes et meules disponibles dans le JSON.",
            ],
        }
    )
    sheets = {
        "Guide": guide,
        "Par rune et monstre": summary,
        "Data_complete": complete,
        "Par set": by_set,
        "Par set et propriete": by_property,
        "Inventaire": inventory_export,
    }
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for sheet_name, frame in sheets.items():
            frame.to_excel(writer, sheet_name=sheet_name, index=False)
            _worksheet_table(writer, sheet_name, frame)
    return output.getvalue()


def _render_detailed_export(namespace: dict[str, Any], data_class: Any) -> None:
    tr = namespace["_tr"]
    namespace["section_header"](
        tr("Export détaillé", "Detailed export"),
        tr(
            "Retrouvez le classeur historique avec toutes les colonnes techniques, les calculs et les agrégats.",
            "Download the historical workbook with every technical column, calculation and aggregate.",
        ),
    )
    st.info(
        tr(
            "Le classeur est préparé uniquement lorsque vous le demandez. Cette opération peut prendre quelques secondes selon le nombre de runes.",
            "The workbook is prepared only when requested. This may take a few seconds depending on the rune count.",
        ),
        icon="📗",
    )
    source_id = id(data_class.data_grind)
    export_state = st.session_state.get("_optimisation_detailed_export")
    if not isinstance(export_state, dict) or export_state.get("source_id") != source_id:
        export_state = None
        st.session_state.pop("_optimisation_detailed_export", None)
    if st.button(
        tr("Préparer le classeur détaillé", "Prepare detailed workbook"),
        width="stretch",
        key="optimisation_prepare_detailed_export",
    ):
        with st.spinner(tr("Création du classeur Excel…", "Creating Excel workbook…")):
            inventory = st.session_state.get("_optimisation_inventory")
            if not isinstance(inventory, pd.DataFrame):
                inventory = namespace["_inventory_dataframe"](data_class)
            workbook = _build_detailed_workbook(data_class, inventory)
            export_state = {"source_id": source_id, "data": workbook}
            st.session_state["_optimisation_detailed_export"] = export_state
    if export_state:
        workbook = export_state["data"]
        size_mb = len(workbook) / (1024 * 1024)
        st.download_button(
            tr("Télécharger les données détaillées complètes", "Download complete detailed data"),
            workbook,
            file_name=f"optimisation_runes_detaillee_{st.session_state.get('pseudo', 'compte')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
            key="optimisation_download_detailed_export",
        )
        st.caption(
            tr(
                f"Classeur prêt · {size_mb:.1f} Mo · 6 feuilles",
                f"Workbook ready · {size_mb:.1f} MB · 6 sheets",
            )
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
        original_advanced = namespace["_render_advanced"]

        def render_advanced(data_class: Any) -> None:
            original_advanced(data_class)
            _render_detailed_export(namespace, data_class)

        namespace["_render_recommendations"] = lambda view: _recommendations(namespace, view)
        namespace["_render_advanced"] = render_advanced
        namespace["optimisation_page"]()
    finally:
        pd.Series.fillna = original_fillna


_run()
