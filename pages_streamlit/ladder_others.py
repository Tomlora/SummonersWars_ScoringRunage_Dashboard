from fonctions.gestion_bdd import lire_bdd_perso, cleaning_only_guilde
import pandas as pd
import streamlit as st
from datetime import timedelta
from streamlit_extras.button_selector import button_selector


from fonctions.visuel import css
css()



dict_type = {st.session_state.langue["arene"] : 'arene',
             'World Boss' : 'WB'}
    

dict_list = list(dict_type.keys())



def to_dataframe_safe(result) -> pd.DataFrame:
    """
    Convertit divers formats (DataFrame, list[dict], dict[str,dict], dict[str,list], list[tuple], etc.)
    en pandas.DataFrame sans générer de doublons de colonnes liés à des clés "dynamiques" (ex: pseudos).
    """
    if isinstance(result, pd.DataFrame):
        df = result.copy()
        return df

    # list[...] ------------------------------------------------------
    if isinstance(result, list):
        if not result:
            return pd.DataFrame()
        # list de dicts (cas le plus propre)
        if isinstance(result[0], dict):
            return pd.DataFrame.from_records(result)
        # list de Row/tuple -> DataFrame tabulaire sans noms
        return pd.DataFrame(result)

    # dict[...] ------------------------------------------------------
    if isinstance(result, dict):
        # dict de dicts -> on prend les valeurs comme lignes
        # (les clés externes ne deviennent PAS des noms de colonnes)
        if all(isinstance(v, dict) for v in result.values()):
            df = pd.DataFrame.from_dict(result, orient="index").reset_index(drop=True)
            return df
        # dict de listes -> on prend les valeurs comme lignes si longueurs homogènes
        if all(isinstance(v, (list, tuple)) for v in result.values()):
            # On essaie d'interpréter comme une liste d'objets (lignes),
            # pour éviter que les clés (souvent des pseudos) deviennent colonnes.
            values = list(result.values())
            try:
                # si ça ressemble à list[dict] aplatie dans un dict de colonnes
                lengths = {len(v) for v in values}
                if len(lengths) == 1:
                    # reformer une liste de lignes
                    rows = [dict(zip(result.keys(), row_vals)) for row_vals in zip(*values)]
                    return pd.DataFrame.from_records(rows)
            except Exception:
                pass
            # fallback: au pire, on empile en lignes
            return pd.DataFrame({"key": list(result.keys()), "value": list(result.values())})
        # un simple dict -> une seule ligne
        return pd.DataFrame([result])

    # fallback ultime ------------------------------------------------
    try:
        return pd.DataFrame(result)
    except Exception:
        return pd.DataFrame()


def _enforce_columns(df: pd.DataFrame, expected_cols: list) -> pd.DataFrame:
    """Garde/ordonne uniquement les colonnes attendues si elles existent."""
    keep = [c for c in expected_cols if c in df.columns]
    if not keep:
        return df  # on laisse tel quel si rien ne correspond
    return df[keep]


