from gestion_bdd import lire_bdd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
import streamlit as st


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


def filter_dataframe(df: pd.DataFrame, key='key') -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters", key=key)

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filtrer la data sur", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 50:
                user_cat_input = right.multiselect(
                    f"Valeurs pour {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Valeurs pour {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Valeurs pour {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Mot ou partie de mot dans {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df