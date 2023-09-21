import traceback

import disnake
from disnake import CmdInter
from disnake.ext import commands

from config import Config


class ExceptionHandler(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @staticmethod
    def fancy_traceback(exc: Exception) -> str:
        # May not fit the message content limit
        text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        return f"```py\n{text[-4086:]}\n```"

    @commands.Cog.listener("on_slash_command_error")
    async def primary_error_handler(self, inter: CmdInter, exc: commands.CommandError):
        guild = self.bot.get_guild(Config.debug_guild) or await self.bot.fetch_guild(
            Config.debug_guild
        )
        debug_channel = disnake.utils.get(guild.text_channels, id=Config.debug_channel)

        match exc:
            case commands.CommandOnCooldown():
                pass
            case commands.CheckFailure():
                pass
            case commands.BadArgument():
                try:
                    await inter.response.send_message("輸入的參數不符合要求的格式", ephemeral=True)
                except disnake.errors.InteractionResponded:
                    await inter.edit_original_response("輸入的參數不符合要求的格式", ephemeral=True)
            case _:
                title = f"Slash command `{inter.data.name}` failed due to `{exc.__class__.__name__}`"
                embed = disnake.Embed(
                    title=title,
                    description=self.fancy_traceback(exc),
                    color=disnake.Colour.red(),
                )
                await debug_channel.send(embed=embed)
