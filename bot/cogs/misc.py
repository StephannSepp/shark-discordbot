""" Some misc commands.

Must be loaded as a Disnake Cog via load_extension() function.

:date: 09-19-2022
"""
# Third-party library imports
from disnake import CmdInter
from disnake import File
from disnake.ext import commands
# Local imports
from utils import embed_builder


class Misc(commands.Cog):
    """ A Disnake Cog wraps commands as a Python class. """

    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(name="ping", description="Ping! Pong!")
    async def ping(self, inter: CmdInter):
        """ Ping the bot. """
        await inter.response.send_message(f"{round(self.bot.latency*1000)}ms", ephemeral=True)

    @commands.slash_command(name="donothing", description="This function does nothing.")
    async def donothing(self, inter: CmdInter):
        """ This function does nothing. """
        await inter.response.send_message(file=File("data/donothing.png"))

    @commands.slash_command(name="botinfo", description="機器人資訊")
    async def botinfo(self, inter: CmdInter):
        """ Display bot information. """
        embed = embed_builder.embed_information(
            title = "機器人資訊",
            description = "不是那隻迷因鯊魚、也不是亞特蘭提斯的後裔，只是在亞特蘭提斯的打工BOT。",
            thumbnail = self.bot.user.avatar.url
        )
        embed.add_field(name="擁有者", value="林昕渪#1202", inline=True)
        embed.add_field(name="原始碼", value="[GitHub](https://github.com/StephannSepp/shark-discordbot)", inline=True)
        embed.add_field(name="版本", value=self.bot.version, inline=False)
        embed.add_field(name="運行時間", value=self.bot.up_time, inline=False)
        await inter.response.send_message(embed=embed, ephemeral=True)


def setup(bot: commands.InteractionBot):
    """ Called when this extension is loaded. """
    bot.add_cog(Misc(bot))
