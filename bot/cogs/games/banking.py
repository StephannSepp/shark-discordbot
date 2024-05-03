import asyncio
import datetime
import io
import math

from disnake import CmdInter
from disnake import File
from disnake.ext import commands
from disnake.ext import tasks
from matplotlib import pyplot as plt
from utils import checks
from utils import embed_builder

from . import DOLLAR_SIGN
from .helpers import Bank
from .helpers import ExchangeRate
from .helpers import GameUser
from .helpers import get_top_ranking


def generate_line_chart(data: dict) -> io.BytesIO:
    data_stream = io.BytesIO()
    plt.plot(data.keys(), data.values())
    plt.xlabel("VALID DATE")
    plt.ylabel("EXCHANGE RATE")
    plt.xticks(rotation=30, ha="right")
    ax = plt.gca()
    ax.yaxis.set_major_formatter(DOLLAR_SIGN + "{x:.03f}")
    plt.tight_layout()
    plt.savefig(data_stream, format="png")
    plt.close()
    data_stream.seek(0)
    return data_stream


class Banking(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.taskloop.start()

    @commands.slash_command(name="banking")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check(checks.is_on_command_channel)
    async def banking(self, inter: CmdInter):
        """Banking group commands. {{BANKING_GROUP}}"""

    @banking.sub_command("profile")
    async def profile(self, inter: CmdInter):
        """Show bank account. {{BANKING_PROFILE}}"""
        user = await GameUser.fetch(inter.author.id)
        embed = embed_builder.information("資產查詢")
        embed.add_field("UID", user.uid, inline=False)
        embed.add_field("黃金餘額", f"{user.gold:,.1f} AU", inline=False)
        user_coin = (
            f"{DOLLAR_SIGN}{user.coin:,}"
            if user.coin >= 0
            else f"-{DOLLAR_SIGN}{abs(user.coin):,}"
        )
        embed.add_field("金幣餘額", user_coin, inline=False)
        if user.is_busy:
            if user.is_mining:
                action_type = "挖礦中"
            if user.is_fishing:
                action_type = "釣魚中"
            embed.add_field("行動狀態", action_type)
        mining_stats = await user.get_action_stats("MINING")
        embed.add_field(
            "已挖礦次數 / 總共產出金礦",
            f"{mining_stats['count']:,} 次 / {mining_stats['profit']:,.1f} AU",
            inline=False,
        )
        fishing_stats = await user.get_action_stats("FISHING")
        embed.add_field(
            "已釣魚次數 / 總共賺得金幣",
            f"{fishing_stats['count']:,} 次 / {DOLLAR_SIGN}{fishing_stats['profit']:,}",
            inline=False,
        )
        await inter.response.send_message(embed=embed)

    @banking.sub_command("atlantean_coin")
    async def atlantean_coin(self, inter: CmdInter):
        """Show information about Atlantean Coins. {{BANKING_ATLANTEAN_COIN}}"""
        exr = await ExchangeRate.create()
        bank = await Bank.bank()
        bank_gold_discount = math.floor((bank.gold + bank.reserve_gold) * 28)
        bank_gold_percentage = bank_gold_discount / (bank.coin + bank_gold_discount)
        bank_coin_percentage = bank.coin / (bank.coin + bank_gold_discount)
        description = (
            "亞特蘭提斯銀行每日將收購的黃金中的 60% 用於鑄造金幣，其餘 40% 則為儲備黃金。\n\n"
            "法典規定每單位黃金不可鑄造多於 28 枚金幣，並確保金幣價值不高於或低於基礎匯率"
            "的 5%，其餘匯率的浮動可由銀行依據市場供需情況進行調整。\n\n"
            "銀行在收購黃金時會額外收取 2% 的鑄幣費用，賣出黃金時則不再收取這項費用。\n\n"
            "使用 `/banking sell_gold` 指令販賣黃金。"
        )
        embed = embed_builder.information("亞特蘭提斯金幣", description)
        embed.add_field("參考匯率", f"{exr.exchange_rate:.3f}", inline=False)
        embed.add_field("適用日期", f"{exr.valid_date:%Y-%m-%d}~", inline=False)
        embed.add_field(
            f"銀行金幣資產 - {bank_coin_percentage:.02%}",
            f"{DOLLAR_SIGN}{bank.coin:,}",
            inline=False,
        )
        embed.add_field(
            f"銀行黃金總值 - {bank_gold_percentage:.02%}",
            f"{DOLLAR_SIGN}{bank_gold_discount:,}",
            inline=False,
        )
        exr_data = await exr.get_recent_exchange_rate()
        data_stream = await asyncio.to_thread(generate_line_chart, exr_data)
        file = File(data_stream, "exchange_rate.png")
        embed.set_image(file=file)
        await inter.response.send_message(embed=embed)

    @banking.sub_command("sell_gold")
    async def sell_gold(self, inter: CmdInter, sell_gold: float = None):
        """Sell gold to the bank. {{BANKING_SELL_GOLD}}"""
        user = await GameUser.fetch(inter.author.id)
        if sell_gold is None:
            sell = user.gold
        else:
            sell = round(sell_gold, 3)
        if sell <= 0:
            await inter.response.send_message("數量不可小於等於 0", ephemeral=True)
            return
        if sell > user.gold:
            await inter.response.send_message("你沒有足夠的黃金", ephemeral=True)
            return
        exr = await ExchangeRate.create()
        coin = math.floor(exr.exchange_rate * sell * 0.98)
        txn_id = await user.bank_transaction(-sell, coin, "Gold sales.")
        embed = embed_builder.information(
            "交易成功", f"{sell:,.1f} AU ⇛ {DOLLAR_SIGN}{coin:,}"
        )
        embed.add_field("參考匯率", f"{exr.exchange_rate:.3f}", inline=False)
        embed.add_field("黃金餘額", f"{user.gold:,.1f} AU", inline=False)
        user_coin = (
            f"{DOLLAR_SIGN}{user.coin:,}"
            if user.coin >= 0
            else f"-{DOLLAR_SIGN}{abs(user.coin):,}"
        )
        embed.add_field("金幣餘額", f"{user_coin}", inline=False)
        embed.set_footer(text=f"TxnID: {txn_id}")
        await inter.response.send_message(embed=embed)

    @banking.sub_command("top")
    async def bank_top(self, inter: CmdInter):
        """Show top 10 user by total assets. {{BANKING_TOP}}"""
        result = await get_top_ranking(inter.author.id)
        descriptions = []
        for row in result:
            position = row["position"]
            uid = row["uid"]
            assets = round(row["total_assets"])
            if uid == inter.author.id:
                text = f"**#{position} | <@{uid}> 總資產: {DOLLAR_SIGN}{assets:,}**"
            else:
                text = f"#{position} | <@{uid}> 總資產: {DOLLAR_SIGN}{assets:,}"
            descriptions.append(text)
        embed = embed_builder.information("資產排行榜", "\n".join(descriptions))
        await inter.response.send_message(embed=embed)

    @tasks.loop(time=datetime.time())
    async def taskloop(self):
        bank = await Bank.bank()
        await bank.save_fin()
        exr = await ExchangeRate.create()
        await exr.update_exchange_rate()

    @taskloop.before_loop
    async def before_taskloop(self):
        await self.bot.wait_until_ready()
