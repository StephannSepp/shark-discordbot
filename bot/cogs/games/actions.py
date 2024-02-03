import datetime
import math

from disnake import CmdInter
from disnake.ext import commands
from utils import embed_builder
from utils import time_process

from . import DOLLAR_SIGN
from .helpers import Fishing
from .helpers import Mining
from .helpers import Player

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
    @commands.cooldown(1, 3)
    async def action(self, inter: CmdInter):
        """Action command group. {{ACTION_GROUP}}"""

    @action.sub_command(name="mining")
    async def mining(self, inter: CmdInter):
        """Go mining gold for 7 hours. {{ACTION_MINING}}"""
        player = Player(inter.author.id)
        if player.is_fishing or player.is_farming:
            await inter.response.send_message("你正在其他行動中", ephemeral=True)
            return
        action = Mining(inter.author.id)
        now = datetime.datetime.utcnow()
        if not player.is_mining:
            action.start_action()
            end_time = now + datetime.timedelta(hours=7)
            timestamp = f"<t:{time_process.to_unix(end_time)}:F>"
            progress = action.draw_progress()
            embed = embed_builder.information("挖礦行動開始", progress)
            embed.add_field("預計完成時間", timestamp)
            await inter.response.send_message(embed=embed)
            return
        if now <= action.start_at + datetime.timedelta(hours=7):
            progress = action.draw_progress()
            end_time = action.start_at + datetime.timedelta(hours=7)
            timestamp = f"<t:{time_process.to_unix(end_time)}:F>"
            embed = embed_builder.information("挖礦行動中", progress)
            embed.add_field("預計完成時間", timestamp)
            await inter.response.send_message(embed=embed)
            return
        profit = action.end_action()
        description = f"本次行動中獲得了黃金 {profit:,.1f} AU"
        embed = embed_builder.information("挖礦行動結束", description)
        embed.add_field("黃金餘額", f"{player.gold + profit:,.1f} AU")
        await inter.response.send_message(embed=embed)

    @action.sub_command(name="fishing")
    async def fishing(self, inter: CmdInter):
        """Go fishing and earning coins for 2 hours. {{ACTION_FISHING}}"""
        player = Player(inter.author.id)
        if player.is_mining or player.is_farming:
            await inter.response.send_message("你正在其他行動中", ephemeral=True)
            return
        action = Fishing(inter.author.id)
        now = datetime.datetime.utcnow()
        if not player.is_fishing:
            action.start_action()
            end_time = now + datetime.timedelta(hours=2)
            timestamp = f"<t:{time_process.to_unix(end_time)}:F>"
            progress = action.draw_progress()
            embed = embed_builder.information("釣魚行動開始", progress)
            embed.add_field("預計完成時間", timestamp)
            await inter.response.send_message(embed=embed)
            return
        if now <= action.start_at + datetime.timedelta(hours=2):
            progress = action.draw_progress()
            end_time = action.start_at + datetime.timedelta(hours=2)
            timestamp = f"<t:{time_process.to_unix(end_time)}:F>"
            embed = embed_builder.information("釣魚行動中", progress)
            embed.add_field("預計完成時間", timestamp)
            await inter.response.send_message(embed=embed)
            return
        profit = action.end_action()
        description = f"本次行動中獲得了金幣 {DOLLAR_SIGN}{profit:,}"
        embed = embed_builder.information("釣魚行動結束", description)
        embed.add_field("金幣餘額", f"{DOLLAR_SIGN}{player.coin + profit:,}")
        await inter.response.send_message(embed=embed)
