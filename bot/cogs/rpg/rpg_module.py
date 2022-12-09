# Standard library imports
import math
import random
# Local imports
from database import rpg_db_manager
from utils import roll
from .models import Player


def battle_calc(attacker: Player, defender: Player, dm: bool=False) -> tuple[str, int]:
    """ Calculating the battle.

    :param attacker: A Player object.
    :param defender: A Player object.
    :param dm: A boolean indicates if it's a death-match.

    :returns: A battle log in list and a reward number.
    :rtype: tuple[<str>, <int>]
    """
    attacker.hp = attacker.crystal
    defender.hp = defender.crystal
    total_damage = 0
    attacker.isWinner = False
    defender.isWinner = False
    attacker.mana += 1
    defender.mana += 1
    attacker_speed = (attacker.mana * 16) + attacker.hp
    defender_speed = (defender.mana * 16) + defender.hp
    damage_modifier = ((attacker.hp + defender.hp) / ((attacker.mana + defender.mana) * 87)) ** 0.5
    attacker_damage_range = [
        round(
            (((attacker.mana * 69) * (attacker.luck / 255)) - (defender.mana - 1 * 5)) * damage_modifier
        ),
        round(
            ((attacker.mana * 87) - (defender.mana - 1 * 6)) * damage_modifier
        )
    ]
    defender_damage_range = [
        round(
            (((defender.mana + 1* 69) * (defender.luck / 255)) - (attacker.mana - 1 * 5)) * damage_modifier
        ),
        round(
            ((defender.mana * 87) - (attacker.mana - 1 * 6)) * damage_modifier
        )
    ]
    attacker_tunrs_counter = attacker_speed + defender_speed
    defender_turns_counter = -1
    turns = 1
    battle_log = []

    while(attacker.hp > 0 and defender.hp > 0 and turns < 50):
        if defender_turns_counter < 0:
            skill_performs = skill_perform_ckeck(defender)
            if skill_performs is not None:
                defender.combo = 1
                for _ in range(0, skill_performs[3]):
                    damage = round(
                        random.randint(*defender_damage_range)
                        * ((defender.combo * 0.1) + 1)
                        * skill_performs[4]
                    )
                    damage = max(damage, 1)
                    attacker.damage(damage)
                    if defender.combo > 1:
                        battle_log.append(
                            f'**{turns}. {defender.name} {defender.combo}連擊！造成了 {damage:,} 傷害**'
                        )
                    else:
                        battle_log.append(
                            f"{turns}. {defender.name} 使出了 __{skill_performs[2]}__，造成了 {damage:,} 傷害"
                        )
                    turns += 1
                    defender.combo += 1
            else:
                damage = round(
                    random.randint(*defender_damage_range)
                    * ((defender.combo * 0.1) + 1)
                )
                damage = max(damage, 1)
                attacker.damage(damage)
                if defender.combo > 1:
                    battle_log.append(
                        f'**{turns}. {defender.name} {defender.combo}連擊！造成了 {damage:,} 傷害**'
                    )
                else:
                    battle_log.append(
                        f"{turns}. {defender.name} 攻擊，造成了 {damage:,} 傷害"
                    )
                turns += 1
                defender.combo += 1

            attacker.combo = 1
            attacker_tunrs_counter -= random.randint(round(attacker_speed * (attacker.luck/255)), attacker_speed)
            defender_turns_counter = attacker_speed + defender_speed
        elif attacker_tunrs_counter < 0:
            skill_performs = skill_perform_ckeck(attacker)
            if skill_performs is not None:
                attacker.combo = 1
                for _ in range(0, skill_performs[3]):
                    damage = round(
                        random.randint(*attacker_damage_range)
                        * ((attacker.combo * 0.1) + 1)
                        * skill_performs[4]
                    )
                    damage = max(damage, 1)
                    total_damage += damage
                    defender.damage(damage)
                    if attacker.combo > 1:
                        battle_log.append(
                            f'**{turns}. {attacker.name} {attacker.combo}連擊！造成了 {damage:,} 傷害**'
                        )
                    else:
                        battle_log.append(
                            f"{turns}. {attacker.name} 使出了 __{skill_performs[2]}__，造成了 {damage:,} 傷害"
                        )
                    turns += 1
                    attacker.combo += 1
            else:
                damage = round(
                    random.randint(*attacker_damage_range)
                    * ((attacker.combo * 0.1) + 1)
                )
                damage = max(damage, 1)
                total_damage += damage
                defender.damage(damage)
                if attacker.combo > 1:
                    battle_log.append(f'**{turns}. {attacker.name} {attacker.combo}連擊！造成了 {damage:,} 傷害**')
                else:
                    battle_log.append(f"{turns}. {attacker.name} 攻擊，造成了 {damage:,} 傷害")
                turns += 1
                attacker.combo += 1

            defender.combo = 1
            defender_turns_counter -= random.randint(round(defender_speed * (defender.luck/255)), defender_speed)
            attacker_tunrs_counter = attacker_speed + defender_speed
        else:
            attacker_tunrs_counter -= random.randint(round(attacker_speed * (attacker.luck/255)), attacker_speed)
            defender_turns_counter -= random.randint(round(defender_speed * (defender.luck/255)), defender_speed)

    # End of battle
    if attacker.hp < 1:
        defender.isWinner = True
        attacker = kill_check(attacker, dm)
        reward = 1
        if attacker.isKilled:
            battle_log.append(
                f"{turns}. ***{attacker.name} 在戰鬥中死亡了！{defender.name} 還有 {defender.hp:,} 個水晶***"
            )
        else:
            battle_log.append(
                f"{turns}. ***{attacker.name} 失去了戰鬥能力！{defender.name} 還有 {defender.hp:,} 個水晶***"
            )
    elif defender.hp < 1:
        attacker.isWinner = True
        defender = kill_check(defender, dm)
        reward = round(total_damage ** 0.25)
        if defender.isKilled:
            battle_log.append(
                f"{turns}. ***{defender.name} 在戰鬥中死亡了！{attacker.name} 還有 {attacker.hp:,} 個水晶***"
            )
        else:
            battle_log.append(
                f"{turns}. ***{defender.name} 失去了戰鬥能力！{attacker.name} 還有 {attacker.hp:,} 個水晶***"
            )
    else:
        reward = round(total_damage ** 0.25)
        battle_log.append(
            f"{turns}. ***雙方大戰了 {turns} 回合也沒能分出勝負***"
        )
    return '\n'.join(battle_log), reward


