from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


RUNE_COLUMNS = [f"Rune{slot}" for slot in range(1, 7)]


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _repair_monster_rune_slots() -> None:
    """Rebuild Rune1..Rune6 from the JSON slot_no field.

    The JSON rune list is not guaranteed to be ordered by slot. The historical
    upload code used the list position, which can associate an existing rune
    with the wrong slot and make the build manager report it as missing.
    """
    data_json = st.session_state.get("data_json")
    monsters = st.session_state.get("df_mobs")
    if not isinstance(data_json, dict) or not isinstance(monsters, pd.DataFrame):
        return
    if "id_unit" not in monsters.columns:
        return

    units = data_json.get("unit_list", [])
    marker = (id(data_json), id(monsters), len(units))
    if st.session_state.get("_build_slot_mapping_source") == marker:
        return

    slot_mapping: dict[int, list[int]] = {}
    for unit in units:
        if not isinstance(unit, dict):
            continue
        unit_id = _safe_int(unit.get("unit_id"))
        if not unit_id:
            continue

        rune_ids = [0, 0, 0, 0, 0, 0]
        runes = unit.get("runes", [])
        if isinstance(runes, dict):
            runes = list(runes.values())

        for rune in runes:
            if not isinstance(rune, dict):
                continue
            slot = _safe_int(rune.get("slot_no"))
            rune_id = _safe_int(rune.get("rune_id"))
            if 1 <= slot <= 6:
                rune_ids[slot - 1] = rune_id
        slot_mapping[unit_id] = rune_ids

    if not slot_mapping:
        return

    slot_frame = pd.DataFrame.from_dict(
        slot_mapping,
        orient="index",
        columns=RUNE_COLUMNS,
    )
    unit_ids = pd.to_numeric(monsters["id_unit"], errors="coerce")
    for column in RUNE_COLUMNS:
        mapped = unit_ids.map(slot_frame[column])
        if column in monsters.columns:
            mapped = mapped.fillna(monsters[column])
        monsters[column] = pd.to_numeric(mapped, errors="coerce").fillna(0).astype("int64")

    st.session_state["_build_slot_mapping_source"] = marker


def _real_rune_label(rune_id: Any) -> str | None:
    data_class = st.session_state.get("data_rune")
    data = getattr(data_class, "data", None)
    rune_id = _safe_int(rune_id)
    if not rune_id or not isinstance(data, pd.DataFrame) or rune_id not in data.index:
        return None

    row = data.loc[rune_id]
    if isinstance(row, pd.DataFrame):
        row = row.iloc[0]

    property_map = getattr(data_class, "property", {})
    main_code = row.get("main_type", 0)
    main_name = property_map.get(main_code, main_code)
    main_value = row.get("main_value", 0)
    try:
        main_number = float(main_value)
        main_value = int(main_number) if main_number.is_integer() else round(main_number, 1)
    except (TypeError, ValueError):
        pass

    efficiency = pd.to_numeric(
        pd.Series([row.get("efficiency", 0)]), errors="coerce"
    ).fillna(0).iloc[0]
    set_name = row.get("rune_set", "—")
    equipped_on = row.get("rune_equiped", "Inventaire")
    return (
        f"{set_name} · {main_name} +{main_value} · {float(efficiency):.1f} % · "
        f"{equipped_on} · #{rune_id}"
    )


def _run_build_manager() -> None:
    _repair_monster_rune_slots()

    page_path = Path(__file__).with_name("build_manager.py")
    original_selectbox = st.selectbox

    def selectbox(label, options, *args, format_func=None, **kwargs):
        is_rune_selector = isinstance(label, str) and label.startswith("Rune slot")
        if not is_rune_selector:
            return original_selectbox(
                label,
                options,
                *args,
                format_func=format_func,
                **kwargs,
            )

        # Rune identifiers are large integers. Keeping them as raw widget
        # values can make the selected value unstable between Streamlit
        # reruns. The widget therefore stores strings, while the build page
        # continues to receive a normal Python int.
        numeric_options = [_safe_int(value) for value in options]
        string_options = [str(value) for value in numeric_options]
        widget_key = kwargs.get("key")

        if widget_key:
            current_value = str(_safe_int(st.session_state.get(widget_key, 0)))
            if current_value not in string_options:
                string_options.append(current_value)
                numeric_options.append(_safe_int(current_value))
            st.session_state[widget_key] = current_value

        original_format = format_func

        def corrected_format(value: Any) -> str:
            rune_id = _safe_int(value)
            if original_format is None:
                text = str(rune_id)
            else:
                text = original_format(rune_id)
            if "Rune introuvable" in str(text) or "Missing rune" in str(text):
                return _real_rune_label(rune_id) or str(text)
            return str(text)

        selected_value = original_selectbox(
            label,
            string_options,
            *args,
            format_func=corrected_format,
            **kwargs,
        )
        return _safe_int(selected_value)

    try:
        st.selectbox = selectbox
        runpy.run_path(str(page_path), run_name="__build_manager_safe__")
    finally:
        st.selectbox = original_selectbox


_run_build_manager()
