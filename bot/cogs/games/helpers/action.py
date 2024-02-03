import datetime
import math
import random
from enum import Enum

from bot import get_cursor


class ActionStatus(Enum):
    STARTED = "STARTED"
    DONE = "DONE"


class Mining:
    action_id: int | None = None
    uid: int
    start_at: datetime.datetime | None = None
    status: ActionStatus = None
    end_at: datetime.datetime | None = None
    PB_FINISHED = "<:minecraft_gold_nugget:1199002510942294026>"
    PB_CURRENT = "<:minecraft_pickaxe:1199002509302308905>"
    PB_UNFINISH = "<:minecraft_stone:1199002505699409940>"
    BASE_TIME = 7 * 60 * 60

    def __init__(self, uid: int):
        self.uid = uid
        self._set_active_action(uid)

    def _set_active_action(self, uid: int) -> None:
        with get_cursor() as cursor:
            query = (
                "SELECT action_id, start_at, status FROM game.action "
                "WHERE uid = %(uid)s AND action_type = 'MINING' AND status = 'STARTED' "
                "ORDER BY start_at DESC LIMIT 1"
            )
            cursor.execute(query, {"uid": uid})
            result = cursor.fetchone()
        if result is None:
            return
        self.action_id = result[0]
        self.start_at = result[1]
        self.status = ActionStatus(result[2])

    def start_action(self) -> None:
        with get_cursor() as cursor:
            query = (
                "INSERT INTO game.action (action_type, uid) VALUES ('MINING', %(uid)s);"
                "UPDATE game.player SET is_mining = True WHERE uid = %(uid)s;"
            )
            cursor.execute(query, {"uid": self.uid})

    def end_action(self) -> float:
        profit = max(round(random.normalvariate(64, 8), 1), 0)
        with get_cursor() as cursor:
            query = (
                "UPDATE game.action SET profit = %(profit)s, "
                "status = 'DONE', end_at = CURRENT_TIMESTAMP "
                "WHERE uid = %(uid)s AND action_id = %(action_id)s;"
                "UPDATE game.player SET gold = gold + %(profit)s, "
                "is_mining = False WHERE uid = %(uid)s;"
            )
            cursor.execute(
                query, {"profit": profit, "uid": self.uid, "action_id": self.action_id}
            )
        return profit

    def draw_progress(self) -> str | None:
        if self.action_id is None:
            self.start_at = datetime.datetime.now()
        now = datetime.datetime.utcnow()
        step = math.floor((now - self.start_at).total_seconds() / self.BASE_TIME * 10)
        progress = []
        for i in range(1, 11):
            if i < step + 1:
                e = self.PB_FINISHED
            elif i == step + 1:
                e = self.PB_CURRENT
            elif i > step + 1:
                e = self.PB_UNFINISH
            progress.append(e)
        return "".join(progress)


class Fishing:
    action_id: int | None = None
    uid: int
    start_at: datetime.datetime | None = None
    status: ActionStatus = None
    end_at: datetime.datetime | None = None
    PB_FINISHED = "<:minecraft_raw_cod:1200101327548723340>"
    PB_CURRENT = "<:minecraft_fishing_rod:1200101325799698522>"
    PB_UNFINISH = "<:minecraft_water:1200101330887393290>"
    BASE_TIME = 4 * 60 * 60

    def __init__(self, uid: int):
        self.uid = uid
        self._set_active_action(uid)

    def _set_active_action(self, uid: int) -> None:
        with get_cursor() as cursor:
            query = (
                "SELECT action_id, start_at, status FROM game.action "
                "WHERE uid = %(uid)s AND action_type = 'FISHING' "
                "AND status = 'STARTED' ORDER BY start_at DESC LIMIT 1"
            )
            cursor.execute(query, {"uid": uid})
            result = cursor.fetchone()
        if result is None:
            return
        self.action_id = result[0]
        self.start_at = result[1]
        self.status = ActionStatus(result[2])

    def start_action(self) -> None:
        with get_cursor() as cursor:
            query = (
                "INSERT INTO game.action (action_type, uid) VALUES ('FISHING', %(uid)s)"
                "; UPDATE game.player SET is_fishing = True WHERE uid = %(uid)s;"
            )
            cursor.execute(query, {"uid": self.uid})

    def end_action(self) -> float:
        profit = max(round(random.normalvariate(527, 16)), 0)
        with get_cursor() as cursor:
            query = (
                "UPDATE game.action SET profit = %(profit)s, "
                "status = 'DONE', end_at = CURRENT_TIMESTAMP "
                "WHERE uid = %(uid)s AND action_id = %(action_id)s;"
                "UPDATE game.player SET coin = coin + %(profit)s, "
                "is_fishing = False WHERE uid = %(uid)s;"
            )
            cursor.execute(
                query, {"profit": profit, "uid": self.uid, "action_id": self.action_id}
            )
        return profit

    def draw_progress(self) -> str:
        if self.action_id is None:
            self.start_at = datetime.datetime.now()
        now = datetime.datetime.utcnow()
        step = math.floor((now - self.start_at).total_seconds() / self.BASE_TIME * 10)
        progress = []
        for i in range(1, 11):
            if i < step + 1:
                e = self.PB_FINISHED
            elif i == step + 1:
                e = self.PB_CURRENT
            elif i > step + 1:
                e = self.PB_UNFINISH
            progress.append(e)
        return "".join(progress)
