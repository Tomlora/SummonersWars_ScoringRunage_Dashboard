"""Visibility rules shared by leaderboard pages. Identity uses stable account IDs."""
import pandas as pd
import streamlit as st
from fonctions.journey import tr

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
              'Rang':st.column_config.NumberColumn(tr('Rang','Rank'), format='%d')}
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


def show_ranking(data, score, columns=None, ascending=False, key_prefix='ui_ranking_', column_config=None):
    data=visible_players(data,st.session_state.id_joueur,st.session_state.guildeid)
    if st.toggle(tr('Ma guilde uniquement','My guild only'),key=key_prefix+'guild'):
        data=data[data.guilde_id.eq(st.session_state.guildeid)]
    data=data.dropna(subset=[score]).sort_values(score,ascending=ascending)
    if data.empty:
        st.info(tr('Aucun relevé disponible.','No snapshots available.'))
        return
    data['Rang']=data[score].rank(method='min',ascending=ascending).astype('int64')
    shown=ranking_page(data,score,key_prefix,ascending)
    ranking_table(shown, ['Rang','joueur',*(columns or [score]),'date','guilde'],column_config)
