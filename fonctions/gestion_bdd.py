from pandas import read_sql, DataFrame
from streamlit import cache_resource, session_state
from sqlalchemy import create_engine, text, Float, BigInteger
from os import environ

# https://betterprogramming.pub/how-to-execute-plain-sql-queries-with-sqlalchemy-627a3741fdb1

DB = environ.get('API_SQL')

@cache_resource
def init_connection():
    engine = create_engine(DB,
                           echo=False,
                           connect_args={'options': '-csearch_path={}'.format('sw')})
    return engine.connect()

conn = init_connection()


def lire_bdd(nom_table, format: str = "df", index=None, distinct: bool = False):
    """Lire la BDD

    Parameters
    -----------
    nom_table: :class:`str`
            Le nom de la table
    format: :class:`str`
            Choix entre 'dict' ou 'df'
    """
    # conn = engine.connect()

    if distinct:
        requetesql = text(f'SELECT distinct * FROM {nom_table}')
    else:
        requetesql = text(f'SELECT * FROM {nom_table}')
    try:
        df = read_sql(requetesql, con=conn, index_col=index)
    except KeyError:
        nom_table = nom_table.lower()
        df = read_sql(requetesql, con=conn, index_col='Joueur')
    except:
        nom_table = nom_table.lower()
        df = read_sql(requetesql, con=conn, index_col=index)
    df = df.transpose()
    if format == "dict":
        df = df.to_dict()
    # conn.close()
    return df


def lire_bdd_perso(requests: str, format: str = "df", index_col: str = "joueur", params=None):
    """Lire la BDD
    Parameters
    -----------
    requests: :class:`str`
            Requête SQL avec obligatoirement SELECT (columns) from (table) et éventuellement WHERE
    format: :class:`str`
            Choix entre 'dict' ou 'df'
    index_col: :class:`str`
            Colonne de l'index de la table
    params : dict avec {'variable' : 'value}


    Les variables doivent être sous forme %(variable)s
    """
    # conn = engine.connect()

    if params == None:
        df = read_sql(text(requests), con=conn, index_col=index_col)
    else:
        df = read_sql(text(requests), con=conn,
                         index_col=index_col, params=params)

    df = df.transpose()
    if format == "dict":
        df = df.to_dict()
    # conn.close()
    return df


def sauvegarde_bdd(df, nom_table, methode_save='replace', dtype={'Score': Float(), 'serie': BigInteger()}, index=True):
    """Sauvegarde la BDD au format dataframe

    Parameters
    -----------
    df: :class:`dict` or  `dataframe`
            Dataframe ou dict
    nom_table: :class:`str`
            Nom de la table sql
    method_save: :class:`str`
            Si la table existe déjà, choix entre "append" pour insérer des nouvelles valeurs ou "replace" pour supprimer la table existante et la remplacer
    """
    # conn = engine.connect()
    # si la variable envoyée n'est pas un dataframe, on l'a met au format dataframe
    if not isinstance(df, DataFrame):
        df = DataFrame(df)
        df = df.transpose()
    df.to_sql(nom_table, con=conn, if_exists=methode_save, index=index,
              method='multi', dtype=dtype)
    conn.commit()
    # conn.close()


def supprimer_bdd(nom_table):
    # conn = engine.connect()
    sql = text(f'DROP TABLE IF EXISTS {nom_table}')
    conn.execute(sql)
    conn.commit()
    # conn.close()


def supprimer_data(joueur, date):
    """
    Supprime les données d'un joueur à une date spécifique dans plusieurs tables de la base de données.

    :param joueur: L'identifiant du joueur.
    :type joueur: int
    :param date: La date des données à supprimer.
    :type date: str
    """
    # conn = engine.connect()
    params_sql = {'joueur': joueur, 'date': date}
    sql1 = text(f'''DELETE FROM sw WHERE "id" = :joueur AND date = :date;
                    DELETE FROM sw_score WHERE "id_joueur" = :joueur AND date = :date;
                    DELETE FROM sw_arte WHERE "id" = :joueur AND date = :date;
                    DELETE FROM sw_spd WHERE "id" = :joueur AND date = :date;
                    DELETE FROM sw_detail WHERE "id" = :joueur AND date = :date;
                    DELETE FROM sw_max WHERE "id" = :joueur AND date = :date;
                    DELETE FROM sw_arte_max WHERE "id" =:joueur AND date = :date;
                    DELETE FROM sw_wb WHERE "id_joueur" =:joueur AND date = :date;
                    DELETE FROM sw_pvp WHERE "id_joueur" =:joueur AND date = :date;
                    DELETE FROM sw_score_qual WHERE "id" = :joueur AND date = :date;''')  # :var_name
    conn.execute(sql1, params_sql)
    conn.commit()

    # conn.close


