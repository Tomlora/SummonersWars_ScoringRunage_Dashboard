"""Visibility rules shared by leaderboard pages. Identity uses stable account IDs."""
import pandas as pd
import streamlit as st
from fonctions.journey import tr


@st.cache_data(ttl=300, show_spinner=False)
def report_versions():
    """Unknown/ambiguous legacy methods must not produce a rank delta."""
    from sqlalchemy import inspect, text
    from fonctions.gestion_bdd import connection
    with connection() as conn:
        if not inspect(conn).has_table('sw_imports'):
            return pd.DataFrame(columns=['id', 'date', 'scoring_version'])
        return pd.read_sql(text('''SELECT id_joueur AS id,date,
            CASE WHEN COUNT(DISTINCT scoring_version)=1 THEN MIN(scoring_version) END AS scoring_version
            FROM sw_imports GROUP BY id_joueur,date'''), conn)


def rank_movement(history, current, user_id, score='score', mode='latest', ascending=False,
                  check_versions=False):
    """Reconstruct the visible ranking at the viewer's previous distinct report day.

    New entrants count in today's rank. Privacy and guild scope must already have
    been applied to BOTH frames. No inference about intraday or deleted reports.
    """
    from fonctions.analysis import select_snapshots
    if history.empty or current.empty or user_id not in current.id.values:
        return None
    history = history.dropna(subset=[score]).copy()
    history['_day'] = pd.to_datetime(history.date, dayfirst=True, format='mixed', errors='coerce')
    dates = history.loc[history.id.eq(user_id), '_day'].dropna().drop_duplicates().sort_values()
    if len(dates) < 2:
        return None
    cutoff = dates.iloc[-2]
    before = select_snapshots(history[history._day.le(cutoff)], score, mode)
    if check_versions:
        methods = pd.concat([before.scoring_version, current.scoring_version])
        if methods.isna().any() or methods.nunique() != 1:
            return None
    old = before.set_index('id')[score].rank(method='min', ascending=ascending)
    new = current.set_index('id')[score].rank(method='min', ascending=ascending)
    if user_id not in old:
        return None
    return {'date': cutoff.strftime('%d/%m/%Y'), 'before': int(old[user_id]),
            'now': int(new[user_id]), 'delta': int(old[user_id]-new[user_id]),
            'players_before': len(before), 'players_now': len(current)}


def movement_caption(history, current, score='score', mode='latest', ascending=False, check_versions=False):
    change = rank_movement(history, current, st.session_state.id_joueur, score, mode, ascending, check_versions)
    if change is None:
        st.caption(tr('Évolution du rang indisponible : il faut deux dates de relevé et des données comparables.',
                      'Rank change unavailable: two report dates and comparable data are required.'))
        return
    delta = change['delta']
    st.metric(tr('Évolution de votre rang', 'Your rank change'), f"#{change['now']}",
              f"{delta:+d} "+('place' if abs(delta)==1 else 'places') if delta else tr('Rang inchangé', 'Rank unchanged'),
              delta_color='normal' if delta else 'off')
    st.caption(tr(
        f"Rang reconstitué au {change['date']} : #{change['before']} parmi {change['players_before']} joueurs ; {change['players_now']} aujourd’hui. Les nouveaux joueurs comptent. Visibilité et filtre de guilde actuels ; les mouvements d’une même journée ne sont pas disponibles.",
        f"Reconstructed rank on {change['date']}: #{change['before']} among {change['players_before']} players; {change['players_now']} today. New players count. Current visibility and guild filter apply; intraday changes are unavailable."))


def nearby_players(data, score, user_id, limit=6):
    """Nearest scores, with the viewer always present, even among many ties."""
    own = data[data.id.eq(user_id)]
    if own.empty:
        return data.iloc[:0].copy()
    others = data[~data.id.eq(user_id)].copy()
    others['_gap'] = (others[score]-own.iloc[0][score]).abs()
    others = others.sort_values(['_gap', 'Rang', 'id'], kind='stable').head(limit).drop(columns='_gap')
    return pd.concat([own, others]).sort_values(['Rang', 'id'], kind='stable')

def visible_players(data, user_id, guild_id):
    data=data.copy()
    own=data.id.eq(user_id)
    guild=data.guilde_id.eq(guild_id) & (guild_id not in (None,0))
    data=data[(data.visibility.ne(0)|own)&(data.visibility.ne(2)|guild|own)].copy()
    own=data.id.eq(user_id)
    guild=data.guilde_id.eq(guild_id) & (guild_id not in (None,0))
    data.loc[(data.visibility.eq(1)&~own)|(data.visibility.eq(4)&~guild&~own),'joueur']='***'
    return data

