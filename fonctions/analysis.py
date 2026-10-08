"""Pure calculations shared by import, statistics and interactive pages."""
from __future__ import annotations

import pandas as pd
import numpy as np

SUBS = ('first_sub', 'second_sub', 'third_sub', 'fourth_sub')
SCORING_VERSION = '2026.10-v2'


def tier_counts(frame, value, edges, labels, keys=('rune_set',)):
    data = frame.loc[:, [*keys, value]].copy()
    data['tier'] = pd.cut(data[value], edges, labels=labels, right=False)
    counted = data.dropna(subset=['tier']).groupby([*keys, 'tier'], observed=True).size()
    if counted.empty:
        index = pd.Index([], name=keys[0]) if len(keys) == 1 else pd.MultiIndex.from_tuples([], names=keys)
        return pd.DataFrame(0, index=index, columns=labels, dtype='int64')
    return counted.unstack('tier', fill_value=0).reindex(columns=labels, fill_value=0).astype('int64')


def objective_counts(frame):
    counts = tier_counts(frame, 'efficiency', [100, 110, np.inf], [100, 110], ('rune_set', 'rune_slot'))
    return counts.rename_axis(columns='efficience').stack().rename('Quantité').reset_index()


def substat_table(data, properties):
    frames = []
    for sub in SUBS:
        part = data[['rune_set', 'rune_slot']].copy()
        part['id_rune'] = data.index
        part['substat'] = data[sub].map(lambda v: properties.get(v, v))
        part['value'] = pd.to_numeric(data[f'{sub}_value'], errors='coerce').fillna(0)
        part['grind'] = pd.to_numeric(data[f'{sub}_grinded_value'], errors='coerce').fillna(0)
        part['total'] = part['value'] + part['grind']
        frames.append(part)
    result = pd.concat(frames, ignore_index=True)
    return result[result['substat'].notna() & ~result['substat'].isin(['Aucun', 0])]


def best_substats(long, by_slot=False):
    keys = ['substat', 'rune_set'] + (['rune_slot'] if by_slot else [])
    columns = keys + ['max_value'] + ([] if by_slot else ['top5', 'top10', 'top15', 'top25']) + [str(i) for i in range(10, 0, -1)]
    rows = []
    for key, group in long.groupby(keys, observed=True, sort=True):
        values = np.sort(group['total'].to_numpy(dtype=float))[::-1]
        row = dict(zip(keys, key))
        row['max_value'] = values[0]
        if not by_slot:
            row.update({f'top{n}': float(values[:n].mean()) for n in (5, 10, 15, 25)})
        row.update({str(n): values[n-1] if len(values) >= n else np.nan for n in range(1, 11)})
        rows.append(row)
    return pd.DataFrame(rows, columns=columns).set_index('substat')


def rune_speed(data):
    result = pd.Series(0.0, index=data.index)
    for sub in SUBS:
        result += pd.to_numeric(data[f'{sub}_value_total'], errors='coerce').fillna(0).where(data[sub].isin([8, 'SPD']), 0)
    if 'innate_type' in data:
        result += pd.to_numeric(data['innate_value'], errors='coerce').fillna(0).where(data['innate_type'].isin([8, 'SPD']), 0)
    return result


def fastest_build(data, primary, secondary=None, slot2_speed=True):
    """Exact six-slot search. One Intangible may fill one missing set piece."""
    columns = ['id_rune', 'rune_set', 'spd', 'main_type', 'main_value']
    empty = pd.DataFrame(columns=columns, index=pd.Index([], name='rune_slot'))
    if data.empty:
        return empty, None
    candidates = data.copy()
    candidates['id_rune'] = candidates.index
    candidates['spd'] = rune_speed(candidates)
    candidates['spd'] += pd.to_numeric(candidates['main_value'], errors='coerce').fillna(0).where(candidates['main_type'].isin([8, 'SPD']), 0)
    if slot2_speed:
        candidates = candidates[(candidates['rune_slot'].astype(int) != 2) | candidates['main_type'].isin([8, 'SPD'])]
    from itertools import combinations, product
    four_piece = {'Fatal', 'Swift', 'Rage', 'Despair', 'Vampire', 'Violent'}
    by_slot = {}
    for slot in range(1, 7):
        rows = candidates[candidates.rune_slot.astype(int).eq(slot)].sort_values(['spd', 'id_rune'], ascending=[False, True]).drop_duplicates('rune_set')
        by_slot[slot] = {r['rune_set']: r for r in rows.to_dict('records')}
    best = None
    def consider(rows):
        nonlocal best
        if any(row is None for row in rows): return
        sets = [row['rune_set'] for row in rows]
        if sets.count('Intangible') > 1: return
        counts = {name: sets.count(name) for name in set(sets) if name != 'Intangible'}
        eligible = [name for name, n in counts.items() if n % (4 if name in four_piece else 2) == (3 if name in four_piece else 1)]
        completed = eligible[0] if sets.count('Intangible') == 1 and len(eligible) == 1 else None
        required = 6 if primary == secondary else 4
        if counts.get(primary, 0) + int(completed == primary) < required: return
        if secondary and secondary != primary and counts.get(secondary,0) + int(completed == secondary) < 2: return
        total = sum(row['spd'] for row in rows)
        if best is None or total > best[0]: best = total, rows
    slots = set(range(1, 7))
    required = 6 if primary == secondary else 4
    # Enumerate primary slot partitions, then only the best rune per set/slot.
    # At most two unrestricted slots remain, independent of inventory size.
    for size in (required, required - 1):
        for primary_slots in combinations(sorted(slots), size):
            core = [by_slot[slot].get(primary) for slot in primary_slots]
            if any(row is None for row in core): continue
            remaining = sorted(slots - set(primary_slots))
            wild_slots = remaining if size < required else [None]
            for wild_slot in wild_slots:
                chosen = core + ([by_slot[wild_slot].get('Intangible')] if wild_slot else [])
                if any(row is None for row in chosen): continue
                other_slots = [slot for slot in remaining if slot != wild_slot]
                options = [list(by_slot[slot].values()) for slot in other_slots]
                for others in product(*options): consider(chosen + list(others))
    if best is None: return empty, None
    score, rows = best
    return pd.DataFrame(rows).set_index('rune_slot').sort_index()[columns], int(score)


def select_snapshots(data, score, mode='latest', identity='id'):
    """Keep all values and the date from the same observation, including ties."""
    frame = data.copy()
    if frame.empty:
        return frame
    frame['_date'] = pd.to_datetime(frame['date'], dayfirst=True, errors='coerce', format='mixed')
    ordering = ['_date', score] if mode == 'latest' else [score, '_date']
    frame = frame.sort_values(ordering, kind='stable', na_position='first')
    return frame.drop_duplicates(identity, keep='last').drop(columns='_date').sort_values(score, ascending=False, kind='stable')
