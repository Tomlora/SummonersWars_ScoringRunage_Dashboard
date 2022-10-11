from gestion_bdd import lire_bdd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def transformation_stats_visu(nom_table, joueur):
    # Lire la bdd
    df_actuel = lire_bdd(nom_table)
    df_actuel = df_actuel.transpose()
    df_actuel.reset_index(inplace=True)
    
    # df_actuel.drop(['id'], axis=1, inplace=True) # inutile
    
    #Datetime
    df_actuel['date'] = pd.to_datetime(df_actuel['date'], format='%d/%m/%Y')
    df_actuel['date'] = df_actuel['date'].dt.strftime('%d/%m/%Y')
    
    # Sort les values
    
    if nom_table == 'sw':
        df_actuel.sort_values(by=['date','Set'], inplace=True)
    else:
        df_actuel.sort_values(by='date', inplace=True)
        # df_actuel.drop(['guilde'], axis=1, inplace=True)
    # df_actuel = df_actuel[df_actuel['Joueur'] == joueur]
    df_actuel = df_actuel[df_actuel['id'] == joueur]
    df_actuel.drop(['id', 'index'], axis=1, inplace=True)
    
    # DF final
    if nom_table == 'sw':
        df_actuel = pd.melt(df_actuel, id_vars=['date', 'Set'], value_vars=['100', '110', '120'], var_name='Palier', value_name='Nombre')
        df_actuel['datetime'] = pd.to_datetime(df_actuel['date'], format='%d/%m/%Y')
        df_actuel.sort_values(by=['datetime', 'Set', 'Palier'], inplace=True)
        df_actuel.drop(['datetime'], axis=1, inplace=True)
    else:
        # df_actuel = pd.pivot_table(df_actuel, 'score', index='date')
        df_actuel['score'] = df_actuel['score'].astype('int')
        df_actuel['datetime'] = pd.to_datetime(df_actuel['date'], format='%d/%m/%Y')
        df_actuel.sort_values(by=['datetime'], inplace=True)
        df_actuel.drop(['datetime'], axis=1, inplace=True)
    
    return df_actuel

def plotline_evol_rune_visu(df):
    fig = px.line(df, x="date", y="Nombre", color="Set")
    fig.update_layout({
                'plot_bgcolor': 'rgb(255, 255, 255)',
                'paper_bgcolor': 'rgba(0, 0, 0,0)'
    })
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
    fig.update_yaxes(showgrid=False)
    return fig