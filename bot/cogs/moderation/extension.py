from disnake import Attachment
from disnake import CmdInter
from disnake import TextChannel
from disnake import User
from disnake.ext import commands

from utils import embed_builder
from utils import time_process

from . import module


class Moderation(commands.Cog):
    """All moderation commands are under this Moderation class."""

    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(name="warn", description="警告系統")
    @commands.default_member_permissions(moderate_members=True)
    @commands.guild_only()
    async def warn(self, inter: CmdInter):
        """A warning system command group.

        This command group are requiring `moderate_members` permission.

        Subcommands:
            add: Add a warning to a user.
            remove: Remove a warning from a user.
            list: List all of the warnings of a user.
        """

    @warn.sub_command(name="add", description="對成員新增一個警告")
    async def warning_add(
        self,
        inter: CmdInter,
        user: User,
        reason: str = "沒有提供理由",
        copy: TextChannel = None,
    ):
        """Add a warning to a user.

        Args
            inter: A disnake `ApplicationCommandInteraction`.
            user: A disnake `User`.
            reason: The reason for the warning, defaults to "沒有提供理由".
            copy: If a `TextChannel` is provided, the bot will send a copy \
                message to the specified channel.
        """
        await inter.response.defer()

        warning_id = module.add_warning(
            user_id=user.id,
            server_id=inter.guild_id,
            moderator_id=inter.author.id,
            reason=reason,
        )
        embed = embed_builder.information(
            title="懲處紀錄",
            description=f"{user.mention} 被 {inter.author.mention} 警告",
            thumbnail=user.avatar.url,
        )
        embed.add_field(name="理由", value=reason, inline=False)
        embed.add_field(name="警告編號", value=warning_id, inline=False)
        if copy:
            await copy.send(embed=embed)
            await inter.followup.send(embed=embed)
        else:
            await inter.followup.send(embed=embed)

    @warn.sub_command(name="remove", description="對成員移除警告")
    async def warning_remove(
        self,
        inter: CmdInter,
        user: User,
        warning_id: commands.LargeInt,
        copy: TextChannel = None,
    ):
        """Remove a warning from a user.

        Args:
            inter: A disnake `ApplicationCommandInteraction`.
            user: A disnake `User`.
            warning_id: The snowflake-like ID of the warning.
            copy: If a `TextChannel` is provided, the bot will send a copy \
                message to the specified channel.
        """
        await inter.response.defer()

        try:
            reason = module.remove_warn(inter.guild_id, user.id, warning_id)
        except:  # pylint: disable=bare-except
            embed = embed_builder.error(
                title="無法執行", description="發生錯誤，請確認該警告編號及對象確實存在"
            )
            await inter.followup.send(embed=embed)
            return

        embed = embed_builder.information(
            title="移除警告",
            description=f"{user.mention} 被 {inter.author.mention} 移除了一個警告",
            thumbnail=user.avatar.url,
        )
        embed.add_field(name="警告理由", value=reason, inline=False)
        embed.add_field(name="警告編號", value=warning_id, inline=False)
        if copy:
            await copy.send(embed=embed)
            await inter.followup.send(embed=embed)
        else:
            await inter.followup.send(embed=embed)

    @warn.sub_command(name="list", description="檢查成員的警告")
    async def warning_list(self, inter: CmdInter, user: User):
        """List all of the warnings from a user.

        Args:
            inter: A disnake `ApplicationCommandInteraction`.
            user: A disnake `User`.
        """

        warning_list = module.list_warns(inter.guild_id, user.id)
        embed = embed_builder.information(
            title="警告紀錄", description="", thumbnail=user.avatar.url
        )
        description = f"以下為{user.mention}的警告紀錄"
        if len(warning_list) == 0:
            description = "該成員沒有任何警告"
        else:
            for warning in warning_list:
                embed.add_field(
                    name=f"#{warning[0]}｜<t:{int(warning[4].timestamp())}>",
                    value=f"•{warning[3]}｜by <@{warning[2]}>",
                    inline=False,
                )
        embed.description = description
        await inter.response.send_message(embed=embed)

    @commands.slash_command(name="mute", description="禁言成員，範例格式：4d2h13m56s，時長支持到28d")
    @commands.default_member_permissions(moderate_members=True)
    @commands.guild_only()
    async def mute(
        self,
        inter: CmdInter,
        user: User,
        raw_duration: str,
        reason: str = "沒有提供理由",
        copy: TextChannel = None,
        attachment: Attachment = None,
    ):
        """Times out a user, the member will not be able to interact with the
        guild. A `moderate_members` permission is required.

        Args:
            inter: A disnake `ApplicationCommandInteraction`.
            user: A disnake `User`.
            raw_duration: How many seconds for the timeout.
            reason: The reason for the timeout, defaults to "沒有提供理由".
            copy: If a `TextChannel` is provided, the bot will send a copy \
                message to the specified channel.
            attachment: Some file or image for the extra information.
        """
        await inter.response.defer()
        file = None
        duration = time_process.parse_time(raw_duration)
        member = inter.guild.get_member(user.id)
        if member is None:
            try:
                member = await inter.guild.fetch_member(user.id)
            except:  # pylint: disable=bare-except
                embed = embed_builder.error(title="無法執行", description="發生錯誤，請確認該對象確實存在")
                await inter.followup.send(embed=embed)
                return

        if (
            member.guild_permissions.administrator
            or member.guild_permissions.moderate_members
        ):
            embed = embed_builder.error(title="無法執行", description="該成員有相同或更大的權限")
            await inter.followup.send(embed=embed)
            return

        try:
            message = f"你在 {inter.guild.name} 被禁言\n" f"原因：{reason}\n" f"時長：{duration}\n"
            if attachment is not None and attachment.content_type.startswith("image"):
                message += "附件：\n"
                file = await attachment.to_file()
            await member.send(message, file=file)
        except:  # pylint: disable=bare-except
            # Pass if failed to DM user
            pass

        try:
            await member.timeout(duration=duration.total_seconds(), reason=reason)
        except:  # pylint: disable=bare-except
            embed = embed_builder.error(title="無法執行", description="禁言成員時發生錯誤")
            await inter.followup.send(embed=embed)
            return

        embed = embed_builder.information(
            title="懲處紀錄",
            description=f"{member.mention} 被 {inter.author.mention} 禁言",
            thumbnail=member.avatar.url,
        )
        embed.add_field(name="理由", value=reason, inline=False)
        embed.add_field(name="時長", value=duration, inline=False)
        if attachment is not None and attachment.content_type.startswith("image"):
            embed = await attach_to_embed(embed, attachment)

        if copy:
            await copy.send(embed=embed)
            if attachment is not None and attachment.content_type.startswith("image"):
                embed = await attach_to_embed(embed, attachment)
            await inter.followup.send(embed=embed)
        else:
            await inter.followup.send(embed=embed)

    @commands.slash_command(name="unmute", description="解除禁言成員")
    @commands.default_member_permissions(moderate_members=True)
    @commands.guild_only()
    async def unmute(
        self,
        inter: CmdInter,
        user: User,
        reason: str = "沒有提供理由",
        copy: TextChannel = None,
    ):
        """Unmute a user. The `moderate_members` permission is required.

        Args:
            inter: A disnake `ApplicationCommandInteraction`.
            user: A disnake `User`.
            reason: The reason for the unmute, defaults to "沒有提供理由".
            copy: If a `TextChannel` is provided, the bot will send a copy \
                message to the specified channel.
        """
        await inter.response.defer()
        member = inter.guild.get_member(user.id)
        if member is None:
            try:
                member = await inter.guild.fetch_member(user.id)
            except:  # pylint: disable=bare-except
                embed = embed_builder.error(title="無法執行", description="發生錯誤，請確認該對象確實存在")
                await inter.followup.send(embed=embed)
                return

        if (
            member.guild_permissions.administrator
            or member.guild_permissions.moderate_members
        ):
            embed = embed_builder.error(title="無法執行", description="該成員有相同或更大的權限")
            await inter.followup.send(embed=embed)
            return

        try:
            await member.send(f"你在 {inter.guild.name} 被解除禁言\n" f"原因：{reason}\n")
        except:  # pylint: disable=bare-except
            # Pass if failed to DM user
            pass

        try:
            await member.timeout(duration=None, reason=reason)
        except:  # pylint: disable=bare-except
            embed = embed_builder.error(title="無法執行", description="解除禁言成員時發生錯誤")
            await inter.followup.send(embed=embed)
            return

        embed = embed_builder.information(
            title="成員被解除禁言",
            description=f"{member.mention} 被 {inter.author.mention} 解除禁言",
            thumbnail=member.avatar.url,
        )
        embed.add_field(name="理由", value=reason, inline=False)
        if copy:
            await copy.send(embed=embed)
            await inter.followup.send(embed=embed)
        else:
            await inter.followup.send(embed=embed)

    @commands.slash_command(name="kick", description="踢除成員")
    @commands.default_member_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(
        self,
        inter: CmdInter,
        user: User,
        reason: str = "沒有提供理由",
        copy: TextChannel = None,
        attachment: Attachment = None,
    ):
        """Kick a user's butt out of server.
            A kick_member permission is required.

        Args:
            inter: A disnake `ApplicationCommandInteraction`.
            user: A disnake `User`.
            reason: The reason for the kick, defaults to "沒有提供理由".
            copy: If a `TextChannel` is provided, the bot will send a copy \
                message to the specified channel.
            attachment: Some file or image for the extra information.
        """
        file = None
        await inter.response.defer()
        member = inter.guild.get_member(user.id)
        if member is None:
            try:
                member = await inter.guild.fetch_member(user.id)
            except:  # pylint: disable=bare-except
                embed = embed_builder.error(title="無法執行", description="發生錯誤，請確認該對象確實存在")
                await inter.followup.send(embed=embed)
                return

        if (
            member.guild_permissions.administrator
            or member.guild_permissions.kick_members
        ):
            embed = embed_builder.error(title="無法執行", description="該成員有相同或更大的權限")
            await inter.followup.send(embed=embed)
            return

        try:
            message = f"你被踢出 {inter.guild.name}\n" f"原因：{reason}\n"
            if attachment is not None and attachment.content_type.startswith("image"):
                message += "附件：\n"
                file = await attachment.to_file()
            await member.send(message, file=file)
        except:  # pylint: disable=bare-except
            # Pass if failed to DM user
            pass

        try:
            await member.kick(reason=reason)
        except:  # pylint: disable=bare-except
            embed = embed_builder.error(title="無法執行", description="踢出成員時發生錯誤")
            await inter.followup.send(embed=embed)
            return

        embed = embed_builder.information(
            title="懲處紀錄",
            description=f"{member.mention} 被 {inter.author.mention} 踢出伺服器",
            thumbnail=member.avatar.url,
        )
        embed.add_field(name="理由", value=reason, inline=False)
        if attachment is not None and attachment.content_type.startswith("image"):
            embed = await attach_to_embed(embed, attachment)

        if copy:
            await copy.send(embed=embed)
            if attachment is not None and attachment.content_type.startswith("image"):
                embed = await attach_to_embed(embed, attachment)
            await inter.followup.send(embed=embed)
        else:
            await inter.followup.send(embed=embed)

    @commands.slash_command(name="ban", description="停權成員")
    @commands.default_member_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(
        self,
        inter: CmdInter,
        user: User,
        reason: str = "沒有提供理由",
        copy: TextChannel = None,
        attachment: Attachment = None,
    ):
        """Ban a user from server.
            A ban_member permission is required.

        Args:
            inter: A disnake `ApplicationCommandInteraction`.
            user: A disnake `User`.
            raw_duration: How many seconds for the timeout.
            reason: The reason for the ban, defaults to "沒有提供理由".
            copy: If a `TextChannel` is provided, the bot will send a copy \
                message to the specified channel.
            attachment: Some file or image for the extra information.
        """
        file = None
        await inter.response.defer()
        member = inter.guild.get_member(user.id)
        if member is None:
            try:
                member = await inter.guild.fetch_member(user.id)
            except:  # pylint: disable=bare-except
                embed = embed_builder.error(title="無法執行", description="發生錯誤，請確認該對象確實存在")
                await inter.followup.send(embed=embed)
                return

        else:
            member = user

        try:
            message = f"你在 {inter.guild.name} 被停權\n" f"原因：{reason}\n"
            if attachment is not None and attachment.content_type.startswith("image"):
                message += "附件：\n"
                file = await attachment.to_file()
            await member.send(message, file=file)
        except:  # pylint: disable=bare-except
            # Pass if failed to DM user
            pass

        try:
            await inter.guild.ban(member, reason=reason)
        except:  # pylint: disable=bare-except
            embed = embed_builder.error(title="無法執行", description="停權成員時發生錯誤")
            await inter.followup.send(embed=embed)
            return

        embed = embed_builder.information(
            title="懲處紀錄",
            description=f"{member.mention} 被 {inter.author.mention} 從伺服器停權",
            thumbnail=member.avatar.url,
        )
        embed.add_field(name="理由", value=reason, inline=False)
        if attachment is not None and attachment.content_type.startswith("image"):
            embed = await attach_to_embed(embed, attachment)

        if copy:
            await copy.send(embed=embed)
            if attachment is not None and attachment.content_type.startswith("image"):
                embed = await attach_to_embed(embed, attachment)
            await inter.followup.send(embed=embed)
        else:
            await inter.followup.send(embed=embed)


async def attach_to_embed(embed, attachment):
    file = await attachment.to_file()
    embed.set_image(file=file)
    return embed


def setup(bot: commands.InteractionBot):
    bot.add_cog(Moderation(bot))
