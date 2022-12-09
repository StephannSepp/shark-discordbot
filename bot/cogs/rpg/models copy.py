"""
rpg.models
----------------

Some models for the RPGame.

:Date:
"""


import random
from dataclasses import dataclass
from datetime import datetime

import psycopg2

from config import Config
from static.rpg_boss import boss_count

@dataclass
class RPGameBase:
    """ A base class for RPGame. """

    name: str
    crystal: int
    mana: int
    luck: int
    floor: int
    skills: dict


@dataclass
class Player(RPGameBase):
    """ A class that is used to represent a RPGame player model. """

    user_id: int
    kills: int
    is_dead: str
    combo: int = 1
    hp: int = 0
    isWinner: bool = False

    def __init__(self, name, user_id, crystal, mana, luck, floor, kills, is_dead, created_at, skills):
        super().__init__(name, crystal, mana, luck, floor, skills)
        self.user_id = user_id
        self.kills = kills
        self.is_dead = is_dead
        self.created_at = created_at

    @classmethod
    def create_new(cls, name: str, user_id: int) -> object:
        query = """
            INSERT INTO players VALUES ({user_id}, 2500, 0, 50, 0, 0, 'N')
        """
        con = psycopg2.connect(Config.database_url)
        cursor = con.cursor()
        cursor.execute(query, (user_id,))
        con.commit()
        con.close()
        return cls(name, user_id, 2500, 0, 50, 0, 0, 'N', datetime.now(), {})

    @classmethod
    def fetch_player(cls, name: str, user_id: int):
        get_player_query = """
            SELECT * FROM players WHERE user_id={user_id}"
        """
        get_skills_query = """
            SELECT * FROM players_skills WHERE user_id={user_id}
        """
        con = psycopg2.connect(Config.database_url)
        cursor = con.cursor()
        cursor.execute(get_player_query, (user_id,))
        player_stats = cursor.fetchone()
        cursor.execute(get_skills_query, (user_id,))
        skills = cursor.fetchall()
        con.close()
        return cls(name, *player_stats, skills)

    @property
    def isKilled(self):
        return False if self._isDead == 'N' else True

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
