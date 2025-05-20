from config import Config
from disnake import Guild
from disnake import Member
from disnake import utils
from disnake.ext import commands


class RoleDivider(commands.Cog):
    mod_role_divider = None
    sup_role_divider = None
    spcl_role_divider = None

    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.Cog.listener("on_member_update")
    async def divide_roles(self, before: Member, after: Member):
        if after.guild.id != Config.home_guild:
            return

        if len(after.roles) == len(before.roles):
            return

        if self.is_mod(after):
            await after.add_roles(self.mod_role_divider)
        else:
            await after.remove_roles(self.mod_role_divider)

        if self.has_sup_role(after):
            await after.add_roles(self.sup_role_divider)
        else:
            await after.remove_roles(self.sup_role_divider)

        if self.has_spcl_role(after):
            await after.add_roles(self.spcl_role_divider)
        else:
            await after.remove_roles(self.spcl_role_divider)

    def get_roles(self, guild: Guild) -> None:
        if self.mod_role_divider is None:
            self.mod_role_divider = utils.get(guild.roles, id=795159043656253470)
        if self.sup_role_divider is None:
            self.sup_role_divider = utils.get(guild.roles, id=1065553075135324210)
        if self.spcl_role_divider is None:
            self.spcl_role_divider = utils.get(guild.roles, id=795159399756857344)

    def is_mod(self, member: Member) -> bool:
        self.get_roles(member.guild)
        for role in member.roles:
            if role == self.mod_role_divider:
                continue
            if role == self.sup_role_divider:
                continue
            if role == self.spcl_role_divider:
                continue
            if role > self.mod_role_divider:
                return True

    def has_sup_role(self, member: Member) -> bool:
        self.get_roles(member.guild)
        for role in member.roles:
            if role == self.mod_role_divider:
                continue
            if role == self.sup_role_divider:
                continue
            if role == self.spcl_role_divider:
                continue
            if self.sup_role_divider < role < self.mod_role_divider:
                return True

    def has_spcl_role(self, member: Member) -> bool:
        self.get_roles(member.guild)
        for role in member.roles:
            if role == self.mod_role_divider:
                continue
            if role == self.sup_role_divider:
                continue
            if role == self.spcl_role_divider:
                continue
            if self.spcl_role_divider < role < self.sup_role_divider:
                return True

        return False
