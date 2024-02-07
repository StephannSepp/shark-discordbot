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
        self.max_life = life

    def take_shot(self, damage: int):
        self.life = max(self.life - damage, 0)

    @property
    def lives(self):
        text = ""
        for i in range(self.max_life):
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
    next_shot_checked = 0

    def __init__(self):
        super().__init__(BASE_LIFE + 1)

    def check_next_shot(self, bullets: list[RouletteShot]) -> RouletteShot | None:
        bullets_count = len(bullets)
        blank_count = countOf(bullets, RouletteShot.BLANK)
        if (
            4 > bullets_count > 1
            and blank_count != 0
            and blank_count != bullets_count
            and self.life < 3
            and self.next_shot_checked < 2
        ):
            if random.random() >= 1 - (bullets_count**1.5 * 0.1):
                return None
            self.next_shot_checked += 1
            return bullets[-1]
        return None

    def aim_at_player(self, bullets: list[RouletteShot]) -> bool:
        if len(bullets) == 1 and bullets[0] == RouletteShot.RANDOM:
            ratio = 50
        elif RouletteShot.RANDOM in bullets:
            ratio = int(countOf(bullets, RouletteShot.BLANK) / (len(bullets) - 1) * 100)
        else:
            ratio = int(countOf(bullets, RouletteShot.BLANK) / len(bullets) * 100)
        if ratio < 3:
            confidence = 0
        elif ratio > 97:
            confidence = 100
        else:
            confidence = round(100 / (1 + math.exp(-ratio + 50) ** 0.01))
        if confidence < 70 and self.life < 3:
            confidence -= 10 * (3 - self.life)
        confidence = min(max(confidence, 0), 100)
        return random.uniform(0, 100) > confidence

    def take_shot(self, damage: int):
        self.life = max(self.life - damage, 0)
