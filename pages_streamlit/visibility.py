
import streamlit as st
from fonctions.gestion_bdd import requete_perso_bdd
from streamlit_extras.switch_page_button import switch_page

from st_pages import add_indentation
from fonctions.visuel import css
css()

add_indentation()


def visibility():
    if 'pseudo' in st.session_state:  # si on a le pseudo du joueur, on l'affiche.
        # slider avec, par défaut, la value dans la bdd
        slider_visibility = st.radio(st.session_state.langue['visibility_ladder'], [
                                        st.session_state.langue['non-visible'],
                                        st.session_state.langue['caché'],
                                        st.session_state.langue['visible_guilde'],
                                        st.session_state.langue['visible_all'],
                                        st.session_state.langue['caché_mais_visible']], 
                                     index=st.session_state.visibility,
                                     help=st.session_state.langue['visibility_ladder_help'])
        dict_visibility = {st.session_state.langue['non-visible']: 0,
                            st.session_state.langue['caché']: 1,
                            st.session_state.langue['visible_guilde']: 2,
                            st.session_state.langue['visible_all']: 3,
                            st.session_state.langue['caché_mais_visible']: 4}
        # on enregistre si changement
        requete_perso_bdd('''UPDATE sw_user SET visibility = :visibility where joueur = :joueur''', {'visibility': dict_visibility[slider_visibility],
                                                                                                        'joueur': st.session_state["pseudo"]})
        
        st.session_state.visibility = dict_visibility[slider_visibility]

        

if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Visibilité du compte')
        visibility()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')
    
    
st.caption('Made by Tomlora')