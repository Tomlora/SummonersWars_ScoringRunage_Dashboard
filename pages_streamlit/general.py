import pandas as pd
import numpy as np
import streamlit as st


def general_page():
    try:
        tcd_column, score_column = st.columns(2)
            
        with tcd_column:
            st.dataframe(st.session_state.tcd[[100, 110, 120]])
            
        with score_column:
            st.metric('Score', st.session_state['score'])
            st.metric('Date', st.session_state.tcd.iloc[0]['date'])
    
    except:
        st.subheader('Erreur')
        st.write('Pas de JSON chargé')