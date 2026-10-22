from __future__ import annotations

from fonctions.access import require_saved_page
require_saved_page()

import streamlit as st

from fonctions.compare import comparaison, comparaison_rune_graph, score_percentile
from fonctions.visuel import css, page_header, section_header
from fonctions.journey import tr


css()


def _safe_rank(df, player: str):
    try:
        return int(df.loc[player]["rank"])
    except (KeyError, TypeError, ValueError):
        return None


def _render_scope(
    *,
    scope_name: str,
    player_score: int,
    score_column: str,
    session_score_key: str,
    population_size: int,
    average_score: int,
    best_score: int,
    population_df,
):
    rank = _safe_rank(population_df, st.session_state["id_joueur"])
    percentile = score_percentile(population_df, score_column, player_score)

    col_players, col_average, col_best, col_rank = st.columns(4)
    col_players.metric(st.session_state.langue["joueurs"], population_size)
    col_average.metric(
        st.session_state.langue["Avg_score"],
        average_score,
        player_score - average_score,
    )
    col_best.metric(
        st.session_state.langue["Best_score"],
        best_score,
        player_score - best_score,
    )
    col_rank.metric(
        st.session_state.langue["Classement"],
        f"#{rank}" if rank is not None else tr('Non classé','Unranked'),
        (f"{percentile:.0f} % "+tr('de scores inférieurs','of scores are lower')) if population_size else None,
        delta_color="off",
    )

    fig = comparaison_rune_graph(
        population_df,
        scope_name,
        score=score_column,
        score_joueur=session_score_key,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_comparison_section(
    *,
    title: str,
    subtitle: str,
    icon: str,
    player_score: int,
    score_column: str,
    session_score_key: str,
    global_data,
    guild_data,
):
    section_header(f"{icon} {title}", subtitle)

    scope_general = tr('Général','Global')
    guild_name = st.session_state.get("guilde") or tr('Ma guilde','My guild')
    selected_scope = st.segmented_control(
        tr('Périmètre de comparaison','Comparison scope'),
        options=['global','guild'],
        format_func=lambda code:scope_general if code=='global' else guild_name,
        default='global',
        key=f"ui_scope_{score_column}",
        label_visibility="collapsed",
    )

    if selected_scope == 'guild':
        size, average, best, df = guild_data
        _render_scope(
            scope_name=guild_name,
            player_score=player_score,
            score_column=score_column,
            session_score_key=session_score_key,
            population_size=size,
            average_score=average,
            best_score=best,
            population_df=df,
        )
    else:
        size, average, best, df = global_data
        _render_scope(
            scope_name=scope_general,
            player_score=player_score,
            score_column=score_column,
            session_score_key=session_score_key,
            population_size=size,
            average_score=average,
            best_score=best,
            population_df=df,
        )


def comparaison_entre_joueurs():
    (
        size_general,
        avg_score_general,
        max_general,
        size_guilde,
        avg_score_guilde,
        max_guilde,
        df_max,
        df_guilde,
    ) = comparaison(st.session_state["guildeid"])

    (
        size_general_arte,
        avg_arte,
        max_arte,
        size_arte_guilde,
        avg_score_arte_guilde,
        max_arte_guilde,
        df_arte_max,
        df_arte_guilde,
    ) = comparaison(st.session_state["guildeid"], "score_arte")

    _render_comparison_section(
        title=f'Runes · {st.session_state["score"]:,} pts'.replace(",", " "),
        subtitle=tr('Situez votre compte par rapport à l’ensemble des joueurs ou à votre guilde.','Compare your account with all players or your guild.'),
        icon="◈",
        player_score=int(st.session_state["score"]),
        score_column="score_general",
        session_score_key="score",
        global_data=(size_general, avg_score_general, max_general, df_max),
        guild_data=(size_guilde, avg_score_guilde, max_guilde, df_guilde),
    )

    _render_comparison_section(
        title=(tr('Artéfacts','Artifacts')+f' · {st.session_state["score_arte"]:,} pts').replace(",", " "),
        subtitle=tr('Comparez la qualité globale de vos artéfacts avec les mêmes repères.','Compare your overall artifact quality using the same benchmarks.'),
        icon="◆",
        player_score=int(st.session_state["score_arte"]),
        score_column="score_arte",
        session_score_key="score_arte",
        global_data=(size_general_arte, avg_arte, max_arte, df_arte_max),
        guild_data=(
            size_arte_guilde,
            avg_score_arte_guilde,
            max_arte_guilde,
            df_arte_guilde,
        ),
    )


if st.session_state.get("submitted"):
    page_header(
        tr('Comparaison','Comparison'),
        tr('Comprenez votre position, l’écart à la moyenne et la proportion de scores inférieurs.','See your rank, the gap to the average, and the proportion of lower scores.'),
        icon="⚖️",
        eyebrow="Scoring",
    )
    comparaison_entre_joueurs()
else:
    st.switch_page("pages_streamlit/upload.py")

st.caption("Made by Tomlora 😎")
