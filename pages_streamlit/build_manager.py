from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable

import pandas as pd
import streamlit as st

from fonctions.gestion_bdd import lire_bdd_perso, requete_perso_bdd
from fonctions.visuel import css, page_header, section_header


css()


def _tr(fr: str, en: str) -> str:
    return en if st.session_state.get("translations_selected") == "English" else fr


def _available_columns(df: pd.DataFrame, columns: Iterable[str]) -> list[str]:
    return [column for column in columns if column in df.columns]


def _compact_rune_catalog(data_class: Any) -> pd.DataFrame:
    source = data_class.data
    source_id = id(source)
    if getattr(data_class, "_build_catalog_source_id", None) == source_id:
        cached = getattr(data_class, "_build_catalog", None)
        if isinstance(cached, pd.DataFrame):
            return cached

    raw_columns = [
        "rune_set",
        "rune_slot",
        "rune_equiped",
        "main_type",
        "main_value",
        "innate_type",
        "innate_value",
        "first_sub",
        "first_sub_value_total",
        "second_sub",
        "second_sub_value_total",
        "third_sub",
        "third_sub_value_total",
        "fourth_sub",
        "fourth_sub_value_total",
        "efficiency",
    ]
    catalog = source.loc[:, _available_columns(source, raw_columns)].copy()
    catalog.insert(0, "id_rune", source.index.to_numpy(copy=False))
    catalog.rename(
        columns={
            "rune_set": "Set",
            "rune_slot": "Slot",
            "rune_equiped": "Équipée sur",
            "main_type": "Stat principale",
            "main_value": "Valeur principale",
            "innate_type": "Innée",
            "innate_value": "Valeur innée",
            "first_sub": "Substat 1",
            "first_sub_value_total": "Valeur 1",
            "second_sub": "Substat 2",
            "second_sub_value_total": "Valeur 2",
            "third_sub": "Substat 3",
            "third_sub_value_total": "Valeur 3",
            "fourth_sub": "Substat 4",
            "fourth_sub_value_total": "Valeur 4",
            "efficiency": "Efficience",
        },
        inplace=True,
    )

    stat_columns = _available_columns(
        catalog,
        ["Stat principale", "Innée", "Substat 1", "Substat 2", "Substat 3", "Substat 4"],
    )
    if stat_columns:
        mapped = data_class.map_stats(catalog, stat_columns)
        if isinstance(mapped, pd.DataFrame):
            catalog = mapped

    defaults = {
        "Set": "—",
        "Slot": 0,
        "Équipée sur": "Inventaire",
        "Stat principale": "—",
        "Valeur principale": 0,
        "Innée": "Aucun",
        "Valeur innée": 0,
        "Substat 1": "Aucun",
        "Valeur 1": 0,
        "Substat 2": "Aucun",
        "Valeur 2": 0,
        "Substat 3": "Aucun",
        "Valeur 3": 0,
        "Substat 4": "Aucun",
        "Valeur 4": 0,
        "Efficience": 0,
    }
    for column, default in defaults.items():
        if column not in catalog.columns:
            catalog[column] = default

    catalog["id_rune"] = pd.to_numeric(catalog["id_rune"], errors="coerce").fillna(0).astype("int64")
    catalog["Slot"] = pd.to_numeric(catalog["Slot"], errors="coerce").fillna(0).astype(int)
    for column in ["Valeur principale", "Valeur innée", "Valeur 1", "Valeur 2", "Valeur 3", "Valeur 4", "Efficience"]:
        catalog[column] = pd.to_numeric(catalog[column], errors="coerce").fillna(0)
    catalog["Équipée sur"] = catalog["Équipée sur"].replace({0: "Inventaire", "0": "Inventaire"}).fillna("Inventaire").astype(str)

    catalog = catalog[
        [
            "id_rune",
            "Set",
            "Slot",
            "Équipée sur",
            "Stat principale",
            "Valeur principale",
            "Innée",
            "Valeur innée",
            "Substat 1",
            "Valeur 1",
            "Substat 2",
            "Valeur 2",
            "Substat 3",
            "Valeur 3",
            "Substat 4",
            "Valeur 4",
            "Efficience",
        ]
    ].sort_values(["Slot", "Efficience"], ascending=[True, False])

    data_class._build_catalog = catalog
    data_class._build_catalog_source_id = source_id
    return catalog


