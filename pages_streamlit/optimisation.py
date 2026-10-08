from __future__ import annotations

from typing import Any, Iterable
from io import BytesIO

import pandas as pd
import streamlit as st

from fonctions.runes import CRAFT_TYPE_MAP, COM2US_QUALITY_MAP
from fonctions.visuel import css, page_header, section_header


css()


def _tr(fr: str, en: str) -> str:
    return en if st.session_state.get("translations_selected") == "English" else fr


def _first_column(df: pd.DataFrame, names: Iterable[str]) -> str | None:
    return next((name for name in names if name in df.columns), None)


def _series(
    df: pd.DataFrame,
    names: Iterable[str],
    *,
    default: Any = "",
    numeric: bool = False,
) -> pd.Series:
    column = _first_column(df, names)
    if column is None:
        values = pd.Series(default, index=df.index)
    else:
        values = df[column]
    if numeric:
        return pd.to_numeric(values, errors="coerce").fillna(0)
    return values.astype(object).fillna(default)


def _truthy(value: Any) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return str(value).strip().lower() not in {"", "0", "false", "non", "none", "nan", "aucun"}


def _extract_stat(df: pd.DataFrame, data_class: Any, stat_name: str) -> pd.Series:
    direct = _first_column(df, [stat_name])
    if direct is not None:
        return pd.to_numeric(df[direct], errors="coerce").fillna(0)

    result = pd.Series(0.0, index=df.index)
    property_map = getattr(data_class, "property", {})
    pairs = [
        (("first_sub", "Substat 1"), ("first_sub_value_total", "Substat total 1", "first_sub_value")),
        (("second_sub", "Substat 2"), ("second_sub_value_total", "Substat total 2", "second_sub_value")),
        (("third_sub", "Substat 3"), ("third_sub_value_total", "Substat total 3", "third_sub_value")),
        (("fourth_sub", "Substat 4"), ("fourth_sub_value_total", "Substat total 4", "fourth_sub_value")),
    ]
    for name_candidates, value_candidates in pairs:
        name_column = _first_column(df, name_candidates)
        value_column = _first_column(df, value_candidates)
        if name_column is None or value_column is None:
            continue
        names = df[name_column]
        if property_map:
            names = names.map(lambda value: property_map.get(value, value))
        mask = names.astype(str).str.upper().eq(stat_name.upper())
        values = pd.to_numeric(df[value_column], errors="coerce").fillna(0)
        result = result.where(~mask, values)
    return result


def _inventory_dataframe(data_class: Any) -> pd.DataFrame:
    items = st.session_state.get("data_json", {}).get("rune_craft_item_list", [])
    rows: list[dict[str, Any]] = []
    for item in items:
        code = str(item.get("craft_type_id", ""))
        if len(code) < 5 or not code.isdigit():
            continue
        try:
            set_code = int(code[:-4])
            stat_code = int(code[-4:-2])
            quality_code = int(code[-2:])
            craft_type = int(item.get("craft_type", 0))
        except (TypeError, ValueError):
            continue
        rows.append(
            {
                "Type": CRAFT_TYPE_MAP.get(craft_type, str(craft_type)),
                "Set": getattr(data_class, "set", {}).get(set_code, str(set_code)),
                "Stat": getattr(data_class, "property", {}).get(stat_code, str(stat_code)),
                "Qualité": COM2US_QUALITY_MAP.get(quality_code, str(quality_code)),
                "Quantité": int(item.get("amount", 0) or 0),
            }
        )
    return pd.DataFrame(rows, columns=["Type", "Set", "Stat", "Qualité", "Quantité"])


def _analysis_ready(data_class: Any) -> bool:
    return (
        st.session_state.get("_optimisation_source_id") == id(data_class)
        and hasattr(data_class, "data_short")
        and isinstance(data_class.data_short, pd.DataFrame)
    )


