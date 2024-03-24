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

    async def record(self):
        """Save the class attributes to the databse."""
        params = {
            "user_id": self.uid,
            "luck": self.luck,
            "angel": self.angel,
            "number": self.number,
            "colour": self.colour,
            "draw_date": self.draw_date,
        }
        async with get_cursor() as cursor:
            query = (
                "INSERT INTO fortune_records VALUES (%(user_id)s, %(luck)s, "
                "%(angel)s, %(number)s, %(colour)s, %(draw_date)s)"
            )
            await cursor.execute(query, params)
            query = (
                "UPDATE fortune_statistics SET item_count = item_count + 1 "
                "WHERE item_type = 'general' AND item = 'total_draws'"
            )
            await cursor.execute(query)
            query = (
                "UPDATE fortune_statistics SET item_count = item_count + 1 "
                "WHERE item_type = 'luck' AND item = %s"
            )
            await cursor.execute(query, (self.luck,))
            query = (
                "UPDATE fortune_statistics SET item_count = item_count + 1 "
                "WHERE item_type = 'angel' AND item = %s"
            )
            await cursor.execute(query, (self.angel,))

    @staticmethod
    async def get_stats_by(category: str) -> tuple[str, int]:
        async with get_cursor() as cursor:
            query = (
                "SELECT item, item_count "
                "FROM fortune_statistics "
                "WHERE item_type = %s ORDER BY item_count DESC LIMIT 9"
            )
            await cursor.execute(query, (category,))
            result = await cursor.fetchall()
        return result

    @staticmethod
    async def get_total_draws() -> int:
        async with get_cursor() as cursor:
            query = (
                "SELECT item_count "
                "FROM fortune_statistics "
                "WHERE item_type = 'general' AND item = 'total_draws'"
            )
            await cursor.execute(query)
            result = await cursor.fetchone()
        return result[0]

    @staticmethod
    async def get_by_user(
        user_id: int,
    ) -> tuple[tuple[tuple[str, datetime]], tuple[str, int]]:
        async with get_cursor() as cursor:
            query = (
                "SELECT luck, draw_date FROM fortune_records "
                "WHERE user_id = %s "
                "AND draw_date > current_date - interval '7 days' "
                "ORDER BY draw_date DESC"
            )
            await cursor.execute(query, (user_id,))
            last_week_result = cursor.fetchall()
            query = (
                "SELECT angel, COUNT(*) as count "
                "FROM fortune_records "
                "WHERE user_id = %s "
                "AND draw_date > current_date - interval '90 days' "
                "GROUP BY angel "
                "ORDER BY count DESC "
                "LIMIT 1"
            )
            await cursor.execute(query, (user_id,))
            most_common_angel_result = await cursor.fetchone()
        return last_week_result, most_common_angel_result