@st.cache_data(ttl=60, show_spinner=False)
def _load_saved_builds(user_id: int) -> pd.DataFrame:
    raw = lire_bdd_perso(
        """
        SELECT id_build, monstre, nom_build, rune1, rune2, rune3, rune4, rune5, rune6
        FROM sw_build
        WHERE id = :user_id
        ORDER BY monstre, nom_build
        """,
        index_col="id_build",
        params={"user_id": int(user_id)},
    )
    if raw.empty:
        return pd.DataFrame(
            columns=["id_build", "monstre", "nom_build", "rune1", "rune2", "rune3", "rune4", "rune5", "rune6"]
        )
    result = raw.transpose().reset_index()
    if "id_build" not in result.columns and not result.empty:
        result.rename(columns={result.columns[0]: "id_build"}, inplace=True)
    return result


def _monster_catalog() -> pd.DataFrame:
    required = ["id_unit", "name_monstre", "Rune1", "Rune2", "Rune3", "Rune4", "Rune5", "Rune6"]
    source = st.session_state.df_mobs
    missing = [column for column in required if column not in source.columns]
    if missing:
        raise KeyError(", ".join(missing))
    monsters = source.loc[:, required].copy()
    monsters["id_unit"] = pd.to_numeric(monsters["id_unit"], errors="coerce").fillna(0).astype("int64")
    monsters["name_monstre"] = monsters["name_monstre"].fillna(_tr("Monstre inconnu", "Unknown monster")).astype(str)
    return monsters


def _monster_label(row: pd.Series) -> str:
    return f"{row['name_monstre']} · #{int(row['id_unit'])}"


def _rune_labels(catalog: pd.DataFrame) -> dict[int, str]:
    labels: dict[int, str] = {0: _tr("Aucune rune", "No rune")}
    for _, row in catalog.iterrows():
        rune_id = int(row["id_rune"])
        main_number = float(row["Valeur principale"])
        main_value = int(main_number) if main_number.is_integer() else round(main_number, 1)
        efficiency_number = float(row["Efficience"])
        efficiency = f"{efficiency_number:.1f} %" if efficiency_number else "—"
        labels[rune_id] = (
            f"{row['Set']} · {row['Stat principale']} +{main_value} · {efficiency} · "
            f"{row['Équipée sur']} · #{rune_id}"
        )
    return labels


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _initial_runes(monster: pd.Series, saved_build: pd.Series | None) -> list[int]:
    if saved_build is not None:
        return [_safe_int(saved_build.get(f"rune{slot}", 0)) for slot in range(1, 7)]
    return [_safe_int(monster.get(f"Rune{slot}", 0)) for slot in range(1, 7)]


def _selected_rows(catalog: pd.DataFrame, rune_ids: list[int]) -> pd.DataFrame:
    valid = [rune_id for rune_id in rune_ids if rune_id]
    if not valid:
        return catalog.iloc[0:0]
    order = {rune_id: position for position, rune_id in enumerate(valid)}
    rows = catalog[catalog["id_rune"].isin(valid)].copy()
    rows["_order"] = rows["id_rune"].map(order)
    return rows.sort_values("_order").drop(columns="_order")


