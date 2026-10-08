"""Readable rune identities and data-driven SVG cards; no external image required."""
from html import escape
from textwrap import wrap
import pandas as pd
import streamlit as st
from fonctions.journey import tr

SUBS = ('first_sub', 'second_sub', 'third_sub', 'fourth_sub')


def slot_shape(slot):
    """Clockwise orientation: 1 at the top, 4 at the bottom, as in game."""
    slot = int(slot)
    if slot not in range(1, 7):
        raise ValueError('Rune slot must be between 1 and 6')
    angle = (slot - 1) * 60
    return (
        f'<g data-rune-slot="{slot}" transform="translate(75 163)">'
        f'<g transform="rotate({angle})">'
        '<path d="M0 -48 L30 0 L17 27 L-17 27 L-30 0 Z" fill="#35251c" stroke="#d4a55e" stroke-width="4" stroke-linejoin="round"/>'
        '<path d="M0 -39 L23 0 L13 20 L-13 20 L-23 0 Z" fill="#55402b" stroke="#836138" stroke-width="2"/>'
        '<path d="M0 -44 L-27 0 L-15 24" fill="none" stroke="#f0ca85" stroke-width="2"/>'
        '</g>'
        f'<text x="0" y="5" text-anchor="middle" fill="#f4d378" font-family="Arial, sans-serif" font-size="28" font-weight="700">{slot}</text></g>'
    )


def slot_wheel(slot):
    """Small position guide: six petals with the current slot highlighted."""
    from math import cos, sin, radians
    parts = ['<g transform="translate(480 437) scale(.46)" aria-hidden="true">']
    for number in range(1, 7):
        angle = (number - 1) * 60
        active = number == int(slot)
        fill, stroke = ('#79562b', '#f4d378') if active else ('#30251e', '#725437')
        parts.append(f'<path d="M100 8 L128 55 L116 80 L84 80 L72 55 Z" transform="rotate({angle} 100 100)" fill="{fill}" stroke="{stroke}" stroke-width="4"/>')
        x, y = 100 + 47*sin(radians(angle)), 100 - 47*cos(radians(angle))
        parts.append(f'<text x="{x:g}" y="{y+7:g}" text-anchor="middle" fill="{stroke}" font-family="Arial, sans-serif" font-size="22" font-weight="700">{number}</text>')
    parts.append('<path d="M100 80 L117 90 L117 110 L100 120 L83 110 L83 90 Z" fill="#624626" stroke="#a47c46" stroke-width="3"/></g>')
    return ''.join(parts)


def stat_text(runes, code, value):
    name = runes.property.get(code, code)
    if name in (0, '0', 'Aucun', 'None') or pd.isna(name):
        return ''
    percent = str(name).endswith('%') or name in ('CRIT', 'DCC', 'RES', 'ACC')
    labels = {'HP': tr('PV', 'HP'), 'ATQ': tr('ATQ', 'ATK'),
              'CRIT': tr('Taux crit.', 'CRI Rate'), 'DCC': tr('Dégâts crit.', 'CRI Dmg'),
              'ACC': tr('Précision', 'Accuracy'), 'RES': tr('Résistance', 'Resistance')}
    label = labels.get(str(name).rstrip('%'), str(name).rstrip('%'))
    number = '—' if pd.isna(value) else f'+{value:g}'
    return f'{label} {number}{"%" if percent else ""}'


def equipped_on(row):
    value = row.rune_equiped
    return tr('Inventaire', 'Inventory') if value in (0, '0', 'Inventaire', 'Inventory') else str(value)


def substats(runes, row):
    return ' · '.join(filter(None, (stat_text(runes, row[sub], row[f'{sub}_value_total']) for sub in SUBS)))


def rune_label(runes, rune_id):
    if rune_id not in runes.data.index:
        return tr('Rune absente du dernier import', 'Rune missing from the latest import') + f' (#{rune_id})'
    row = runes.data.loc[rune_id]
    return f'{row.rune_set} · Slot {row.rune_slot} · {equipped_on(row)} · {stat_text(runes, row.main_type, row.main_value)} · {substats(runes, row)}'


