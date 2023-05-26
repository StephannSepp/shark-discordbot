""" A fortune draw slash command.

Must be loaded as a Disnake Cog via load_extension() function.

:date: 09-21-2022
"""

import datetime
import hashlib

from disnake import CmdInter
from disnake import File
from disnake.ext import commands
from disnake.ext import tasks

from config import Config
from utils import embed_builder
from utils import time_process

from . import FortuneResult
from . import module

ROLES = {
    "大吉": 1043736817700175902,
    "中吉": 1043736928949907506,
    "小吉": 1043736890894991380,
    "凶": 1043736582760439838,
    "大凶": 1043737502080581722,
}
ROLE_REVOKE_START = datetime.time() # 00:00:00
ROLE_REVOKE_END = datetime.time(minute=2) # 00:01:00


class Fortune(commands.Cog):
    """ A Disnake Cog wraps commands as a Python class. """

    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.pause = False
        self.today = datetime.datetime.utcnow().date()
        self.taskloop.start()

    @commands.slash_command(name="fortune", description="抽籤")
    @commands.guild_only()
    async def fortune(self, inter: CmdInter):
        """ Fortune command group. """

    @fortune.sub_command(name="draw", description="抽籤！每日早上八點重置")
    async def fortune_draw(self, inter: CmdInter):
        """ This command will draw a fortune lot. Reset on 0:00 UTC time
        everyday.
        """
        # Defer for avoiding interaction timeout.
        await inter.response.defer()

        if ROLE_REVOKE_START < datetime.datetime.now().time() < ROLE_REVOKE_END or self.pause:
            await inter.followup.send("機器人正在移除身分組，請稍後再試")
            return

        date = int(datetime.datetime.utcnow().strftime("%Y%m%d"))
        reset_time = datetime.datetime.utcnow().date() + datetime.timedelta(days=1)
        reset_time_unix = time_process.to_unix(reset_time)
        # The raw seed is a combination of Discord user ID and date in integer
        # both in binary strings, and then hash the string with sha256.
        # The seed for each fortune result is by dividing the raw seed into
        # four strings.
        raw_seed = format(date, "b") + format(inter.author.id, "b")
        seed = hashlib.sha256(raw_seed.encode()).hexdigest()
        result = FortuneResult(uid=inter.author.id, draw_date=datetime.datetime.utcnow().date())
        result.luck = module.draw_fortune(seed[:16])
        result.colour = module.get_lucky_colour(seed[16:32])
        result.number = module.get_lucky_number(seed[32:48])
        result.angel, url = module.get_guardian_angel(seed[48:])
        file = File(module.get_image_url(result.luck, seed), filename="fortune.png")
        embed = embed_builder.build_embed(
            title=f"抽籤結果🌸{result.luck}",
            description=f"{inter.author.mention}的抽籤結果\n",
            colour=module.to_colour_obj(result.colour)
        )
        embed.add_field(name="幸運天使", value=result.angel, inline=False)
        embed.set_thumbnail(url=url)
        embed.add_field(name="開運數字", value=result.number)
        embed.add_field(name="幸運色", value=result.colour)
        embed.set_image(file=file)

        role = inter.guild.get_role(ROLES[result.luck])
        if role is not None and role not in inter.author.roles:
            await inter.author.add_roles(role)
            result.record()

        await inter.followup.send(
            content=f"下次抽籤重置時間：<t:{reset_time_unix}> <t:{reset_time_unix}:R>",
            embed=embed
        )

    GROUP_OPT = commands.option_enum(["運氣", "幸運天使"])
    @fortune.sub_command(name="statistics", description="抽籤統計")
    async def fortune_statistics(self, inter: CmdInter, group_by: GROUP_OPT=None):
        if group_by is not None:
            match group_by:
                case "運氣":
                    result = FortuneResult.get_stats_by("luck")
                    # ..:example:
                    # result = [('中吉', 9), ('小吉', 7), ('大吉', 5), ('大凶', 3)]
                    inline = False
                case "幸運天使":
                    result = FortuneResult.get_stats_by("angel")
                    # ..:example:
                    # result = [('Ayunda Risu', 5), ('Ceres Fauna', 4), ('戌神ころね', 4), ...]
                    inline = True

            result_count = (row[1] for row in result)
            total = sum(result_count)
            embed = embed_builder.embed_information(
                title="全域抽籤統計📊",
                description=f"截至目前為止已經抽出了 {total} 支籤\n",
            )
            for index, row in enumerate(result):
                if index >= 9:
                    break

                p = (row[1] / total) * 100
                value = f"{row[1]:,} 次({p:.2f}%)"
                embed.add_field(name=row[0], value=value, inline=inline)
            await inter.response.send_message(embed=embed)
        else:
            # The result of get_by_user is a tuple pairs
            # Here we assign the result pairs to last_week_result
            # and most_common_angel_result
            #
            # ..:example:
            # last_week_result = (('大吉', <datetime object>), ('凶', <datetime object>), ...)
            # most_common_angel_result = ('Ceres Fauna', 3)
            result = FortuneResult.get_by_user(inter.author.id)
            last_week_result, most_common_angel_result = result
            embed = embed_builder.embed_information(
                title="個人抽籤統計📊",
                description=f"以下是 {inter.author.mention} 的個人運勢統計"
            )
            if last_week_result:
                last_week_lucks = []
                for row in last_week_result:
                    luck, date = row
                    date_unix = time_process.to_unix(date)
                    last_week_lucks.append(f"<t:{date_unix}:D> - {luck}")
                value = "\n".join(last_week_lucks)
                embed.add_field(
                    name="過去 7 日的運氣",
                    value=value,
                    inline=False
                )
            if most_common_angel_result:
                common_angel, count = most_common_angel_result
                url = module.get_guardian_angel_image(common_angel)
                value = f"{common_angel} - {count} 次"
                embed.add_field(
                    name="過去 30 日最常抽到的幸運天使",
                    value=value,
                    inline=False
                )
                embed.set_thumbnail(url=url)
            await inter.response.send_message(embed=embed)

    async def revoke_roles(self):
        if self.today == datetime.datetime.utcnow().date():
            return

        self.pause = True
        self.today = datetime.datetime.utcnow().date()
        guild = (
            self.bot.get_guild(Config.atlantis_id)
            or await self.bot.fetch_guild(Config.atlantis_id)
        )
        for _k, v in ROLES.items():
            role = guild.get_role(v)
            if role.members:
                for m in role.members:
                    await m.remove_roles(role)

    @tasks.loop(seconds=59)
    async def taskloop(self):
        await self.revoke_roles()
        # Make sure it's always False unless
        # the bot starts to revoke roles.
        self.pause = False

    @taskloop.before_loop
    async def before_taskloop(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.InteractionBot):
    """ Called when this extension is loaded. """
    bot.add_cog(Fortune(bot))
