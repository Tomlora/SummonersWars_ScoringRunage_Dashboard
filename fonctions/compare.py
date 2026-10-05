from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fonctions.gestion_bdd import lire_bdd_perso
from fonctions.visuel import THEME, apply_plotly_theme


@st.cache_data(ttl=300, show_spinner=False)
def comparison_population():
    # Filter history on the server and share the same population across metrics/guilds.
    return lire_bdd_perso('WITH ranked AS (\n        SELECT id_joueur,date,score_general,score_arte,score_spd,\n               ROW_NUMBER() OVER (PARTITION BY id_joueur\n                  ORDER BY substr(date,7,4)||substr(date,4,2)||substr(date,1,2) DESC,\n                           score_general DESC,score_arte DESC) AS position\n        FROM sw_score\n    ) SELECT u.id,u.joueur,u.guilde_id,s.date,s.score_general,s.score_arte,s.score_spd\n      FROM ranked s JOIN sw_user u ON u.id=s.id_joueur WHERE s.position=1',index_col=None).T


@st.cache_data(ttl="1h")
def comparaison(guilde_id, score="score_general"):
    """Return global and guild comparison indicators for a score."""
    data = comparison_population()
    def indicators(frame):
        frame = frame.set_index('id').copy()
        frame['rank'] = frame[score].rank(ascending=False, method='min')
        return (len(frame), int(round(frame[score].mean())) if len(frame) else 0,
                int(frame[score].max()) if len(frame) else 0, frame)
    size, average, best, general = indicators(data)
    gsize, gavg, gbest, guild = indicators(data[data.guilde_id == guilde_id])
    return size, average, best, gsize, gavg, gbest, general, guild


def score_percentile(df: pd.DataFrame, score: str, value: int) -> float:
    """Return the percentage of the population whose score is strictly lower."""
    values = pd.to_numeric(df.get(score, pd.Series(dtype=float)), errors="coerce").dropna()
    if values.empty:
        return 0.0
    return float((values < value).mean() * 100)


def comparaison_rune_graph(
    df: pd.DataFrame,
    name: str,
    score: str = "score_general",
    score_joueur: str = "score",
):
    """Create a readable score distribution with the current player highlighted."""
    player_score = int(st.session_state[score_joueur])
    values = pd.to_numeric(df.get(score, pd.Series(dtype=float)), errors="coerce").dropna()

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
