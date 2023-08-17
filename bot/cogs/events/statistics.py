from disnake import utils
from disnake.ext import commands


class Statistics(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.member_count = 0

    @commands.Cog.listener("on_guild_update")
    async def update_subscription_count(self, before, after):
        if before.member_count != after.member_count:
            member_stats_channel = utils.get(
                after.voice_channels, id=804256287184388116
            )
            await member_stats_channel.edit(name=f"Shrimp - {after.member_count:,}")

        if before.premium_subscription_count != after.premium_subscription_count:
            booster_stats_channel = utils.get(
                after.voice_channels, id=804264456150188043
            )
            await booster_stats_channel.edit(
                name=f"Boosters - {len(after.premium_subscribers):,}"
            )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        await self.update_member_count(guild)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        await self.update_member_count(guild)

    async def update_member_count(self, guild):
        if self.member_count == guild.member_count:
            return

        member_stats_channel = utils.get(guild.voice_channels, id=804256287184388116)
        self.member_count = guild.member_count
        await member_stats_channel.edit(name=f"Shrimp - {guild.member_count:,}")
