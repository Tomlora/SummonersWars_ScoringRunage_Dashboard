"""Theoretical grind-only efficiency at the rune's current substat values."""
import math
from fonctions.analysis import SUBS


def maximum_grind_efficiencies(runes, row):
    if int(row.stars) % 10 != 6 or int(row.level) < 12 or not math.isfinite(float(row.efficiency)):
        return None, None
    ancient = str(row['qualité_original']).startswith('ANTIQUE')
    limits = (runes.sub_max_heroique_antique, runes.sub_max_lgd_antique) if ancient else (runes.sub_max_heroique, runes.sub_max_lgd)
    maxima = []
    for maximum in limits:
        total = 1.0
        if row.innate_type != 0:
            total += row.innate_value / row.innate_value_max
        for sub in SUBS:
            # Never replace an existing grind with a weaker one. Non-grindable
            # substats keep their current value; gems and level-ups are excluded.
            grind = max(row[f'{sub}_grinded_value'], maximum.get(row[sub], 0))
            total += (row[f'{sub}_value'] + grind) / row[f'{sub}_value_max']
        value = round(total / 2.8 * 100, 2)
        maxima.append(max(float(row.efficiency), value) if math.isfinite(value) else None)
    return tuple(maxima)
