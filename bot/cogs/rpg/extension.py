"""A Discord RPGame. WIP.

:TODO: luck events.
:TODO: action 做善事.
"""
# Standard library imports
import asyncio
import datetime
# Third-party library imports
import disnake
from disnake import CmdInter
from disnake import File
from disnake import User
from disnake import utils
from disnake.ext import commands
# Local imports
from database import rpg_db_manager
from static.rpg_boss import boss_lst
from utils import embed_builder
from utils import gen
from utils import time_process
from . import rpg_module
from .models import Boss
from .models import Player


class RPGame(commands.Cog):
    """ A Disnake Cog wraps commands as a Python class. """

    def __init__(self, bot):
        self.bot = bot
        self.player = None

    # RPGame
    @commands.slash_command(name="rpg", description="酥米宇宙RPGame")
    @commands.default_member_permissions(administrator=True) # debugging usage
    async def rpg(self, inter: CmdInter):
        """ A parent group of RPGame commands.

        When command in this group invoked,
        a player object is created and saved under RPGame class.
        """
        stats = rpg_db_manager.get_player(inter.author.id)
        if stats is not None:
            self.player = Player(inter.author.name, *stats)
        else:
            self.player = None

    # Action command group
    @commands.cooldown(rate=1, per=7200, type=commands.BucketType.user)
    @rpg.sub_command_group(name="action", description="酥米宇宙RPGame - 行動指令")
    async def action(self, inter: CmdInter):
        """ A subcommand group for actions.

        :raise commands.CommandsOnCoolDown:
        :raise commands.CheckFailure:
            When a player is dead or haven't started the game,
            raise a CheckFailure error.
        """
        # Player existence check
        if self.player is None:
            inter.application_command.reset_cooldown(inter)
            raise commands.CheckFailure(message="你還沒有開始冒險！\n請使用`/rpg start`開始進行冒險")
        # Player survival check
        if self.player.isKilled:
            inter.application_command.reset_cooldown(inter)
            raise commands.CheckFailure(message="你的角色已經死亡！\n請使用`/rpg end`結束目前冒險")

    @action.error
    async def action_err_handler(self, inter: CmdInter, error):
        """ Handling errors from action command group. """
        match error:
            case commands.CheckFailure():
                await inter.response.send_message(error, ephemeral=True)
            case commands.CommandOnCooldown():
                dt = datetime.datetime.now() + datetime.timedelta(seconds=error.retry_after)
                t = time_process.to_unix(dt)
                await inter.response.send_message(f"CD 中, 請於 <t:{t}:R> 後再使用", ephemeral=True)

    @action.sub_command(name="work", description="酥米宇宙RPGame - 去工作")
    async def action_work(self, inter: CmdInter):
        """ TODO: work events"""
        salary, event = self.player.action_work()
        rpg_db_manager.update_player(self.player.user_id, crystal=self.player.crystal)
        if salary > 0:
            await inter.response.send_message(
                f"{inter.author.mention} 去工作了，賺取了 {salary} 水晶"
            )
        else:
            await inter.response.send_message(
                f"{inter.author.mention} 去工作了，但倒賠了 {abs(salary)} 水晶"
            )

    @action.sub_command(name="go-out", description="酥米宇宙RPGame - 去探險")
    async def action_go_out(self, inter: CmdInter):
        """ Going on an adventure, a new skill could be learnt via this action. """
        skills = rpg_db_manager.get_player_skills(inter.author.id)
        if len(skills or "") >= 5:
            await inter.response.send_message(
                f"{inter.author.mention} 去探險了！（已達到技能擁有上限）"
            )
            return

        skill_tuple = rpg_module.get_skill_checker(self.player)
        if skill_tuple is not None:
            combo, damage_modifier = skill_tuple
            skill_id = gen.OTP_str(5)
            has_skill = rpg_db_manager.get_skill(skill_id)
            if has_skill:
                rpg_db_manager.add_skill(inter.author.id, has_skill[1], has_skill[2], has_skill[3], has_skill[4])
                await inter.response.send_message(
                    f"{inter.author.mention} 在探險期間習得了技能__{has_skill[2]}__！"
                )
                return

            await inter.response.send_modal(
                title="習得新技能",
                custom_id=f"get_skill_{skill_id}",
                components=[
                    disnake.ui.TextInput(
                        label=f"恭喜獲得技能(Combo:{combo}, 傷害倍數:{damage_modifier}x)！",
                        placeholder="技能名稱",
                        custom_id=f"user_input_{skill_id}",
                        style=disnake.TextInputStyle.short,
                        max_length=10,
                    )
                ]
            )
            try:
                modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                    "modal_submit",
                    check=lambda i: i.custom_id == f"get_skill_{skill_id}" and i.author.id == inter.author.id,
                    timeout=300
                )
            except asyncio.TimeoutError:
                return

            skill_name = modal_inter.text_values[f"user_input_{skill_id}"]
            rpg_db_manager.add_skill(inter.author.id, skill_id, skill_name, combo, damage_modifier)
            await modal_inter.response.send_message(
                f"{inter.author.mention} 在探險期間習得了技能__{skill_name}__！"
            )
        else:
            await inter.response.send_message(
                f"{inter.author.mention} 去探險了"
            )

    @action.sub_command(name="do-charity", description="酥米宇宙RPGame - 做善事")
    async def action_do_charity(self, inter: CmdInter):
        """ TODO: do charity event """
        luck, event = self.player.action_charity()
        rpg_db_manager.update_player(self.player.user_id, luck=self.player.luck)
        await inter.response.send_message(
            f"{inter.author.mention} 做了善事獲得了 {luck} 運氣"
        )

    # Battle command group
    @rpg.sub_command_group(name="battle", description="酥米宇宙RPGame - 戰鬥指令")
    async def battle(self, inter: CmdInter):
        """ A subcommand group for battle.

        :raise commands.CheckFailure:
            When a player is dead or haven't started the game,
            raise a CheckFailure error.
        """
        # Player existence check
        if self.player is None:
            inter.application_command.reset_cooldown(inter)
            raise commands.CheckFailure(message="你還沒有開始冒險！\n請使用`/rpg start`開始進行冒險")
        # Player survival check
        if self.player.isKilled:
            inter.application_command.reset_cooldown(inter)
            raise commands.CheckFailure(message="你的角色已經死亡！\n請使用`/rpg end`結束目前冒險")

    @battle.error
    async def battle_err_handler(self, inter: CmdInter, error):
        """ Handling errors from battle command group. """
        match error:
            case commands.CheckFailure():
                await inter.response.send_message(error, ephemeral=True)

    @commands.cooldown(rate=5, per=1800, type=commands.BucketType.user)
    @battle.sub_command(name="boss-fight", description="酥米宇宙RPGame - 攻略Boss")
    async def boss_fight(self, inter: CmdInter):
        """ Boss fight commnad. """
        boss_stats = boss_lst[self.player.floor]
        boss = Boss(**boss_stats)
        battle_log, reward = rpg_module.battle_calc(self.player, boss)
        self.player.update_crystal(reward)
        file = File(f"data/bossIMG/{boss_stats['url']}", filename="boss.png")
        embed = embed_builder.embed_information(
            title=f"{inter.author.name} 攻略了第 {boss.floor} 層 Boss：{boss.name}",
            description=battle_log,
        )
        embed.set_thumbnail(file=file)

        if self.player.isWinner:
            new_floor = self.player.add_floor()
            embed.add_field(name="戰鬥結果", value=f"{inter.author.name} 攻略成功")
            rpg_db_manager.update_player(inter.author.id, crystal=self.player.crystal, floor=new_floor)
            rpg_db_manager.log_battle(self.player.user_id, boss.user_id, "B", "勝利", "戰敗")
        elif boss.isWinner:
            embed.add_field(name="戰鬥結果", value=f"{inter.author.name} 攻略失敗")
            if self.player.isKilled:
                rpg_db_manager.update_player(inter.author.id, dead='Y', crystal=self.player.crystal)
                rpg_db_manager.log_battle(self.player.user_id, boss.user_id, "B", "死亡", "勝利")
            else:
                rpg_db_manager.update_player(inter.author.id, crystal=self.player.crystal)
                rpg_db_manager.log_battle(self.player.user_id, boss.user_id, "B", "戰敗", "勝利")
        else:
            embed.add_field(name="戰鬥結果", value="平手")
            rpg_db_manager.update_player(inter.author.id, crystal=self.player.crystal)
            rpg_db_manager.log_battle(self.player.user_id, boss.user_id, "B", "平手", "平手")
        embed.add_field(name="戰鬥獎勵", value=f"{reward} 水晶")
        await inter.response.send_message(embed=embed)

    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    @battle.sub_command(name="friendly-match", description="酥米宇宙RPGame - 友好切磋")
    async def friendly_match(self, inter: CmdInter, target: User):
        """ A friendly match battle, the odds of death is very low. """
        stats = rpg_db_manager.get_player(target.id)
        if stats is None:
            await inter.response.send_message("該玩家並不是冒險者！", ephemeral=True)
            return

        target_player = Player(target.name, *stats)
        if target_player == self.player:
            await inter.response.send_message("你不能攻擊自己！", ephemeral=True)
            return
        if target_player.isKilled:
            await inter.response.send_message("該玩家已經死亡了！", ephemeral=True)
            return

        battle_log, reward = rpg_module.battle_calc(self.player, target_player)
        self.player.update_crystal(reward)
        embed = embed_builder.embed_information(
            title=f"{inter.author.name} 與 {target.name} 的友好切磋",
            description=battle_log
        )
        if self.player.isWinner:
            embed.add_field(name="戰鬥結果", value=f"{inter.author.name} 勝利")
            if target_player.isKilled:
                rpg_db_manager.update_player(self.player.user_id, kills=self.player.kills+1, crystal=self.player.crystal)
                rpg_db_manager.update_player(target.id, dead='Y')
                rpg_db_manager.log_battle(self.player.user_id, target_player.user_id, "N", "勝利", "死亡")
            else:
                rpg_db_manager.update_player(self.player.user_id, crystal=self.player.crystal)
                rpg_db_manager.log_battle(self.player.user_id, target_player.user_id, "N", "勝利", "戰敗")
        elif target_player.isWinner:
            embed.add_field(name="戰鬥結果", value=f"{target.name} 勝利")
            if self.player.isKilled:
                rpg_db_manager.update_player(target.id, kills=target_player.kills+1)
                rpg_db_manager.update_player(self.player.user_id, dead='Y', crystal=self.player.crystal)
                rpg_db_manager.log_battle(self.player.user_id, target_player.user_id, "N", "死亡", "勝利")
            else:
                rpg_db_manager.update_player(self.player.user_id, crystal=self.player.crystal)
                rpg_db_manager.log_battle(self.player.user_id, target_player.user_id, "N", "戰敗", "勝利")
        else:
            embed.add_field(name="戰鬥結果", value="平手")
            rpg_db_manager.update_player(self.player.user_id, crystal=self.player.crystal)
            rpg_db_manager.log_battle(self.player.user_id, target_player.user_id, "N", "平手", "平手")
        embed.add_field(name="戰鬥獎勵", value=f"{reward} 水晶")
        await inter.response.send_message(embed=embed)

    @commands.cooldown(rate=1, per=7200, type=commands.BucketType.user)
    @battle.sub_command(name="death-match", description="酥米宇宙RPGame - 認真對決")
    async def death_match(self, inter: CmdInter, target: User):
        """ A death-match battle, the odds of death is high. """
        stats = rpg_db_manager.get_player(target.id)
        if stats is None:
            await inter.response.send_message("該玩家並不是冒險者！", ephemeral=True)
            return

        target_player = Player(target.name, *stats)
        if target_player == self.player:
            await inter.response.send_message("你不能攻擊自己！", ephemeral=True)
            return
        if target_player.isKilled:
            await inter.response.send_message("該玩家已經死亡了！", ephemeral=True)
            return

        battle_log, reward = rpg_module.battle_calc(self.player, target_player, dm=True)
        self.player.update_crystal(reward)
        embed = embed_builder.embed_information(
            title=f"{inter.author.name} 與 {target.name} 的認真對決",
            description=battle_log
        )
        if self.player.isWinner:
            embed.add_field(name="戰鬥結果", value=f"{inter.author.name} 勝利")
            if target_player.isKilled:
                rpg_db_manager.update_player(self.player.user_id, kills=self.player.kills+1, crystal=self.player.crystal)
                rpg_db_manager.update_player(target.id, dead='Y')
                rpg_db_manager.log_battle(self.player.user_id, target_player.user_id, "Y", "勝利", "死亡")
            else:
                rpg_db_manager.update_player(self.player.user_id, crystal=self.player.crystal)
                rpg_db_manager.log_battle(self.player.user_id, target_player.user_id, "Y", "勝利", "戰敗")
        elif target_player.isWinner:
            embed.add_field(name="戰鬥結果", value=f"{target.name} 勝利")
            if self.player.isKilled:
                rpg_db_manager.update_player(target.id, kills=target_player.kills+1)
                rpg_db_manager.update_player(self.player.user_id, dead='Y', crystal=self.player.crystal)
                rpg_db_manager.log_battle(self.player.user_id, target_player.user_id, "Y", "死亡", "勝利")
            else:
                rpg_db_manager.log_battle(self.player.user_id, target_player.user_id, "Y", "戰敗", "勝利")
        else:
            embed.add_field(name="戰鬥結果", value="平手")
            rpg_db_manager.update_player(self.player.user_id, crystal=self.player.crystal)
        embed.add_field(name="戰鬥獎勵", value=f"{reward} 水晶")
        await inter.response.send_message(embed=embed)

    @boss_fight.error
    async def boss_fight_err_handler(self, inter: CmdInter, error):
        """ Handling the errors from boss fight command. """
        match error:
            case commands.CommandOnCooldown():
                dt = datetime.datetime.now() + datetime.timedelta(seconds=error.retry_after)
                t = time_process.to_unix(dt)
                await inter.response.send_message(f"CD 中, 請於 <t:{t}:R> 後再使用", ephemeral=True)

    @friendly_match.error
    async def friendly_match_err_handler(self, inter: CmdInter, error):
        """ Handling the errors from death-match command. """
        match error:
            case commands.CommandOnCooldown():
                dt = datetime.datetime.now() + datetime.timedelta(seconds=error.retry_after)
                t = time_process.to_unix(dt)
                await inter.response.send_message(f"CD 中, 請於 <t:{t}:R> 後再使用", ephemeral=True)

    @death_match.error
    async def death_match_err_handler(self, inter: CmdInter, error):
        """ Handling the errors from friendly match command. """
        match error:
            case commands.CommandOnCooldown():
                dt = datetime.datetime.now() + datetime.timedelta(seconds=error.retry_after)
                t = time_process.to_unix(dt)
                await inter.response.send_message(f"你殺了人還想殺阿？請於 <t:{t}:R> 後再使用")

    # Eco command group
    @rpg.sub_command_group(name="eco", description="酥米宇宙RPGame - 經濟指令")
    async def eco(self, inter: CmdInter):
        """ An economic related subcommand group.

        :raise commands.CheckFailure:
            When a player is dead or haven't started the game,
            raise a CheckFailure error.
        """
        # Player existence check
        if self.player is None:
            raise commands.CheckFailure(message="你還沒有開始冒險！\n請使用`/rpg start`開始進行冒險")
        # Player survival check
        if self.player.isKilled:
            raise commands.CheckFailure(message="你的角色已經死亡！\n請使用`/rpg end`結束目前冒險")

    @eco.error
    async def eco_err_handler(self, inter: CmdInter, error):
        """ Handling the errors from eco command group. """
        match error:
            case commands.CheckFailure():
                await inter.response.send_message(error, ephemeral=True)

    @eco.sub_command(name="mana-price", description="酥米宇宙RPGame - 瑪那價格查詢")
    async def mana_price(self, inter: CmdInter):
        """ Show the mana price in a Discord embed. """
        buy_price = 69 + (2 * (self.player.mana ** 3))
        buy_price = []
        sell_price = []
        sum_buy_price = 0
        sum_sell_price = 0

        for i in range(0, 5):
            next_buy_price = 69 + (2 * ((i+self.player.mana)**3))
            sum_buy_price += next_buy_price
            buy_price.append(f"{i+1}個 {sum_buy_price:,} (+{next_buy_price:,}) 水晶")
        for j in range(0, 5):
            if self.player.mana - j == 0:
                break
            next_sell_price = round((69 + (2 * ((self.player.mana-j-1)**3))) / 2)
            sum_sell_price += next_sell_price
            sell_price.append(f"{j+1}個 {sum_sell_price:,} (+{next_sell_price:,}) 水晶")
        if not sell_price:
            sell_price = ["不適用"]

        embed = embed_builder.embed_information(
            title="瑪那價格",
            description=f"{inter.author.mention} 現在擁有 {self.player.mana} 個瑪那\n{self.player.crystal} 個水晶",
            thumbnail=inter.author.avatar.url
        )
        embed.add_field(name="購買", value="\n".join(buy_price), inline=True)
        embed.add_field(name="賣出", value="\n".join(sell_price), inline=True)
        await inter.response.send_message(embed=embed, ephemeral=True)

    @eco.sub_command(name="buy-mana", description="酥米宇宙RPGame - 購買瑪那")
    async def buy_mana(self, inter: CmdInter, amount: commands.Range[1,5]):
        """ Buying mana from market.

        :param inter: A disnake ApplicationCommandInteraction.
        :param amount: The amount of mana, 1 to 5.
        """
        sum_buy_price = 0
        for i in range(0, amount):
            sum_buy_price += 69 + (2 * ((i+self.player.mana)**3))
        if self.player.crystal - sum_buy_price < 0:
            await inter.response.send_message(
                "購買失敗！你沒有足夠的水晶", ephemeral=True
            )
            return

        self.player.crystal -= sum_buy_price
        self.player.mana += amount
        rpg_db_manager.update_player(inter.author.id, crystal=self.player.crystal, mana=self.player.mana)
        await inter.response.send_message(
            f"購買成功！你現在擁有 {self.player.mana} 個瑪那", ephemeral=True
        )

    @eco.sub_command(name="sell-mana", description="酥米宇宙RPGame - 販售瑪那")
    async def sell_mana(self, inter: CmdInter, amount: commands.Range[1,5]):
        """ Selling mana to the market.

        :param inter: A disnake ApplicationCommandInteraction.
        :param amount: The amount of mana, in 1 to 5.
        """
        if self.player.mana - amount >= 0:
            sum_sell_price = 0
            for i in range(1, amount+1):
                sum_sell_price += round((69 + (2 * ((self.player.mana - i)**3))) / 2)
            self.player.crystal += sum_sell_price
            self.player.mana -= amount
            rpg_db_manager.update_player(inter.author.id, crystal=self.player.crystal, mana=self.player.mana)
            await inter.response.send_message(
                f"販售成功！你現在擁有 {self.player.mana} 個瑪那", ephemeral=True
            )
        else:
            await inter.response.send_message(
                "販售失敗！你沒有足夠的瑪那", ephemeral=True
            )

    # Information commands
    @rpg.sub_command_group(name="info", description="酥米宇宙RPGame - 資訊指令")
    async def information(self, inter: CmdInter):
        """ An RPGame info related subcommand group.

        :raise commands.CheckFailure:
            When a player haven't started the game,
            raise a CheckFailure error.
        """
        # Player existence check
        if self.player is None:
            raise commands.CheckFailure(message="你還沒有開始冒險！\n請使用`/rpg start`開始進行冒險")

    @information.error
    async def display_err_handler(self, inter: CmdInter, error):
        """ Handling the errors from info command group. """
        match error:
            case commands.CheckFailure():
                await inter.response.send_message(error, ephemeral=True)

    @information.sub_command(name="stats", description="酥米宇宙RPGame - 顯示玩家狀態")
    async def display_stats(self, inter: CmdInter, display: bool=False):
        """ Display RPGame player stats. """
        start_time = time_process.to_unix(self.player.created_at)
        is_alive = "死亡" if self.player.isKilled else "存活"
        embed = embed_builder.embed_information(
            title="冒險者資訊",
            description=f"{inter.author.mention} 於 <t:{start_time}> <t:{start_time}:R> 開始了冒險",
            thumbnail=inter.author.avatar.url
        )
        embed.add_field(name="水晶", value=f"{self.player.crystal:,}", inline=True)
        embed.add_field(name="瑪那", value=f"{self.player.mana:,}", inline=True)
        embed.add_field(name="運氣", value=f"{self.player.luck}/255", inline=True)
        embed.add_field(name="樓層", value=f"第 {self.player.floor} 層", inline=False)
        embed.add_field(name="狀態", value=is_alive, inline=False)
        embed.add_field(name="殺人數", value=self.player.kills, inline=False)
        await inter.response.send_message(embed=embed, ephemeral=display)

    @information.sub_command(name="skills", description="酥米宇宙RPGame - 玩家技能列表")
    async def display_skills(self, inter:CmdInter):
        """ Display the skills that the player has. """
        skill_lst = rpg_db_manager.get_player_skills(inter.author.id)
        if skill_lst is not None:
            desc = [f"{row[1]}｜{row[2]}｜{row[4]}x{row[3]}" for row in skill_lst]
        else:
            desc = ["沒有技能"]

        embed = embed_builder.embed_information(
            title=f"{inter.author.name} 的技能列表",
            description="\n".join(desc)
        )
        await inter.response.send_message(embed=embed)

    LOG_OPT = commands.option_enum(["防守", "攻擊"])
    @information.sub_command(name="battle-logs", description="酥米宇宙RPGame - 玩家戰報")
    async def display_batlle_logs(self, inter: CmdInter, logs_type: LOG_OPT):
        """ Display battle results from the player,
            defensive and offensive battle log are indicated logs_type parameter.
        """
        match logs_type:
            case "防守":
                r_battlelogs = rpg_db_manager.get_defense_battle_logs(inter.author.id)
                target_field_index = 0
                result_field_index = 4
            case "攻擊":
                r_battlelogs = rpg_db_manager.get_attack_battle_logs(inter.author.id)
                target_field_index = 1
                result_field_index = 3
            case "攻略":
                r_battlelogs = rpg_db_manager.get_attack_battle_logs(inter.author.id)
                target_field_index = 1
                result_field_index = 3

        if r_battlelogs is not None:
            battlelogs_lst = []
            for row in r_battlelogs:
                player = utils.get(inter.guild.members, id=row[target_field_index])
                match row[2]:
                    case 'Y':
                        battle_type = "認真對決"
                    case 'N':
                        battle_type = "友好切磋"
                    case 'B':
                        battle_type = "攻略戰報"
                result = row[result_field_index]
                battle_time_at = time_process.to_unix(row[5])
                if result == "死亡":
                    battlelogs_lst.append(
                        f"***<t:{battle_time_at}> 的 {battle_type}：{result}｜對手：{player.mention}***"
                    )
                else:
                    battlelogs_lst.append(
                        f"<t:{battle_time_at}> 的 {battle_type}：{result}｜對手：{player.mention}"
                    )
        else:
            battlelogs_lst = ["沒有戰報顯示"]

        embed = embed_builder.embed_information(
            title=f"{inter.author.name} 的{logs_type}戰報",
            description="\n".join(battlelogs_lst)
        )
        await inter.response.send_message(embed=embed)

    @information.sub_command(name="boss-stats", description="酥米宇宙RPGame - Boss情報")
    async def display_boss(self, inter: CmdInter):
        """ Display the next boss's stats. """
        boss_stats = boss_lst[self.player.floor]
        file = File(f"data/bossIMG/{boss_stats['url']}", filename="boss.png")
        embed = embed_builder.embed_information(
            title=f"第 {self.player.floor+1} 層 - {boss_stats['name']}",
        )
        embed.set_thumbnail(file=file)
        embed.add_field(name="水晶", value=f"{boss_stats['crystal']:,}", inline=True)
        embed.add_field(name="瑪那", value=f"{boss_stats['mana']:,}", inline=True)
        embed.add_field(name="運氣", value=f"{boss_stats['luck']}/255", inline=True)
        await inter.response.send_message(embed=embed)

    # 技能指令
    @rpg.sub_command_group(name="skill", description="酥米宇宙RPGame - 技能指令")
    async def rpg_skill(self, inter: CmdInter):
        """ A skill related subcommands group.

        :raise commands.CheckFailure:
            When a player haven't started the game,
            raise a CheckFailure error.
        """
        # Player existence check
        if self.player is None:
            raise commands.CheckFailure(message="你還沒有開始冒險！\n請使用`/rpg start`開始進行冒險")

    @rpg_skill.error
    async def skill_err_handler(self, inter: CmdInter, error):
        """ Handling error from rpg_skill command group. """
        match error:
            case commands.CheckFailure():
                await inter.response.send_message(error, ephemeral=True)

    @rpg_skill.sub_command(name="forget", description="酥米宇宙RPGame - 遺忘技能")
    async def forget_skill(self, inter: CmdInter, skill_id: str):
        """ Forget a skill. """
        rpg_db_manager.remove_skill(inter.author.id, skill_id)
        await inter.response.send_message("已遺忘該技能", ephemeral=True)

    @rpg_skill.sub_command(name="combine", description="酥米宇宙RPGame - 技能融合")
    async def combine_skill(self, inter: CmdInter, first_skill_id: str, second_skill_id: str):
        """ TODO: WIP """
        await inter.response.send_message("還在做", ephemeral=True)

    # 基本指令
    @rpg.sub_command(name="start", description="酥米宇宙RPGame - 開始新冒險")
    async def rpg_start(self, inter: CmdInter):
        """ Start a RPGame. """
        player_data = rpg_db_manager.get_player(inter.author.id)
        if player_data is not None:
            await inter.response.send_message("你已經開始冒險了！", ephemeral=True)
            return
        rpg_db_manager.player_create(inter.author.id)
        await inter.response.send_message("一位冒險者已經開始冒險了！")

    @rpg.sub_command(name="end", description="酥米宇宙RPGame - 結束冒險（移除所有資料）")
    async def rpg_end(self, inter: CmdInter):
        """ End a RPGame. """
        if self.player is None:
            await inter.response.send_message(
                "你還沒有開始冒險！\n請使用`/rpg start`開始進行冒險", ephemeral=True
            )
            return

        otpwd = gen.OTP_num()
        await inter.response.send_modal(
            title="刪除資料確認",
            custom_id=f"confirm_delete_{inter.author.id}",
            components=[
                disnake.ui.TextInput(
                    label=f"輸入「{otpwd}」以確認刪除（大小寫不拘），此舉動將會永久刪除玩家資料",
                    placeholder=otpwd,
                    custom_id="user_input",
                    style=disnake.TextInputStyle.short
                )
            ]
        )
        try:
            modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == f"confirm_delete_{inter.author.id}",
                timeout=90
            )
        except asyncio.TimeoutError:
            return

        if modal_inter.text_values["user_input"].lower() == otpwd.lower():
            rpg_db_manager.remove_player(inter.author.id)
            await modal_inter.response.send_message(
                "一名冒險者決定從RPG世界中黯然離開…", ephemeral=False
            )
        else:
            await modal_inter.response.send_message(
                "輸入錯誤，操作取消", ephemeral=True
            )


