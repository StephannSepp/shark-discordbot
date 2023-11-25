import asyncio
import time
from enum import Enum

from disnake import AllowedMentions
from disnake import CmdInter
from disnake import User
from disnake.ext import commands

from . import Player


class DuelResult(Enum):
    WIN = "勝利"
    LOSE = "戰敗"
    TIE = "平手"


class Rpg(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    def process_round(self, attacker: Player, defender: Player):
        def process_turn(sub: Player, obj: Player):
            DAMAGE_GIVEN = sub.do_damage(seed)
            DAMAGE = obj.do_defend(DAMAGE_GIVEN, seed)
            obj.health_point = max(obj.health_point - DAMAGE, 0)
            if DAMAGE_GIVEN > DAMAGE:
                defend_info = f"(已抵擋 {DAMAGE_GIVEN} => {DAMAGE})"
            elif DAMAGE_GIVEN < DAMAGE:
                defend_info = f"(破防！ {DAMAGE_GIVEN} => {DAMAGE})"
            else:
                defend_info = ""
            duel_log.append(
                f"{rounds:>2}. {sub.name} 對 {obj.name} 造成了 {DAMAGE} 傷害{defend_info}! "
                f"{obj.name} 還有 {obj.health_point} HP."
            )

        ATTACKER_BASE_DEX_WEIGHT = attacker.dexterity * 1.5
        DEFENDER_BASE_DEX_WEIGHT = defender.dexterity * 1.5
        attacker_priority = defender.dexterity + DEFENDER_BASE_DEX_WEIGHT
        defender_priority = attacker.dexterity + ATTACKER_BASE_DEX_WEIGHT
        duel_log = []
        seed = time.time_ns()
        rounds = 0
        while rounds < 10 and attacker.health_point > 0 and defender.health_point > 0:
            seed += 1
            rounds += 1
            if attacker_priority > defender_priority:
                process_turn(attacker, defender)
                defender_priority += DEFENDER_BASE_DEX_WEIGHT
            else:
                process_turn(defender, attacker)
                attacker_priority += ATTACKER_BASE_DEX_WEIGHT
        rounds += 1
        if attacker.health_point <= 0:
            duel_log.append(
                f"{rounds:>2}. {attacker.name} 倒下了! "
                f"{defender.name} 阻止了 {attacker.name} 的攻擊."
            )
            rounds += 1
            duel_log.append(
                f"{rounds:>2}. {defender.name} 剩餘 HP: {defender.health_point}.\n"
            )
            duel_result = DuelResult.WIN
        elif defender.health_point <= 0:
            duel_log.append(
                f"{rounds:>2}. {defender.name} 倒下了! "
                f"{attacker.name} 打敗了 {defender.name}."
            )
            rounds += 1
            duel_log.append(
                f"{rounds:>2}. {attacker.name} 剩餘 HP: {attacker.health_point}.\n"
            )
            duel_result = DuelResult.LOSE
        else:
            duel_log.append(f"{rounds:>2}. 雙方不分勝負打成了平手!")
            rounds += 1
            duel_log.append(
                f"{rounds:>2}. {attacker.name} 剩餘 HP: {attacker.health_point}."
            )
            rounds += 1
            duel_log.append(
                f"{rounds:>2}. {defender.name} 剩餘 HP: {defender.health_point}."
            )
            duel_result = DuelResult.TIE
        return duel_result, duel_log

    @commands.slash_command(name="duel")
    @commands.guild_only()
    async def duel(self, inter: CmdInter, opponent: User):
        """IT'S TIME TO DU-DU-DU-DU-DU-DU-DU-DU-DU-DUEL!"""
        if opponent == inter.author:
            await inter.response.send_message(f"{inter.author.mention} 自殺了.")
            return
        attacker = Player(inter.author.name, inter.author.id)
        defender = Player(opponent.name, opponent.id)
        message = (
            f"{inter.author.mention} 對 {opponent.mention} 發起了攻擊\n"
            f"{inter.author.name} 的素質\n"
            f"```HP {attacker.health_point:4>,}｜STR {attacker.strength:4>}"
            f"｜DEX {attacker.dexterity:4>}｜CON {attacker.constitution:4>}"
            f"｜LUK {attacker.luck:4>}```\n"
            f"{opponent.name} 的素質\n"
            f"```HP {defender.health_point:4>,}｜STR {defender.strength:4>}"
            f"｜DEX {defender.dexterity:4>}｜CON {defender.constitution:4>}"
            f"｜LUK {defender.luck:4>}```\n"
        )
        result, log = await asyncio.to_thread(self.process_round, attacker, defender)
        duel_log = "\n".join(log)
        message += f"```{duel_log}```"
        await inter.response.send_message(
            message, allowed_mentions=AllowedMentions().none()
        )


def setup(bot: commands.InteractionBot):
    bot.add_cog(Rpg(bot))
