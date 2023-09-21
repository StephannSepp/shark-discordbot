""" A slash command allows to create Discord embeds via Discord client.

Must be loaded as a Disnake Cog via load_extension() function.

:date: 10-07-2022
"""

from disnake import CmdInter
from disnake import TextChannel
from disnake.ext import commands

from utils import embed_builder


class MakeEmbed(commands.Cog):
    """ A Disnake Cog wraps commands as a Python class. """

    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    # Choices of embed type options.
    EMBED_OPT = commands.option_enum(["Information", "Error"])

    @commands.slash_command(name="make-embed", description="製作 Embed 元件, 雙空格代替換行")
    @commands.default_member_permissions(manage_messages=True)
    async def make_embed(
        self, inter: CmdInter, title: str, description: str, content: str=None,
        embed_type: EMBED_OPT="Information", copy: TextChannel=None
    ):
        """ This command allows user to make a Discord embed via Discord client. """
        await inter.response.defer()
        # Use double space to break a new line.
        description = description.replace("  ", "\n")
        match embed_type:
            case "Information":
                embed = embed_builder.information(title=title, description=description)
            case "Error":
                embed = embed_builder.error(title=title, description=description)
            case _:
                pass

        if copy:
            await copy.send(content=content, embed=embed)
            await inter.followup.send(content=content, embed=embed)
        else:
            await inter.edit_original_response(content=content, embed=embed)


def setup(bot: commands.InteractionBot):
    """ Called when this extension is loaded. """
    bot.add_cog(MakeEmbed(bot))
