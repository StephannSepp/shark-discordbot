from config import Config
from disnake import CmdInter
from disnake.ext.commands.errors import CheckFailure


def is_on_command_channel(inter: CmdInter):
    if inter.guild_id == Config.home_guild:
        if inter.channel_id != 761814788589223978:
            raise CheckFailure("該指令僅能用於<#761814788589223978>中")
    return True
