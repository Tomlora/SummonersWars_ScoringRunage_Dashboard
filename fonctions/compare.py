from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fonctions.gestion_bdd import lire_bdd_perso
from fonctions.visuel import THEME, apply_plotly_theme


@st.cache_data(ttl="1h")
def comparaison(guilde_id, score="score_general"):
    """Return global and guild comparison indicators for a score."""
    df_actuel = lire_bdd_perso(
        "SELECT * from sw_user, sw_score WHERE sw_user.id = sw_score.id_joueur"
    )
    df_actuel = df_actuel.transpose()
    df_actuel.reset_index(inplace=True)
    df_actuel.drop(["id"], axis=1, inplace=True)
    df_actuel = df_actuel[df_actuel[score] != 0]

    df_max = df_actuel.groupby("joueur").max()
    df_max["rank"] = df_max[score].rank(ascending=False, method="min")

    size_general = len(df_max)
    avg_score_general = int(round(df_max[score].mean(), 0))
    max_general = int(df_max[score].max())

    df_guilde = df_actuel[df_actuel["guilde_id"] == guilde_id]
    df_guilde_max = df_guilde.groupby("joueur").max()
    size_guilde = len(df_guilde_max)

    if df_guilde_max.empty:
        avg_score_guilde = 0
        max_guilde = 0
        df_guilde_max["rank"] = pd.Series(dtype="float64")
    else:
        avg_score_guilde = int(round(df_guilde_max[score].mean(), 0))
        max_guilde = int(df_guilde_max[score].max())
        df_guilde_max["rank"] = df_guilde_max[score].rank(
            ascending=False, method="min"
        )

    return (
        size_general,
        avg_score_general,
        max_general,
        size_guilde,
        avg_score_guilde,
        max_guilde,
        df_max,
        df_guilde_max,
    )


def score_percentile(df: pd.DataFrame, score: str, value: int) -> float:
    """Return the percentage of the population whose score is lower or equal."""
    values = pd.to_numeric(df.get(score), errors="coerce").dropna()
    if values.empty:
        return 0.0
    return float((values <= value).mean() * 100)


def comparaison_rune_graph(
    df: pd.DataFrame,
    name: str,
    score: str = "score_general",
    score_joueur: str = "score",
):
    """Create a readable score distribution with the current player highlighted."""
    player_score = int(st.session_state[score_joueur])
    values = pd.to_numeric(df.get(score), errors="coerce").dropna()

    fig = go.Figure()
    fig.add_trace(
        go.Box(
            x=[name] * len(values),
            y=values,
            name=name,
            boxmean=True,
            boxpoints="outliers",
            fillcolor="rgba(73, 164, 255, 0.20)",
            line={"color": THEME["primary"], "width": 2},
            marker={"color": THEME["primary"], "opacity": 0.55},
            hovertemplate="Score %{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[name],
            y=[player_score],
            name=st.session_state.pseudo,
            mode="markers+text",
            text=[f"{player_score:,}".replace(",", " ")],
            textposition="top center",
            marker={
                "size": 16,
                "color": THEME["gold"],
                "symbol": "diamond",
                "line": {"color": "#ffffff", "width": 1.5},
            },
            hovertemplate=(
                f"{st.session_state.pseudo}<br>Score {player_score:,}<extra></extra>"
            ),
        )
    )

    percentile = score_percentile(df, score, player_score)
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"Meilleur que {percentile:.0f} % des joueurs",
        showarrow=False,
        align="left",
        font={"color": THEME["muted"], "size": 13},
        bgcolor="rgba(16, 31, 51, 0.82)",
        bordercolor="rgba(191, 211, 236, 0.12)",
        borderpad=8,
    )

    fig.update_xaxes(title=None, showgrid=False)
    fig.update_yaxes(title="Score", rangemode="tozero")
    return apply_plotly_theme(fig, height=430)
