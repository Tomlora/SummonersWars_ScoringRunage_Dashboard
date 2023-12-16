import requests
import streamlit as st
from streamlit_extras.app_logo import add_logo


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
        
        
    # st.markdown(
    #     """
    #     <style>
    #         [data-testid="stSidebarNav"] {
    #             background-image: url(https://i.imgur.com/AUwdzno.png);
    #             background-repeat: no-repeat;
    #             padding-top: 65px;
    #             background-position: 100px 20px;
    #         }
    #         [data-testid="stSidebarNav"]::before {
    #             margin-left: 20px;
    #             margin-bottom: 100px;
    #             font-size: 30px;
    #             position: relative;
    #             top: 100px;
    #         }
            
    #         [data-testid="stSidebarNav"] >ul {
    #         padding-top: 0;
    #         margin-top: 6rem; \\ space for logo 
    #         }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    # )
        
       

@st.cache_data
def icon(emoji:str):
    """Montre une emoji en icone de page
    
    Args:
        emoji (str): emoji à afficher, comme :":balloon:" """
        
    st.write(
        f'<span style="font-size: 50px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True
    )
    
    
def load_logo():
    # https://www.canva.com/design/DAF2h9-cIVM/uH7VzR-ivEtLeOx_okkOUA/view?utm_content=DAF2h9-cIVM&utm_campaign=designshare&utm_medium=link&utm_source=publishsharelink&mode=preview
    # logo = st.image('assets/logo.png')
    st.markdown('''<center><img src="https://i.imgur.com/AUwdzno.png" /></center>''', unsafe_allow_html=True)
    # return logo


