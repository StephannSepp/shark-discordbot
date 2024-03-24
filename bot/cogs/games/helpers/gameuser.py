from bot import get_cursor


class GameUser:
    uid: int
    gold: float
    coin: int
    is_mining: bool
    is_fishing: bool
    is_farming: bool

    def __init__(self, uid: int):
        self.uid = uid

    @classmethod
    async def fetch(cls, uid: int):
        self = cls(uid)
        await self._get_player(uid)
        return self

    async def _get_player(self, uid: int) -> None:
        async with get_cursor() as cursor:
            query = (
                "SELECT uid, gold::float, coin, is_mining, is_fishing, is_farming "
                "FROM game.player WHERE uid = %(uid)s"
            )
            await cursor.execute(query, {"uid": uid})
            result = await cursor.fetchone()
        if result is None:
            async with get_cursor() as cursor:
                query = "INSERT INTO game.player (uid) VALUES (%(uid)s)"
                await cursor.execute(query, {"uid": uid})
            self.gold = 0
            self.coin = 8690
            self.is_mining = False
            self.is_fishing = False
            self.is_farming = False
        else:
            self.gold = result[1]
            self.coin = result[2]
            self.is_mining = result[3]
            self.is_fishing = result[4]
            self.is_farming = result[5]

    async def get_action_stats(self, action_type: str) -> dict:
        params = {"uid": self.uid, "action_type": action_type}
        async with get_cursor() as cursor:
            query = (
                "SELECT count(*), COALESCE(SUM(profit), 0) FROM game.action "
                "WHERE uid = %(uid)s AND action_type = %(action_type)s"
            )
            await cursor.execute(query, params)
            result = await cursor.fetchone()
        return {"count": result[0], "profit": result[1]}

    async def bank_transaction(
        self,
        gold_change_to_player: float = 0,
        coin_change_to_player: int = 0,
        note: str = "",
    ) -> int:
        self.gold += gold_change_to_player
        self.coin += coin_change_to_player
        params = {
            "uid": self.uid,
            "gold": gold_change_to_player,
            "coin": coin_change_to_player,
            "inv_gold": -gold_change_to_player,
            "inv_coin": -coin_change_to_player,
            "note": note,
        }
        async with get_cursor() as cursor:
            query = (
                "UPDATE game.player SET gold = gold + %(gold)s, coin = coin + %(coin)s "
                "WHERE uid = %(uid)s"
            )
            await cursor.execute(query, params)
            query = "SELECT * FROM game.bank FOR UPDATE"
            await cursor.execute(query)
            query = "UPDATE game.bank SET gold = gold - %(gold)s,coin = coin - %(coin)s"
            await cursor.execute(query, params)
            query = (
                "INSERT INTO game.bank_transaction "
                "(uid, gold_change, coin_change, txn_note) VALUES "
                "(%(uid)s, %(inv_gold)s, %(inv_coin)s, %(note)s) RETURNING txn_id;"
            )
            await cursor.execute(query, params)
            txn_id = (await cursor.fetchone())[0]
        return txn_id

    async def save(self) -> None:
        params = {
            "uid": self.uid,
            "gold": self.gold,
            "coin": self.coin,
            "is_mining": self.is_mining,
            "is_fishing": self.is_fishing,
            "is_farming": self.is_farming,
        }
        async with get_cursor() as cursor:
            query = (
                "UPDATE game.player SET gold = %(gold)s, coin = %(coin)s,  "
                "is_mining = %(is_mining)s, is_fishing = %(is_fishing)s, "
                "is_farming = %(is_farming)s WHERE uid = %(uid)s"
            )
            await cursor.execute(query, params)

    @property
    def is_busy(self):
        return self.is_mining or self.is_fishing or self.is_farming
