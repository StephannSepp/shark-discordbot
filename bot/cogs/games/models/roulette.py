import math
import random
from enum import Enum
from operator import countOf

BASE_LIFE = 5


class RouletteShot(Enum):
    BLANK = "<:Shotgun_Shell_Green:1202947686911844433>"
    LIVE = "<:Shotgun_Shell:1202947684877471774>"
    SLUG = "<:Shotgun_Shell_Black:1203509902782369792>"
    RANDOM = "<:Shotgun_Shell_White:1203990875135287317>"

    def __lt__(self, other: "RouletteShot"):
        return self.name < other.name

    def __gt__(self, other: "RouletteShot"):
        return self.name > other.name


class BaseRoulettePlayer:
    def __init__(self, life: int = BASE_LIFE):
        self.life = life

    def take_shot(self, damage: int):
        self.life = max(self.life - damage, 0)

    @property
    def lives(self):
        text = ""
        for i in range(BASE_LIFE):
            if i < self.life:
                text += "❤️"
            else:
                text += "💔"
        return text


class RoulettePlayer(BaseRoulettePlayer):
    pop_chance = 2
    shoot_dealer_attampt = 0
    shot_at_dealer = 0
    shoot_self_attampt = 0
    shot_at_self = 0
    shot_taken_from_dealer = 0
    pop_shot = 0


class RouletteDealer(BaseRoulettePlayer):
    sanity = 0

    def aim_at_player(self, bullets: list[RouletteShot]) -> bool:
        if len(bullets) == 1 and bullets[0] == RouletteShot.RANDOM:
            ratio = 50
        elif RouletteShot.RANDOM in bullets:
            ratio = 100 - int(
                countOf(bullets, RouletteShot.BLANK) / (len(bullets) - 1) * 100
            )
        else:
            ratio = 100 - int(countOf(bullets, RouletteShot.BLANK) / len(bullets) * 100)
        if ratio < 3:
            ratio = 0
        elif ratio > 97:
            ratio = 100
        else:
            ratio = round(100 / (1 + math.exp(-ratio + 50) ** 0.08))
        sanity = min(max(math.floor(self.sanity**2 / 250), 0), 100)
        sanity = sanity * math.copysign(1, self.sanity)
        weight = min(max(ratio + sanity, 0), 100)
        weights = (100 - weight, weight)
        return random.choices((False, True), weights)[0]

    def take_shot(self, damage: int):
        self.life = max(self.life - damage, 0)
        self.sanity = self.sanity + (15 * damage)

    def sanitize(self):
        self.sanity = self.sanity + 6 * (-math.copysign(1, self.sanity))
