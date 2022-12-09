""" A set of functions for accessing the database.
    Specifically for RPGame.

:Date:
"""
import os
import psycopg2


DATABASE = os.environ.get("DATABASE_URL")


def init_table() -> bool:
    """ Delete all the RPGame tables and re-create a new one.

    :return failure: Return True if commit has failed.
    """
    failure = False
    con = psycopg2.connect(DATABASE)
    cursor = con.cursor()
    try:
        with open("database/rpg_destroy.sql", "r") as f:
            cursor.execute(f.read())
            con.commit()
        with open("database/schema.sql", "r") as f:
            cursor.execute(f.read())
            con.commit()
    except psycopg2.Error:
        con.rollback()
        failure = True
    con.close()
    return failure


def db_commit(sql) -> bool:
    """ Execute a SQL statement.

    :return failure: Return True if commit has failed.
    """
    failure = False
    con = psycopg2.connect(DATABASE)
    cursor = con.cursor()
    try:
        cursor.execute(sql)
        con.commit()
    except psycopg2.Error:
        con.rollback()
        failure = True
    con.close()
    return failure


def player_create(user_id: int) -> bool:
    """ Insert a new player into the database with default values.

    :param user_id: The ID of user.

    :return failure: Return True if commit has failed.
    """
    sql = f"INSERT INTO players VALUES ({user_id}, 2500, 0, 50, 0, 0, 'N')"
    return db_commit(sql)


def log_battle(atk_id: int, def_id: int, battle_type: str, user_result: str, target_result: str) -> bool:
    """ Insert the battle result into the database.

    :param atk_id: The ID of the attacker.
    :param def_id: The ID of the defender.
    :param battle_type:
        Should be 'N' or 'Y' or 'B',
            'Y' for death-match.
            'N' for friendly match.
            'B' for boss fight.
    :param user_result: The result of the battle from the defender's perspective.
    :param target_result: The result of the battle from the attacker's perspective.

    :return failure: Return True if commit has failed.
    """
    sql = f"INSERT INTO battle_log VALUES ({atk_id}, {def_id}, '{battle_type}', '{user_result}', '{target_result}')"
    return db_commit(sql)


def add_skill(user_id: int, skill_id: str, skill_name: str, combo: int, damage_modifier: float) -> bool:
    """ Insert a skill to a player in the database.

    :param user_id: The ID of the user.
    :param skill_id: The ID of the skill.
    :param skill_name: The name of the skill.
    :param combo: The combo of the skill.
    :param damage_modifier: The damage modifier of the skill.

    :return failure: Return True if commit has failed.
    """
    sql = f"INSERT INTO players_skills VALUES ({user_id}, '{skill_id}', '{skill_name}', {combo}, {damage_modifier})"
    return db_commit(sql)


def remove_player(user_id: int) -> bool:
    """ Remove a player from database.

    :prarm user_id: The ID of user.

    :return failure: If the commit has failed, return True.
    """
    sql = f"DELETE FROM players WHERE user_id = {user_id}"
    failure_player = db_commit(sql)
    sql = f"DELETE FROM players_skills WHERE user_id = {user_id}"
    failure_skills = db_commit(sql)
    return failure_player or failure_skills


def remove_skill(user_id: int, skill_id: str) -> bool:
    """ Delete a skill from player in the database.

    :param user_id: The ID of the user.
    :param skill_id: The ID of the skill.

    :return failure: Return True if commit has failed.
    """
    sql = f"DELETE FROM players_skills WHERE user_id = {user_id} AND skill_id='{skill_id}'"
    return db_commit(sql)


def update_player(user_id: int, **kwargs) -> bool:
    """ Execute an update SQL statement.

    :param user_id: The ID of user.
    :param kwargs:
        These keys should be the exsisting table field
        from the players table in the databse.

    :return failure: Return True if commit has failed.

    :example:
        >> update_player(666, mana=5, dead='Y')
        >> The SQL statement will be:
        >> "UPDATE players SET mana=5, dead='Y' WHERE user_id=666"
    """
    sql = "UPDATE players SET "
    sql += ", ".join([("%s=%r" % x) for x in kwargs.items()])
    sql += f" WHERE user_id={user_id}"
    failure = db_commit(sql)
    return failure


