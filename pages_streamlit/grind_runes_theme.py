from __future__ import annotations

from typing import Any, Iterable

import pandas as pd
import streamlit as st

from fonctions.runes import CRAFT_TYPE_MAP, COM2US_QUALITY_MAP
from fonctions.streamlit_compat import ensure_pygwalker_streamlit_compatibility
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
    return values.fillna(default)


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
    view["Équipée sur"] = view["Équipée sur"].replace({0: "Inventaire", "0": "Inventaire"}).astype(str)
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
            action = _tr("Réappraisal", "Reappraisal")
        elif "gem" in lowered or "gemm" in lowered:
            action = _tr("Gemmer", "Gem")
        elif _truthy(legendary):
            action = _tr("Meule légendaire", "Legendary grind")
        elif _truthy(hero):
            action = _tr("Meule héroïque", "Hero grind")
        else:
            action = _tr("À examiner", "Review")
        actions.append(action)
        clean_comment = " · ".join(part.strip() for part in comment.splitlines() if part.strip())
        recommendations.append(clean_comment or action)

    view["Action"] = actions
    view["Recommandation"] = recommendations
    view["Priorité"] = pd.cut(
        view["Gain potentiel"],
        bins=[-0.01, 4.99, 9.99, float("inf")],
        labels=[_tr("🟡 Faible", "🟡 Low"), _tr("🟠 Moyenne", "🟠 Medium"), _tr("🔴 Haute", "🔴 High")],
    ).astype(str)
    return view.sort_values(["Gain potentiel", "SPD"], ascending=[False, False])


def _render_recommendations(view: pd.DataFrame) -> None:
    section_header(
        _tr("À améliorer", "Upgrade recommendations"),
        _tr(
            "Filtrez les runes selon le gain potentiel et l'action à effectuer.",
            "Filter runes by potential gain and recommended action.",
        ),
    )

    high_label = _tr("🔴 Haute", "🔴 High")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(_tr("Runes analysées", "Runes analysed"), f"{len(view):,}".replace(",", " "))
    kpi2.metric(_tr("Priorité haute", "High priority"), int((view["Priorité"] == high_label).sum()))
    mean_gain = float(view["Gain potentiel"].mean()) if not view.empty else 0.0
    kpi3.metric(_tr("Gain moyen", "Average gain"), f"+{mean_gain:.1f} pts")
    kpi4.metric(_tr("Runes équipées", "Equipped runes"), int((view["Équipée sur"] != "Inventaire").sum()))

    with st.expander(_tr("Filtres", "Filters"), expanded=True):
        filter1, filter2, filter3, filter4 = st.columns([1.4, 1.2, 1.1, 1])
        selected_sets = filter1.multiselect(
            _tr("Sets", "Sets"),
            sorted(value for value in view["Set"].dropna().unique() if value and value != "—"),
            placeholder=_tr("Tous les sets", "All sets"),
        )
        selected_actions = filter2.multiselect(
            _tr("Actions", "Actions"),
            sorted(view["Action"].dropna().unique()),
            placeholder=_tr("Toutes les actions", "All actions"),
        )
        selected_priority = filter3.selectbox(
            _tr("Priorité", "Priority"),
            [_tr("Toutes", "All"), high_label, _tr("🟠 Moyenne", "🟠 Medium"), _tr("🟡 Faible", "🟡 Low")],
        )
        only_equipped = filter4.toggle(_tr("Équipées uniquement", "Equipped only"), value=False)

        max_gain = max(float(view["Gain potentiel"].max()), 1.0) if not view.empty else 1.0
        min_gain = st.slider(
            _tr("Gain potentiel minimum", "Minimum potential gain"),
            0.0,
            float(round(max_gain, 1)),
            0.0,
            0.5,
        )

    filtered = view
    if selected_sets:
        filtered = filtered[filtered["Set"].isin(selected_sets)]
    if selected_actions:
        filtered = filtered[filtered["Action"].isin(selected_actions)]
    if selected_priority != _tr("Toutes", "All"):
        filtered = filtered[filtered["Priorité"] == selected_priority]
    if only_equipped:
        filtered = filtered[filtered["Équipée sur"] != "Inventaire"]
    filtered = filtered[filtered["Gain potentiel"] >= min_gain]

    display_limit = st.select_slider(
        _tr("Nombre de lignes", "Rows displayed"),
        options=[50, 100, 200, 400],
        value=200,
    )
    shown = filtered.head(display_limit)
    st.caption(
        _tr(
            f"{len(filtered)} recommandation(s) · {len(shown)} affichée(s)",
            f"{len(filtered)} recommendation(s) · {len(shown)} displayed",
        )
    )
    st.dataframe(
        shown[
            [
                "Priorité",
                "Set",
                "Slot",
                "Équipée sur",
                "Action",
                "Efficience",
                "Potentiel",
                "Gain potentiel",
                "SPD",
                "Recommandation",
            ]
        ],
        width="stretch",
        height=620,
        hide_index=True,
        column_config={
            "Slot": st.column_config.NumberColumn("Slot", format="%d", width="small"),
            "Efficience": st.column_config.NumberColumn(_tr("Efficience", "Efficiency"), format="%.2f"),
            "Potentiel": st.column_config.NumberColumn(_tr("Potentiel", "Potential"), format="%.2f"),
            "Gain potentiel": st.column_config.ProgressColumn(
                _tr("Gain potentiel", "Potential gain"),
                format="+%.2f",
                min_value=0,
                max_value=max(max_gain, 1.0),
            ),
            "SPD": st.column_config.NumberColumn("SPD", format="%d"),
        },
    )

    csv_data = filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        _tr("Exporter les recommandations filtrées", "Export filtered recommendations"),
        csv_data,
        file_name=f"optimisation_runes_{st.session_state.get('pseudo', 'compte')}.csv",
        mime="text/csv",
        width="stretch",
    )


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
        ensure_pygwalker_streamlit_compatibility()
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
    else:
        _render_recommendations(view)

    st.caption("Made by Tomlora 😎")


optimisation_page()