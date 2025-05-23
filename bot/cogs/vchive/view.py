import math
from datetime import timedelta
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
    FAILED = "失敗"


class Topic(Enum):
    SINGING = "歌回"
    BIRTHDAY = "生日直播"
    _3D_STREAM = "3D 直播"
    ANNIVERSARY = "週年直播"
    ASMR = "ASMR"


class ArchiveMenu(View):
    rowcount: int

    def __init__(self, channel: str = None, exclude_failed: bool = True):
        super().__init__(timeout=720)
        self.per_page = 5
        self.page = 0
        self.channel = channel
        self.exclude_failed = exclude_failed

    @classmethod
    async def create(cls, channel: str = None, exclude_failed: bool = True):
        self = cls(channel, exclude_failed)
        self.rowcount = await module.get_archive_rowcount(channel)
        return self

    async def build_embed(self) -> Embed:
        embed = embed_builder.information(
            title="直播存檔列表",
            description="請利用相同指令以 VID 參數搜尋、下載",
        )
        archives = await module.get_archives(
            page=self.page, channel=self.channel, exclude_failed=self.exclude_failed
        )
        for archive in archives:
            start_time = time_process.to_unix(archive["start_at"])
            title = (
                f"(🔒) {archive['title']}" if archive["private"] else archive["title"]
            )
            channel_name = archive["channel_name"]
            channel_id = archive["channel_id"]
            value = (
                f"[{title}](<https://youtu.be/{archive['vid']}>)",
                f"[{channel_name}](<https://www.youtube.com/channel/{channel_id}>)",
                f"開始: <t:{start_time}:F> <t:{start_time}:R>",
            )
            if (e := archive["end_at"]) is not None:
                end_time = time_process.to_unix(e)
                value += (f"結束: <t:{end_time}:F> <t:{end_time}:R>",)
            if (d := archive["duration"]) is not None:
                duration = time_process.strftimedelta(timedelta(seconds=d))
                value += (duration,)
            embed.add_field(
                f"VID: {archive['vid']} - {getattr(Status, archive['status']).value}",
                "\n".join(value),
                inline=False,
            )
        max_page = math.ceil(self.rowcount / self.per_page)
        embed.set_footer(text=f"Page {self.page + 1} / {max_page}")
        return embed

    @disnake.ui.button(emoji="⏮️", style=ButtonStyle.blurple)
    async def first_page(self, button: Button, inter: CmdInter):
        self.page = 0
        embed = await self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="◀️", style=ButtonStyle.secondary)
    async def prev_page(self, button: Button, inter: CmdInter):
        self.page = max(self.page - 1, 0)
        embed = await self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="🔄", style=ButtonStyle.success)
    async def refresh_page(self, button: Button, inter: CmdInter):
        embed = await self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="▶️", style=ButtonStyle.secondary)
    async def next_page(self, button: Button, inter: CmdInter):
        max_page = math.ceil(self.rowcount / self.per_page)
        self.page = min(self.page + 1, max_page)
        embed = await self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="⏭️", style=ButtonStyle.blurple)
    async def last_page(self, button: Button, inter: CmdInter):
        self.page = math.ceil(self.rowcount / self.per_page) - 1
        embed = await self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)


class ArchiveView(View):
    def __init__(self, vid: str):
        super().__init__(timeout=720)
        self.vid = vid

    async def build_embed(self) -> Embed:
        archive = await module.archive_detail(self.vid)
        if archive["v_org"].lower() == "independents":
            organization = "個人勢"
        else:
            organization = f"{archive['v_org']} {archive['v_group']}"
        description = f"{archive['channel_name']}\n{organization}"
        title = f"(🔒) {archive['title']}" if archive["private"] else archive["title"]
        embed = embed_builder.information(title=title, description=description)
        start_time = time_process.to_unix(archive["start_at"])
        embed.add_field(
            "VID",
            f"[{archive['vid']}](<https://youtu.be/{archive['vid']}>)",
            inline=False,
        )
        embed.add_field(
            "直播開始時間", f"<t:{start_time}:F> <t:{start_time}:R>", inline=False
        )
        if (e := archive["end_at"]) is not None:
            end_time = time_process.to_unix(e)
            embed.add_field(
                "直播結束時間", f"<t:{end_time}:F> <t:{end_time}:R>", inline=False
            )
        if (d := archive["duration"]) is not None:
            duration = time_process.strftimedelta(timedelta(seconds=d))
            embed.add_field("直播長度", duration, inline=False)
        embed.add_field(
            "存檔狀態", getattr(Status, archive["status"]).value, inline=False
        )
        embed.set_thumbnail(url=archive["photo"])
        return embed

    @disnake.ui.button(label="下載", emoji="🔗", style=ButtonStyle.secondary)
    async def last_page(self, button: Button, inter: CmdInter):
        await inter.response.send_message("暫不提供下載")
        return
        # await inter.response.defer()
        # m = await inter.followup.send("請求下載連結中...", ephemeral=True, wait=True)
        # try:
        #     result = await module.get_share_link(inter.author.id, self.vid)
        # except Exception as exc:
        #     await inter.response.send_message(exc, ephemeral=True)
        #     return

        # filename, url, password = result
        # await m.edit(f"{filename}\n[下載密碼: {password} (期限 3 日)](<{url}>)")


class ChannelMenu(View):
    rowcount: int

    def __init__(self):
        super().__init__(timeout=720)
        self.per_page = 7
        self.page = 0

    @classmethod
    async def create(cls):
        self = cls()
        self.rowcount = await module.get_channel_rowcount()
        return self

    async def build_embed(self) -> Embed:
        embed = embed_builder.information(title="存檔頻道列表")
        channels = await module.get_channels(page=self.page)
        for channel in channels:
            if channel["v_org"].lower() == "independents":
                organization = "個人勢"
            else:
                organization = f"{channel['v_org']} {channel['v_group']}"
            yt_handle = channel["yt_handle"]
            value = (
                f"[{yt_handle}](<https://www.youtube.com/{yt_handle}>)",
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
        max_page = math.ceil(self.rowcount / self.per_page)
        embed.set_footer(text=f"Page {self.page + 1} / {max_page}")
        return embed

    @disnake.ui.button(emoji="⏮️", style=ButtonStyle.blurple)
    async def first_page(self, button: Button, inter: CmdInter):
        self.page = 0
        embed = await self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="◀️", style=ButtonStyle.secondary)
    async def prev_page(self, button: Button, inter: CmdInter):
        self.page = max(self.page - 1, 0)
        embed = await self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="▶️", style=ButtonStyle.secondary)
    async def next_page(self, button: Button, inter: CmdInter):
        max_page = math.ceil(self.rowcount / self.per_page)
        self.page = min(self.page + 1, max_page)
        embed = await self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="⏭️", style=ButtonStyle.blurple)
    async def last_page(self, button: Button, inter: CmdInter):
        self.page = math.ceil(self.rowcount / self.per_page) - 1
        embed = await self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)
