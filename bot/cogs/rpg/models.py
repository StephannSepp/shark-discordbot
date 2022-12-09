"""
rpg.models
----------------

Some models for the RPGame.

:Date:
"""


import random
from dataclasses import dataclass
from datetime import datetime

from static.rpg_boss import boss_count


@dataclass
class Player:
    """ A class that is used to represent a RPGame player model. """

    name: str
    user_id: int
    crystal: int
    mana: int
    luck: int
    floor: int
    kills: int
    _isDead: str
    created_at: datetime

    def __post_init__(self):
        self.isWinner = False
        self.isKilled = False if self._isDead == 'N' else True
        self.combo = 1
        self.hp = 0

    def damage(self, damage: int) -> int:
        """ Giving damage to the player.
        The hp number cannot go below 0.

        :param damage: The damage given to the player.

        :return hp: The new hp number.
        """
        self.hp -= damage
        self.hp = max(self.hp, 0)
        return self.hp

    def action_work(self) -> tuple[int, str]:
        """ For actions,
        Get a random salary number and add to the crystal.

        :return salary: The number of crystals player get.
        :return event: An event str.
        """
        event = ""
        salary = random.randint(-29, 60)
        if salary < 1:
            salary -= 1
        self.crystal += salary
        self.crystal = max(self.crystal, 0)
        return salary, event

    def action_charity(self) -> tuple[int, str]:
        """ For actions,
        Get a random luck number and add to the crystal.

        :return salary: The number of luck player get.
        :return event: An event str.
        """
        event = ""
        luck = random.randint(-2, 6)
        if luck < 1:
            luck -= 1
        self.luck += luck
        self.luck = max(min(self.luck, 255), 0)
        return luck, event

    def update_crystal(self, n: int) -> int:
        """ Update player's crystal number.

        :param n:
            The crystal number that adds to the player.
            Can be a negative number.

        :return crystal: The new cystal number.
        """
        self.crystal += n
        self.crystal = max(self.crystal, 0)
        return self.crystal

    def add_floor(self) -> int:
        """ Add a floor by 1.

        :return new_floor: New floor.
        """
        if self.floor < boss_count:
            self.floor += 1
        return self.floor

@dataclass
class Boss:
    """ A class that is used to represent a RPGame boss model. """

    name: str
    crystal: int
    mana: int
    luck: int
    floor: int
    skills: dict
    url: str

    def __post_init__(self):
        self.user_id = None
        self.kills = 0
        self._isDead = 'N'
        self.created_at = None
        self.isWinner = False
        self.isKilled = False if self._isDead == 'N' else True
        self.combo = 1
        self.hp = 0

    def damage(self, damage: int) -> int:
        """ Giving damage to the player.
        The hp number cannot go below 0.

        :param damage: The damage given to the player.

        :return hp: The new hp number.
        """
        self.hp -= damage
        self.hp = max(self.hp, 0)
        return self.hp
