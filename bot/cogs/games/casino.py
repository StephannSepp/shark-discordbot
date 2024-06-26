from disnake import CmdInter
from disnake.ext import commands
from utils import checks

from . import DOLLAR_SIGN
from .helpers import GameUser
from .views import BlackjackView
from .views import RouletteDealer
from .views import RoulettePlayer
from .views import RouletteView


class Casino(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(name="casino")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check(checks.is_on_command_channel)
    async def casino(self, inter: CmdInter):
        """Casino group commands. {{CASINO_GROUP}}"""

    @casino.sub_command(name="blackjack")
    @commands.cooldown(30, 1800, commands.BucketType.user)
    async def blackjack(self, inter: CmdInter, bet: int):
        """Play blackjack game. {{CASINO_BLACKJACK}}"""
        user = await GameUser.fetch(inter.author.id)
        if user.is_busy:
            message = "你正在行動中, 不能進行此操作"
            await inter.response.send_message(message, ephemeral=True)
            return
        if bet <= 0:
            message = "賭注不可小於等於 0"
            await inter.response.send_message(message, ephemeral=True)
            return
        if bet > 250:
            message = f"賭注不可大於 {DOLLAR_SIGN}250"
            await inter.response.send_message(message, ephemeral=True)
            return
        if user.coin < 0:
            message = f"請先還債, 您的債務還有 {DOLLAR_SIGN}{abs(user.coin):,}"
            await inter.response.send_message(message, ephemeral=True)
            return
        if user.coin < bet:
            message = "你沒有足夠的金幣下賭注"
            await inter.response.send_message(message, ephemeral=True)
            return
        await user.bank_transaction(
            coin_change_to_player=-bet, note="Casino consumption."
        )
        view = BlackjackView(user, bet)
        embed = await view.build_embed()
        await inter.response.send_message(embed=embed, view=view)

    @casino.sub_command(name="roulette")
    @commands.cooldown(30, 1800, commands.BucketType.user)
    async def roulette(self, inter: CmdInter):
        """Play shotgun roulette. {{CASINO_ROULETTE}}"""
        user = await GameUser.fetch(inter.author.id)
        if user.is_busy:
            message = "你正在行動中, 不能進行此操作"
            await inter.response.send_message(message, ephemeral=True)
            return
        if user.coin < 0:
            message = f"請先還債, 您的債務還有 {DOLLAR_SIGN}{abs(user.coin):,}"
            await inter.response.send_message(message, ephemeral=True)
            return
        if user.coin < 2100:
            message = f"你至少需要 {DOLLAR_SIGN}2,100 才能遊玩"
            await inter.response.send_message(message, ephemeral=True)
            return
        await user.bank_transaction(
            coin_change_to_player=-2100, note="Casino consumption."
        )
        dealer = RouletteDealer()
        player = RoulettePlayer()
        view = RouletteView(user, player, dealer)
        embed = await view.build_embed()
        await inter.response.send_message(embed=embed, view=view)
