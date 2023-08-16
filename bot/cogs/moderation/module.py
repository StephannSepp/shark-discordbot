""" A set of functions for accessing database. """

import psycopg2

from config import Config
from utils import gen


def add_warning(user_id:int, server_id: int, moderator_id: int, reason: str) -> int:
    """ Insert a warning to the database.

    :param user_id: The ID of the user.
    :param server_id: The ID of the server.
    :param moderator_id: The ID of the user who give the warning.
    :param reason: The reason for the warning.

    :return warning_id: The ID of the warning.
    """
    warning_id = gen.snowflake()
    query = """
        INSERT INTO warns
        VALUES (%(id)s, %(user_id)s, %(server_id)s, %(moderator_id)s, %(reason)s)
    """
    con = psycopg2.connect(Config.database_url)
    cursor = con.cursor()
    cursor.execute(
        query, {
            "id": warning_id,
            "user_id": user_id,
            "server_id": server_id,
            "moderator_id": moderator_id,
            "reason": reason,
        }
    )
    con.commit()
    con.close()
    return warning_id


def remove_warn(server_id: int, user_id: int, warning_id: int) -> str:
    """ Delete a warning from the database.

    :param server_id: The ID of the server.
    :param user_id: The ID of the user.
    :param warning_id: The ID the warning.

    :return result: The reason of the warning.
    """
    query = (
        "SELECT reason FROM warns "
        "WHERE warn_id = %(id)s "
        "AND user_id = %(user_id)s "
        "AND server_id = %(server_id)s"
    )
    con = psycopg2.connect(Config.database_url)
    cursor = con.cursor()
    cursor.execute(query, {
            "id": warning_id,
            "user_id": user_id,
            "server_id": server_id,
        }
    )
    result = cursor.fetchone()[0]
    query = (
        "DELETE FROM warns "
        "WHERE warn_id = %(id)s "
        "AND user_id = %(user_id)s "
        "AND server_id = %(server_id)s"
    )
    cursor.execute(query, {
            "id": warning_id,
            "user_id": user_id,
            "server_id": server_id,
        }
    )
    con.commit()
    con.close()
    return result


def list_warns(server_id: int, user_id: int) -> list:
    """ Return a list of warnings on the user.

    :param server_id: The ID of the server.
    :param user_id: The ID of the user.

    :retrun result: A list composed of
        1: warn ID          <int>
        2: user ID          <int>
        3: ID of moderator  <int>
        4: reason           <str>
        5: warn issue time  <datetime.datetime>
    """
    query = (
        "SELECT warn_id, user_id, moderator_id, reason, created_at FROM warns "
        "WHERE user_id = %(user_id)s "
        "AND server_id = %(server_id)s"
    )
    con = psycopg2.connect(Config.database_url)
    cursor = con.cursor()
    cursor.execute(query, {
            "user_id": user_id,
            "server_id": server_id,
        }
    )
    result = cursor.fetchall()
    con.close()
    return result
