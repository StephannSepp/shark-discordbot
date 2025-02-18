import disnake
from disnake.ext import commands

class ForumPinCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @commands.slash_command(name="pin", description="將貼文置頂或解除置頂")
    async def pin(self, inter: disnake.ApplicationCommandInteraction, message: disnake.Message):
        if not isinstance(inter.channel, disnake.Thread):
            await inter.response.send_message("此功能只能在討論串中使用", ephemeral=True)
            return
        if inter.channel.owner_id != inter.user.id:
            await inter.response.send_message("此功能只能由討論串發文者使用", ephemeral=True)
            return
        try:
            if not message.pinned:
                await message.pin()
                await inter.response.send_message("已置頂", ephemeral=True)
            else:
                await message.unpin()
                await inter.response.send_message("已解除置頂", ephemeral=True)
        except Exception as e:
            print(f"Error toggling pin status: {e}")
            await inter.response.send_message("發生錯誤",ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(ForumPinCog(bot))
