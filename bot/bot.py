""" A self-use discord bot. """


import os
from contextlib import closing
from datetime import datetime

import disnake
import psycopg2
from disnake.ext import commands
from pkg_resources import parse_version

from config import Config
from utils.time_process import strftimedelta

__version__ = "2.2.532"


def init_db():
    with closing(connect_db()) as db:
        with open("database/schema.sql", "r") as f:
            db.cursor().execute(f.read())
        db.commit()


def connect_db():
    return psycopg2.connect(Config.database_url, sslmode="allow")


class Bot(commands.InteractionBot):
    def __init__(self):
        super().__init__(
            intents=disnake.Intents().all(),
            command_sync_flags=commands.CommandSyncFlags.all()
        )
        self._start_time = datetime.now()

    def load_all_extensions(self, folder: str):
        """ Load all Disnake cogs as extensions under a specific folder.

        :param folder: A pathlike string indicate the folder location.
        """
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            if os.path.isdir(path):
                self.load_extension(f"{folder}.{filename}.extension")
            else:
                self.load_extension(f"{folder}.{filename[:-3]}")

    @property
    def up_time(self):
        return strftimedelta(datetime.now() - self._start_time)

    @property
    def version(self):
        return parse_version(__version__)


if __name__ == "__main__":
    init_db()
    bot = Bot()
    bot.load_all_extensions('cogs')
    bot.run(Config.token)
