from bot import get_cursor
from utils import gen


def add_warning(user_id: int, server_id: int, moderator_id: int, reason: str) -> int:
    """Insert a warning to the database.

    Args:
        user_id: The ID of the user.
        server_id: The ID of the server.
        moderator_id: The ID of the user who give the warning.
        reason: The reason for the warning.

    Returns:
        The ID of the warning.
    """
    warning_id = gen.snowflake()
    with get_cursor() as cursor:
        query = (
            "INSERT INTO warns"
            "VALUES (%(id)s, %(user_id)s, %(server_id)s, %(moderator_id)s, %(reason)s)"
        )
        cursor.execute(
            query,
            {
                "id": warning_id,
                "user_id": user_id,
                "server_id": server_id,
                "moderator_id": moderator_id,
                "reason": reason,
            },
        )
    return warning_id


def remove_warn(server_id: int, user_id: int, warning_id: int) -> str:
    """Delete a warning from the database.

    Args:
        server_id: The ID of the server.
        user_id: The ID of the user.
        warning_id: The ID the warning.

    Retruns:
        The reason of the warning.
    """
    query = (
        "SELECT reason FROM warns "
        "WHERE warn_id = %(id)s "
        "AND user_id = %(user_id)s "
        "AND server_id = %(server_id)s"
    )
    with get_cursor() as cursor:
        cursor.execute(
            query,
            {
                "id": warning_id,
                "user_id": user_id,
                "server_id": server_id,
            },
        )
        result = cursor.fetchone()[0]
        query = (
            "DELETE FROM warns "
            "WHERE warn_id = %(id)s "
            "AND user_id = %(user_id)s "
            "AND server_id = %(server_id)s"
        )
        cursor.execute(
            query,
            {
                "id": warning_id,
                "user_id": user_id,
                "server_id": server_id,
            },
        )
    return result


def list_warns(server_id: int, user_id: int) -> list:
    """Return a list of warnings on the user.

    Args
        server_id: The ID of the server.
        user_id: The ID of the user.

    Returns:
        A list composed contains as following:
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
    with get_cursor() as cursor:
        cursor.execute(
            query,
            {
                "user_id": user_id,
                "server_id": server_id,
            },
        )
        result = cursor.fetchall()
    return result
