"""
events.role_divider
----------------

A simple listener to detect any role changes.

When a member's role changes, the bot will assign or revoke
a role divider to the member.

This feature is only for Atlantis.

:Date: 11-27-2022
"""
# Third-party library imports
from disnake import Member
from disnake import utils
from disnake.ext import commands
# Local imports
from config import Config


class RoleDivider(commands.Cog):
    """ A Disnake Cog wraps commands as a Python class. """

    mod_role_divider = None
    spcl_role_divider = None

    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.Cog.listener("on_member_update")
    async def divide_roles(self, before: Member, after: Member):
        if after.guild.id != Config.atlantis_id:
            return

        if len(after.roles) == len(before.roles):
            return

        if self.is_mod(after):
            await after.add_roles(self.mod_role_divider)
        else:
            await after.remove_roles(self.mod_role_divider)

        if self.has_spcl_role(after):
            await after.add_roles(self.spcl_role_divider)
        else:
            await after.remove_roles(self.spcl_role_divider)

    def is_mod(self, member: Member):
        """ Check whether the member is assigned as a moderator or not. """
        if self.mod_role_divider is None:
            self.mod_role_divider = utils.get(member.guild.roles, id=795159043656253470)

        return member.top_role > self.mod_role_divider

    def has_spcl_role(self, member: Member):
        """ Check whether the member has a speical role or not. """
        if self.spcl_role_divider is None:
            self.spcl_role_divider = utils.get(member.guild.roles, id=795159399756857344)

        for role in member.roles:
            if self.spcl_role_divider < role < self.mod_role_divider:
                return True

        return False
