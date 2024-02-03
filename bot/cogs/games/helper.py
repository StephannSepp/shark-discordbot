import random

from bot import get_cursor

BASE_EXCHANGE_RATE = 28


def get_mining_text(rich: bool | None = None) -> list:
    text = []
    minute = random.randint(0, 15)
    if rich is None:
        action_stage = "NORMAL"
    elif rich:
        action_stage = "POSITIVE"
    else:
        action_stage = "NEGATIVE"
    with get_cursor() as cursor:
        query = (
            "SELECT action_text FROM game.action_text "
            "WHERE action_type = 'MINING' AND action_stage = 'START' "
            "ORDER BY Random() LIMIT 1"
        )
        cursor.execute(query)
        mining_start = cursor.fetchone()[0]
        query = (
            "SELECT action_text FROM game.action_text "
            "WHERE action_type = 'MINING' AND action_stage = %(action_stage)s "
            "ORDER BY Random() LIMIT 5"
        )
        cursor.execute(query, {"action_stage": action_stage})
        result = cursor.fetchall()
        mining_progress = [row[0] for row in result]
    text.append((f"0 小時 {minute:02} 分", mining_start))
    hours = sorted(random.sample(range(1, 6), 3))
    broken = False
    broke_at = 0
    for index, hour in enumerate(hours):
        if hour == broke_at + 1:
            continue
        minute = random.randint(10, 50)
        broken = random.random() <= (0.3 if rich is False else 0.15) and not rich
        if broken:
            broke_at = hour
            with get_cursor() as cursor:
                query = (
                    "SELECT action_text FROM game.action_text "
                    "WHERE action_type = 'MINING' AND action_stage = 'ACCIDENT' "
                    "ORDER BY Random() LIMIT 1"
                )
                cursor.execute(query)
                mining_accident = cursor.fetchone()[0]
                query = (
                    "SELECT action_text FROM game.action_text "
                    "WHERE action_type = 'MINING' AND action_stage = 'SOLVED' "
                    "ORDER BY Random() LIMIT 1"
                )
                cursor.execute(query)
                mining_solved = cursor.fetchone()[0]
            text.append((f"{hour} 小時 {minute:02} 分", mining_accident))
            broken = False
            if hour >= 6:
                continue
            minute = random.randint(10, 50)
            text.append((f"{hour + 1} 小時 {minute:02} 分", mining_solved))
        else:
            text.append((f"{hour} 小時 {minute:02} 分", mining_progress[index]))
    if rich is None:
        action_stage = "NORMAL_END"
    elif rich:
        action_stage = "POSITIVE_END"
    else:
        action_stage = "NEGATIVE_END"
    with get_cursor() as cursor:
        query = (
            "SELECT action_text FROM game.action_text "
            "WHERE action_type = 'MINING' AND action_stage = %(action_stage)s "
            "ORDER BY Random() LIMIT 1"
        )
        cursor.execute(query, {"action_stage": action_stage})
        mining_result = cursor.fetchone()[0]
    text.append(("7 小時 00 分", mining_result))
    return text
