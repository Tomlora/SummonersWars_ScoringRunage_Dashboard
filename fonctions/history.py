"""Remove exact duplicate score reports without touching rune snapshots."""
from sqlalchemy import text
from fonctions.access import require_user
from fonctions.gestion_bdd import transaction


def deduplicate_scores(user_id):
    require_user(user_id)
    with transaction() as conn:
        # Physical row identifiers retain one existing row, including its metadata.
        locator = 'ctid' if conn.dialect.name == 'postgresql' else 'rowid'
        if conn.dialect.name not in ('postgresql', 'sqlite'):
            raise RuntimeError('Unsupported history database')
        result = conn.execute(text(f'''
            DELETE FROM sw_score WHERE {locator} IN (
                SELECT location FROM (
                    SELECT {locator} AS location,
                           ROW_NUMBER() OVER (
                               PARTITION BY id_joueur,date,score_general,score_spd,score_arte,score_qual
                               ORDER BY {locator}
                           ) AS occurrence
                    FROM sw_score WHERE id_joueur=:id
                ) AS duplicates WHERE occurrence>1
            )
        '''), {'id': int(user_id)})
        return result.rowcount
