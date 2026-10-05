"""Visibility rules shared by leaderboard pages. Identity uses stable account IDs."""
import pandas as pd
import streamlit as st

def visible_players(data, user_id, guild_id):
    data=data.copy()
    own=data.id.eq(user_id)
    guild=data.guilde_id.eq(guild_id) & (guild_id not in (None,0))
    data=data[(data.visibility.ne(0)|own)&(data.visibility.ne(2)|guild|own)].copy()
    own=data.id.eq(user_id)
    guild=data.guilde_id.eq(guild_id) & (guild_id not in (None,0))
    data.loc[(data.visibility.eq(1)&~own)|(data.visibility.eq(4)&~guild&~own),'joueur']='***'
    return data

def show_ranking(data, score, columns=None, ascending=False):
    data=visible_players(data,st.session_state.id_joueur,st.session_state.guildeid)
    if st.toggle('Ma guilde uniquement / My guild only'):
        data=data[data.guilde_id.eq(st.session_state.guildeid)]
    data=data.dropna(subset=[score]).sort_values(score,ascending=ascending)
    if data.empty:
        st.info('Aucun relevé disponible / No snapshots available.')
        return
    data['Rang']=data[score].rank(method='min',ascending=ascending).astype('int64')
    size=st.selectbox('Lignes par page / Rows per page',[25,50,100])
    page=st.number_input('Page',1,max(1,(len(data)+size-1)//size),1)
    st.dataframe(data.iloc[(page-1)*size:page*size][['Rang','joueur',*(columns or [score]),'date','guilde']],hide_index=True,width='stretch')
