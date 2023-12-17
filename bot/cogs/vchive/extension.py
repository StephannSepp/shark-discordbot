from disnake import CmdInter
from disnake.ext import commands

from . import ArchiveMenu
from . import ArchiveView
from . import ChannelMenu
from . import module


class Vchive(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(name="vchive")
    async def vchive(self, inter: CmdInter):
        """Vchive group commands."""

    @vchive.sub_command(name="archive")
    async def archive(self, inter: CmdInter, vid: str = None):
        """Show all stream archives or a specific archive. {{VCHIVE_ARCHIVE}}"""
        if vid:
            vid = vid.split(" - ")[0]
            view = ArchiveView(vid)
            embed = view.build_embed()
        else:
            view = ArchiveMenu()
            embed = view.build_embed()
        await inter.response.send_message(embed=embed, view=view, delete_after=1800)

    @archive.autocomplete("vid")
    async def vid_autocomp(self, inter: CmdInter, vid: str):
        return module.lookup_archives(vid)

    @vchive.sub_command_group(name="channel")
    async def channel(self, inter: CmdInter):
        """Channel information."""

    @channel.sub_command(name="all")
    async def all_channel(self, inter: CmdInter):
        """Show all channels being monitored. {{VCHIVE_CHANNEL_ALL}}"""
        view = ChannelMenu()
        embed = view.build_embed()
        await inter.response.send_message(embed=embed, view=view, delete_after=1800)

    @channel.sub_command(name="add")
    async def add_channel(self, inter: CmdInter, channel_id: str):
        """Add a channel to be monitored. {{VCHIVE_CHANNEL_ADD}}"""
        if inter.author.id not in self.bot.owner_ids:
            await inter.response.send_message("你沒有權限")
            return
        channel = await module.request_holodex_channel(channel_id)
        if channel is None:
            await inter.response.send_message(
                f"找不到 ID 為 {channel_id} 所屬頻道", ephemeral=False
            )
            return
        result = module.insert_channel(**channel)
        if result:
            await inter.response.send_message(f"新增頻道 {channel['name']} 成功")
        else:
            await inter.response.send_message(f"新增頻道 {channel['name']} 失敗")

    @channel.sub_command(name="remove")
    async def remove_channel(self, inter: CmdInter, channel_id: str):
        """Remove a channel from monitored. {{VCHIVE_CHANNEL_REMOVE}}"""
        if inter.author.id not in self.bot.owner_ids:
            await inter.response.send_message("你沒有權限")
            return
        result = module.delete_channel(channel_id)
        if result:
            await inter.response.send_message("刪除頻道成功")
        else:
            await inter.response.send_message("刪除頻道失敗")


def setup(bot: commands.InteractionBot):
    bot.add_cog(Vchive(bot))