def _stat_totals(rows: pd.DataFrame) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    pairs = [
        ("Stat principale", "Valeur principale"),
        ("Innée", "Valeur innée"),
        ("Substat 1", "Valeur 1"),
        ("Substat 2", "Valeur 2"),
        ("Substat 3", "Valeur 3"),
        ("Substat 4", "Valeur 4"),
    ]
    for _, row in rows.iterrows():
        for name_column, value_column in pairs:
            name = str(row.get(name_column, "Aucun"))
            if name in {"Aucun", "None", "nan", "—", "0"}:
                continue
            totals[name] += float(row.get(value_column, 0) or 0)
    return dict(totals)


def _rune_details(row: pd.Series | None) -> str:
    if row is None:
        return _tr("Emplacement vide", "Empty slot")
    substats = []
    for index in range(1, 5):
        name = str(row.get(f"Substat {index}", "Aucun"))
        if name not in {"Aucun", "None", "nan", "—", "0"}:
            value = row.get(f"Valeur {index}", 0)
            value = int(value) if float(value).is_integer() else round(float(value), 1)
            substats.append(f"{name} +{value}")
    return " · ".join(substats) or _tr("Aucune sous-statistique", "No substats")


def _render_summary(rows: pd.DataFrame, monster_name: str) -> None:
    section_header(
        _tr("Résumé du combo", "Combo summary"),
        _tr("Les valeurs affichées correspondent aux bonus des six runes.", "Displayed values are bonuses from the six runes."),
    )
    totals = _stat_totals(rows)
    primary_stats = ["SPD", "HP%", "ATQ%", "DEF%", "CRIT", "DCC"]
    metrics = st.columns(6)
    for column, stat in zip(metrics, primary_stats):
        value = totals.get(stat, 0)
        suffix = "" if stat == "SPD" else "%"
        formatted = int(value) if float(value).is_integer() else round(value, 1)
        column.metric(stat, f"+{formatted}{suffix}")

    set_counts = Counter(rows["Set"].astype(str))
    set_text = " · ".join(f"{name} ×{count}" for name, count in set_counts.items()) or "—"
    st.caption(f"**{_tr('Sets sélectionnés', 'Selected sets')} :** {set_text}")

    conflicts = rows[
        (~rows["Équipée sur"].isin(["Inventaire", "0", "None", "nan", ""]))
        & (rows["Équipée sur"].str.lower() != monster_name.lower())
    ]
    if not conflicts.empty:
        names = sorted(conflicts["Équipée sur"].dropna().astype(str).unique())
        st.warning(
            _tr(
                f"{len(conflicts)} rune(s) sont actuellement équipées sur : {', '.join(names)}.",
                f"{len(conflicts)} rune(s) are currently equipped on: {', '.join(names)}.",
            ),
            icon="⚠️",
        )


def _save_build(user_id: int, monster_name: str, build_name: str, rune_ids: list[int], overwrite: bool) -> None:
    saved = _load_saved_builds(user_id)
    duplicate = saved[
        saved["monstre"].astype(str).str.lower().eq(monster_name.lower())
        & saved["nom_build"].astype(str).str.lower().eq(build_name.lower())
    ]
    if not duplicate.empty and not overwrite:
        st.error(_tr("Ce nom existe déjà pour ce monstre.", "This name already exists for this monster."))
        return

    if not duplicate.empty:
        requete_perso_bdd(
            "DELETE FROM sw_build WHERE id = :user_id AND LOWER(monstre) = LOWER(:monster) AND LOWER(nom_build) = LOWER(:build_name)",
            {"user_id": int(user_id), "monster": monster_name, "build_name": build_name},
        )

    params = {
        "user_id": int(user_id),
        "monster": monster_name.lower(),
        "build_name": build_name,
        **{f"rune{slot}": int(rune_ids[slot - 1]) for slot in range(1, 7)},
    }
    requete_perso_bdd(
        """
        INSERT INTO sw.sw_build(id, monstre, nom_build, rune1, rune2, rune3, rune4, rune5, rune6)
        VALUES (:user_id, :monster, :build_name, :rune1, :rune2, :rune3, :rune4, :rune5, :rune6)
        """,
        params,
    )
    _load_saved_builds.clear()
    st.success(_tr("Combo sauvegardé.", "Combo saved."))
    st.rerun()


