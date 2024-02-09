import platform as pf

from disnake import AllowedMentions
from disnake import CmdInter
from disnake import File
from disnake.ext import commands
from utils import embed_builder

MahjongSoulGameMode = commands.option_enum(
    {
        "三人": "三人",
        "四人": "四人",
        "赤羽之戰": "四人(赤羽)",
        "暗夜之戰": "四人(暗夜)",
        "修羅之戰": "四人(修羅)",
    }
)
MahjongSoulGameLength = commands.option_enum(
    {
        "一局": "一局",
        "東風場": "東",
        "半莊": "南",
    }
)


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
        owner_field = []
        for owner_id in self.bot.owner_ids:
            owner = await self.bot.getch_user(owner_id)
            owner_field.append(f"{owner.display_name}@{owner.name}")
        embed.add_field(name="擁有者", value="\n".join(owner_field), inline=True)
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
        await inter.response.send_message(embed=embed)

    @commands.slash_command(name="kuaikuai")
    async def kuaikuai(self, inter: CmdInter):
        """Digital Kuai Kaui makes the bot behave well. {{KUAIKUAI}}"""
        file = File(
            "static/kuaikuai_20240901C3.png", filename="kuaikuai_20231220A4.png"
        )
        embed = embed_builder.information(
            title="數位板乖乖",
            description="祈求 BOT 運作穩定。",
        )
        embed.add_field(
            name="保存期限", value="<t:1725120000:D> <t:1725120000:R>", inline=False
        )
        embed.set_image(file=file)
        await inter.response.send_message(embed=embed)

    @commands.slash_command(name="mahjongsoul")
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def mahjongsoul(
        self,
        inter: CmdInter,
        game_mode: MahjongSoulGameMode,
        game_length: MahjongSoulGameLength,
        room: str,
        description: str = "",
    ):
        """Ping other Janshis. {{MAHJONGSOUL}}"""
        if len(room) != 5 or not room.isdigit():
            await inter.response.send_message("房號無效", ephemeral=True)
            return
        url = f"https://game.maj-soul.com/1/?room={room}"
        jp_url = f"https://game.mahjongsoul.com/?room={room}"
        role_assign_url = (
            "https://discord.com/channels/740908503585259553/758068566263332874"
            "/1081556163805593641"
        )
        embed = embed_builder.information(
            title=f"雀魂友人場 {room} {game_mode}{game_length}",
            description=f"{description}\n\n[國際版快速入口]({url})\n[日版快速入口]({jp_url})",
        )
        embed.add_field("發起人", inter.author.mention)
        await inter.response.send_message(
            f"<@&1202555563226177536>\n想被揪的可以從 {role_assign_url} 領取身分組",
            embed=embed,
            allowed_mentions=AllowedMentions(
                roles=[self.bot.main_guild.get_role(1202555563226177536)]
            ),
        )

    @commands.slash_command(name="changelog")
    async def changelog(self, inter: CmdInter):
        """Show the changelog of the current version. {{MISC_CHANGELOG}}"""
        description = (
            "# 2.6.7\n"
            "## 行動\n"
            "* 現在行動開始時或行動進行中會顯示其他玩家的名字及數量\n"
            "\n"
            "## 銀行\n"
            "* 個人帳戶資訊中現在會顯示進行中的行動\n"
            "* 與銀行的交易現在會被記錄\n"
            "* 銀行每日財務狀況現在也會被記錄\n"
            "* 修正金幣餘額負數顯示錯誤的問題\n"
            "\n"
            "## 霰彈槍輪盤\n"
            "* 增加天選之人、長壽兩個獎勵\n"
            "\n"
            "## 其他\n"
            "* "
        )
        embed = embed_builder.information("更新日誌", description)
        await inter.response.send_message(embed=embed)


def setup(bot: commands.InteractionBot):
    bot.add_cog(Misc(bot))
