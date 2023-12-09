import random
import textwrap
from enum import Enum

from disnake import CmdInter
from disnake.ext import commands

from utils import embed_builder


class GachaResult(Enum):
    WON = "🟩"
    LOST = "⬛"
    GUARANTEE = "🟦"


class GachaSim(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(name="gacha")
    @commands.guild_only()
    async def gacha(self, inter: CmdInter):
        """Gacha simulation command group. {{GACHA}}"""

    @gacha.sub_command(name="pure_rate")
    async def pure_rate(self, inter: CmdInter, rate_percentage: float, spins: int = 10):
        """Gacha uses pure random rate percentage selection. {{GACHA_PURE_RATE}}

        Parameters
        ----------
        rate_percentage: Rate in percentage of the desired item.
        spins: How many times the gacha pulls.
        """
        if spins > 100:
            await inter.response.send_message("抽卡次數不可大於 100", ephemeral=True)
            return
        real_rate = rate_percentage / 100
        result = [random.random() for _ in range(spins)]
        result_visual = [
            GachaResult.WON.value if i <= real_rate else GachaResult.LOST.value
            for i in result
        ]
        won = result_visual.count(GachaResult.WON.value)
        user_rate = round(won / spins * 100, 4)
        description = f"預期機率: {rate_percentage}%\n抽卡機率: {user_rate}%\n"
        embed = embed_builder.information(title="抽卡結果", description=description)
        value = "\n".join(textwrap.wrap(" ".join(result_visual), 20))
        embed.add_field(name=f"抽卡結果: {won} / {spins}", value=value)
        await inter.response.send_message(embed=embed)


def setup(bot: commands.InteractionBot):
    bot.add_cog(GachaSim(bot))
