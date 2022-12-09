"""
:date: 12-08-2022
"""
import io

from disnake import CmdInter
from disnake import File
from disnake import Role
from disnake.ext import commands
from jinja2 import Environment, FileSystemLoader

from . import PERMS_NAME_LOCALIZED


class PermissionCheck(commands.Cog):
    """ A Disnake Cog wraps commands as a Python class. """

    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.env = Environment(loader=FileSystemLoader("templates"))

    @commands.slash_command(name="check_every_channel", description="權限稽核")
    @commands.guild_only()
    @commands.default_member_permissions(administrator=True)
    async def check_every_channel(self, inter: CmdInter, role: Role):
        guild = inter.guild
        synced_channels = dict.fromkeys(guild.categories, [])
        permissions = []
        channels = []
        for channel in guild.channels:
            # If channel is permission synced to its category,
            # then ignore this channel since the categories are
            # printed out anyway.
            if channel.permissions_synced:
                channel_under_category = synced_channels.get(channel.category)
                channel_under_category.append(channel)
                synced_channels.update({channel: channel_under_category})
                continue

            permission_objs = channel.permissions_for(role)
            permissions_dict = dict(list(iter(permission_objs)))
            result = []
            for k in PERMS_NAME_LOCALIZED:
                result.append(
                    (PERMS_NAME_LOCALIZED.get(k), permissions_dict.get(k))
                )
            permissions.append(result)
            channels.append(channel)

        template = self.env.get_template('channel_permission_for.html')
        template_output = template.render(
            role=role.name,
            channels=channels,
            synced_channels=synced_channels,
            permissions=permissions
        )

        filename = f"{role.name}.html"
        file = File(io.StringIO(template_output), filename=filename)
        await inter.response.send_message(
            file=file
        )


def setup(bot: commands.InteractionBot):
    """ Called when this extension is loaded. """
    bot.add_cog(PermissionCheck(bot))