def supprimer_data_all(joueur):
    """
    Supprime toutes les données associées à un joueur dans la base de données.

    Args:
        joueur (int): L'identifiant du joueur.

    Returns:
        None
    """
    # conn = engine.connect()
    params_sql = {'joueur': joueur}
    sql1 = text(f'''DELETE FROM sw WHERE "id" = :joueur;
                    DELETE FROM sw_score WHERE "id_joueur" = :joueur;
                    DELETE FROM sw_arte WHERE "id" = :joueur;
                    DELETE FROM sw_spd WHERE "id" = :joueur;
                    DELETE FROM sw_max WHERE "id" = :joueur;
                    DELETE from sw_monsters WHERE "id" = :joueur;
                    DELETE from sw_detail WHERE "id" = :joueur;
                    DELETE from sw_objectifs_arte WHERE "id" = :joueur;
                    DELETE from sw_objectifs_rune WHERE "id" = :joueur;
                    DELETE from sw_arte_max WHERE "id" = :joueur;
                    DELETE FROM sw_wb WHERE "id_joueur" =:joueur;
                    DELETE FROM sw_pvp WHERE "id_joueur" =:joueur;
                    DELETE FROM sw_score_qual WHERE "id_joueur" =:joueur;
                    DELETE FROM sw_user WHERE "id" = :joueur;
                    ''')  
    conn.execute(sql1, params_sql)
    conn.commit()

    # conn.close


def update_info_compte(joueur, guildeid, compteid):
    """
    Met à jour les informations du compte d'un joueur dans la base de données.

    Args:
        joueur (str): Le nom du joueur.
        guildeid (int): L'identifiant de la guilde.
        compteid (int): L'identifiant du compte.

    Returns:
        None
    """
    # conn = engine.connect()
    params_sql = {'joueur': joueur,
                  'guilde_id': guildeid, 'joueur_id': compteid}
    # sql1 = text('UPDATE sw_score SET guilde = :guilde WHERE "Joueur" = :joueur')
    sql1 = text(
        'UPDATE sw_user SET guilde_id = :guilde_id, joueur = :joueur WHERE joueur_id = :joueur_id;')
    conn.execute(sql1, params_sql)
    conn.commit()
    # conn.close()



def requete_perso_bdd(request: text, dict_params: dict):
    """
    request : requête sql au format text

    dict_params : dictionnaire {variable : valeur}

    Rappel
    -------
    Dans la requête sql, une variable = :variable """
    # conn = engine.connect()
    sql = text(request)
    conn.execute(sql, dict_params)
    conn.commit()

    # conn.close()


def get_user(joueur, type: str = 'name_user', id_compte: int = 0):
    '''Return l'id, la guilde, la visibilité et le rank du joueur demandé
        id_compte est dans le cas de l'ancien système où on ne prenait pas l'id du compte. Utile pour faire la maj et adapter la ligne au nouveau système
    type : name_user ou id'''
    # conn = engine.connect()
    if type == 'name_user':
        sql = text('SELECT id, guilde_id, visibility , joueur_id, rank, (SELECT guilde from sw_guilde where sw_user.guilde_id = sw_guilde.guilde_id) as guilde FROM sw_user WHERE joueur = :joueur ')
        data = conn.execute(sql, {'joueur': joueur})
    elif type == 'id':
        sql = text('SELECT id, guilde_id, visibility , joueur_id, rank, (SELECT guilde from sw_guilde where sw_user.guilde_id = sw_guilde.guilde_id) as guilde FROM sw_user WHERE joueur_id =:joueur ')
        data = conn.execute(sql, {'joueur': joueur})
    data = data.mappings().all()
    id_joueur = data[0]['id']
    visibility = data[0]['visibility']
    guildeid = data[0]['guilde_id']
    rank = data[0]['rank']
    
    # Dans l'ancien système, on ne prenait pas l'id. On regarde s'il faut maj
    if data[0]['joueur_id'] == 0 and type == 'name_user':
        sql = text(
            'UPDATE sw_user SET joueur_id = :joueur_id where joueur = :joueur')
        data = conn.execute(sql, {'joueur_id': id_compte, 'joueur': joueur})
        conn.commit()
    # conn.close()
    return id_joueur, visibility, guildeid, rank


def cancel():
    conn.rollback()
    


def optimisation_int(data, int_cols_before:list, int_cols_after:str='int16'): 
    """
    Optimize the integer columns of a DataFrame by changing their data type.

    Parameters:
    data (DataFrame): The input DataFrame.
    int_cols_before (list): List of integer column data types before optimization.
    int_cols_after (str, optional): The desired integer data type after optimization. Defaults to 'int16'.

    Returns:
    DataFrame: The optimized DataFrame.
    """
    if 'rune_equiped' in data.columns:  # on la retire car elle pose pb pour l'identification des monstres
        int_cols = data.drop('rune_equiped', axis=1).select_dtypes(include=int_cols_before).columns
    else:
        int_cols = data.select_dtypes(include=int_cols_before).columns

    data[int_cols] = data[int_cols].astype(int_cols_after)
    
    if int_cols_before.count('float64')>0:
        float_cols = data.select_dtypes(include=['float64']).columns
        data[float_cols] = data[float_cols].astype('float32')

    return data


def cleaning_only_guilde(x):
    """
    Nettoie les données en ne gardant que celles liées à la guilde spécifiée.

    Args:
        x (dict): Un dictionnaire contenant les données à nettoyer.

    Returns:
        dict: Le dictionnaire nettoyé.
    """
    x['private'] = 0
    if x['visibility'] == 2:
        if x['guilde'] != session_state.guilde:
            x['private'] = 1
    return x


def get_number_row(table):
    """
    Renvoie le nombre de lignes dans une table donnée.

    Args:
        table (str): Le nom de la table.

    Returns:
        int: Le nombre de lignes dans la table.
    """
    sql = text(f'SELECT COUNT(*) FROM {table}')
    data = conn.execute(sql)
    data = data.mappings().all()
    return data[0]['count']