def classement():
    # Bandeau d'info
    st.info(f'**Note** : {st.session_state.langue["update_ladder"]}', icon="ℹ️")
    if st.session_state.visibility == 0:
        st.warning(st.session_state.langue['no_visibility'], icon="ℹ️")

    # Le checkbox doit être lu hors cache pour éviter clé de cache différente à chaque clic
    filtre_guilde_checked = st.checkbox(st.session_state.langue['filter_guilde'])

    @st.cache_data(ttl=timedelta(minutes=10),
                   show_spinner=st.session_state.langue["loading_data"])
    def load_data_ladder(classement_type: str, pseudo: str, guilde: str, filter_guilde: bool):
        if classement_type == "arene":
            query = """
            WITH data AS (
              SELECT
                  u.id,
                  u.joueur,
                  u.visibility,
                  u.guilde_id,
                  to_date(p.date, 'DD/MM/YYYY')::date AS date_,
                  p.win,
                  p.lose,
                  (SELECT g.guilde FROM sw_guilde g WHERE g.guilde_id = u.guilde_id) AS guilde
              FROM sw_user u
              JOIN sw_pvp  p ON u.id = p.id_joueur
              WHERE u.visibility <> 0
            ),
            agg AS (
              SELECT
                  joueur,
                  guilde,
                  MAX(visibility) AS visibility,
                  MAX(date_)      AS date_,
                  MAX(win)        AS win,
                  MAX(lose)       AS lose,
                  ROUND( (MAX(win)::numeric / NULLIF(MAX(win)+MAX(lose),0)) * 100, 1) AS score
              FROM data
              GROUP BY joueur, guilde
            ),
            anonym AS (
              SELECT
                CASE
                  WHEN visibility = 1 AND joueur <> :pseudo THEN '***'
                  WHEN visibility = 4 AND joueur <> :pseudo AND guilde <> :guilde THEN '***'
                  ELSE joueur
                END AS joueur,
                score,
                to_char(date_, 'DD/MM/YYYY') AS date,
                guilde
              FROM agg
            ),
            filtered AS (
              SELECT *
              FROM anonym
              WHERE (NOT :filter_guilde) OR (guilde = :guilde)
            )
            SELECT joueur, score, date, guilde
            FROM filtered
            ORDER BY score DESC;
            """
            expected_cols = ["joueur", "score", "date", "guilde"]
        else:  # classement WB
            query = """
            WITH data AS (
              SELECT
                  u.id,
                  u.joueur,
                  u.visibility,
                  u.guilde_id,
                  to_date(w.date, 'DD/MM/YYYY')::date AS date_wb,
                  w.rank,
                  w.damage AS dmg,
                  (SELECT g.guilde FROM sw_guilde g WHERE g.guilde_id = u.guilde_id) AS guilde
              FROM sw_user u
              JOIN sw_wb   w ON u.id = w.id_joueur
              WHERE u.visibility <> 0
            ),
            agg AS (
              SELECT
                  joueur,
                  guilde,
                  MIN(rank)        AS meilleur_rank,
                  MAX(dmg)         AS dmg,
                  MAX(date_wb)     AS date_,
                  MAX(visibility)  AS visibility
              FROM data
              GROUP BY joueur, guilde
            ),
            anonym AS (
              SELECT
                CASE
                  WHEN visibility = 1 AND joueur <> :pseudo THEN '***'
                  WHEN visibility = 4 AND joueur <> :pseudo AND guilde <> :guilde THEN '***'
                  ELSE joueur
                END AS joueur,
                meilleur_rank,
                dmg,
                to_char(date_, 'DD/MM/YYYY') AS date,
                guilde
              FROM agg
            ),
            filtered AS (
              SELECT *
              FROM anonym
              WHERE (NOT :filter_guilde) OR (guilde = :guilde)
            )
            SELECT joueur, meilleur_rank, date, guilde, dmg
            FROM filtered
            ORDER BY meilleur_rank ASC;
            """
            expected_cols = ["joueur", "meilleur_rank", "date", "guilde", "dmg"]

        params = {
            "pseudo": pseudo,
            "guilde": guilde,
            "filter_guilde": bool(filter_guilde),
        }

        raw = lire_bdd_perso(query, params=params)
        df = to_dataframe_safe(raw)
        # Sélection/ordre des colonnes attendues (évite toute colonne "parasite")
        df = _enforce_columns(df, expected_cols)
        return df

    # Choix du classement (variables externes supposées définies: button_selector, dict_type, dict_list)
    choice_radio = button_selector(dict_type.keys())
    classement_type = dict_type[dict_list[choice_radio]]

    # Chargement
    data = load_data_ladder(
        classement_type,
        st.session_state['pseudo'],
        st.session_state['guilde'],
        filtre_guilde_checked
    ).T


    if data is None or data.empty:
        st.warning(st.session_state.langue['no_data'])
    else:
        height_dataframe = 70 * data.shape[0]
        st.dataframe(data, height=height_dataframe, use_container_width=True)

        

    


if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Classement Scoring')
        classement()
    
    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")
    
    
st.caption('Made by Tomlora :sunglasses:')