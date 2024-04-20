import datetime

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

    async def callback(self, inter: ModalInteraction):  # pylint: disable=W0221
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
        if self.role not in self.message.author.roles:
            await self.message.author.add_roles(self.role)
            try:
                description = (
                    "[CN] 您的會員證明已被驗證，現在可以使用以下會限頻道了！\n"
                    "[EN] Your proof have been verified and you can now access "
                    "to the following membership channel.\n"
                    "------------------------------------------------------\n"
                    "<#803473713369710653>\n"
                    "<#851664375319494676>\n"
                )
                embed = embed_builder.information("會員審核結果通知", description)
                embed.add_field(
                    "下次帳單日期/Next billing date",
                    next_billing_date.strftime("%Y-%m-%d"),
                    inline=False,
                )
                embed.add_field("審核人/Reviewer", f"<@{inter.author.id}>")
                await self.message.author.send(embed=embed)
            except Exception:
                status = "未通知審核結果(未開啟私訊)"
            else:
                status = "已通知審核結果(新增身分組)"
        else:
            status = "未通知審核結果(已有身分組)"
        embed = embed_builder.information("更新會員完成")
        embed.add_field("會員", f"<@{self.message.author.id}>", inline=False)
        embed.add_field("下次結帳日期", f"{next_billing_date:%Y-%m-%d}", inline=False)
        embed.add_field("通知狀態", status)
        await inter.response.send_message(embed=embed)


class Membership(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.taskloop.start()

    async def revoke_roles(self, member_uids: list) -> None:
        role = self.bot.main_guild.get_role(846616775148044318)
        for member_uid in member_uids:
            async with get_cursor() as cursor:
                query = (
                    "UPDATE public.membership SET role_assigned = false "
                    "WHERE member_uid = %(member_uid)s"
                )
                await cursor.execute(query, {"member_uid": member_uid})
            member = await self.bot.main_guild.getch_member(member_uid)
            if member is None:
                continue
            if role not in member.roles:
                continue
            await member.remove_roles(role)

    async def notify_members(self, member_uids: list) -> str:
        notif_list = []
        for member_uid in member_uids:
            member = await self.bot.main_guild.getch_member(member_uid)
            if member is None:
                continue
            notif_list.append(f"<@{member_uid}>")
        return "\n".join(notif_list)

    async def check_membership(self) -> None:
        async with get_cursor() as cursor:
            query = (
                "SELECT member_uid FROM public.membership "
                "WHERE next_bill_date = CURRENT_DATE - INTERVAL '2 days' "
                "AND role_assigned = true"
            )
            await cursor.execute(query)
            to_notify = await cursor.fetchall()
            query = (
                "SELECT member_uid FROM public.membership "
                "WHERE next_bill_date <= CURRENT_DATE - INTERVAL '3 days' "
                "AND role_assigned = true"
            )
            await cursor.execute(query)
            to_revoke = await cursor.fetchall()
            query = (
                "DELETE FROM public.membership "
                "WHERE next_bill_date <= CURRENT_DATE - INTERVAL '28 days'"
                "AND role_assigned = false"
            )
            await cursor.execute(query)
        await self.revoke_roles([row[0] for row in to_revoke])
        if not to_notify:
            return
        notif = await self.notify_members([row[0] for row in to_notify])
        channel = self.bot.get_channel(847459494253690930)
        await channel.send(
            "以下蝦蝦們請於 <#846613455351185429> 重新提交會員證明\n"
            f"若已使用自動審核請無視這次通知\n{notif}"
        )

    @commands.slash_command(name="manual_check_membership")
    @commands.default_member_permissions(administrator=True)
    async def manual_check_membership(self, inter: CmdInter) -> None:
        await inter.response.defer()
        await self.check_membership()
        await inter.edit_original_response("Done")

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
