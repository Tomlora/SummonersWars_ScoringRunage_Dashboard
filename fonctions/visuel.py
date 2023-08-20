import requests
import streamlit as st


@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

@st.cache_resource
def css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
        
        
@st.cache_data
def icon(emoji:str):
    """Montre une emoji en icone de page
    
    Args:
        emoji (str): emoji à afficher, comme :":balloon:" """
        
    st.write(
        f'<span style="font-size: 50px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True
    )