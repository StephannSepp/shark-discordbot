"""
events.dm_logger
----------------

A simple listener to catch the direct messages to the bot.

:Date: 11-13-2022
"""
import disnake
from disnake.ext import commands
from config import Config


class DirectMessageLogger(commands.Cog):
    """ A Disnake Cog wraps commands as a Python class. """

    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def log_dm_message(self, message: disnake.Message):
        if message.author.bot:
            return

        if isinstance(message.channel, disnake.channel.DMChannel):
            debug_guild = self.bot.get_guild(Config.debug_guild) or await self.bot.fetch_guild(Config.debug_guild)
            debug_channel = disnake.utils.get(debug_guild.text_channels, id=Config.debug_channel)
            title = f"DM by {str(message.author)}"
            embed = disnake.Embed(
                    title=title,
                    description=message.content,
                    color=disnake.Colour.greyple(),
            )
            embed.add_field(name="ID", value=message.author.id)
            await debug_channel.send(embed=embed)