def build_manager_page() -> None:
    page_header(
        _tr("Bibliothèque de builds", "Build library"),
        _tr(
            "Mémorisez plusieurs combos de runes par monstre et rechargez-les selon le scénario.",
            "Save multiple rune combos per monster and reload them for each scenario.",
        ),
        icon="🔨",
        eyebrow=_tr("Runages", "Runes"),
    )

    if not st.session_state.get("submitted", False):
        st.switch_page("pages_streamlit/upload.py")
        return

    st.info(
        _tr(
            "Seuls le nom du monstre, le nom du scénario et les six identifiants de runes sont sauvegardés.",
            "Only the monster name, scenario name and six rune identifiers are saved.",
        ),
        icon="🔒",
    )

    data_class = st.session_state.data_rune
    catalog = _compact_rune_catalog(data_class)
    monsters = _monster_catalog()
    saved_builds = _load_saved_builds(int(st.session_state.id_joueur))

    total1, total2, total3 = st.columns(3)
    total1.metric(_tr("Combos sauvegardés", "Saved combos"), len(saved_builds))
    total2.metric(_tr("Monstres concernés", "Monsters covered"), saved_builds["monstre"].nunique() if not saved_builds.empty else 0)
    total3.metric(_tr("Runes disponibles", "Available runes"), len(catalog))

    section_header(
        _tr("1. Choisir le monstre et le point de départ", "1. Choose a monster and starting point"),
        _tr("Chargez l'équipement actuel ou un scénario déjà sauvegardé.", "Load current equipment or a saved scenario."),
    )

    monster_labels = {int(row.id_unit): _monster_label(pd.Series(row._asdict())) for row in monsters.itertuples(index=False)}
    monster_ids = list(monster_labels)
    selector_column, portrait_column = st.columns([5, 1])
    with selector_column:
        selected_unit = st.selectbox(
            _tr("Monstre", "Monster"),
            monster_ids,
            format_func=lambda unit_id: monster_labels.get(int(unit_id), str(unit_id)),
        )
    monster = monsters[monsters["id_unit"] == int(selected_unit)].iloc[0]
    monster_name = str(monster["name_monstre"])
    with portrait_column:
        swarfarm = st.session_state.get("swarfarm")
        if isinstance(swarfarm, pd.DataFrame) and {"name", "image_filename"}.issubset(swarfarm.columns):
            match = swarfarm[swarfarm["name"] == monster_name]
            if not match.empty:
                st.image(
                    f"https://swarfarm.com/static/herders/images/monsters/{match.iloc[0]['image_filename']}",
                    width=88,
                )

    monster_builds = saved_builds[saved_builds["monstre"].astype(str).str.lower() == monster_name.lower()]
    sources: list[tuple[str, int | None]] = [(_tr("Équipement actuel", "Current equipment"), None)]
    sources.extend((f"💾 {row.nom_build}", int(row.id_build)) for row in monster_builds.itertuples(index=False))
    source_labels = [label for label, _ in sources]
    selected_source_label = selector_column.selectbox(_tr("Charger", "Load"), source_labels)
    selected_build_id = dict(sources)[selected_source_label]
    saved_row = None
    if selected_build_id is not None:
        saved_row = monster_builds[monster_builds["id_build"] == selected_build_id].iloc[0]

    context = (int(selected_unit), selected_build_id)
    if st.session_state.get("_build_manager_context") != context:
        initial = _initial_runes(monster, saved_row)
        for slot, rune_id in enumerate(initial, start=1):
            st.session_state[f"build_manager_slot_{slot}"] = rune_id
        st.session_state["build_manager_name"] = str(saved_row["nom_build"]) if saved_row is not None else ""
        st.session_state["_build_manager_context"] = context

    section_header(
        _tr("2. Composer le combo", "2. Compose the combo"),
        _tr("Chaque liste ne contient que les runes du slot correspondant.", "Each list contains only runes for the corresponding slot."),
    )

    labels = _rune_labels(catalog)
    selected_ids: list[int] = []
    for slot_group in ((1, 2, 3), (4, 5, 6)):
        columns = st.columns(3)
        for column, slot in zip(columns, slot_group):
            with column:
                with st.container(border=True):
                    st.markdown(f"**Slot {slot}**")
                    options = [0] + catalog.loc[catalog["Slot"] == slot, "id_rune"].astype(int).tolist()
                    current = _safe_int(st.session_state.get(f"build_manager_slot_{slot}", 0))
                    if current not in options:
                        options.append(current)
                        labels[current] = _tr(f"Rune introuvable · #{current}", f"Missing rune · #{current}")
                    selected = st.selectbox(
                        f"Rune slot {slot}",
                        options,
                        key=f"build_manager_slot_{slot}",
                        format_func=lambda rune_id, labels=labels: labels.get(int(rune_id), f"#{rune_id}"),
                        label_visibility="collapsed",
                    )
                    selected_ids.append(int(selected))
                    row = catalog[catalog["id_rune"] == int(selected)]
                    if row.empty:
                        st.caption(_tr("Emplacement vide", "Empty slot"))
                    else:
                        rune = row.iloc[0]
                        st.caption(_rune_details(rune))
                        st.caption(
                            f"{_tr('Équipée sur', 'Equipped on')} : {rune['Équipée sur']} · "
                            f"{_tr('Efficience', 'Efficiency')} : {float(rune['Efficience']):.1f} %"
                        )

    rows = _selected_rows(catalog, selected_ids)
    _render_summary(rows, monster_name)

    section_header(
        _tr("3. Sauvegarder le scénario", "3. Save the scenario"),
        _tr("Utilisez un nom explicite : RTA rapide, Siège, Boss, etc.", "Use a clear name: Fast RTA, Siege, Boss, etc."),
    )
    build_name = st.text_input(
        _tr("Nom du scénario", "Scenario name"),
        key="build_manager_name",
        placeholder=_tr("Ex. RTA rapide", "E.g. Fast RTA"),
        max_chars=80,
    ).strip()
    overwrite = st.toggle(_tr("Remplacer le scénario s'il existe déjà", "Replace the scenario if it already exists"), value=False)
    if st.button(_tr("Sauvegarder ce combo", "Save this combo"), type="primary", width="stretch"):
        if not build_name:
            st.error(_tr("Donnez un nom au scénario.", "Enter a scenario name."))
        elif not any(selected_ids):
            st.error(_tr("Sélectionnez au moins une rune.", "Select at least one rune."))
        else:
            _save_build(int(st.session_state.id_joueur), monster_name, build_name, selected_ids, overwrite)

    if saved_row is not None:
        with st.expander(_tr("Supprimer le scénario chargé", "Delete loaded scenario")):
            confirmation = st.checkbox(
                _tr("Je confirme la suppression définitive", "I confirm permanent deletion"),
                key=f"delete_build_{selected_build_id}",
            )
            if st.button(
                _tr("Supprimer", "Delete"),
                type="secondary",
                disabled=not confirmation,
                width="stretch",
            ):
                requete_perso_bdd(
                    "DELETE FROM sw_build WHERE id = :user_id AND id_build = :build_id",
                    {"user_id": int(st.session_state.id_joueur), "build_id": int(selected_build_id)},
                )
                _load_saved_builds.clear()
                st.success(_tr("Scénario supprimé.", "Scenario deleted."))
                st.session_state.pop("_build_manager_context", None)
                st.rerun()

    st.caption("Made by Tomlora 😎")


try:
    build_manager_page()
except KeyError as error:
    st.warning(
        _tr(
            f"Les données nécessaires au gestionnaire de builds sont absentes : {error}",
            f"Required build manager data is missing: {error}",
        ),
        icon="⚠️",
    )
