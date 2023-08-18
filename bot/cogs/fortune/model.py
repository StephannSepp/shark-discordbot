from dataclasses import dataclass
from datetime import datetime

from bot import get_cursor


@dataclass
class FortuneResult:
    """Store the fortune draw results.

    Attributes:
        uid: Discord user ID.
        luck: The result of the fortune draw.
        angel: The guardian angel.
        number: The lucky number.
        colour: The lucky colour.
        draw_date: The date when the fortune was drawed.

    Methods:
        record(): Save the result to the database.
        get_stats_by: Get the fortune statistics by some optional parameters.
        get_by_user: Get the fortune records of a specific user.
    """

    uid: int = None
    luck: str = None
    angel: str = None
    number: int = None
    colour: str = None
    draw_date: str = None

    def record(self):
        """Save the class attributes to the databse."""
        with get_cursor() as cursor:
            query = (
                "INSERT INTO fortune_records "
                "VALUES (%(user_id)s, %(luck)s, %(angel)s, %(number)s, %(colour)s, %(draw_date)s)"
            )
            cursor.execute(
                query,
                {
                    "user_id": self.uid,
                    "luck": self.luck,
                    "angel": self.angel,
                    "number": self.number,
                    "colour": self.colour,
                    "draw_date": self.draw_date,
                },
            )
            query = (
                "UPDATE fortune_statistics SET item_count = item_count + 1 WHERE item_type = 'general' AND item = 'total_draws';"
                "UPDATE fortune_statistics SET item_count = item_count + 1 WHERE item_type = 'luck' AND item = %s;"
                "UPDATE fortune_statistics SET item_count = item_count + 1 WHERE item_type = 'angel' AND item = %s;"
            )
            cursor.execute(query, (self.luck, self.angel))

    @staticmethod
    def get_stats_by(category: str) -> tuple[str, int]:
        with get_cursor() as cursor:
            query = (
                "SELECT item, item_count "
                "FROM fortune_statistics "
                "WHERE item_type = %s ORDER BY item_count DESC LIMIT 9"
            )
            cursor.execute(query, (category,))
            result = cursor.fetchall()
        return result

    @staticmethod
    def get_total_draws() -> int:
        with get_cursor() as cursor:
            query = (
                "SELECT item_count "
                "FROM fortune_statistics "
                "WHERE item_type = 'general' AND item = 'total_draws'"
            )
            cursor.execute(query)
            result = cursor.fetchone()[0]
        return result

    @staticmethod
    def get_by_user(
        user_id: int,
    ) -> tuple[tuple[tuple[str, datetime]], tuple[str, int]]:
        with get_cursor() as cursor:
            query = (
                "SELECT luck, draw_date FROM fortune_records "
                "WHERE user_id = %s "
                "AND draw_date > current_date - interval '7 days' "
                "ORDER BY draw_date DESC"
            )
            cursor.execute(query, (user_id,))
            last_week_result = cursor.fetchall()

            query = (
                "SELECT angel, COUNT(*) as count "
                "FROM fortune_records "
                "WHERE user_id = %s "
                "AND draw_date > current_date - interval '30 days' "
                "GROUP BY angel "
                "ORDER BY count DESC "
                "LIMIT 1"
            )
            cursor.execute(query, (user_id,))
            most_common_angel_result = cursor.fetchone()

        return last_week_result, most_common_angel_result

    @staticmethod
    def clear_history_data():
        with get_cursor() as cursor:
            query = (
                "DELETE FROM fortune_records "
                "WHERE draw_date < current_date - interval '31 days'"
            )
            cursor.execute(query)
