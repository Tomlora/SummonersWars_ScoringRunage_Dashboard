"""Structural checks before pandas or score calculations see untrusted values."""
import math


def validate_values(data):
    def walk(value, path):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f'{path}: nombre non fini / non-finite number')
        if isinstance(value, dict):
            for key, child in value.items():
                walk(child, f'{path}.{key}')
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, f'{path}[{i}]')
    walk(data, 'export')


def validate_inventory(data, runes, artifacts):
    def integer(value, path, minimum=0):
        if type(value) is not int or not minimum <= value <= 2**63-1:
            raise ValueError(f'{path}: entier invalide / invalid integer')
    def unique(rows, key):
        seen = set()
        for row in rows:
            value = row[key]
            integer(value, key, 1)
            if value in seen:
                raise ValueError(f'{key} {value}: identifiant dupliqué / duplicate ID')
            seen.add(value)
    integer(data['wizard_info']['wizard_id'], 'wizard_id', 1)
    unique(data['unit_list'], 'unit_id')
    unique(runes, 'rune_id')
    unique(artifacts, 'rid')
    for row in runes:
        for key in ('set_id','slot_no','occupied_id','class','rank','extra','upgrade_curr'):
            integer(row[key], f"rune {row['rune_id']}.{key}")
        for key in ('pri_eff','prefix_eff','sec_eff'):
            effects = row[key] if key == 'sec_eff' else [row[key]]
            if len(effects) > 4:
                raise ValueError(f"rune {row['rune_id']}.{key}: trop de statistiques / too many stats")
            for effect in effects:
                for value in effect:
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                        raise ValueError(f"rune {row['rune_id']}.{key}: valeur invalide / invalid value")
                integer(effect[0], key)
    for row in artifacts:
        for key in ('type','attribute','occupied_id','unit_style','level'):
            integer(row[key], f"artifact {row['rid']}.{key}")
        if row['level'] > 15:
            raise ValueError('artifact level > 15')
        for effect in [row['pri_effect'], *row['sec_effects']]:
            if len(effect) < 2 or any(isinstance(v, bool) or not isinstance(v, (int,float)) for v in effect):
                raise ValueError(f"artifact {row['rid']}: invalid effect")
    for unit in data['unit_list']:
        integer(unit['unit_master_id'], 'unit_master_id', 1)
    for item in data['rune_craft_item_list']:
        for key in ('craft_type','craft_type_id','amount'):
            integer(item[key], f'craft.{key}')
