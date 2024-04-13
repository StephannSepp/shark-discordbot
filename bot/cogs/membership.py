import datetime

from config import Config
from dateutil.relativedelta import relativedelta
from disnake import CmdInter
from disnake import Message
from disnake import ModalInteraction
from disnake import Role
from disnake.ext import commands
from disnake.ext import tasks
from disnake.ui import Modal
from disnake.ui import TextInput
from utils import embed_builder

from bot import get_cursor


class MembershipModal(Modal):
    def __init__(self, message: Message, role: Role, value: str = None) -> None:
        self.message = message
        self.role = role
        components = [
            TextInput(
                label="下次結帳日期",
                custom_id="date",
                placeholder="yyyy-mm-dd",
                value=value,
            )
        ]
        super().__init__(title="會員審核", components=components)

    async def callback(self, inter: ModalInteraction):
        try:
            next_billing_date = datetime.datetime.strptime(
                inter.text_values.get("date"), "%Y-%m-%d"
            )
        except ValueError:
            await inter.response.send_message("日期格式錯誤", ephemeral=True)
            return
        if next_billing_date < datetime.datetime.now():
            await inter.response.send_message("日期不可小於今天日期", ephemeral=True)
            return
        params = {
            "member_uid": self.message.author.id,
            "date": next_billing_date.strftime("%Y-%m-%d"),
            "message_id": self.message.id,
            "reviewer_uid": inter.author.id,
        }
        async with get_cursor() as cursor:
            query = (
                "INSERT INTO public.membership (member_uid, next_bill_date, "
                "message_id, reviewer_uid) VALUES (%(member_uid)s, %(date)s, "
                "%(message_id)s, %(reviewer_uid)s) "
                "ON CONFLICT (member_uid) DO UPDATE SET "
                "next_bill_date = %(date)s, "
                "message_id = %(message_id)s, "
                "reviewer_uid = %(reviewer_uid)s"
            )
            await cursor.execute(query, params)
        await self.message.author.add_roles(self.role)
        try:
            await self.message.author.send(
                "[CN] 您的會員證明已被驗證，現在可以使用以下會限頻道了！\n"
                "[EN] Your proof have been verified and you can now access "
                "to the following membership channel.\n"
                "------------------------------------------------------\n"
                "<#803473713369710653>\n"
                "<#851664375319494676>\n"
                "------------------------------------------------------\n"
                "審核資訊/Review info\n"
                f"下次帳單日期/Next billing date: {next_billing_date:%Y-%m-%d}\n"
                f"審核人/Reviewer: <@{inter.author.id}>"
            )
        except Exception:
            status = "未通知審核結果(未開啟DM)"
        else:
            status = "已通知審核結果"
        embed = embed_builder.information("更新會員完成")
        embed.add_field("會員", f"<@{self.message.author.id}>", inline=False)
        embed.add_field("下次結帳日期", f"{next_billing_date:%Y-%m-%d}", inline=False)
        embed.add_field("通知狀態", status)
        await inter.response.send_message(embed=embed)


class Membership(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.taskloop.start()

    async def check_membership(self) -> None:
        async with get_cursor() as cursor:
            query = (
                "DELETE FROM public.membership "
                "WHERE next_bill_date <= CURRENT_DATE - INTERVAL '7 days'"
            )
            await cursor.execute(query)
            query = (
                "SELECT member_uid FROM public.membership "
                "WHERE next_bill_date = CURRENT_DATE - INTERVAL '3 days' "
                "AND role_assigned = true"
            )
            await cursor.execute(query)
            result = await cursor.fetchall()
        notif_list = []
        for row in result:
            member_uid = row[0]
            role = self.bot.main_guild.get_role(846616775148044318)
            member = await self.bot.main_guild.getch_member(member_uid)
            if member is None:
                continue
            await member.remove_roles(role)
            notif_list.append(f"<@{member_uid}>")
            async with get_cursor() as cursor:
                query = (
                    "UPDATE public.membership SET role_assigned = false "
                    "WHERE member_uid = %(member_uid)s"
                )
                await cursor.execute(query, {"member_uid": member_uid})
        notif = "\n".join(notif_list)
        channel = self.bot.get_channel(847459494253690930)
        await channel.send(
            "以下蝦蝦們請於 <#846613455351185429> 重新提交會員證明\n"
            f"若已使用自動審核請無視這次通知\n{notif}"
        )

    @commands.message_command(name="membership")
    @commands.default_member_permissions(moderate_members=True)
    async def membership(self, inter: CmdInter, message: Message):
        role = self.bot.main_guild.get_role(846616775148044318)
        async with get_cursor() as cursor:
            query = (
                "SELECT next_bill_date FROM public.membership "
                "WHERE member_uid = %(uid)s"
            )
            await cursor.execute(query, {"uid": message.author.id})
            result = await cursor.fetchone()
        if result:
            new_date = result[0] + relativedelta(months=1)
            modal = MembershipModal(message, role, f"{new_date:%Y-%m-%d}")
        else:
            modal = MembershipModal(message, role)
        await inter.response.send_modal(modal=modal)

    @tasks.loop(time=datetime.time(hour=12))
    async def taskloop(self):
        await self.check_membership()

    @taskloop.before_loop
    async def before_taskloop(self):
        await self.bot.wait_until_ready()


def setup(bot):
    """Called when this extension is loaded."""
    bot.add_cog(Membership(bot))