def _run_analysis(data_class: Any) -> None:
    with st.status(
        _tr("Analyse des possibilités d'amélioration…", "Analysing upgrade opportunities…"),
        expanded=True,
    ) as status:
        status.write(_tr("Calcul du potentiel des runes", "Calculating rune potential"))
        data_class.calcul_potentiel()
        status.write(_tr("Identification des gemmes et meules utiles", "Finding useful gems and grinds"))
        data_class.grind()
        st.session_state["_optimisation_inventory"] = _inventory_dataframe(data_class)
        st.session_state["_optimisation_source_id"] = id(data_class)
        st.session_state.pop("_optimisation_advanced_ready", None)
        st.session_state.pop("_optimisation_open_explorer", None)
        status.update(
            label=_tr("Analyse terminée", "Analysis complete"),
            state="complete",
            expanded=False,
        )


def _recommendation_dataframe(data_class: Any) -> pd.DataFrame:
    source = data_class.data_short
    view = pd.DataFrame(index=source.index)
    view["Id rune"] = source.index
    view["Set"] = _series(source, ["rune_set", "Set rune", "Set"], default="—").astype(str)
    view["Slot"] = _series(source, ["rune_slot", "Slot"], default=0, numeric=True).astype(int)
    view["Équipée sur"] = _series(source, ["rune_equiped", "Equipé", "Équipée sur"], default="Inventaire")
    view["Équipée sur"] = view["Équipée sur"].replace({0: "Inventaire", "0": "Inventaire", "Inventory": "Inventaire"}).astype(str)
    view["is_equipped"] = view["Équipée sur"].ne("Inventaire")
    view["Efficience"] = _series(source, ["efficiency", "Efficience"], numeric=True).round(2)
    view["Potentiel"] = _series(
        source,
        ["efficiency_max_lgd", "Efficience_max_lgd", "efficiency_max_hero", "Efficience_max_hero"],
        numeric=True,
    ).round(2)
    view["Gain potentiel"] = (view["Potentiel"] - view["Efficience"]).clip(lower=0).round(2)
    view["SPD"] = _extract_stat(source, data_class, "SPD").round().astype(int)

    comments = _series(source, ["Commentaires", "comments", "commentaires"], default="").astype(str)
    grind_lgd = _series(source, ["Grind_lgd", "grind_lgd"], default="")
    grind_hero = _series(source, ["Grind_hero", "grind_hero"], default="")

    actions: list[str] = []
    recommendations: list[str] = []
    for comment, legendary, hero in zip(comments, grind_lgd, grind_hero):
        lowered = comment.lower()
        if "reapp" in lowered:
            action = 'reappraisal'
        elif "gem" in lowered or "gemm" in lowered:
            action = 'gem'
        elif _truthy(legendary):
            action = 'legendary_grind'
        elif _truthy(hero):
            action = 'hero_grind'
        else:
            action = 'review'
        actions.append(action)
        clean_comment = " · ".join(part.strip() for part in comment.splitlines() if part.strip())
        recommendations.append(clean_comment or action_label(action))

    view["Action"] = actions
    view["Recommandation"] = recommendations
    view["Priorité"] = pd.cut(
        view["Gain potentiel"],
        bins=[-float("inf"), 5, 10, float("inf")], right=False,
        labels=['low','medium','high'],
    ).astype(str)
    from fonctions.improvements import grind_opportunities
    opportunities = getattr(data_class, '_stock_opportunities', None)
    if opportunities is None:
        opportunities = grind_opportunities(data_class, data_class.data_json.get('rune_craft_item_list', []))
        data_class._stock_opportunities = opportunities
    view = view.join(opportunities)
    return view.sort_values(["Gain potentiel", "SPD"], ascending=[False, False])





