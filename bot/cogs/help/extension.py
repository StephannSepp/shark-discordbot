from disnake import CmdInter
from disnake.ext import commands

from .views import HelpView


class Help(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(name="help")
    @commands.guild_only()
    async def help(self, inter: CmdInter):
        view = HelpView()
        embed = view.get_embed()
        await inter.response.send_message(view=view, embed=embed)


def setup(bot: commands.InteractionBot):
    bot.add_cog(Help(bot))
