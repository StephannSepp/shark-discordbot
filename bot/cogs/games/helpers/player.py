from bot import get_cursor


class Player:
    uid: int
    gold: float
    coin: int
    is_mining: bool
    is_fishing: bool
    is_farming: bool

    def __init__(self, uid: int):
        self.uid = uid
        self._get_player(uid)

    def _get_player(self, uid: int) -> None:
        with get_cursor() as cursor:
            query = (
                "SELECT uid, gold::float, coin, is_mining, is_fishing, is_farming "
                "FROM game.player WHERE uid = %(uid)s"
            )
            cursor.execute(query, {"uid": uid})
            result = cursor.fetchone()
        if result is None:
            with get_cursor() as cursor:
                query = "INSERT INTO game.player (uid) VALUES (%(uid)s)"
                cursor.execute(query, {"uid": uid})
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

    def bank_transaction(
        self, gold_change_to_player: float = 0, coin_change_to_player: int = 0
    ):
        self.gold += gold_change_to_player
        self.coin += coin_change_to_player
        with get_cursor() as cursor:
            query = (
                "UPDATE game.player SET gold = gold + %(gold)s, coin = coin + %(coin)s "
                "WHERE uid = %(uid)s;"
                "SELECT * FROM game.bank FOR UPDATE;"
                "UPDATE game.bank SET gold = gold - %(gold)s, coin = coin - %(coin)s;"
            )
            cursor.execute(
                query,
                {
                    "uid": self.uid,
                    "gold": gold_change_to_player,
                    "coin": coin_change_to_player,
                },
            )

    def save(self) -> None:
        with get_cursor() as cursor:
            query = (
                "UPDATE game.player SET gold = %(gold)s, coin = %(coin)s,  "
                "is_mining = %(is_mining)s, is_fishing = %(is_fishing)s, "
                "is_farming = %(is_farming)s WHERE uid = %(uid)s"
            )
            cursor.execute(
                query,
                {
                    "uid": self.uid,
                    "gold": self.gold,
                    "coin": self.coin,
                    "is_mining": self.is_mining,
                    "is_fishing": self.is_fishing,
                    "is_farming": self.is_farming,
                },
            )

    @property
    def is_busy(self):
        return self.is_mining or self.is_fishing or self.is_farming
