import hashlib
import random

from disnake.utils import escape_markdown


class BaseEntity:
    name: str
    health_point: int
    strength: int
    dexterity: int
    constitution: int
    luck: int

    def do_damage(self, seed: int) -> int:
        CRITICAL_RATE = self.luck / 255
        DAMAGE_LOW = round(self.strength * (1 - CRITICAL_RATE))
        DAMAGE_HIGH = round(self.strength * (1 + CRITICAL_RATE))
        random.seed(seed)
        return random.randint(DAMAGE_LOW, DAMAGE_HIGH)

    def do_defend(self, damage: int, seed: int) -> int:
        random.seed(seed)
        return round((damage * damage * 1.5) / (damage + self.constitution))


class Player(BaseEntity):
    attack: int = 0
    defence: int = 0

    def __init__(self, name: str, user_id: int):
        self.name = escape_markdown(name)
        raw_stats = hashlib.md5(str(user_id).encode()).digest()
        (
            self.strength,
            self.dexterity,
            self.constitution,
            self.luck,
            *stats,
        ) = raw_stats
        self.health_point = sum(stats[:3])
        self.health_point += 1
        self.strength += 1
        self.dexterity += 1
        self.constitution += 1
        self.luck += 1

    def do_damage(self, seed: int) -> int:
        return super().do_damage(seed) + self.attack

    def do_defend(self, damage: int, seed: int) -> int:
        return max(super().do_defend(damage, seed) - self.defence, 0)