def rune_identity(runes, rune_id):
    if rune_id not in runes.data.index:
        return {tr('Rune', 'Rune'): rune_label(runes, rune_id)}
    row = runes.data.loc[rune_id]
    return {'Set': str(row.rune_set), 'Slot': int(row.rune_slot),
            tr('Équipée sur', 'Equipped on'): equipped_on(row),
            tr('Principale', 'Main stat'): stat_text(runes, row.main_type, row.main_value),
            tr('Sous-statistiques', 'Substats'): substats(runes, row)}


def rune_svg(runes, rune_id):
    row = runes.data.loc[rune_id]
    quality = str(row.get('qualité_original', row.get('qualité', '')))
    names = {'1': tr('Normale','Normal'), '2': tr('Magique','Magic'), '3': tr('Rare','Rare'),
             '4': tr('Héroïque','Hero'), '5': tr('Légendaire','Legend')}
    quality = names.get(quality[-1:], quality) if quality.isdigit() else quality.replace('LGD', tr('Légendaire','Legend')).replace('HEROIQUE', tr('Héroïque','Hero'))
    original_quality = str(row.get('qualité_original', ''))
    if int(row.stars) > 10 or original_quality.startswith('ANTIQUE') or original_quality in ('11','12','13','14','15'):
        quality = tr('Antique · ', 'Ancient · ') + quality.replace('ANTIQUE_', '')
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 550" role="img">',
             f'<title>{escape(rune_label(runes, rune_id))}</title>',
             '<defs><linearGradient id="panel" x2="0" y2="1"><stop stop-color="#352517"/><stop offset="1" stop-color="#17130f"/></linearGradient></defs>',
             '<rect x="3" y="3" width="594" height="544" rx="22" fill="url(#panel)" stroke="#c8a24d" stroke-width="3"/>']
    def text(x, y, value, size=25, color='#f5df9b', weight='400'):
        parts.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}">{escape(str(value))}</text>')
    text(28, 47, f'+{row.level} {row.rune_set} · Slot {row.rune_slot}', 30, '#efbf61', '700')
    text(28, 78, quality, 20, '#c5ac80')
    parts.append(slot_shape(row.rune_slot))
    text(27, 102, '★' * (int(row.stars) % 10), 17, '#f0a2ed')
    text(145, 145, stat_text(runes, row.main_type, row.main_value), 32, '#fff8e7', '700')
    text(145, 182, stat_text(runes, row.innate_type, row.innate_value), 23, '#e6d6b7')
    parts.append('<path d="M28 228 H572" stroke="#6b5532"/>')
    for index, sub in enumerate(SUBS):
        value = stat_text(runes, row[sub], row[f'{sub}_value_total'])
        text(30, 270 + index*44, value, 29)
        grind = row.get(f'{sub}_grinded_value', 0)
        if value and pd.notna(grind) and grind > 0:
            text(445, 270 + index*44, tr('dont ', 'incl. ') + f'+{grind:g}', 19, '#b5cf84')
    parts.append('<path d="M28 425 H572" stroke="#6b5532"/>')
    owner = tr('Équipée sur : ', 'Equipped on: ') + equipped_on(row)
    for index, line in enumerate(wrap(owner, 34)[:2]):
        text(28, 460 + index*26, line, 22, '#e6d6b7')
    parts.append(slot_wheel(row.rune_slot))
    efficiency = row.efficiency
    text(28, 522, tr('Efficience : ', 'Efficiency: ') + ('—' if pd.isna(efficiency) else f'{efficiency:.2f}%'), 21, '#b5cf84')
    parts.append('</svg>')
    return ''.join(parts)


def show_rune(runes, rune_id):
    st.image(rune_svg(runes, rune_id), width=600)
