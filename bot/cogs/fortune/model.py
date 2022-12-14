# Standard library imports
from dataclasses import dataclass
from datetime import datetime
# Third-party library imports
import psycopg2
from psycopg2 import sql
# Local imports
from config import Config


@dataclass
class FortuneResult():
    """ A fortune draw result class.

    :attr uid: An <int>, a discord user ID.
    :attr luck: The result of the draw, <str>.
    :attr angel: The guardian angel, <str>.
    :attr number: The lucky number, <int>.
    :attr colour: The lucky colour, <str>.
    :attr draw_date: The date when the fortune drawed, <datetime.datetime>.

    :meth record: Save the attributes into the database.
    :meth get_stats_by: Get the fortune statistics from database with optional group by query.
    :meth get_by_user: Get the specific fortune statistics of a user.
    """

    uid: int = None
    luck: str = None
    angel: str = None
    number: int = None
    colour:str = None
    draw_date:str = None

    def record(self):
        """ Save the class attributes to the databse. """
        con = psycopg2.connect(Config.database_url)
        cursor = con.cursor()
        query = """
            INSERT INTO fortune_statistics
            VALUES (%(user_id)s, %(luck)s, %(angel)s, %(number)s, %(colour)s, %(draw_date)s)
        """
        cursor.execute(
            query, {
                "user_id": self.uid,
                "luck": self.luck,
                "angel": self.angel,
                "number": self.number,
                "colour": self.colour,
                "draw_date": self.draw_date,
            }
        )
        con.commit()
        con.close()

    @staticmethod
    def get_stats_by(category: str) -> tuple[str, int]:
        con = psycopg2.connect(Config.database_url)
        cursor = con.cursor()

        query = sql.SQL("""
            SELECT {category}, COUNT(*) as count
            FROM fortune_statistics
            GROUP BY {category}
            ORDER BY count DESC
        """)
        cursor.execute(
            query.format(category=sql.Identifier(category))
        )
        result = cursor.fetchall()
        con.close()
        return result

    @staticmethod
    def get_by_user(user_id: int) -> tuple[tuple[tuple[str, datetime]], tuple[str, int]]:
        con = psycopg2.connect(Config.database_url)
        cursor = con.cursor()

        query = """
            SELECT luck, draw_date FROM fortune_statistics
            WHERE user_id = %s
            AND draw_date > current_date - interval '7 days'
            ORDER BY draw_date DESC
        """
        cursor.execute(
            query, (user_id,)
        )
        last_week_result = cursor.fetchall()

        query = """
            SELECT angel, COUNT(*) as count
            FROM fortune_statistics
            WHERE user_id = %s
            AND draw_date > current_date - interval '30 days'
            GROUP BY angel
            ORDER BY count DESC
            LIMIT 1
        """
        cursor.execute(
            query, (user_id,)
        )
        most_common_angel_result = cursor.fetchone()
        con.close()

        return last_week_result, most_common_angel_result
