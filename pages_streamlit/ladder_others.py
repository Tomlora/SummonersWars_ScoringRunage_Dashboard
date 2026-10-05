from fonctions.access import require_saved_page
require_saved_page()
import streamlit as st
from fonctions.gestion_bdd import lire_bdd_perso
from fonctions.analysis import select_snapshots
from fonctions.leaderboards import show_ranking
from fonctions.visuel import css,page_header

@st.cache_data(ttl=300)
def load_data(kind):
    table,fields=('sw_pvp','d.win,d.lose') if kind=='Arena' else ('sw_wb','d.rank,d.damage')
    return lire_bdd_perso(f'SELECT u.id,u.joueur,u.visibility,u.guilde_id,g.guilde,d.date,{fields} FROM {table} d JOIN sw_user u ON u.id=d.id_joueur LEFT JOIN sw_guilde g ON g.guilde_id=u.guilde_id',index_col=None).T

css()
page_header('PvP · World Boss','Dernier relevé complet / Latest complete snapshot',icon='🏆')
kind=st.radio('Classement / Ranking',['Arena','World Boss'],horizontal=True)
data=load_data(kind)
if kind=='Arena':
    data['score']=100*data.win/data.eval('win+lose').replace(0,float('nan'))
    score='score'; columns=['win','lose','score']
else:
    score='damage'; columns=['rank','damage']
data=select_snapshots(data,score,'latest')
show_ranking(data,score,columns)
