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
    BASE_HOUR = 7
    BASE_TIME = BASE_HOUR * 60 * 60

    @classmethod
    async def mining(cls, uid: int):
        self = cls()
        self.uid = uid
        await self._set_active_action(uid)
        return self

    async def _set_active_action(self, uid: int) -> None:
        async with get_cursor() as cursor:
            query = (
                "SELECT action_id, start_at, status FROM game.action "
                "WHERE uid = %(uid)s AND action_type = 'MINING' AND status = 'STARTED' "
                "ORDER BY start_at DESC LIMIT 1"
            )
            await cursor.execute(query, {"uid": uid})
            result = await cursor.fetchone()
        if result is None:
            return
        self.action_id = result[0]
        self.start_at = result[1]
        self.status = ActionStatus(result[2])

    async def start_action(self, message: str) -> None:
        async with get_cursor() as cursor:
            query = (
                "INSERT INTO game.action (action_type, uid, message) VALUES "
                "('MINING', %(uid)s, %(message)s)"
            )
            await cursor.execute(query, {"uid": self.uid, "message": message})
            query = "UPDATE game.player SET is_mining = True WHERE uid = %(uid)s"
            await cursor.execute(query, {"uid": self.uid})

    async def end_action(self) -> float:
        profit = max(round(random.normalvariate(64, 8), 1), 0)
        params = {"profit": profit, "uid": self.uid, "action_id": self.action_id}
        async with get_cursor() as cursor:
            query = (
                "UPDATE game.action SET profit = %(profit)s, "
                "status = 'DONE', end_at = CURRENT_TIMESTAMP "
                "WHERE uid = %(uid)s AND action_id = %(action_id)s"
            )
            await cursor.execute(query, params)
            query = (
                "UPDATE game.player SET gold = gold + %(profit)s, "
                "is_mining = False WHERE uid = %(uid)s"
            )
            await cursor.execute(query, params)
        return profit

    async def get_other_workers(self) -> list[tuple[int, str]]:
        async with get_cursor() as cursor:
            query = (
                "SELECT uid, message FROM game.action "
                "WHERE status = 'STARTED' AND action_type = 'MINING' "
                "ORDER BY start_at DESC"
            )
            await cursor.execute(query)
            result = await cursor.fetchall()
        workers = [(row[0], row[1]) for row in result]
        return workers

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
    BASE_HOUR = 2
    BASE_TIME = BASE_HOUR * 60 * 60

    @classmethod
    async def fishing(cls, uid: int):
        self = cls()
        self.uid = uid
        await self._set_active_action(uid)
        return self

    async def _set_active_action(self, uid: int) -> None:
        async with get_cursor() as cursor:
            query = (
                "SELECT action_id, start_at, status FROM game.action "
                "WHERE uid = %(uid)s AND action_type = 'FISHING' "
                "AND status = 'STARTED' ORDER BY start_at DESC LIMIT 1"
            )
            await cursor.execute(query, {"uid": uid})
            result = await cursor.fetchone()
        if result is None:
            return
        self.action_id = result[0]
        self.start_at = result[1]
        self.status = ActionStatus(result[2])

    async def start_action(self, message: str) -> None:
        params = {"uid": self.uid, "message": message}
        async with get_cursor() as cursor:
            query = (
                "INSERT INTO game.action (action_type, uid, message) VALUES "
                "('FISHING', %(uid)s, %(message)s)"
            )
            await cursor.execute(query, params)
            query = "UPDATE game.player SET is_fishing = True WHERE uid = %(uid)s"
            await cursor.execute(query, params)

    async def end_action(self) -> float:
        profit = max(round(random.normalvariate(384, 24)), 0)
        params = {"profit": profit, "uid": self.uid, "action_id": self.action_id}
        async with get_cursor() as cursor:
            query = (
                "UPDATE game.action SET profit = %(profit)s, "
                "status = 'DONE', end_at = CURRENT_TIMESTAMP "
                "WHERE uid = %(uid)s AND action_id = %(action_id)s"
            )
            await cursor.execute(query, params)
            query = (
                "UPDATE game.player SET coin = coin + %(profit)s, "
                "is_fishing = False WHERE uid = %(uid)s;"
            )
            await cursor.execute(query, params)
        return profit

    async def get_other_workers(self) -> list[tuple[int, str]]:
        async with get_cursor() as cursor:
            query = (
                "SELECT uid, message FROM game.action "
                "WHERE status = 'STARTED' AND action_type = 'FISHING' "
                "ORDER BY start_at DESC"
            )
            await cursor.execute(query)
            result = await cursor.fetchall()
        workers = [(row[0], row[1]) for row in result]
        return workers

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