def _render_inventory(inventory: pd.DataFrame) -> None:
    section_header(
        _tr("Inventaire de gemmes et meules", "Gem and grind inventory"),
        _tr(
            "Vue agrégée des ressources réellement disponibles dans le JSON.",
            "Aggregated view of the resources available in the JSON.",
        ),
    )
    if inventory.empty:
        st.info(_tr("Aucune gemme ou meule trouvée.", "No gems or grinds found."))
        return

    grouped = (
        inventory.groupby(["Type", "Set", "Stat", "Qualité"], observed=True, as_index=False)["Quantité"]
        .sum()
        .sort_values("Quantité", ascending=False)
    )
    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric(_tr("Objets", "Items"), int(grouped["Quantité"].sum()))
    metric2.metric(_tr("Combinaisons", "Combinations"), len(grouped))
    metric3.metric(_tr("Sets couverts", "Sets covered"), grouped["Set"].nunique())
    metric4.metric(_tr("Stats couvertes", "Stats covered"), grouped["Stat"].nunique())

    col1, col2, col3 = st.columns(3)
    selected_types = col1.multiselect(_tr("Type", "Type"), sorted(grouped["Type"].unique()))
    selected_sets = col2.multiselect(_tr("Set", "Set"), sorted(grouped["Set"].unique()))
    selected_quality = col3.multiselect(_tr("Qualité", "Quality"), sorted(grouped["Qualité"].unique()))

    filtered = grouped
    if selected_types:
        filtered = filtered[filtered["Type"].isin(selected_types)]
    if selected_sets:
        filtered = filtered[filtered["Set"].isin(selected_sets)]
    if selected_quality:
        filtered = filtered[filtered["Qualité"].isin(selected_quality)]

    st.dataframe(
        filtered,
        width="stretch",
        hide_index=True,
        height=580,
        column_config={
            "Quantité": st.column_config.ProgressColumn(
                _tr("Quantité", "Quantity"),
                format="%d",
                min_value=0,
                max_value=max(int(filtered["Quantité"].max()) if not filtered.empty else 1, 1),
            )
        },
    )


def _render_advanced(data_class: Any) -> None:
    section_header(
        _tr("Analyse avancée", "Advanced analysis"),
        _tr(
            "Les outils lourds ne sont chargés que lorsque vous les demandez.",
            "Heavy tools are loaded only when requested.",
        ),
    )
    st.info(
        _tr(
            "Cette zone peut consommer davantage de mémoire. Les tableaux sont limités à 500 lignes par défaut.",
            "This area can use more memory. Tables are limited to 500 rows by default.",
        ),
        icon="ℹ️",
    )

    if st.button(_tr("Calculer les agrégats détaillés", "Calculate detailed aggregates"), width="stretch"):
        with st.spinner(_tr("Calcul des agrégats…", "Calculating aggregates…")):
            data_class.count_meules_manquantes()
            data_class.count_rune_with_potentiel_left()
            st.session_state["_optimisation_advanced_ready"] = id(data_class)

    if st.session_state.get("_optimisation_advanced_ready") == id(data_class):
        tab1, tab2 = st.tabs([_tr("Par set", "By set"), _tr("Par propriété", "By property")])
        with tab1:
            if hasattr(data_class, "df_rune"):
                st.dataframe(data_class.df_rune.head(500), width="stretch", height=480)
        with tab2:
            if hasattr(data_class, "df_count"):
                st.dataframe(data_class.df_count.head(500), width="stretch", height=480)

    show_raw = st.toggle(_tr("Afficher un extrait des données techniques", "Show a technical data sample"), value=False)
    if show_raw:
        raw = getattr(data_class, "data_grind", data_class.data_short)
        st.dataframe(raw.head(500), width="stretch", height=520)
        if len(raw) > 500:
            st.caption(_tr("Aperçu limité aux 500 premières lignes.", "Preview limited to the first 500 rows."))

    if st.button(_tr("Ouvrir l'explorateur interactif", "Open interactive explorer"), width="stretch"):
        st.session_state["_optimisation_open_explorer"] = True

    if st.session_state.get("_optimisation_open_explorer"):
        from fonctions.visualisation import load_pygwalker

        raw = getattr(data_class, "data_grind", data_class.data_short)
        renderer = load_pygwalker(raw)
        renderer.explorer()


