import datetime
import math
import random

from bot import get_cursor

from .constants import BASE_EXCHANGE_RATE


class Bank:
    gold: float
    coin: int
    reserve_gold: float

    @classmethod
    async def bank(cls):
        self = cls()
        async with get_cursor() as cursor:
            query = "SELECT gold::float, coin, reserve_gold::float FROM game.bank"
            await cursor.execute(query)
            result = await cursor.fetchone()
        self.gold = result[0]
        self.coin = result[1]
        self.reserve_gold = result[2]
        return self

    async def gold_to_coin(self) -> float:
        last_gold_hold = self.gold
        self.gold += round(random.normalvariate(192, 24), 1)
        self.coin += math.floor(self.gold * 0.6 * BASE_EXCHANGE_RATE)
        self.reserve_gold += math.floor(self.gold * 4) / 10
        self.gold = 0
        await self.save()
        return last_gold_hold

    async def save_fin(self) -> None:
        today = datetime.datetime.utcnow().date()
        async with get_cursor() as cursor:
            query = (
                "SELECT fin_date FROM game.bank_financial "
                "ORDER BY fin_date DESC LIMIT 1"
            )
            await cursor.execute(query)
            result = await cursor.fetchone()
        if result[0] == today:
            return
        params = {"gold": (self.gold + self.reserve_gold) * 28, "coin": self.coin}
        async with get_cursor() as cursor:
            query = (
                "INSERT INTO game.bank_financial (gold, coin) "
                "VALUES (%(gold)s, %(coin)s)"
            )
            await cursor.execute(query, params)

    async def save(self) -> None:
        params = {
            "gold": self.gold,
            "coin": self.coin,
            "reserve_gold": self.reserve_gold,
        }
        async with get_cursor() as cursor:
            query = (
                "UPDATE game.bank "
                "SET gold = %(gold)s, coin = %(coin)s, reserve_gold = %(reserve_gold)s"
            )
            await cursor.execute(query, params)


class ExchangeRate:
    exchange_rate: float
    valid_date: datetime.date

    @classmethod
    async def create(cls):
        self = cls()
        await self.update_exchange_rate()
        return self

    async def update_exchange_rate(self) -> None:
        today = datetime.datetime.utcnow().date()
        async with get_cursor() as cursor:
            query = (
                "SELECT valid_date, exchange_rate::float FROM game.exchange_rate "
                "ORDER BY valid_date DESC LIMIT 1"
            )
            await cursor.execute(query)
            result = await cursor.fetchone()
        if result[0] == today:
            self.valid_date = result[0]
            self.exchange_rate = result[1]
        else:
            self.exchange_rate = await self._calc_new_exchange_rate()
            self.valid_date = today

    async def get_recent_exchange_rate(self, limit: int = 30) -> dict:
        async with get_cursor() as cursor:
            query = (
                "SELECT valid_date, exchange_rate::float FROM game.exchange_rate "
                "ORDER BY valid_date DESC LIMIT %(limit)s"
            )
            await cursor.execute(query, {"limit": limit})
            result = await cursor.fetchall()
        return {r[0]: r[1] for r in result}

    async def _calc_new_exchange_rate(self) -> float:
        today = datetime.datetime.utcnow().date()
        yesterday = today - datetime.timedelta(1)
        bank = await Bank.bank()
        last_gold_hold = await bank.gold_to_coin()
        params = {"yesterday": yesterday, "today": today}
        async with get_cursor() as cursor:
            query = (
                "SELECT SUM(profit)::float FROM game.action "
                "WHERE action_type = 'MINING' "
                "AND end_at BETWEEN %(yesterday)s AND %(today)s"
            )
            await cursor.execute(query, params)
            last_gold_mined = (await cursor.fetchone())[0] or 0
            query = (
                "SELECT AVG(last_day_gold_sold)::float FROM game.exchange_rate "
                "WHERE valid_date > CURRENT_DATE - INTERVAL '7 days'"
            )
            await cursor.execute(query)
            recent_avg_income = (await cursor.fetchone())[0] or 0
            query = (
                "SELECT exchange_rate::float, trend::float FROM game.exchange_rate "
                "WHERE valid_date BETWEEN %(yesterday)s AND %(today)s"
            )
            await cursor.execute(query, params)
            result = await cursor.fetchone()
            rate, trend = result

        if rate > BASE_EXCHANGE_RATE + 1.4:
            normalize_modifier = 0.05
        elif rate > BASE_EXCHANGE_RATE + 0.93:
            normalize_modifier = 0.33
        elif rate > BASE_EXCHANGE_RATE + 0.47:
            normalize_modifier = 0.5
        elif rate < BASE_EXCHANGE_RATE - 1.4:
            normalize_modifier = 1.29
        elif rate < BASE_EXCHANGE_RATE - 0.93:
            normalize_modifier = 1.01
        elif rate < BASE_EXCHANGE_RATE - 0.47:
            normalize_modifier = 0.84
        else:
            normalize_modifier = 0.67
        trend_modifier = math.log(
            (last_gold_mined + 1) * normalize_modifier / (recent_avg_income + 1)
        )
        trend = round(trend + trend_modifier * 0.01, 6)
        trend = max(min(trend, 0.97), 0.03)
        sign = 1 if random.random() < trend else -1
        rate_change = math.sqrt(abs(random.normalvariate(0, trend - 0.5))) * 0.02 * sign
        rate = round(rate + rate_change, 3)
        params = {
            "rate": rate,
            "gold_mined": last_gold_mined,
            "gold_sold": last_gold_hold,
            "trend": trend,
        }
        async with get_cursor() as cursor:
            query = (
                "INSERT INTO game.exchange_rate (exchange_rate, last_day_gold_mined, "
                "last_day_gold_sold, trend) VALUES (%(rate)s, %(gold_mined)s, "
                "%(gold_sold)s, %(trend)s)"
            )
            await cursor.execute(query, params)
        return rate


async def get_top_ranking(uid: int) -> list[dict]:
    async with get_cursor() as cursor:
        query = (
            "WITH temp_table AS (SELECT uid, gold * ("
            "SELECT exchange_rate FROM game.exchange_rate "
            "ORDER BY valid_date DESC LIMIT 1) + coin AS total_assets "
            "FROM game.player ORDER BY total_assets DESC) "
            "SELECT * FROM (SELECT uid, total_assets, ROW_NUMBER() OVER ("
            "ORDER BY total_assets DESC) AS pos FROM temp_table)"
            "WHERE uid = %(uid)s OR pos <= 10"
        )
        await cursor.execute(query, {"uid": uid})
        result = await cursor.fetchall()
    return [
        {"uid": row[0], "total_assets": row[1], "position": row[2]} for row in result
    ]
