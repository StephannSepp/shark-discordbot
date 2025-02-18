import disnake
from disnake import CmdInter
from disnake import Message
from disnake.ext import commands


class ThreadPinCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.message_command(name="thread_pin", description="將貼文置頂或解除置頂")
    async def thread_pin(self, inter: CmdInter, message: Message) -> None:
        if not isinstance(message.channel, disnake.Thread):
            await inter.response.send_message(
                "此功能只能在論壇貼文中使用",
                ephemeral=True,
            )
            return
        if message.channel.owner_id != inter.user.id:
            await inter.response.send_message(
                "此功能只能由論壇貼文原PO使用",
                ephemeral=True,
            )
            return
        try:
            if not message.pinned:
                await message.pin()
                await inter.response.send_message("已釘選訊息", ephemeral=True)
            else:
                await message.unpin()
                await inter.response.send_message("已解除釘選", ephemeral=True)
        except Exception as e:
            print(f"Error toggling pin status: {e}")
            await inter.response.send_message("發生錯誤", ephemeral=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(ThreadPinCog(bot))
