
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from fonctions.gestion_bdd import requete_perso_bdd
from fonctions.visuel import css
from st_pages import add_indentation

try:
    st.set_page_config(layout='wide')
except:
    pass


css()
add_indentation()

st.title("Feedback")
add_vertical_space(1)
st.markdown("Si vous avez des suggestions ou des bugs à signaler, veuillez les écrire ici :")

st.info("Je ne suis pas developpeur web, l'application est réalisée avec mes faibles compétences dans le domaine :) ")


type = st.selectbox("Type de feedback", ["Bug", "Suggestion", "Autre"])
feedback = st.text_area("Écrivez votre feedback ici")


if st.button("Envoyer"):
    requete_perso_bdd('''INSERT INTO public.sw_feedback(
                        type, text)
                        VALUES (:type, :text); ''', 
                    dict_params={'type':type, 'text':feedback})
    
    st.success("Merci pour votre feedback!")
        
        

st.caption('Made by Tomlora :sunglasses:')
