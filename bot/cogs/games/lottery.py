import datetime

from disnake import CmdInter
from disnake.ext import commands
from disnake.ext import tasks
from utils import embed_builder

from . import DOLLAR_SIGN
from .helpers import GameUser
from .helpers import Lottery


class LotteryGame(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.taskloop.start()

    @commands.slash_command(name="lottery")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lottery(self, inter: CmdInter):
        """Lottery group commands. {{LOTTERY_GROUP}}"""

    @lottery.sub_command("buy")
    async def buy(self, inter: CmdInter, number: commands.Range[int, 0, 9999]):
        """Buy a lottery ticket for 100 coins, choose 4-digit number. {{LOTTERY_BUY}}"""
        tickets = Lottery(inter.author.id)
        user = GameUser(inter.author.id)
        if len(tickets.tickets) >= 3:
            await inter.response.send_message("最多只能購買 3 張彩券", ephemeral=True)
            return
        if user.coin < 0:
            message = f"請先還債, 您的債務還有 {DOLLAR_SIGN}{abs(user.coin):,}"
            await inter.response.send_message(message, ephemeral=True)
            return
        if user.coin < 100:
            message = "你沒有足夠的金幣購買彩券"
            await inter.response.send_message(message, ephemeral=True)
            return
        number = f"{number:04}"
        tickets.buy(number)
        await inter.response.send_message(f"你已購買彩券號碼 {number}")

    @lottery.sub_command("winning_number")
    async def winning_number(self, inter: CmdInter):
        """Check last winning number and claim the reward. {{LOTTERY_WINNING_NUMBER}}"""
        user = GameUser(inter.author.id)
        lottery = Lottery(inter.author.id)
        description = f"第 {lottery.no - 1} 期彩券頭獎號碼: {lottery.winning_number}"
        embed = embed_builder.information("亞特蘭提斯彩券", description)
        if lottery.tickets:
            for ticket in lottery.tickets:
                embed.add_field(f"第 {ticket.lottery_no} 期擁有的彩券", ticket.pick_number)
        if lottery.last_tickets:
            for ticket in lottery.last_tickets:
                embed.add_field(f"第 {ticket.lottery_no} 期擁有的彩券", ticket.pick_number)
            rewards = lottery.claim()
            if rewards > 0:
                user.bank_transaction(coin_change_to_player=rewards)
            embed.add_field("共贏得獎金", f"{DOLLAR_SIGN}{rewards:,}", inline=False)
        await inter.response.send_message(embed=embed)

    @tasks.loop(time=datetime.time())
    async def taskloop(self):
        if datetime.date.today().weekday() not in (2, 6):
            return
        Lottery.generate_winning_number()

    @taskloop.before_loop
    async def before_taskloop(self):
        await self.bot.wait_until_ready()
