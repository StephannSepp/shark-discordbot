import datetime
import logging

from disnake import CmdInter
from disnake.ext import commands
from disnake.ext import tasks
from utils import embed_builder
from utils import gen
from utils import time_process

from bot import get_cursor


class Reminder(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.next_reminder = None
        self.DEFAULT_REMINDER = {"remind_at": datetime.datetime(3199, 1, 25)}
        self.taskloop.start()

    async def cog_load(self):
        await self._fetch_next_reminder()

    async def _fetch_next_reminder(self):
        logging.info("Fetching next reminder...")
        async with get_cursor() as cursor:
            query = "SELECT * FROM reminder ORDER BY remind_at LIMIT 1"
            await cursor.execute(query)
            result = await cursor.fetchone()

        if result:
            self.next_reminder = {
                "remind_id": result[0],
                "user_id": result[1],
                "server_id": result[2],
                "channel_id": result[3],
                "remind_text": result[4],
                "remind_at": result[5],
                "created_at": result[6],
            }
            logging.info("Next reminder at %s", result[5])
        else:
            self.next_reminder = self.DEFAULT_REMINDER
            logging.info("All remind tasks done")

    async def _clear_remind(self, remind_id: int):
        async with get_cursor() as cursor:
            query = "DELETE FROM reminder WHERE remind_id = %s"
            await cursor.execute(query, (remind_id,))

    async def _do_remind(self):
        if self.next_reminder.get("remind_at") is None:
            return
        if datetime.datetime.now() < self.next_reminder["remind_at"]:
            return

        remind_id = self.next_reminder["remind_id"]
        user_id = self.next_reminder["user_id"]
        server_id = self.next_reminder["server_id"]
        channel_id = self.next_reminder["channel_id"]
        with_message = self.next_reminder["remind_text"]
        created_at = self.next_reminder["created_at"]
        time_in_unix = time_process.to_unix(created_at)
        guild = self.bot.get_guild(server_id) or await self.bot.fetch_guild(server_id)
        channel = guild.get_channel(channel_id) or await self.bot.fetch_channel(
            channel_id
        )
        await self._clear_remind(remind_id)
        await self._fetch_next_reminder()
        await channel.send(
            f"**<@{user_id}> 以下是你在<t:{time_in_unix}:R>要求的提醒訊息:**\n{with_message}"
        )

    @commands.slash_command(name="remind", description="提醒")
    @commands.guild_only()
    async def remind(self, inter: CmdInter):
        pass

    @remind.sub_command(
        name="me", description="提醒我，格式範例：2d8h5m20s，雙空格代替換行"
    )
    @commands.guild_only()
    async def remind_add(self, inter: CmdInter, after: str, message: str):
        try:
            duration = time_process.parse_time(after)
        except ValueError:
            await inter.response.send_message("時間格式不被接受")
            return

        if duration > datetime.timedelta(hours=2160):
            await inter.response.send_message("不允許設定超過 3 個月的提醒")
            return

        message = message.replace("  ", "\n")

        time_to_remind = datetime.datetime.now() + duration
        timestamp = time_process.to_unix(time_to_remind)
        remind_id = gen.snowflake()
        user_id = inter.author.id
        server_id = inter.guild.id
        channel_id = inter.channel_id

        async with get_cursor() as cursor:
            query = "SELECT count(*) FROM reminder WHERE user_id = %s"
            await cursor.execute(query, (user_id,))
            user_reminders = (await cursor.fetchone())[0]
        if user_reminders >= 3:
            await inter.response.send_message("你不能設定超過三個提醒")
            return
        params = {
            "remind_id": remind_id,
            "user_id": user_id,
            "server_id": server_id,
            "channel_id": channel_id,
            "remind_text": message,
            "remind_at": time_to_remind,
            "created_at": datetime.datetime.now(),
        }
        async with get_cursor() as cursor:
            query = (
                "INSERT INTO reminder VALUES (%(remind_id)s,%(user_id)s,%(server_id)s, "
                "%(channel_id)s, %(remind_text)s, %(remind_at)s, %(created_at)s)"
            )
            await cursor.execute(query, params)

        await self._fetch_next_reminder()
        await inter.response.send_message(
            f"我會在 **<t:{timestamp}>**（<t:{timestamp}:R>）提醒你\n提醒內容:\n**{message}**"
        )

    @remind.sub_command("list")
    @commands.guild_only()
    async def remind_list(self, inter: CmdInter):
        async with get_cursor() as cursor:
            query = "SELECT * FROM reminder WHERE user_id = %s ORDER BY remind_at"
            await cursor.execute(query, (inter.author.id,))
            result = await cursor.fetchall()
        messages = []
        for remind in result:
            timestamp = time_process.to_unix(remind[5])
            message = remind[4]
            channel = f"<#{remind[3]}>"
            messages.append(f"* {timestamp} - {message} in {channel}")
        if not message:
            embed = embed_builder.information("提醒列表", "你沒有任何設定的提醒")
            await inter.response.send_message(embed=embed)
            return
        embed = embed_builder.information("提醒列表", "\n".join(messages))
        await inter.response.send_message("\n".join(message))

    @tasks.loop(seconds=10)
    async def taskloop(self):
        await self._do_remind()

    @taskloop.before_loop
    async def before_taskloop(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.InteractionBot):
    bot.add_cog(Reminder(bot))
