from disnake import CmdInter
from disnake import File
from disnake.ext import commands

from utils import embed_builder


class Misc(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(name="ping", description="Ping! Pong!")
    async def ping(self, inter: CmdInter):
        """Ping the bot."""
        await inter.response.send_message(
            f"{round(self.bot.latency*1000)}ms", ephemeral=True
        )

    @commands.slash_command(name="donothing", description="This function does nothing.")
    async def donothing(self, inter: CmdInter):
        """This function does nothing."""
        await inter.response.send_message(file=File("static/donothing.png"))

    @commands.slash_command(name="botinfo", description="機器人資訊")
    async def botinfo(self, inter: CmdInter):
        """Display bot information."""
        embed = embed_builder.information(
            title="機器人資訊",
            description="不是那隻迷因鯊魚、也不是亞特蘭提斯的後裔，只是在亞特蘭提斯的打工BOT。",
            thumbnail=self.bot.user.avatar.url,
        )
        embed.add_field(name="擁有者", value="林昕渪@stevesepp87", inline=True)
        embed.add_field(
            name="原始碼",
            value="[GitHub](https://github.com/StephannSepp/shark-discordbot)",
            inline=True,
        )
        embed.add_field(name="版本", value=self.bot.version, inline=False)
        embed.add_field(name="運行時間", value=self.bot.up_time, inline=False)
        await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(name="kuaikuai", description="乖乖 - 數位板")
    async def kuaikuai(self, inter: CmdInter):
        file = File(
            "static/kuaikuai_20231220A4.png", filename="kuaikuai_20231220A4.png"
        )
        embed = embed_builder.information(
            title="數位板乖乖",
            description="祈求 BOT 運作穩定。",
        )
        embed.add_field(name="品名", value="乖乖玉米脆條", inline=True)
        embed.add_field(name="口味", value="奶油椰子", inline=True)
        embed.add_field(name="保存期限", value="1年", inline=True)
        embed.add_field(name="有效日期", value="20231220A4", inline=False)
        embed.add_field(name="原產地", value="台灣", inline=False)
        embed.set_image(file=file)
        await inter.response.send_message(embed=embed)


def setup(bot: commands.InteractionBot):
    bot.add_cog(Misc(bot))
