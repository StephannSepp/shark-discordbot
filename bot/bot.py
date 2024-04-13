""" A self-use discord bot. """

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

import disnake
from config import Config
from disnake import AllowedMentions
from disnake.ext import commands
from pkg_resources import parse_version
from psycopg import AsyncCursor
from psycopg_pool import AsyncConnectionPool
from utils.time_process import parse_time
from utils.time_process import strftimedelta

__version__ = "2.7.3"


conn_pool = AsyncConnectionPool(conninfo=Config.database_url, open=False)
vchive_pool = AsyncConnectionPool(conninfo=Config.vchive_db_url, open=False)
OWNERS = (387573599919276032, 482210938141802517)


@asynccontextmanager
async def get_cursor() -> AsyncGenerator[AsyncCursor, None]:
    await conn_pool.open()
    async with conn_pool.connection() as conn:
        conn.transaction()
        async with conn.cursor() as cur:
            yield cur


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
        self.conn_pool = conn_pool
        self.vchive_pool = vchive_pool

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
        await self.conn_pool.open()
        await self.vchive_pool.open()

    async def db_up_time(self):
        try:
            async with get_cursor() as cursor:
                query = (
                    "SELECT TO_CHAR(now() - pg_postmaster_start_time(), "
                    "'DD\"d\"HH24hMImSSs')"
                )
                await cursor.execute(query)
                result = await cursor.fetchone()
        except Exception:
            return "連線狀態不明"
        return strftimedelta(parse_time(result[0]))

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
