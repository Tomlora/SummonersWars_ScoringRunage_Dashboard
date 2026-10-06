"""Readable rune identities and data-driven SVG cards; no external image required."""
from html import escape
from textwrap import wrap
import pandas as pd
import streamlit as st
from fonctions.journey import tr

SUBS = ('first_sub', 'second_sub', 'third_sub', 'fourth_sub')


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
    parts.append('<path d="M75 107 L115 157 L100 207 L50 207 L35 157 Z" fill="#5d503b" stroke="#c8a24d" stroke-width="3"/>')
    text(64, 175, row.rune_slot, 35, '#f4d378', '700')
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
    for index, line in enumerate(wrap(owner, 42)[:2]):
        text(28, 460 + index*26, line, 22, '#e6d6b7')
    efficiency = row.efficiency
    text(28, 522, tr('Efficience : ', 'Efficiency: ') + ('—' if pd.isna(efficiency) else f'{efficiency:.2f}%'), 21, '#b5cf84')
    parts.append('</svg>')
    return ''.join(parts)


def show_rune(runes, rune_id):
    st.image(rune_svg(runes, rune_id), width=600)
