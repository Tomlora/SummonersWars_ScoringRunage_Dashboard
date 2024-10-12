from fonctions.gestion_bdd import lire_bdd_perso, cleaning_only_guilde
import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from params.coef import coef_set, coef_set_spd
from datetime import timedelta
from streamlit_extras.button_selector import button_selector
import json 
from streamlit_timeline import timeline

### https://github.com/innerdoc/streamlit-timeline?tab=readme-ov-file

### https://timeline.knightlab.com/docs/json-format.html

from fonctions.visuel import css
css()


def timeline_page():

    df_mobs = st.session_state.df_mobs_name_all

    options = ['LD 5nat', '5nat']
    button_select = button_selector(options)

    if button_select == 0:
        df_filter = df_mobs[df_mobs['element_number'].isin([3, 4])]
        df_filter = df_filter[df_filter['natural_stars'] == 5]
        height = 1000

    elif button_select == 1:
        df_filter = df_mobs[df_mobs['natural_stars'] == 5]
        height = 1000


    df_filter['Date_invocation'] = pd.to_datetime(df_filter['Date_invocation'])
    df_filter['Jour'] = df_filter['Date_invocation'].dt.day
    df_filter['Mois'] = df_filter['Date_invocation'].dt.month
    df_filter['Année'] = df_filter['Date_invocation'].dt.year

    # Fonction pour créer la structure d'événement
    def create_event(row):

        event = {
                            # "media": {
                            #     "url": row["url"],
                            #     "caption": f"{row['caption']} (<a target=\"_blank\" href='#'>credits</a>)"
                            # },
                            "start_date": {
                                "year": str(row["Année"]),
                                "month": str(row["Mois"]),
                            },
                            "text": {
                                "headline": row["name"],
                                "text": f'Invoqué le {str(row["Date_invocation"])} <br>  Element : {row["element"]}'
                            },
                            "background" : {
                                "url" : row["url"]
                            }
                        }
                        
                        # Ajouter le jour s'il est disponible
        if pd.notna(row["Jour"]):
            event["start_date"]["day"] = str(row["Jour"])
                        
        return event
                
    events = df_filter.apply(create_event, axis=1).tolist()

    # Créer le dictionnaire final
    timeline_dict = {"events":  events}

    # Convertir en JSON
    timeline_json = json.dumps(timeline_dict, indent=2)

    timeline(timeline_json, height=height)
    




if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Historique Invocation')
        timeline_page()
    
    else:
        st.switch_page("pages_streamlit/upload.py")

else:
    st.switch_page("pages_streamlit/upload.py")
    
    
st.caption('Made by Tomlora :sunglasses:')