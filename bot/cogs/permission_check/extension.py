""" A command for checking permission for a specific role.

:date: 12-11-2022
"""

import io

from disnake import CategoryChannel
from disnake import CmdInter
from disnake import File
from disnake import Role
from disnake.ext import commands
from jinja2 import Environment
from jinja2 import FileSystemLoader

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
        # category_channels = {
        #     category_A: [channel_A1, channel_A2, ...],
        #     category_B: [...],
        #     ...
        # }
        category_channels: dict = dict.fromkeys(guild.categories, [])
        for category in category_channels:
            channels = [channel for channel in category.channels if not channel.permissions_synced]
            category_channels.update({category: channels})

        # unsynced_channel_permissions = {
        #     unsynced_channel_A: [('建立邀請', False), ('踢出成員', False), ...],
        #     unsynced_channel_B: [(...), ...],
        #     ...
        # }
        unsynced_channel_permissions = {}
        uncategory_channel = []
        for channel in guild.channels:
            if channel.permissions_synced:
                continue

            if channel.category is None and not isinstance(channel, CategoryChannel):
                uncategory_channel.append(channel)

            permissions = channel.permissions_for(role)
            permissions = self.localize_permissions(permissions)
            unsynced_channel_permissions.update({channel: permissions})

        # category_permissions = {
        #     category_A: [('建立邀請', False), ('踢出成員', False), ...],
        #     category_B: [(...), ...],
        #     ...
        # }
        category_permissions: dict = dict.fromkeys(guild.categories, [])
        for category in category_permissions:
            permissions = category.permissions_for(role)
            permissions = self.localize_permissions(permissions)
            category_permissions.update({category: permissions})

        template = self.env.get_template('channel_permission_for.html')
        template_output = template.render(
            role=role.name,
            category_channels=category_channels,
            uncategory_channel=uncategory_channel,
            category_permissions=category_permissions,
            unsynced_channel_permissions=unsynced_channel_permissions
        )

        filename = f"{role.name}.html"
        file = File(io.StringIO(template_output), filename=filename)
        await inter.response.send_message(
            file=file
        )

    @staticmethod
    def localize_permissions(permissions) -> list:
        """ Sort and localize the permission name. """
        permissions_dict = dict(list(iter(permissions)))
        result = []
        for k in PERMS_NAME_LOCALIZED:
            result.append(
                (PERMS_NAME_LOCALIZED.get(k), permissions_dict.get(k))
            )
        return result


def setup(bot: commands.InteractionBot):
    """ Called when this extension is loaded. """
    bot.add_cog(PermissionCheck(bot))