def optimisation_page() -> None:
    page_header(
        _tr("Optimisation des runes", "Rune optimisation"),
        _tr(
            "Identifiez les améliorations utiles sans recalculer toute la page à chaque interaction.",
            "Find useful upgrades without recalculating the whole page on every interaction.",
        ),
        icon="🔍",
        eyebrow=_tr("Runages", "Runes"),
    )

    if not st.session_state.get("submitted", False):
        st.switch_page("pages_streamlit/upload.py")
        return

    data_class = st.session_state.data_rune
    ready = _analysis_ready(data_class)

    action1, action2 = st.columns([4, 1])
    with action1:
        st.info(
            _tr(
                "L'analyse est lancée uniquement sur demande puis réutilisée pendant toute la session.",
                "Analysis runs only on request and is then reused throughout the session.",
            ),
            icon="⚙️",
        )
    with action2:
        button_label = _tr("Recalculer", "Recalculate") if ready else _tr("Lancer l'analyse", "Run analysis")
        if st.button(button_label, type="primary", width="stretch"):
            _run_analysis(data_class)
            st.rerun()

    if not ready:
        st.empty()
        st.caption(
            _tr(
                "Aucun calcul lourd n'est effectué tant que vous ne lancez pas l'analyse.",
                "No heavy calculation is performed until you start the analysis.",
            )
        )
        return

    view = _recommendation_dataframe(data_class)
    inventory = st.session_state.get("_optimisation_inventory")
    if not isinstance(inventory, pd.DataFrame):
        inventory = _inventory_dataframe(data_class)
        st.session_state["_optimisation_inventory"] = inventory

    selected_view = st.segmented_control(
        _tr("Vue", "View"),
        [
            _tr("À améliorer", "Recommendations"),
            _tr("Inventaire", "Inventory"),
            _tr("Analyse avancée", "Advanced analysis"),
        ],
        default=_tr("À améliorer", "Recommendations"),
        width="stretch",
        label_visibility="collapsed",
    )

    if selected_view == _tr("Inventaire", "Inventory"):
        _render_inventory(inventory)
    elif selected_view == _tr("Analyse avancée", "Advanced analysis"):
        _render_advanced(data_class)
        _render_detailed_export(data_class)
    else:
        _render_recommendations(view)

    st.caption("Made by Tomlora 😎")


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


