from collections import defaultdict

import pandas as pd
import streamlit as st
from streamlit_lottie import st_lottie

from fonctions.visuel import load_lottieurl, css

try:
    # Chemin conseillé si gestion_bdd.py est dans le package fonctions/
    from fonctions.gestion_bdd import lire_bdd_perso
except ImportError:
    # Fallback utile si gestion_bdd.py est au même niveau que cette page
    from gestion_bdd import lire_bdd_perso


try:
    st.set_page_config(layout="wide")
except Exception:
    pass

css()

def format_update_content(content) -> str:
    """Convertit les retours à la ligne stockés en base en Markdown compatible Streamlit."""
    if content is None:
        return ""

    content = str(content)

    # Cas fréquent depuis PostgreSQL : les caractères sont stockés littéralement comme \n
    # au lieu d'être de vrais retours à la ligne.
    content = content.replace("\\r\\n", "\n")
    content = content.replace("\\n", "\n")
    content = content.replace("\r\n", "\n")

    # Dans st.info, un saut Markdown fiable s'écrit avec deux espaces avant le retour ligne.
    content = content.replace("\n\n", "  \n")
    content = content.replace("\n", "  \n")

    return content


@st.cache_data(ttl=300, show_spinner=False)
def load_updates() -> pd.DataFrame:
    """Charge les mises à jour depuis PostgreSQL via gestion_bdd.lire_bdd_perso.

    Attention : lire_bdd_perso transpose automatiquement le DataFrame.
    On le transpose donc une seconde fois pour retrouver une ligne par mise à jour.
    """
    query = """
        SELECT
            id,
            version_date,
            year,
            content,
            expanded
        FROM app_updates
        WHERE is_active = TRUE
        ORDER BY year DESC, version_date DESC, id DESC
    """

    df = lire_bdd_perso(query, index_col="id")

    # gestion_bdd.lire_bdd_perso fait déjà df.transpose().
    # Ici, on revient au format attendu par la page : 1 ligne = 1 update.
    df = df.transpose().reset_index()

    # Selon la version de pandas / le nom de l'index, la colonne peut s'appeler index ou id.
    if "index" in df.columns and "id" not in df.columns:
        df = df.rename(columns={"index": "id"})

    if not df.empty:
        df["version_date"] = pd.to_datetime(df["version_date"])
        df["year"] = df["year"].astype(int)
        df["expanded"] = df["expanded"].astype(bool)

    return df


st.subheader("Mise à jour")

col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
with col2:
    img = load_lottieurl("https://assets7.lottiefiles.com/private_files/lf30_rzhdjuoe.json")
    st_lottie(img, height=200, width=200)

try:
    updates_df = load_updates()
except Exception as exc:
    st.error("Impossible de charger les mises à jour depuis PostgreSQL.")
    st.exception(exc)
    st.stop()

if updates_df.empty:
    st.info("Aucune mise à jour à afficher.")
else:
    updates_by_year = defaultdict(list)

    for update in updates_df.to_dict("records"):
        updates_by_year[int(update["year"])].append(update)

    years = sorted(updates_by_year.keys(), reverse=True)
    tabs = st.tabs([str(year) for year in years])

    for tab, year in zip(tabs, years):
        with tab:
            for update in updates_by_year[year]:
                version_date = pd.to_datetime(update["version_date"]).strftime("%d/%m/%Y")
                with st.expander(
                    f"Version {version_date}",
                    expanded=bool(update.get("expanded", True)),
                ):
                    st.info(format_update_content(update["content"]))

st.caption("Made by Tomlora :sunglasses:")
