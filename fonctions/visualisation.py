from fonctions.gestion_bdd import lire_bdd, lire_bdd_perso
import pandas as pd
import plotly.express as px


from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

import streamlit as st




def transformation_stats_visu(nom_table, joueur, distinct: bool = False, score='score_general', ascending=True):
    """Met en page les scorings d'un joueur.

    Parameters
    ----------
    nom_table : str
        nom de la table sql à lire
    joueur : str
        nom du joueur
    distinct : bool, optional
        prise en compte des doublons dans la table, by default False
    score : str, optional
        variable représentant les scores dans la table sql, by default 'score_general'

    Returns
    -------
    DataFrame
        _description_
    """
    # Lire la bdd
    if nom_table == 'sw_score':
        df_actuel : pd.DataFrame = lire_bdd_perso('''SELECT DISTINCT score_general, date, id_joueur, score_spd, score_arte, score_qual FROM public.sw_score;''', index_col='id_joueur')
    else:
        df_actuel : pd.DataFrame = lire_bdd(nom_table, distinct=distinct)
    df_actuel = df_actuel.transpose()
    df_actuel.reset_index(inplace=True)

    # df_actuel.drop(['id'], axis=1, inplace=True) # inutile

    # Datetime
    df_actuel['date'] = pd.to_datetime(df_actuel['date'], format='%d/%m/%Y')
    df_actuel['date'] = df_actuel['date'].dt.strftime('%d/%m/%Y')

    # Sort les values

    if nom_table == 'sw':
        df_actuel.sort_values(by=['date', 'Set'], inplace=True)
        df_actuel = df_actuel[df_actuel['id'] == joueur]
        df_actuel.drop(['id', 'index'], axis=1, inplace=True)
        
    elif nom_table == 'sw_score':
        df_actuel.sort_values(by=['date'], inplace=True)
        # df_actuel.drop(['guilde'], axis=1, inplace=True)
    # df_actuel = df_actuel[df_actuel['Joueur'] == joueur]
        df_actuel = df_actuel[df_actuel['id_joueur'] == joueur]
        df_actuel.drop(['id_joueur'], axis=1, inplace=True)
        
    else:
        df_actuel.sort_values(by='date', inplace=True)
        # df_actuel.drop(['guilde'], axis=1, inplace=True)
    # df_actuel = df_actuel[df_actuel['Joueur'] == joueur]
        df_actuel = df_actuel[df_actuel['id'] == joueur]
        df_actuel.drop(['id', 'index'], axis=1, inplace=True)

    # DF final
    if nom_table == 'sw':
        df_actuel = pd.melt(df_actuel, id_vars=['date', 'Set'], value_vars=[
                            '100', '110', '120'], var_name='Palier', value_name='Nombre')
        df_actuel['datetime'] = pd.to_datetime(
            df_actuel['date'], format='%d/%m/%Y')
        df_actuel.sort_values(by=['datetime', 'Set', 'Palier'], inplace=True, ascending=[ascending, True, True])
        # df_actuel.drop(['datetime'], axis=1, inplace=True)
        
    elif nom_table == 'sw_arte':
        df_actuel = pd.melt(df_actuel, id_vars=['date', 'arte_type', 'type'], value_vars=[
                            '80', '85', '90', '95', '100+'], var_name='Palier', value_name='Nombre')
        df_actuel['datetime'] = pd.to_datetime(
            df_actuel['date'], format='%d/%m/%Y')
        df_actuel.sort_values(by=['datetime', 'arte_type', 'type'], inplace=True, ascending=[ascending, True, True])
        # df_actuel.drop(['datetime'], axis=1, inplace=True)
        
    elif nom_table == 'sw_spd':
        df_actuel = pd.melt(df_actuel, id_vars=['date', 'Set'], value_vars=[
                            '23-25', '26-28', '29-31', '32-35', '36+'], var_name='Palier', value_name='Nombre')
        df_actuel['datetime'] = pd.to_datetime(
            df_actuel['date'], format='%d/%m/%Y')
        df_actuel.sort_values(by=['datetime', 'Set', 'Palier'], inplace=True, ascending=[ascending, True, True])
        # df_actuel.drop(['datetime'], axis=1, inplace=True)
    else:
        # df_actuel = pd.pivot_table(df_actuel, 'score', index='date')
        df_actuel[score] = df_actuel[score].astype('int')
        df_actuel['datetime'] = pd.to_datetime(
            df_actuel['date'], format='%d/%m/%Y')
        df_actuel.sort_values(by=['datetime'], ascending=ascending, inplace=True)
        # df_actuel.drop(['datetime'], axis=1, inplace=True)

    return df_actuel


def plotline_evol_rune_visu(df, color='Set'):
    """Crée un graphique montrant l'évolution des scorings.

    Parameters
    ----------
    df : DataFrame
        DataFrame contenant les scorings
    color : str, optional
        variable à différencier par des couleurs, by default 'Set'

    Returns
    -------
    Figure plotly
        Graphique montrant l'évolution du score en fonction de la date
    """
    fig = px.line(df, x="date", y="Nombre", color=color, markers=True)

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
    fig.update_yaxes(showgrid=False)
    return fig


def filter_dataframe(df: pd.DataFrame, key='key', nunique:int=50, type_number='float', disabled=False) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe
        disabled = Coché ou non par défault

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters", key=key, value=disabled)

    if not modify:
        return df

    df = df.copy()
    

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]) and key != 'df_count' and key != 'timelapse':
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
            if is_categorical_dtype(df[column]) and df[column].nunique() < nunique:
                left.write("↳")
                user_cat_input = right.multiselect(
                    f"Valeurs pour {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                if type_number == 'float':
                    left.write("↳")
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                elif type_number == 'int':
                    left.write("↳")
                    _min = int(df[column].min())
                    _max = int(df[column].max())
                    step = 1
                user_num_input = right.slider(
                    f"Valeurs pour {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                left.write("↳")
                user_date_input = right.date_input(
                    f"Valeurs pour {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(
                        map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                left.write("↳")
                user_text_input = right.text_input(
                    f"Mot ou partie de mot dans {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(
                        str).str.contains(user_text_input)]

    return df



def table_with_images(df: pd.DataFrame, url_columns):

    df_ = df.copy()

    @st.cache_data
    def _path_to_image_html(path):
        return '<img src="' + path + '" width="60" >'

    for column in url_columns:
        df_[column] = df_[column].apply(_path_to_image_html)

    return df_.to_html(escape=False)



    