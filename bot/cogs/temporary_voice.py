"""
10/15/22 TODO: need to re-write the code
10/15/22 change to default_member_permissions decorator
"""

import os
from random import choice

from disnake import Permissions
from disnake.ext import commands
from disnake.ext import tasks
from disnake.utils import get


class TemporaryVoice(commands.Cog):
    Atlantis_ID = int(os.environ.get("Atlantis_ID"))
    def __init__(self, bot):
        self.bot = bot
        self.taskloop.start() # pylint: disable=maybe-no-member

    @commands.slash_command(name='tvclock', description='鎖定/解鎖當前語音頻道')
    async def lock(self, inter):
        channel = get(inter.guild.voice_channels, name=f'{inter.author.name} 的頻道')
        if channel is None:
            await inter.response.send_message("你必須在自己的動態語音頻道內.", ephemeral=True)
        else:
            if channel.permissions_for(inter.guild.default_role).connect:
                await channel.set_permissions(inter.guild.default_role, connect=False)
                await inter.response.send_message(f"上鎖 {inter.author.name} 的頻道.")
            else:
                await channel.set_permissions(inter.guild.default_role, connect=True)
                await inter.response.send_message(f"解鎖 {inter.author.name} 的頻道.")

    @commands.slash_command(name='tvcclaim', description='宣示當前語音頻道')
    @commands.default_member_permissions(administrator=True)
    async def claim(self, inter):
        channel = inter.author.voice.channel
        if channel.name == f'{inter.author.name} 的頻道':
            await inter.response.send_message("這個頻道已經屬於你.", ephemeral=True)
        elif channel.category_id == 973743537994752000 and channel.id != 973743539089457223:
            await channel.edit(name=f'{inter.author.name} 的頻道')
            await inter.response.send_message(f"{inter.author.mention} 已宣稱此頻道.")
        else:
            await inter.response.send_message("你必須在動態語音頻道內.", ephemeral=True)


    @commands.Cog.listener('on_voice_state_update')
    async def create_tvc(self, member, before, after):
        if after.channel is not None and after.channel.id == 973743539089457223:
            channel = get(member.guild.voice_channels, name=f'{member.name} 的頻道')
            if channel is None:
                category = get(member.guild.categories, id=973743537994752000)
                new_channel = await member.guild.create_voice_channel(name=f'{member.name} 的頻道', category=category, bitrate=64000, user_limit=0)
                await member.move_to(new_channel)
            else:
                await member.move_to(channel)
        elif before.channel and before.channel.category_id == 973743537994752000 and before.channel.id != 973743539089457223 and not before.channel.members:
            await before.channel.delete()

    async def tvc_helper(self) -> None:
        guild = self.bot.get_guild(self.Atlantis_ID)
        for channel in self.bot.get_guild(self.Atlantis_ID).voice_channels:
            if channel.category_id == 973743537994752000 and channel.id != 973743539089457223:
                if not channel.members:
                    await channel.delete()
                else:
                    members_list = []
                    owner = get(guild.members, name=channel.name[:-4])
                    for member in channel.members:
                        if not member.bot:
                            members_list.append(member.id)
                    if not owner or owner.id not in members_list:
                        new_owner = get(guild.members, id=choice(members_list))
                        await channel.edit(name=f'{new_owner.name} 的頻道')

    async def creat_vc_cleaner(self) -> None:
        guild = self.bot.get_guild(self.Atlantis_ID)
        channel = get(guild.voice_channels, id=973743539089457223)
        for member in channel.members:
            channel = get(member.guild.voice_channels, name=f'{member.name} 的頻道')
            if channel is None:
                category = get(member.guild.categories, id=973743537994752000)
                new_channel = await member.guild.create_voice_channel(name=f'{member.name} 的頻道', category=category, bitrate=64000, user_limit=0)
                await member.move_to(new_channel)
            else:
                await member.move_to(channel)

    @tasks.loop(seconds=5.0)
    async def taskloop(self) -> None:
        try:
            await self.tvc_helper()
            await self.creat_vc_cleaner()
        except Exception as err: # pylint: disable=broad-except
            print(err)

    @taskloop.before_loop
    async def before_taskloop(self) -> None:
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(TemporaryVoice(bot))