def kill_check(player: Player, dm_match: bool) -> Player:
    """ Decides the player is killed or not,
        based on the luck of player.

    :param player: A Player object, always should be the defeated one.
    :param dm: The battle match type, True if it's a death-match.

    :retrun player: Return the modified Player object.
    """
    if dm_match:
        p = random.uniform(0, 512)
    else:
        p = random.uniform(0, 17664)
    if p <= ((256 - player.luck) + (10.24 * player.kills)):
        player.isKilled = True
    return player


def skill_perform_ckeck(player: Player) -> list|None:
    """ Checks can the player has a chance to perform a skill. """
    if player.user_id is None:
        return None
    p = random.uniform(0, 100)
    skill_perform = rpg_db_manager.skill_performs(player.user_id, p)
    return skill_perform


def sys_get_skill(player: Player) -> tuple[int, float]:
    """ Get a new skill, for debug usage. """
    combo = 1 + roll.rolls_under(15, 1020, player.luck)
    damage_modifier = round((roll.rolls_sum(6, player.luck) / 100)**0.5, 2)
    return combo, damage_modifier


def get_skill_checker(player: Player) -> tuple[int, float]|None:
    """ Check is the player validate to get a new skill.

    :param player: Player object.

    :return tuple:
        If the random float number is lower then the player's luck,
        this player is validate to  get a new skill, then return
        a tuple of (combo, damage_modifier) of the skill.
        Otherwise it will return None.
    """
    chance = 1 + math.ceil((255 - player.luck) / 51)
    if roll.rolls_lowest(chance, 1024) <= player.luck:
        combo = 1 + roll.rolls_under(15, 400, player.luck)
        damage_modifier = round((roll.rolls_sum(6, player.luck) / 100)**0.5, 2)
        return combo, damage_modifier
    return None
