import datetime
import math
import random

from bot import get_cursor

BASE = 183
REWARDS = [1000 * BASE, 100 * BASE, 20 * BASE, 5 * BASE, 0 * BASE]


class LotteryTicket:
    def __init__(self, ticket_id: int, uid: int, lottery_no: int, pick_number: str):
        self.ticket_id = ticket_id
        self.uid = uid
        self.lottery_no = lottery_no
        self.pick_number = pick_number


class Lottery:
    winning_number: str = None
    valid_date: datetime.datetime = None

    def __init__(self, uid: int | None = None):
        self.tickets: list[LotteryTicket] = []
        self.last_tickets: list[LotteryTicket] = []
        self.no = self.get_lottery_no()
        self._get_last_winning_number()
        if uid is not None:
            self.uid = uid
            self._get_last_lottery_tickets()
            self._get_lottery_tickets()

    def _get_lottery_tickets(self) -> None:
        with get_cursor() as cursor:
            query = (
                "SELECT ticket_id, uid, lottery_no, pick_number "
                "FROM game.lottery_ticket WHERE uid = %(uid)s "
                "AND lottery_no = %(lottery_no)s AND claimed = False"
            )
            cursor.execute(query, {"lottery_no": self.no, "uid": self.uid})
            result = cursor.fetchall()
        for row in result:
            self.tickets.append(LotteryTicket(*row))

    def _get_last_lottery_tickets(self) -> None:
        with get_cursor() as cursor:
            query = (
                "SELECT ticket_id, uid, lottery_no, pick_number "
                "FROM game.lottery_ticket WHERE uid = %(uid)s "
                "AND lottery_no = %(lottery_no)s AND claimed = False"
            )
            cursor.execute(query, {"lottery_no": self.no - 1, "uid": self.uid})
            result = cursor.fetchall()
        for row in result:
            self.last_tickets.append(LotteryTicket(*row))

    def claim(self) -> int:
        with get_cursor() as cursor:
            query = (
                "UPDATE game.lottery_ticket SET claimed = True "
                "WHERE uid = %(uid)s AND lottery_no = %(lottery_no)s "
                "AND claimed = False"
            )
            cursor.execute(query, {"lottery_no": self.no - 1, "uid": self.uid})
        rewards = 0
        for ticket in self.last_tickets:
            reward_level = 4
            for index, digit in enumerate(reversed(ticket.pick_number)):
                index = 3 - index
                if digit != self.winning_number[index]:
                    break
                reward_level -= 1
            rewards = rewards + REWARDS[reward_level]
        return rewards

    def buy(self, number: str) -> None:
        with get_cursor() as cursor:
            query = (
                "UPDATE game.player SET coin = coin - 100 WHERE uid = %(uid)s;"
                "UPDATE game.bank SET coin = coin + 100;"
                "INSERT INTO game.lottery_ticket (uid, lottery_no, "
                "pick_number) VALUES (%(uid)s, %(lottery_no)s, "
                "%(pick_number)s);"
            )
            cursor.execute(
                query,
                {
                    "uid": self.uid,
                    "lottery_no": self.no,
                    "pick_number": number,
                },
            )

    def _get_last_winning_number(self) -> None:
        with get_cursor() as cursor:
            query = (
                "SELECT lottery_no, valid_date, winning_number, update_time "
                "FROM game.lottery WHERE lottery_no = %(lottery_no)s"
            )
            cursor.execute(query, {"lottery_no": self.no - 1})
            result = cursor.fetchone()
        if result is None:
            return
        self.winning_number = result[2]
        self.valid_date = result[1]

    @staticmethod
    def get_lottery_no() -> int:
        epoch = datetime.date(2023, 12, 31)
        today = datetime.date.today()
        no = math.floor((today - epoch).days / 7) * 2
        no = no + 2 if today.weekday() in (2, 3, 4, 5) else no + 1
        return no

    @staticmethod
    def generate_winning_number() -> str:
        no = Lottery.get_lottery_no() - 1
        winning_number = f"{random.randint(0, 9999):04}"
        with get_cursor() as cursor:
            query = (
                "INSERT INTO game.lottery (lottery_no, winning_number) "
                "VALUES (%(lottery_no)s, %(winning_number)s)"
            )
            cursor.execute(query, {"lottery_no": no, "winning_number": winning_number})
        return winning_number
