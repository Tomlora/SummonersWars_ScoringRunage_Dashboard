from fonctions.gestion_bdd import lire_bdd_perso
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly_express as px
from datetime import datetime, timedelta
from fonctions.visualisation import filter_dataframe
from streamlit_extras.switch_page_button import switch_page
from st_pages import add_indentation
from fonctions.visuel import css


css()

add_indentation()



def cleaning_only_guilde(x):
    x['private'] = 0
    if x['visibility'] == 2:
        if x['guilde'] != st.session_state.guilde:
            x['private'] = 1

    return x

def timelapse_graph(dataset):
        # make list of continents
    weeks = dataset['semaine'].sort_values().unique().tolist()
    
    min_week = min(weeks)
    max_week = max(weeks)
    
    min_points = min(dataset['score_general'])
    max_points = max(dataset['score_general'])
    
    continents = []
    for continent in dataset["joueur"]:
        if continent not in continents:
            continents.append(continent)
    # make figure
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }

    # fill in most of layout
    fig_dict["layout"]["xaxis"] = {"range": [min_week-3, max_week+3], "title": "Semaine"}
    fig_dict["layout"]["yaxis"] = {"title": "Points", "range": [min_points-50,max_points+50]}
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": False},
                                    "fromcurrent": True, "transition": {"duration": 300,
                                                                        "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Semaine:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    # make data
    week = weeks[0]
    for continent in continents:
        dataset_by_week = dataset[dataset["semaine"] == week]
        dataset_by_week_and_cont = dataset_by_week[
            dataset_by_week["joueur"] == continent]

        data_dict = {
            "x": list(dataset_by_week_and_cont["semaine"]),
            "y": list(dataset_by_week_and_cont["score_general"]),
            "mode": "markers+text",
            "text": list(dataset_by_week_and_cont["joueur"]),
            "name": continent
        }
        fig_dict["data"].append(data_dict)

    # make frames
    for week in weeks:
        frame = {"data": [], "name": str(week)}
        for continent in continents:
            dataset_by_week = dataset[dataset["semaine"] == int(week)]
            dataset_by_week_and_cont = dataset_by_week[
                dataset_by_week["joueur"] == continent]

            data_dict = {
                "x": list(dataset_by_week_and_cont["semaine"]),
                "y": list(dataset_by_week_and_cont["score_general"]),
                "mode": "markers+text",
                "text": list(dataset_by_week_and_cont["joueur"]),
                "name": continent
            }
            frame["data"].append(data_dict)

        fig_dict["frames"].append(frame)
        slider_step = {"args": [
            [week],
            {"frame": {"duration": 300, "redraw": False},
            "mode": "immediate",
            "transition": {"duration": 300}}
        ],
            "label": week,
            "method": "animate"}
        sliders_dict["steps"].append(slider_step)


    fig_dict["layout"]["sliders"] = [sliders_dict]

    fig = go.Figure(fig_dict)
    fig.update_layout(height=800, width=1000, showlegend=False)
    
    return fig

def timelapse_joueur():
    # On lit la BDD
    # on récupère la data
    
    st.info('Mise à jour 1 fois par jour', icon="ℹ️")
    @st.cache_data(ttl=timedelta(days=1))
    def recup_data():
        dataset = lire_bdd_perso('''SELECT sw_user.id, sw_user.joueur, sw_user.visibility, sw_user.guilde_id, sw_user.joueur_id, sw_score.date, sw_score.score_general, (SELECT guilde from sw_guilde where sw_guilde.guilde_id = sw_user.guilde_id) as guilde
                            FROM sw_user
                            INNER JOIN sw_score ON sw_user.id = sw_score.id_joueur
                            where sw_user.visibility != 0''').transpose().reset_index()

        # on transpose la date au format date
        dataset['date'] = pd.to_datetime(dataset['date'], format="%d/%m/%Y")
        
        return dataset
    
    dataset = recup_data()
    
    st.warning('Experimental')
    
    filtre_guilde = st.checkbox('Filtrer sur ma guilde')
    
    
    dataset = dataset.apply(cleaning_only_guilde, axis=1)
    dataset = dataset[dataset['private'] == 0]
    dataset['joueur'] = dataset.apply(
        lambda x: "***" if x['visibility'] == 1 else x['joueur'], axis=1)
    
    if filtre_guilde:
        dataset = dataset[dataset['guilde'] == st.session_state.guilde]
        
        
    dataset['semaine'] = dataset['date'].apply(lambda x : datetime.date(x).isocalendar().week)
    dataset['year'] = dataset['date'].apply(lambda x : datetime.date(x).isocalendar().year)
    
    annee = st.radio('Année', dataset['year'].unique().tolist(), horizontal=True)
    
    dataset_annee = dataset[dataset['year'] == annee]
    
    dataset_final = dataset_annee[['joueur', 'score_general', 'guilde', 'semaine']]
    
    dataset_final = filter_dataframe(dataset_final, 'timelapse', 10, 'int')
    
    dataset_final1 = dataset_final.groupby(['joueur', 'semaine']).agg(
        {'score_general': 'max'}).reset_index()
    
    dataset_final2 = dataset_final.groupby(['joueur', 'semaine', 'guilde']).agg(
        {'score_general': 'max'}).reset_index()
    
    
    
    try:
        fig = timelapse_graph(dataset_final1)

        st.write(fig)
         
        # fig2 = px.scatter(dataset_final2, x='semaine', y ='score_general', color='joueur',
        #                  animation_frame='semaine', hover_name='guilde',
        #                  text='joueur',
        #                  range_x = [dataset_final2['semaine'].min()-1, dataset_final2['semaine'].max()+1],
        #                  range_y=[dataset_final2['score_general'].min(), dataset_final2['score_general'].max()])
            
        # fig2.update_layout(height=800, width=1000, showlegend=False)
            
        # st.plotly_chart(fig2)
            
    except ValueError:
        st.warning('Tu dois au moins selectionner un joueur')
        
    # data = Data()
    
    # data.add_data_frame(dataset_final1)
    
    # story = Story(data=data)
    
    # story.set_size(750, 450)
    
    # for semaine in dataset_final1['semaine'].unique():
    #     slide = Slide(
    #         Step(
    #             Style({'backgroundColor' : '#03152A'}),
    #             data.filter("record.semaine <= {}".format(semaine)),
    #             Config({'color' : 'joueur', 'x' : 'semaine', 'y' : 'score_general', "geometry" : "circle"}),
    #         ))
        
    #     story.add_slide(slide)
    # # joueur / semaine / score_general
   
    # html(story._repr_html_(), width=750, height=450)
    
    
        

if 'submitted' in st.session_state:
    if st.session_state.submitted:    
        st.title('Timelapse')
        timelapse_joueur()
    
    else:
        switch_page('Upload JSON')

else:
    switch_page('Upload JSON')
    
    
st.caption('Made by Tomlora')