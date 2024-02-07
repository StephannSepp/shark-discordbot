import datetime
import math
import random

from bot import get_cursor

from .constants import BASE_EXCHANGE_RATE


class Bank:
    gold: float
    coin: int
    reserve_gold: float

    def __init__(self) -> None:
        with get_cursor() as cursor:
            query = "SELECT gold::float, coin, reserve_gold::float FROM game.bank"
            cursor.execute(query)
            result = cursor.fetchone()
        self.gold = result[0]
        self.coin = result[1]
        self.reserve_gold = result[2]

    def gold_to_coin(self) -> float:
        last_gold_hold = self.gold
        self.gold += round(random.normalvariate(192, 24), 1)
        self.coin += math.floor(self.gold * 0.6 * BASE_EXCHANGE_RATE)
        self.reserve_gold += math.floor(self.gold * 4) / 10
        self.gold = 0
        self.save()
        return last_gold_hold

    def save(self) -> None:
        with get_cursor() as cursor:
            query = (
                "UPDATE game.bank "
                "SET gold = %(gold)s, coin = %(coin)s, reserve_gold = %(reserve_gold)s"
            )
            cursor.execute(
                query,
                {
                    "gold": self.gold,
                    "coin": self.coin,
                    "reserve_gold": self.reserve_gold,
                },
            )


class ExchangeRate:
    exchange_rate: float
    valid_date: datetime.date

    def __init__(self):
        self.update_exchange_rate()

    def update_exchange_rate(self) -> None:
        today = datetime.datetime.utcnow().date()
        with get_cursor() as cursor:
            query = (
                "SELECT valid_date, exchange_rate::float FROM game.exchange_rate "
                "ORDER BY valid_date DESC LIMIT 1"
            )
            cursor.execute(query)
            result = cursor.fetchone()
        if result[0] == today:
            self.valid_date = result[0]
            self.exchange_rate = result[1]
        else:
            self.rate = self._calc_new_exchange_rate()
            self.valid_date = today

    def get_recent_exchange_rate(self, limit: int = 30) -> dict:
        with get_cursor() as cursor:
            query = (
                "SELECT valid_date, exchange_rate::float FROM game.exchange_rate "
                "ORDER BY valid_date DESC LIMIT %(limit)s"
            )
            cursor.execute(query, {"limit": limit})
            result = cursor.fetchall()
        return {r[0]: r[1] for r in result}

    def _calc_new_exchange_rate(self) -> float:
        today = datetime.datetime.utcnow().date()
        yesterday = today - datetime.timedelta(1)
        bank = Bank()
        last_gold_hold = bank.gold_to_coin()
        with get_cursor() as cursor:
            query = (
                "SELECT SUM(profit)::float FROM game.action "
                "WHERE action_type = 'MINING' "
                "AND end_at BETWEEN %(yesterday)s AND %(today)s"
            )
            cursor.execute(query, {"yesterday": yesterday, "today": today})
            last_gold_mined = cursor.fetchone()[0] or 0
            query = (
                "SELECT AVG(last_day_gold_sold)::float FROM game.exchange_rate "
                "WHERE valid_date > CURRENT_DATE - INTERVAL '7 days'"
            )
            cursor.execute(query)
            recent_avg_income = cursor.fetchone()[0] or 0
            query = (
                "SELECT exchange_rate::float, trend::float FROM game.exchange_rate "
                "WHERE valid_date BETWEEN %(yesterday)s AND %(today)s"
            )
            cursor.execute(query, {"yesterday": yesterday, "today": today})
            result = cursor.fetchone()
            rate, trend = result

        if rate > BASE_EXCHANGE_RATE + 1.4:
            normalize_modifier = 0.5 - 0.25
        elif rate > BASE_EXCHANGE_RATE + 0.93:
            normalize_modifier = 0.9 - 0.25
        elif rate > BASE_EXCHANGE_RATE + 0.47:
            normalize_modifier = 0.95 - 0.25
        elif rate < BASE_EXCHANGE_RATE - 1.4:
            normalize_modifier = 1.05 - 0.25
        elif rate < BASE_EXCHANGE_RATE - 0.93:
            normalize_modifier = 1.1 - 0.25
        elif rate < BASE_EXCHANGE_RATE - 0.47:
            normalize_modifier = 1.5 - 0.25
        else:
            normalize_modifier = 1 - 0.25
        trend_modifier = math.log(
            (last_gold_mined + 1) * normalize_modifier / (recent_avg_income + 1)
        )
        trend = round(trend + trend_modifier * 0.01, 6)
        trend = max(min(trend, 0.97), 0.03)
        sign = 1 if random.random() < trend else -1
        rate_change = math.sqrt(abs(random.normalvariate(0, trend - 0.5))) * 0.02 * sign
        rate = round(rate + rate_change, 3)
        with get_cursor() as cursor:
            query = (
                "INSERT INTO game.exchange_rate (exchange_rate, last_day_gold_mined, "
                "last_day_gold_sold, trend) VALUES (%(rate)s, %(gold_mined)s, "
                "%(gold_sold)s, %(trend)s)"
            )
            cursor.execute(
                query,
                {
                    "rate": rate,
                    "gold_mined": last_gold_mined,
                    "gold_sold": last_gold_hold,
                    "trend": trend,
                },
            )
        return rate
