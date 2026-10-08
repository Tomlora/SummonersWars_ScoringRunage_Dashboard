"""Named defaults remain valid when database columns are reordered."""
from fonctions.access import require_user
from fonctions.gestion_bdd import lire_bdd_perso


def artifact_goals(user_id):
    require_user(user_id)
    defaults={name:10 for name in ('reduction','dmg_elem','crit_dmg','precision','soin','spd')}
    defaults.update({f'{name}_{stat}':True for name in tuple(defaults) for stat in ('hp','atk','def')})
    rows=lire_bdd_perso('SELECT * FROM sw_objectifs_arte WHERE id=:id',index_col='id',params={'id':int(user_id)}).T
    if not rows.empty:
        defaults.update({key:value for key,value in rows.iloc[0].items() if key in defaults and value is not None})
    return defaults
