""" A self-use discord bot. """


import os
from contextlib import contextmanager
from datetime import datetime
from typing import Generator

import disnake
import psycopg2
import psycopg2.pool
from disnake.ext import commands
from pkg_resources import parse_version
from psycopg2.extensions import cursor

from config import Config
from utils.time_process import strftimedelta

__version__ = "2.3.639"


def init_db():
    with get_cursor() as cur:
        with open("database/schema.sql", "r", encoding="utf-8") as f:
            cur.execute(f.read())


con_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=0, maxconn=16, dsn=Config.database_url, sslmode="allow"
)


@contextmanager
def get_cursor() -> Generator[cursor, None, None]:
    con = con_pool.getconn()
    try:
        with con.cursor() as cur:
            yield cur
            con.commit()
    except:
        con.rollback()
        raise
    finally:
        con_pool.putconn(con)


class Bot(commands.InteractionBot):
    def __init__(self):
        super().__init__(
            intents=disnake.Intents().all(),
            command_sync_flags=commands.CommandSyncFlags.all(),
        )
        self._start_at = datetime.now()

    def load_all_extensions(self, folder: str):
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            if os.path.isdir(path):
                self.load_extension(f"{folder}.{filename}.extension")
            else:
                self.load_extension(f"{folder}.{filename[:-3]}")

    @property
    def up_time(self):
        return strftimedelta(datetime.now() - self._start_at)

    @property
    def version(self):
        return parse_version(__version__)


if __name__ == "__main__":
    init_db()
    bot = Bot()
    bot.load_all_extensions("cogs")
    bot.run(Config.token)
