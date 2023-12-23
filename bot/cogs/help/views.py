import disnake
from disnake import ButtonStyle
from disnake import CmdInter
from disnake import Embed
from disnake.ui import Button
from disnake.ui import View

from .embeds import embeds


class HelpView(View):
    def __init__(self, channel: str = None):
        super().__init__(timeout=720)
        self.embeds = embeds
        self.index = 0
        self.max_index = len(embeds) - 1

    def get_embed(self) -> Embed:
        embed = self.embeds[self.index]
        embed.set_footer(text=f"{self.index + 1} / {self.max_index + 1}")
        return self.embeds[self.index]

    @disnake.ui.button(emoji="⏮️", style=ButtonStyle.blurple)
    async def first_page(self, button: Button, inter: CmdInter):
        self.index = 0
        embed = self.get_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="◀️", style=ButtonStyle.secondary)
    async def prev_page(self, button: Button, inter: CmdInter):
        self.index = max(self.index - 1, 0)
        embed = self.get_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="▶️", style=ButtonStyle.secondary)
    async def next_page(self, button: Button, inter: CmdInter):
        self.index = min(self.index + 1, self.max_index)
        embed = self.get_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="⏭️", style=ButtonStyle.blurple)
    async def last_page(self, button: Button, inter: CmdInter):
        self.index = self.max_index
        embed = self.get_embed()
        await inter.response.edit_message(embed=embed, view=self)