def get_player(user_id: int) -> list|None:
    """ Get the player data from the database.

    :param user_id: The ID of the player.

    :return result:
        Return None if the user_id is not in the database.
        Otherwise will return a list composed of
            0: user_id      <int>
            1: crystal      <int>
            2: mana         <int>
            3: luck         <int>
            4: floor        <int>
            5: kills        <int>
            6: dead         <str>
            7: created_at   <datetime.datetime>
    """
    sql = f"SELECT * FROM players WHERE user_id={user_id}"
    con = psycopg2.connect(DATABASE)
    cursor = con.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    con.close()
    return result if result else None


def get_skill(skill_id: str) -> list|None:
    """ Get the skill data from the database.

    :param skill_id: The ID of the skill.

    :return result:
        Return None if the skill_id is not in the database.
        Otherwise will return a list composed of
            0: user_id          <int>
            1: skill_id         <str>
            2: skill_name       <str>
            3: combo            <int>
            4: damage_modifier  <float>

    """
    sql = f"SELECT * FROM players_skills WHERE skill_id='{skill_id}'"
    con = psycopg2.connect(DATABASE)
    cursor = con.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    con.close()
    return result if result else None


def get_player_skills(user_id: int) -> list|None:
    """ Get all skills the player has from the database.

    :param user_id: The ID of the player.

    :return result:
        Return None if there's no data in the database.
        Otherwise will return a list composed of
            0: user_id          <int>
            1: skill_id         <str>
            2: skill_name       <str>
            3: combo            <int>
            4: damage_modifier  <float>
    """
    sql = f"SELECT * FROM players_skills WHERE user_id={user_id}"
    con = psycopg2.connect(DATABASE)
    cursor = con.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    con.close()
    return result if result else None


def skill_performs(user_id: int, p: float) -> list|None:
    """ Randomly select a validate skill from the database.

    :param user_id: The ID of the user.
    :param p: The probability decides will the skill perform.

    :return result:
        Return None if there's no data in the database.
        Otherwise will return a list composed of
            0: user_id          <int>
            1: skill_id         <str>
            2: skill_name       <str>
            3: combo            <int>
            4: damage_modifier  <float>
    """
    sql = f"SELECT * FROM players_skills WHERE user_id={user_id} AND {p} <= (25 - sqrt(combo*damage_modifier)) ORDER BY RANDOM() LIMIT 1"
    con = psycopg2.connect(DATABASE)
    cursor = con.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    con.close()
    return result if result else None


def get_attack_battle_logs(user_id: int) -> list|None:
    """ Get all the offensive battle results from the database.

    :param user_id: The ID of the player.

    :return result:
        Return None if there's no data in the database.
        Otherwise will return a list composed of
            0: user_id          <int>
            1: target_id        <int>
            2: dm               <str>
            3: user_result      <str>
            4: target_result    <str>
            5: time_at          <datetime.datetime>
    """
    sql = f"SELECT * FROM battle_log WHERE user_id={user_id} ORDER BY time_at DESC LIMIT 9"
    con = psycopg2.connect(DATABASE)
    cursor = con.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    con.close()
    return result if result else None


def get_defense_battle_logs(user_id: int) -> list|None:
    """ Get all the defensive battle results from the database.

    :param user_id: The ID of the player.

    :return result:
        Return None if there's no data in the database.
        Otherwise will return a list composed of
            0: user_id          <int>
            1: target_id        <int>
            2: dm               <str>
            3: user_result      <str>
            4: target_result    <str>
            5: time_at          <datetime.datetime>
    """
    sql = f"SELECT * FROM battle_log WHERE target_id={user_id} ORDER BY time_at DESC LIMIT 9"
    con = psycopg2.connect(DATABASE)
    cursor = con.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    con.close()
    return result if result else None
