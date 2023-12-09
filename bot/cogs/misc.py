import platform as pf

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

    @commands.slash_command(name="botinfo")
    async def botinfo(self, inter: CmdInter):
        """To show bot and system information. {{BOTINFO}}"""
        embed = embed_builder.information(
            title="機器人資訊",
            description="不是那隻迷因鯊魚、也不是亞特蘭提斯的後裔，只是在亞特蘭提斯的打工BOT。",
            thumbnail=self.bot.user.avatar.url,
        )
        owner = await self.bot.getch_user(self.bot.owner_id)
        embed.add_field(
            name="擁有者", value=f"{owner.display_name}@{owner.name}", inline=True
        )
        embed.add_field(
            name="原始碼",
            value="[GitHub](https://github.com/StephannSepp/shark-discordbot)",
            inline=True,
        )
        version_info = f"{self.bot.version} with Python {pf.python_version()}"
        system_info = f"{pf.system()}-{pf.release()}-{pf.machine()}"
        up_time_info = f"{self.bot.up_time} on {system_info}"
        embed.add_field(name="Bot 版本", value=version_info, inline=False)
        embed.add_field(name="Bot 運行狀態", value=up_time_info, inline=False)
        embed.add_field(name="DB 運行狀態", value=self.bot.db_up_time, inline=False)
        await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(name="kuaikuai")
    async def kuaikuai(self, inter: CmdInter):
        """Digital Kuai Kaui makes the bot behave well. {{KUAIKUAI}}"""
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
