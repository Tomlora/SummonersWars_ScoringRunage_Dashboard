
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
        slider_visibility = st.radio('Visibilité du compte Classement', [
                                        'Non-visible', 'Caché', 'Visible à ma guilde',
                                        'Visible à tous',
                                        'Caché en public mais visible à ma guilde'], index=st.session_state.visibility)
        dict_visibility = {'Non-visible': 0,
                            'Caché': 1,
                            'Visible à ma guilde': 2,
                            'Visible à tous': 3,
                            'Caché en public mais visible à ma guilde': 4}
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