""" A self-use discord bot. """


import os
from contextlib import contextmanager
from datetime import datetime
from typing import Generator

import disnake
import psycopg2
import psycopg2.pool
from config import Config
from disnake import AllowedMentions
from disnake.ext import commands
from pkg_resources import parse_version
from psycopg2.extensions import cursor
from utils.time_process import parse_time
from utils.time_process import strftimedelta

__version__ = "2.6.6"


con_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=0, maxconn=16, dsn=Config.database_url, sslmode="allow"
)

OWNERS = (387573599919276032, 482210938141802517)


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

    def __init__(self):
        super().__init__(
            intents=disnake.Intents().all(),
            command_sync_flags=commands.CommandSyncFlags.all(),
            owner_ids=OWNERS,
        )
        self._start_at = datetime.now()
        self.allowed_mentions = AllowedMentions(everyone=False, roles=False)
        self.activity = disnake.Activity(
            name="シリウスの心臓",
            type=disnake.ActivityType.listening,
        )

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
    def db_up_time(self):
        try:
            with get_cursor() as cursor:
                query = "SELECT TO_CHAR(now() - pg_postmaster_start_time(), 'DD\"d\"HH24hMImSSs')"
                cursor.execute(query)
                result = cursor.fetchone()[0]
        except Exception:
            return "連線狀態不明"
        return strftimedelta(parse_time(result))

    @property
    def up_time(self):
        return strftimedelta(datetime.now() - self._start_at)

    @property
    def version(self):
        return parse_version(__version__)


if __name__ == "__main__":
    bot = Bot()
    bot.load_all_extensions("cogs")
    bot.i18n.load("locale/")
    bot.run(Config.token)
