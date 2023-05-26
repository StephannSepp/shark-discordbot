"""
events.dm_logger
----------------

A simple listener to catch the direct messages to the bot.

:Date: 11-13-2022
"""
import disnake
from disnake.ext import commands

from config import Config
from utils import embed_builder


class DirectMessageLogger(commands.Cog):
    """ A Disnake Cog wraps commands as a Python class. """

    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def log_dm_message(self, message: disnake.Message):
        if message.author.bot:
            return

        if not isinstance(message.channel, disnake.channel.DMChannel):
            return

        embed = embed_builder.embed_error(
            title="你正在對機器人傳送私人訊息",
            description=(
                "任何情況下機器人並不會回覆您，但此訊息仍然會被開發者紀錄。\n\n"
                "\* 若您有任何關於群組的問題歡迎至 <#761928471144038420> 提交客服單。\n"
                "\* 若您有任何關於此機器人的問題，歡迎向 <@387573599919276032> 詢問。"
            )
        )
        await message.author.send(embed=embed)

        debug_guild = (
            self.bot.get_guild(Config.debug_guild)
            or await self.bot.fetch_guild(Config.debug_guild)
        )
        debug_channel = disnake.utils.get(debug_guild.text_channels, id=Config.debug_channel)
        title = f"DM by {str(message.author)}"
        embed = disnake.Embed(
            title=title,
            description=message.content,
            color=disnake.Colour.greyple(),
        )
        embed.add_field(name="ID", value=message.author.id)
        await debug_channel.send(embed=embed)
