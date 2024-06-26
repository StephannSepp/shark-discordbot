import datetime
import math

from disnake import CmdInter
from disnake.ext import commands
from utils import checks
from utils import embed_builder
from utils import time_process

from . import DOLLAR_SIGN
from .helpers import Fishing
from .helpers import GameUser
from .helpers import Mining

GOLD_NUGGET = "<:minecraft_gold_nugget:1199002510942294026>"
PICKAXE = "<:minecraft_pickaxe:1199002509302308905>"
STONE = "<:minecraft_stone:1199002505699409940>"
RAW_COD = "<:minecraft_raw_cod:1200101327548723340>"
FISHING_ROD = "<:minecraft_fishing_rod:1200101325799698522>"
WATER = "<:minecraft_water:1200101330887393290>"


def draw_mining_progress(start_at: datetime.datetime) -> str:
    now = datetime.datetime.utcnow()
    step = math.floor((now - start_at).total_seconds() / 25200 * 10)
    progress = []
    for i in range(1, 11):
        if i < step + 1:
            e = GOLD_NUGGET
        elif i == step + 1:
            e = PICKAXE
        elif i > step + 1:
            e = STONE
        progress.append(e)
    return "".join(progress)


def draw_fishing_progress(start_at: datetime.datetime) -> str:
    now = datetime.datetime.utcnow()
    step = math.floor((now - start_at).total_seconds() / 25200 * 10)
    progress = []
    for i in range(1, 11):
        if i < step + 1:
            e = RAW_COD
        elif i == step + 1:
            e = FISHING_ROD
        elif i > step + 1:
            e = WATER
        progress.append(e)
    return "".join(progress)


class Action(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(name="action")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check(checks.is_on_command_channel)
    async def action(self, inter: CmdInter):
        """Action command group. {{ACTION_GROUP}}"""

    @action.sub_command(name="mining")
    async def mining(self, inter: CmdInter, message: str = ""):
        """Go mining gold for 7 hours. {{ACTION_MINING}}"""
        user = await GameUser.fetch(inter.author.id)
        if user.is_fishing or user.is_farming:
            await inter.response.send_message("你正在其他行動中", ephemeral=True)
            return
        action = await Mining.mining(inter.author.id)
        now = datetime.datetime.utcnow()
        if not user.is_mining:
            await action.start_action(message)
            end_time = now + datetime.timedelta(hours=action.BASE_HOUR)
            timestamp = f"<t:{time_process.to_unix(end_time)}:F>"
            progress = action.draw_progress()
            embed = embed_builder.information("挖礦行動開始", progress)
            embed.add_field("預計完成時間", timestamp, inline=False)
            workers = await action.get_other_workers()
            if workers:
                text = [
                    f"* <@{uid}>: {message}" if message else f"* <@{uid}>"
                    for uid, message in workers[:4]
                ]
                if len(workers) > 4:
                    text.append(f"...其他 {len(workers) - 4} 名礦工")
                embed.add_field("礦坑中的礦工", "\n".join(text), inline=False)
            await inter.response.send_message(embed=embed)
            return
        if now <= action.start_at + datetime.timedelta(hours=action.BASE_HOUR):
            progress = action.draw_progress()
            end_time = action.start_at + datetime.timedelta(hours=action.BASE_HOUR)
            timestamp = f"<t:{time_process.to_unix(end_time)}:F>"
            embed = embed_builder.information("挖礦行動中", progress)
            embed.add_field("預計完成時間", timestamp)
            workers = await action.get_other_workers()
            if workers:
                text = [
                    f"* <@{uid}>: {message}" if message else f"* <@{uid}>"
                    for uid, message in workers[:4]
                ]
                if len(workers) > 4:
                    text.append(f"...其他 {len(workers) - 4} 名礦工")
                embed.add_field("礦坑中的礦工", "\n".join(text), inline=False)
            await inter.response.send_message(embed=embed)
            return
        profit = await action.end_action()
        description = (
            f"## 本次行動中獲得了黃金 {profit:,.1f} AU\n"
            "使用 `/banking sell_gold` 或 `/銀行 販賣黃金` 來販賣黃金"
        )
        embed = embed_builder.information("挖礦行動結束", description)
        embed.add_field("黃金餘額", f"{user.gold + profit:,.1f} AU")
        await inter.response.send_message(embed=embed)

    @action.sub_command(name="fishing")
    async def fishing(self, inter: CmdInter, message: str = ""):
        """Go fishing and earning coins for 2 hours. {{ACTION_FISHING}}"""
        user = await GameUser.fetch(inter.author.id)
        if user.is_mining or user.is_farming:
            await inter.response.send_message("你正在其他行動中", ephemeral=True)
            return
        action = await Fishing.fishing(inter.author.id)
        now = datetime.datetime.utcnow()
        if not user.is_fishing:
            await action.start_action(message)
            end_time = now + datetime.timedelta(hours=action.BASE_HOUR)
            timestamp = f"<t:{time_process.to_unix(end_time)}:F>"
            progress = action.draw_progress()
            embed = embed_builder.information("釣魚行動開始", progress)
            embed.add_field("預計完成時間", timestamp)
            workers = await action.get_other_workers()
            if workers:
                text = [
                    f"* <@{uid}>: {message}" if message else f"* <@{uid}>"
                    for uid, message in workers[:4]
                ]
                if len(workers) > 4:
                    text.append(f"...其他 {len(workers) - 4} 名釣友")
                embed.add_field("釣場中的釣友", "\n".join(text), inline=False)
            await inter.response.send_message(embed=embed)
            return
        if now <= action.start_at + datetime.timedelta(hours=action.BASE_HOUR):
            progress = action.draw_progress()
            end_time = action.start_at + datetime.timedelta(hours=action.BASE_HOUR)
            timestamp = f"<t:{time_process.to_unix(end_time)}:F>"
            embed = embed_builder.information("釣魚行動中", progress)
            embed.add_field("預計完成時間", timestamp)
            workers = await action.get_other_workers()
            if workers:
                text = [
                    f"* <@{uid}>: {message}" if message else f"* <@{uid}>"
                    for uid, message in workers[:4]
                ]
                if len(workers) > 4:
                    text.append(f"...其他 {len(workers) - 4} 名釣友")
                embed.add_field("釣場中的釣友", "\n".join(text), inline=False)
            await inter.response.send_message(embed=embed)
            return
        profit = await action.end_action()
        description = f"本次行動中獲得了金幣 {DOLLAR_SIGN}{profit:,}"
        embed = embed_builder.information("釣魚行動結束", description)
        user_coin = (
            f"{DOLLAR_SIGN}{user.coin + profit:,}"
            if user.coin >= 0
            else f"-{DOLLAR_SIGN}{abs(user.coin + profit):,}"
        )
        embed.add_field("金幣餘額", user_coin)
        await inter.response.send_message(embed=embed)
