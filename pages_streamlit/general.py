import pandas as pd
import numpy as np
import streamlit as st


def general_page():
    try:
        tcd_column, score_column = st.columns(2)
            
        with tcd_column:
            st.dataframe(st.session_state.tcd)
            
        with score_column:
            st.metric('Score', st.session_state['score'])
    
    except:
        st.subheader('Erreur')
        st.write('Pas de JSON chargé')