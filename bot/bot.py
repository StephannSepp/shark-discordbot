""" A self-use discord bot. """


import os
from contextlib import contextmanager
from datetime import datetime
from typing import Generator

import disnake
import psycopg2
import psycopg2.pool
from disnake import AllowedMentions
from disnake.ext import commands
from pkg_resources import parse_version
from psycopg2.extensions import cursor

from config import Config
from utils.time_process import strftimedelta

__version__ = "2.4.5"


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
    main_guild = None
    debug_guild = None
    owner_id = 387573599919276032

    def __init__(self):
        super().__init__(
            intents=disnake.Intents().all(),
            command_sync_flags=commands.CommandSyncFlags.all(),
        )
        self._start_at = datetime.now()
        self.allowed_mentions = AllowedMentions(everyone=False, roles=False)

    def load_all_extensions(self, folder: str):
        for ext_name in os.listdir(folder):
            if ext_name.startswith("_"):
                continue
            path = os.path.join(folder, ext_name)
            if os.path.isdir(path):
                self.load_extension(f"{folder}.{ext_name}.extension")
            else:
                self.load_extension(f"{folder}.{ext_name[:-3]}")

    async def getch_guild(self, id_: int):
        guild = self.get_guild(id_)
        if guild is None:
            guild = await self.fetch_guild(id_)
        return guild

    async def on_ready(self):
        main_guild_id = Config.home_guild
        debug_guild_id = Config.debug_guild
        self.main_guild = await self.getch_guild(main_guild_id)
        self.debug_guild = await self.getch_guild(debug_guild_id)

    @property
    def up_time(self):
        return strftimedelta(datetime.now() - self._start_at)

    @property
    def version(self):
        return parse_version(__version__)


if __name__ == "__main__":
    bot = Bot()
    bot.load_all_extensions("cogs")
    bot.run(Config.token)
