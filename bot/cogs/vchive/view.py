from enum import Enum

import disnake
from disnake import ButtonStyle
from disnake import CmdInter
from disnake import Embed
from disnake.ui import Button
from disnake.ui import View

from utils import embed_builder
from utils import time_process

from . import module


class Status(Enum):
    WAIT = "等待中"
    PEDDING = "下載中"
    DONE = "已存檔"


class Topic(Enum):
    SINGING = "歌回"
    BIRTHDAY = "生日直播"
    _3D_STREAM = "3D 直播"
    ANNIVERSARY = "週年直播"
    ASMR = "ASMR"


class ArchiveMenu(View):
    def __init__(self):
        super().__init__(timeout=1800)
        self.per_page = 5
        self.page = 0
        self.rowcount = module.get_archive_rowcount()

    def build_embed(self) -> Embed:
        embed = embed_builder.information(
            title="直播存檔列表",
            description="請利用相同指令以 VID 參數搜尋、下載",
        )
        archives = module.get_archives(page=self.page)
        for archive in archives:
            start_time = time_process.to_unix(archive["start_at"])
            value = (
                archive["title"],
                archive["channel_name"],
                f"<t:{start_time}:F> <t:{start_time}:R>",
            )
            embed.add_field(
                f"VID: {archive['vid']} - {getattr(Status, archive['status']).value}",
                "\n".join(value),
                inline=False,
            )
        embed.set_footer(text=f"Page {self.page + 1}")
        return embed

    @disnake.ui.button(emoji="⏮️", style=ButtonStyle.blurple)
    async def first_page(self, button: Button, inter: CmdInter):
        self.page = 0
        embed = self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="◀️", style=ButtonStyle.secondary)
    async def prev_page(self, button: Button, inter: CmdInter):
        self.page = max(self.page - 1, 0)
        embed = self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="🔄", style=ButtonStyle.success)
    async def refresh_page(self, button: Button, inter: CmdInter):
        embed = self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="▶️", style=ButtonStyle.secondary)
    async def next_page(self, button: Button, inter: CmdInter):
        self.page = min(self.page + 1, self.rowcount // self.per_page)
        embed = self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="⏭️", style=ButtonStyle.blurple)
    async def last_page(self, button: Button, inter: CmdInter):
        self.page = self.rowcount // self.per_page
        embed = self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)


class ArchiveView(View):
    def __init__(self, vid: str):
        super().__init__(timeout=1800)
        self.vid = vid

    def build_embed(self) -> Embed:
        archive = module.archive_detail(self.vid)
        if archive["v_org"].lower() == "independents":
            organization = "個人勢"
        else:
            organization = f"{archive['v_org']} {archive['v_group']}"
        description = f"{archive['channel_name']}\n{organization}"
        embed = embed_builder.information(
            title=archive["title"],
            description=description,
        )
        start_time = time_process.to_unix(archive["start_at"])
        embed.add_field("VID", archive["vid"], inline=False)
        embed.add_field(
            "直播開始時間", f"<t:{start_time}:F> <t:{start_time}:R>", inline=False
        )
        embed.add_field("存檔狀態", getattr(Status, archive["status"]).value, inline=False)
        embed.set_thumbnail(url=archive["photo"])
        return embed

    @disnake.ui.button(label="下載", emoji="🔗", style=ButtonStyle.secondary)
    async def last_page(self, button: Button, inter: CmdInter):
        result = await module.get_share_link(self.vid)
        if result is None:
            await inter.response.send_message("該存檔尚未開放", ephemeral=True)
        else:
            url, password = result
            await inter.response.send_message(
                f"下載連結: {url}\n下載密碼: {password}\n下載期限: 3 日", ephemeral=True
            )


class ChannelMenu(View):
    def __init__(self):
        super().__init__(timeout=1800)
        self.per_page = 7
        self.page = 0
        self.rowcount = module.get_channel_rowcount()

    def build_embed(self) -> Embed:
        embed = embed_builder.information(title="存檔頻道列表")
        channels = module.get_channels(page=self.page)
        for channel in channels:
            if channel["v_org"].lower() == "independents":
                organization = "個人勢"
            else:
                organization = f"{channel['v_org']} {channel['v_group']}"
            value = (
                channel["yt_handle"],
                organization,
            )
            if channel["english_name"] is None:
                channel_name = channel["channel_name"]
            else:
                channel_name = f"{channel['channel_name']} ({channel['english_name']})"
            embed.add_field(
                channel_name,
                "\n".join(value),
                inline=False,
            )
        embed.set_footer(text=f"Page {self.page + 1}")
        return embed

    @disnake.ui.button(emoji="⏮️", style=ButtonStyle.blurple)
    async def first_page(self, button: Button, inter: CmdInter):
        self.page = 0
        embed = self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="◀️", style=ButtonStyle.secondary)
    async def prev_page(self, button: Button, inter: CmdInter):
        self.page = max(self.page - 1, 0)
        embed = self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="▶️", style=ButtonStyle.secondary)
    async def next_page(self, button: Button, inter: CmdInter):
        self.page = min(self.page + 1, self.rowcount // self.per_page)
        embed = self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="⏭️", style=ButtonStyle.blurple)
    async def last_page(self, button: Button, inter: CmdInter):
        self.page = self.rowcount // self.per_page
        embed = self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)