def _render_recommendations(view: pd.DataFrame) -> None:
    from fonctions.workspace import active_locks
    view=view.loc[~view.index.isin(active_locks())].copy()
    tr = _tr
    section_header(
        tr("À améliorer", "Upgrade recommendations"),
        tr(
            "Filtrez les runes selon leur potentiel, l’action recommandée et leurs sous-statistiques.",
            "Filter runes by potential, recommended action and substats.",
        ),
    )
    data_class = st.session_state.data_rune
    high = 'high'

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(tr("Runes analysées", "Runes analysed"), f"{len(view):,}".replace(",", " "))
    k2.metric(tr("Priorité haute", "High priority"), int((view["Priorité"] == high).sum()))
    mean_gain = float(view["Gain potentiel"].mean()) if not view.empty else 0.0
    k3.metric(tr("Gain moyen", "Average gain"), f"+{mean_gain:.1f} pts")
    k4.metric(tr("Runes équipées", "Equipped runes"), int(view["is_equipped"].sum()))

    st.caption(tr("Priorité : faible <5, moyenne <10, haute ≥10 points de gain théorique. Le gain avec stock est un maximum pour les meules seules, évalué rune par rune ; les ressources sont partagées et les tirages restent aléatoires.", "Priority: low <5, medium <10, high ≥10 theoretical gain points. Inventory gain is a maximum for grinds only, evaluated one rune at a time; resources are shared and rolls remain random."))
    preset_tools()
    selected_stats: list[str] = []
    minimums: dict[str, int] = {}
    display_mode = tr("Total", "Total")
    with st.expander(tr("Filtres et colonnes", "Filters and columns"), expanded=True):
        available_sets=set(view['Set'].dropna())
        for key, options in [('optimisation_filter_sets',available_sets),('optimisation_displayed_substats',set(SUBSTATS))]:
            if key in st.session_state:
                st.session_state[key]=[v for v in st.session_state[key] if v in options]
        c1, c2, c3, c4 = st.columns([1.4, 1.2, 1.1, 1])
        sets = c1.multiselect(
            tr("Sets", "Sets"),
            sorted(value for value in view["Set"].dropna().unique() if value and value != "—"),
            placeholder=tr("Tous les sets", "All sets"),
            key="optimisation_filter_sets",
        )
        actions = c2.multiselect(
            tr("Actions", "Actions"),
            ['reappraisal','gem','legendary_grind','hero_grind','review'],
            format_func={code:action_label(code) for code in ['reappraisal','gem','legendary_grind','hero_grind','review']}.get,
            placeholder=tr("Toutes les actions", "All actions"),
            key="optimisation_filter_actions",
        )
        priority = c3.selectbox(
            tr("Priorité", "Priority"),
            ['all', 'high', 'medium', 'low'],
            format_func={code:priority_label(code) for code in ['all','high','medium','low']}.get,
            key="optimisation_filter_priority",
        )
        equipped = c4.toggle(
            tr("Équipées uniquement", "Equipped only"),
            value=False,
            key="optimisation_filter_equipped",
        )
        max_gain = max(float(view["Gain potentiel"].max()), 1.0) if not view.empty else 1.0
        if 'optimisation_filter_gain' in st.session_state:
            st.session_state.optimisation_filter_gain=min(float(st.session_state.optimisation_filter_gain),float(round(max_gain,1)))
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
                ["total", "with_grind"],
                format_func={"total":"Total", "with_grind":tr("Total + meule", "Total + grind")}.get,
                default="total",
                key="optimisation_substat_display_mode",
                help=tr(
                    "Le second mode affiche par exemple 49 % (+7 %) : total 49, dont 7 apportés par la meule.",
                    "The second mode displays, for example, 49% (+7%): total 49, including 7 from the grind.",
                ),
            ) or "total"
            selected_stats = st.multiselect(
                tr("Sous-statistiques affichées", "Displayed substats"),
                SUBSTATS,
                default=SUBSTATS,
                key="optimisation_displayed_substats",
            )
            if 'optimisation_filtered_substats' in st.session_state:
                st.session_state.optimisation_filtered_substats=[v for v in st.session_state.optimisation_filtered_substats if v in selected_stats]
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
            if display_mode == "with_grind":
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
    if priority != 'all':
        filtered = filtered[filtered["Priorité"] == priority]
    if equipped:
        filtered = filtered[filtered["is_equipped"]]
    filtered = filtered[filtered["Gain potentiel"] >= min_gain]
    for stat, minimum in minimums.items():
        filtered = filtered[filtered[f"{stat}__total"] >= minimum]

    limit = st.select_slider(
        tr("Nombre de lignes", "Rows displayed"),
        options=[50, 100, 200, 400],
        value=200,
        key="optimisation_display_limit",
    )
    page_count = max(1, (len(filtered) + limit - 1) // limit)
    st.session_state['optimisation_page'] = min(int(st.session_state.get('optimisation_page', 1)), page_count)
    page = st.number_input("Page", 1, page_count, key="optimisation_page")
    filtered=filtered.copy()
    filtered['Action']=filtered['Action'].map(action_label)
    filtered['Priorité']=filtered['Priorité'].map(priority_label)
    shown = filtered.iloc[(page-1)*limit:page*limit]
    if filtered.empty:
        st.info(tr("Aucune rune ne correspond aux filtres. Réduisez le gain minimum ou réinitialisez les filtres.", "No runes match. Lower the minimum gain or reset the filters."))
    st.caption(
        tr(
            f"{len(filtered)} recommandation(s) · {len(shown)} affichée(s)",
            f"{len(filtered)} recommendation(s) · {len(shown)} displayed",
        )
    )

    columns = ["Id rune", "Priorité", "Set", "Slot", "Équipée sur", "Action", "Efficience", "Potentiel", "Gain potentiel", "Gain avec stock (max)", "Meules disponibles", "Meules à obtenir"]
    columns.extend(selected_stats or ["SPD"])
    columns.append("Recommandation")
    config: dict[str, Any] = {
        "Slot": st.column_config.NumberColumn("Slot", format="%d", width="small"),
        "Efficience": st.column_config.NumberColumn(tr("Efficience (%)", "Efficiency (%)"), format="%.2f"),
        "Potentiel": st.column_config.NumberColumn(tr("Potentiel (%)", "Potential (%)"), format="%.2f"),
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
    if not filtered.empty:
        rune_details(data_class, filtered)
    export_frame = filtered.loc[:, [column for column in columns if column in filtered.columns]].copy()
    st.download_button(tr("Exporter les recommandations filtrées (Excel)", "Export filtered recommendations (Excel)"), _recommendations_workbook(export_frame), file_name="optimisation_runes.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", on_click="ignore", key="optimisation_export_filtered")

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

def _render_detailed_export(data_class: Any) -> None:
    tr = _tr
    section_header(
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
                inventory = _inventory_dataframe(data_class)
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

@st.cache_data(show_spinner=False)
def _recommendations_workbook(frame: pd.DataFrame) -> bytes:
    """Build the lightweight filtered recommendations workbook once per dataset."""
    export = frame.copy()
    for column in export.select_dtypes(include="category").columns:
        export[column] = export[column].astype("object")

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        sheet_name = "Recommandations"
        export.to_excel(writer, sheet_name=sheet_name, index=False)
        _worksheet_table(writer, sheet_name, export)
    return output.getvalue()



def action_label(code):
    return {'reappraisal':_tr('Réappraisal','Reappraisal'), 'gem':_tr('Gemmer','Gem'),
            'legendary_grind':_tr('Meule légendaire','Legendary grind'),
            'hero_grind':_tr('Meule héroïque','Hero grind'),'review':_tr('À examiner','Review')}.get(code,code)


def priority_label(code):
    return {'all':_tr('Toutes','All'),'high':_tr('🔴 Haute','🔴 High'),
            'medium':_tr('🟠 Moyenne','🟠 Medium'),'low':_tr('🟡 Faible','🟡 Low')}.get(code,code)


def preset_tools():
    from fonctions.workspace import PREFIXES, current_settings, save_current
    current_settings()
    keys = [key for key in st.session_state if key.startswith(PREFIXES)]
    def reset():
        current_settings()['filters']={}
        for key in list(st.session_state):
            if key.startswith(("optimisation_filter", "optimisation_min_", "optimisation_display", "optimisation_substat", "optimisation_show_")) or key == "optimisation_page":
                del st.session_state[key]
    st.button(_tr("Réinitialiser les filtres", "Reset filters"), on_click=reset)
    with st.expander(_tr("Mes filtres enregistrés", "My saved filters")):
        presets=st.session_state.setdefault('saved_filter_presets', {})
        name=st.text_input(_tr("Nom du filtre (ex. RTA rapide, Siège)", "Filter name (e.g. Fast RTA, Siege)"),key='preset_name')
        if st.button(_tr("Enregistrer le filtre", "Save filter")) and name.strip():
            presets[name.strip()]={key:st.session_state[key] for key in keys if key in st.session_state}
            save_current()
            st.success(_tr('Filtre enregistré.','Filter saved.'))
        if presets:
            choice=st.selectbox(_tr("Charger un filtre", "Load a filter"),list(presets),key='preset_choice')
            if st.button(_tr("Appliquer", "Apply")):
                reset()
                st.session_state.update(presets[choice])
                st.rerun()

def rune_details(data_class, filtered):
    with st.expander(_tr("Fiche d’une rune", "Rune details")):
        from fonctions.rune_card import rune_card
        rune_card(data_class, filtered['Id rune'], 'ui_optimisation_rune',
                  dict(zip(filtered['Id rune'].astype(int),filtered['Gain potentiel'])))


if __name__ == "__main__":
    optimisation_page()