class RPGameSystem(commands.Cog):
    """ A Disnake Cog wraps commands as a Python class. """

    def __init__(self, bot):
        self.bot = bot
        self.player = None

    # System admin commands
    @commands.slash_command(name="rpg-sys", description="酥米宇宙RPGame - 系統指令")
    @commands.default_member_permissions(administrator=True)
    async def system_commnads(self, inter: CmdInter):
        """ System command group. """

    @system_commnads.sub_command(name="init-table", description="酥米宇宙RPGame - 重置")
    async def init_table(self, inter: CmdInter):
        """ Recreate all the RPGame tables. """
        rpg_db_manager.init_table()
        await inter.response.send_message("Init table done.", ephemeral=True)

    @system_commnads.sub_command_group(name="debug", description="酥米宇宙RPGame - 權限")
    async def rpg_debug(self, inter: CmdInter):
        """ Debug command group """
        stats = rpg_db_manager.get_player(inter.author.id)
        if stats is not None:
            self.player = Player(inter.author.name, *stats)
        else:
            self.player = None

    @rpg_debug.sub_command(name="get-random-skill", description="酥米宇宙RPGame - 隨機取得技能")
    async def get_random_skill(self, inter: CmdInter):
        """ Get a random skill. """
        skills = rpg_db_manager.get_player_skills(inter.author.id)
        if len(skills or "") >= 5:
            await inter.response.send_message(
                f"{inter.author.mention} 已達到技能擁有上限"
            )
            return

        combo, damage_modifier = rpg_module.sys_get_skill(self.player)
        skill_id = gen.OTP_str(5)
        has_skill = rpg_db_manager.get_skill(skill_id)
        if has_skill:
            rpg_db_manager.add_skill(inter.author.id, has_skill[1], has_skill[2], has_skill[3], has_skill[4])
            await inter.response.send_message(
                f"{inter.author.mention} 在探險期間習得了技能__{has_skill[2]}__！"
            )
            return

        await inter.response.send_modal(
            title="習得新技能",
            custom_id=f"get_skill_{skill_id}",
            components=[
                disnake.ui.TextInput(
                    label=f"恭喜獲得技能(Combo:{combo}, 傷害倍數:{damage_modifier}x)！",
                    placeholder="技能名稱",
                    custom_id="user_input",
                    style=disnake.TextInputStyle.short,
                    max_length=10,
                )
            ]
        )
        try:
            modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == f"get_skill_{skill_id}" and i.author.id == inter.author.id,
                timeout=300
            )
        except asyncio.TimeoutError:
            return

        skill_name = modal_inter.text_values["user_input"]
        rpg_db_manager.add_skill(inter.author.id, skill_id, skill_name, combo, damage_modifier)
        await modal_inter.response.send_message(
            f"{inter.author.mention} 習得了技能__{skill_name}__！"
        )


def setup(bot):
    """ Called when this extension is loaded. """
    bot.add_cog(RPGame(bot))
    bot.add_cog(RPGameSystem(bot))
