"""
events.vxtwitter_helper.py
----------------

A simple listener to detect any of twitter URLs and reply them with a vxtwitter
URL.

:Date: 07-04-2023
"""
import re

import disnake
from disnake import AllowedMentions
from disnake.ext import commands

from utils import embed_builder


class VxTwitterHelper(commands.Cog):
    """A Disnake Cog wraps commands as a Python class."""

    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def vxtwitter_converter(self, message: disnake.Message):
        if isinstance(message.channel, disnake.channel.DMChannel):
            return

        if message.author == self.bot.user:
            return

        r = re.findall(
            r".*(https:\/\/twitter\.com\/?\w{1,15}\/status\/\d{13,}).*", message.content
        )
        if not r:
            return

        content = "\n".join(r)
        content = content.replace("twitter", "vxtwitter")
        content = (
            f"Hi, {message.author.mention}\n"
            "**Twitter 正在透過收費 API 扼殺第三方應用程序**，無嵌入內容的 Twitter 網址會對管理方造成"
            "管理困難，因此由機器人幫您轉換為 vxtwitter 網址。\n\n"
            f"如果想顯示嵌入內容可以將網址中的 `twitter` 改為 `vxtwitter`。\n\n{content}"
        )
        await message.channel.send(
            content=content,
            reference=message,
            mention_author=False,
            suppress_embeds=False,
            allowed_mentions=AllowedMentions.none(),
        )
