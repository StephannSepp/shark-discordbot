from disnake.ext import commands

from .actions import Action
from .banking import Banking
from .casino import Casino
from .lottery import LotteryGame


def setup(bot: commands.InteractionBot):
    bot.add_cog(Action(bot))
    bot.add_cog(Banking(bot))
    bot.add_cog(Casino(bot))
    bot.add_cog(LotteryGame(bot))
