"""Public community totals from the same database view as the original home page."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from fonctions.gestion_bdd import lire_bdd_perso


@st.cache_data(ttl=timedelta(minutes=30))
def community_counts():
    # PostgreSQL connections already use the sw search path.
    counts = lire_bdd_perso('SELECT * FROM count_rows', index_col='table').T
    totals = tuple(int(counts.loc[table].iloc[0]) for table in
                   ('sw_user', 'sw_guilde', 'sw_score'))
    refreshed_at = datetime.now(ZoneInfo('Europe/Paris')).strftime('%H:%M')
    return (*totals, refreshed_at)