def ranking_table(data, columns, column_config=None):
    """Show every row on this page and identify the viewer by account ID."""
    page = data.reset_index(drop=True)
    own = page.id.eq(st.session_state.id_joueur)
    shown = page[columns].copy()
    label = ' (you)' if st.session_state.get('translations_selected') == 'English' else ' (vous)'
    shown.loc[own, 'joueur'] = shown.loc[own, 'joueur'] + label
    highlighted = shown.style.apply(
        lambda row: ['background-color: #173d62; color: #ffffff' if own.iloc[row.name] else ''] * len(row),
        axis=1,
    )
    config = {'joueur':st.column_config.TextColumn(tr('Joueur','Player')),
              'guilde':st.column_config.TextColumn(tr('Guilde','Guild')),
              'date':st.column_config.TextColumn(tr('Date du relevé','Report date')),
              'Rang':st.column_config.NumberColumn(tr('Rang','Rank'), format='%d'),
              'Écart':st.column_config.NumberColumn(tr('Écart avec vous', 'Gap from you'), format='%+.2f')}
    config.update(column_config or {})
    st.caption(tr('Une valeur vide est indisponible ; elle ne représente pas zéro.', 'An empty value is unavailable; it does not mean zero.'))
    st.dataframe(highlighted, hide_index=True, width='stretch', height='content', column_config=config)


def ranking_page(data, score, prefix, ascending=False):
    """Search only visible labels; preserve ranks in the full chosen scope."""
    data = data.reset_index(drop=True)
    size = st.selectbox(tr('Lignes par page','Rows per page'), [25,50,100], key=prefix+'size')
    own = data.index[data.id.eq(st.session_state.id_joueur)]
    if len(own):
        position = int(own[0])
        value = data.iloc[position]
        better = data[data[score].lt(value[score]) if ascending else data[score].gt(value[score])]
        gap = abs(value[score]-better.iloc[-1][score]) if not better.empty else None
        st.caption(tr('Votre rang','Your rank') + f" : #{int(value['Rang'])} / {len(data)} · " + tr('Score','Score') + f" : {value[score]:g}" +
                   ((' · '+tr('Écart au rang précédent','Gap to the previous rank')+f' : {gap:g}') if gap is not None else ''))
        def locate():
            st.session_state[prefix+'query'] = ''
            st.session_state[prefix+'page'] = position//size+1
        st.button(tr('Me retrouver','Find me'), key='action_'+prefix+'locate', on_click=locate)
        if st.toggle(tr('Joueurs proches de mon score', 'Players close to my score'), key=prefix+'nearby'):
            nearby = nearby_players(data, score, st.session_state.id_joueur)
            nearby['Écart'] = nearby[score]-value[score]
            st.caption(tr('Les six scores les plus proches du vôtre. Les rangs restent ceux du classement complet sélectionné.',
                          'The six closest scores to yours. Ranks remain those of the full selected leaderboard.'))
            return nearby
    else:
        st.caption(tr('Votre compte n’est pas classé pour ce critère.','Your account is not ranked for this metric.'))
    def reset_page():
        st.session_state[prefix+'page'] = 1
    query = st.text_input(tr('Rechercher un joueur','Find a player'), key=prefix+'query', on_change=reset_page)
    if query:
        data = data[data.joueur.astype(str).str.contains(query, case=False, regex=False)]
    pages = max(1,(len(data)+size-1)//size)
    st.session_state[prefix+'page'] = min(max(st.session_state.get(prefix+'page',1),1), pages)
    page = st.number_input('Page',1,pages,key=prefix+'page')
    st.caption(tr(f'{len(data)} joueurs · page {page}/{pages}',f'{len(data)} players · page {page}/{pages}'))
    if data.empty:
        st.info(tr('Aucun joueur visible ne correspond à la recherche.','No visible player matches the search.'))
    return data.iloc[(page-1)*size:page*size]


def show_ranking(data, score, columns=None, ascending=False, key_prefix='ui_ranking_', column_config=None, history=None, mode='latest'):
    data=visible_players(data,st.session_state.id_joueur,st.session_state.guildeid)
    guild_only = st.toggle(tr('Ma guilde uniquement','My guild only'),key=key_prefix+'guild')
    if guild_only:
        data=data[data.guilde_id.eq(st.session_state.guildeid)]
    data=data.dropna(subset=[score]).sort_values(score,ascending=ascending)
    if data.empty:
        st.info(tr('Aucun relevé disponible.','No snapshots available.'))
        return
    data['Rang']=data[score].rank(method='min',ascending=ascending).astype('int64')
    if history is not None:
        history = visible_players(history, st.session_state.id_joueur, st.session_state.guildeid)
        if guild_only:
            history = history[history.guilde_id.eq(st.session_state.guildeid)]
        movement_caption(history, data, score, mode, ascending)
    else:
        st.caption(tr('L’historique de ce classement n’est pas conservé : la variation de rang est indisponible.',
                      'This leaderboard has no retained history: rank changes are unavailable.'))
    shown=ranking_page(data,score,key_prefix,ascending)
    ranking_table(shown, ['Rang','joueur',*(columns or [score]),*(['Écart'] if 'Écart' in shown else []),'date','guilde'],column_config)
