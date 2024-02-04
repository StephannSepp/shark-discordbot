import math
import random
from collections import deque

import disnake
from disnake import ButtonStyle
from disnake import CmdInter
from disnake import Colour
from disnake import Embed
from disnake.ui import Button
from disnake.ui import View
from utils import embed_builder

from . import Card
from . import RouletteDealer
from . import RoulettePlayer
from . import RouletteShot
from . import create_cards_pool
from .helpers import GameUser


class BlackjackView(View):
    first_hand = True

    def __init__(self, user: GameUser, bet: int):
        super().__init__(timeout=1440)
        self.user = user
        self.bet = bet
        self.cards: list[Card] = create_cards_pool()
        random.shuffle(self.cards)
        self.dealer_hand: list[Card] = []
        self.player_hand: list[Card] = []
        self.dealer_hand.append(self.cards.pop())
        self.player_hand.append(self.cards.pop())
        self.player_hand.append(self.cards.pop())

    def build_embed(self, end_of_game=False) -> Embed:
        player_value = self.calc_value(self.player_hand)
        dealer_value = self.calc_value(self.dealer_hand)
        description = f"莊家點數: {dealer_value}\n" f"閒家(你)點數: {player_value}\n"
        embed = embed_builder.information("21 點", description)
        embed.add_field("莊家的牌", "".join(map(str, self.dealer_hand)), inline=False)
        embed.add_field(
            "閒家(你)的牌", "".join(map(str, self.player_hand)), inline=False
        )
        if self.first_hand and player_value == 21:
            # Player got the Blackjack, disable all button.
            self._disable_all_child()
            self.user.bank_transaction(coin_change_to_player=math.floor(self.bet * 1.5))
            embed.color = Colour.green()
            embed.add_field("結果", "二十一點", inline=False)
            embed.add_field(
                "贏回金幣", f"A€{math.floor(self.bet * 1.5):,}", inline=False
            )
            self.stop()
            return embed
        if player_value > 21:
            # Player busted, disable all button.
            self._disable_all_child()
            embed.color = Colour.red()
            embed.add_field("結果", "爆牌", inline=False)
            self.stop()
            return embed
        if end_of_game:
            # Game ends, determine winner.
            for child in self.children:
                if child.label == "雙倍下注":
                    child.disabled = True
            if dealer_value > 21 or player_value > dealer_value:
                self.user.bank_transaction(
                    coin_change_to_player=math.floor(self.bet * 2)
                )
                embed.color = Colour.green()
                embed.add_field("結果", "閒家(你)勝", inline=False)
                embed.add_field("贏回金幣", f"A€{self.bet * 2:,}", inline=False)
                self.stop()
            elif player_value < dealer_value:
                embed.color = Colour.red()
                embed.add_field("結果", "莊家勝", inline=False)
                self.stop()
            elif player_value == dealer_value:
                self.user.bank_transaction(
                    coin_change_to_player=math.floor(self.bet * 1)
                )
                embed.color = Colour.yellow()
                embed.add_field("結果", "平局", inline=False)
                embed.add_field("贏回金幣", f"A€{self.bet:,}", inline=False)
                self.stop()
        return embed

    def _disable_all_child(self):
        for child in self.children:
            child.disabled = True

    @staticmethod
    def calc_value(hand: list[Card]) -> int:
        value = sum(card.value for card in hand)
        if value <= 21:
            return value
        for card in filter(lambda c: c.is_ace, hand):
            card.use_lower_value = True
            value = sum(card.value for card in hand)
            if value <= 21:
                break
        return value

    def dealer_round(self) -> Embed:
        while self.calc_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.cards.pop())
        embed = self.build_embed(end_of_game=True)
        return embed

    @disnake.ui.button(label="要牌", emoji="🔼", style=ButtonStyle.green)
    async def player_hit(self, button: Button, inter: CmdInter):
        if inter.author.id != self.user.uid:
            await inter.response.send_message("該遊戲並非您發起的", ephemeral=True)
        self.first_hand = False
        # Disable double bet
        for child in self.children:
            if child.label == "雙倍下注":
                child.disabled = True
        self.player_hand.append(self.cards.pop())
        if self.calc_value(self.player_hand) >= 21:
            # Player's value reaches 21 or more, stop automatically
            self._disable_all_child()
        if self.calc_value(self.player_hand) == 21:
            embed = self.dealer_round()
        else:
            # Player busted, no need to continue.
            embed = self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="停牌", emoji="⏸️", style=ButtonStyle.gray)
    async def player_stop(self, button: Button, inter: CmdInter):
        if inter.author.id != self.user.uid:
            await inter.response.send_message("該遊戲並非您發起的", ephemeral=True)
        self.first_hand = False
        self._disable_all_child()
        embed = self.dealer_round()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="雙倍下注", emoji="⏫", style=ButtonStyle.blurple)
    async def player_double(self, button: Button, inter: CmdInter):
        if inter.author.id != self.user.uid:
            await inter.response.send_message("該遊戲並非您發起的", ephemeral=True)
        self.user.bank_transaction(coin_change_to_player=-self.bet)
        self.bet *= 2
        self.first_hand = False
        self._disable_all_child()
        self.player_hand.append(self.cards.pop())
        if self.calc_value(self.player_hand) > 21:
            # Player busted, no need to continue.
            self._disable_all_child()
            embed = self.build_embed()
        else:
            embed = self.dealer_round()
        await inter.response.edit_message(embed=embed, view=self)


class RouletteView(View):
    def __init__(
        self,
        user: GameUser,
        player: RoulettePlayer,
        dealer: RouletteDealer,
    ):
        super().__init__(timeout=1440)
        self.game_logs = deque(maxlen=10)
        self.player = player
        self.dealer = dealer
        self.user = user
        self.game_round = 0
        self._start_round()

    def _start_round(self) -> None:
        self.game_round += 1
        self.bullets = deque(maxlen=8)
        bullets: list[RouletteShot] = random.choices(
            (RouletteShot.BLANK, RouletteShot.LIVE, RouletteShot.SLUG),
            weights=(50, 47, 3),
            k=random.randint(2, 8),
        )
        self.bullets.extend(bullets)
        self.game_logs.append(f"第 {self.game_round} 回合")
        self.game_logs.append("".join(b.value for b in sorted(bullets)))

    def _fire_once(self) -> int:
        shot = self.bullets.pop()
        if shot == RouletteShot.SLUG:
            return 2
        if shot == RouletteShot.LIVE:
            return 1
        return 0

    def _get_score(self) -> tuple[int, str, bool]:
        game_round = self.game_round
        remaining_life = self.player.life
        shot_dealer = self.player.shot_at_dealer
        self_blank = self.player.shoot_self_attampt - self.player.shot_at_self
        shot_taken = self.player.shot_taken_from_dealer
        self_shot = self.player.shot_at_self
        shot_pop = self.player.pop_shot
        reward = 0
        reward += (game_round - 1) * 50
        reward += remaining_life * 100
        reward += shot_dealer * 250
        reward += self_blank * 400
        if remaining_life == 0:
            reward -= shot_taken * 600
            reward -= self_shot * 1200
            reward -= shot_pop * 200
            reward = min(reward, 0)
            win = False
        else:
            reward -= shot_taken * 100
            reward -= self_shot * 800
            reward -= shot_pop * 50
            reward = max(reward, 0)
            win = True
        text = (
            f"活過 {game_round - 1} 回合 x 50 = {(game_round - 1) * 50:,}\n"
            f"{remaining_life} 剩餘生命 x 100 = {remaining_life * 100:,}\n"
            f"{shot_dealer} 次向荷官開槍 x 250 = {shot_dealer * 250:,}\n"
            f"{self_blank} 次向自射擊安然無恙 x 400 = {self_blank * 400:,}\n"
        )
        if remaining_life == 0:
            text += (
                f"{shot_taken} 次被荷官開槍 x -600 = {shot_taken * -600:,}\n"
                f"{self_shot} 次向自己開槍 x -1200 = {self_shot * -1200:,}\n"
                f"{shot_pop} 次退出彈藥 x -200 = {shot_pop * -200:,}\n"
            )
        else:
            text += (
                f"{shot_taken} 次被荷官開槍 x -100 = {shot_taken * -100:,}\n"
                f"{self_shot} 次向自己開槍 x -800 = {self_shot * -800:,}\n"
                f"{shot_pop} 次退出彈藥 x -50 = {shot_pop * -50:,}\n"
            )
        return reward, text, win

    def _disable_all_child(self):
        for child in self.children:
            child.disabled = True

    def build_embed(self) -> Embed:
        result = ""
        if self.player.life == 0 or self.dealer.life == 0:
            reward, result, win = self._get_score()
            result = f"\n\n{result}"
            self._disable_all_child()
            self.stop()
        elif self.empty:
            self._start_round()
        description = "\n".join(self.game_logs) + result
        embed = embed_builder.information("霰彈槍輪盤", description)
        if self.player.life == 0 or self.dealer.life == 0:
            self.user.bank_transaction(coin_change_to_player=reward)
            field_name = "勝利獎金" if win else "失敗罰金"
            if reward >= 0:
                embed.add_field(field_name, f"A€{reward:,}")
            else:
                embed.add_field(field_name, f"-A€{abs(reward):,}")
            if self.user.coin >= 0:
                embed.add_field("金幣餘額", f"A€{self.user.coin:,}")
            else:
                embed.add_field("金幣餘額", f"-A€{abs(self.user.coin):,}")
        else:
            embed.add_field("玩家生命", self.player.lives)
            embed.add_field("荷官生命", self.dealer.lives)
        return embed

    @disnake.ui.button(label="對荷官開槍", style=ButtonStyle.green)
    async def shoot_at_dealer(self, button: Button, inter: CmdInter):
        if inter.author.id != self.user.uid:
            await inter.response.send_message("該遊戲並非您發起的", ephemeral=True)
        self.player.shoot_dealer_attampt += 1
        damage = self._fire_once()
        if damage == 2:
            self.dealer.take_shot(damage)
            self.player.shot_at_dealer += 1
            self.game_logs.append(
                f"* {inter.author.mention}把獨彈頭{RouletteShot.SLUG.value}送進了荷官的腦門裡"
            )
        elif damage == 1:
            self.dealer.take_shot(damage)
            self.player.shot_at_dealer += 1
            self.game_logs.append(
                f"* {inter.author.mention}把實彈{RouletteShot.LIVE.value}打在了荷官的臉上"
            )
        else:
            self.game_logs.append(
                f"* {inter.author.mention}朝荷官扣動了扳機, 但是一枚假彈{RouletteShot.BLANK.value}"
            )
        self.dealers_turn()
        embed = self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="對自己開槍", style=ButtonStyle.blurple)
    async def shoot_at_self(self, button: Button, inter: CmdInter):
        if inter.author.id != self.user.uid:
            await inter.response.send_message("該遊戲並非您發起的", ephemeral=True)
        self.player.shoot_self_attampt += 1
        damage = self._fire_once()
        if damage == 2:
            self.player.take_shot(damage)
            self.player.shot_at_self += 1
            self.game_logs.append(
                f"* {inter.author.mention}朝自己的腦袋賞了一發獨彈頭{RouletteShot.SLUG.value}"
            )
            self.dealers_turn()
        elif damage == 1:
            self.player.take_shot(damage)
            self.player.shot_at_self += 1
            self.game_logs.append(
                f"* {inter.author.mention}朝自己扣了扳機, 是枚貨真價實的實彈{RouletteShot.LIVE.value}"
            )
            self.dealers_turn()
        else:
            self.game_logs.append(
                f"* {inter.author.mention}朝自己扣動了扳機, 是一枚假彈{RouletteShot.BLANK.value}"
            )
        embed = self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="退出一發彈藥", style=ButtonStyle.blurple)
    async def pop_one_shot(self, button: Button, inter: CmdInter):
        if inter.author.id != self.user.uid:
            await inter.response.send_message("該遊戲並非您發起的", ephemeral=True)
        shot = self.bullets.pop()
        if shot == RouletteShot.SLUG:
            self.game_logs.append(
                f"* {inter.author.mention}退出了一發彈藥, 是枚獨彈頭{RouletteShot.SLUG.value}"
            )
        elif shot == RouletteShot.LIVE:
            self.game_logs.append(
                f"* {inter.author.mention}退出了一發彈藥, 是枚實彈{RouletteShot.LIVE.value}"
            )
        else:
            self.game_logs.append(
                f"* {inter.author.mention}退出了一發彈藥, 是枚假彈{RouletteShot.BLANK.value}"
            )
        self.player.pop_shot += 1
        if self.player.pop_shot >= 2:
            for child in self.children:
                if child.label == "退出一發彈藥":
                    child.disabled = True
        embed = self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    def dealers_turn(self) -> bool:
        if self.player.life == 0 or self.dealer.life == 0:
            return
        if self.empty:
            self._start_round()
            return
        if self.dealer.aim_at_player(self.bullets):
            damage = self._fire_once()
            if damage == 2:
                self.player.take_shot(damage)
                self.dealer.sanitize()
                self.player.shot_taken_from_dealer += 1
                self.game_logs.append(
                    f"* 荷官將獨彈頭{RouletteShot.SLUG.value}送進了你的頭顱"
                )
            elif damage == 1:
                self.player.take_shot(damage)
                self.dealer.sanitize()
                self.player.shot_taken_from_dealer += 1
                self.game_logs.append(
                    f"* 荷官朝你的臉上開了一槍{RouletteShot.LIVE.value}"
                )
            else:
                self.game_logs.append(
                    f"* 荷官朝你扣動了扳機, 是一枚假彈{RouletteShot.BLANK.value}"
                )
        else:
            damage = self._fire_once()
            if damage == 2:
                self.game_logs.append(
                    f"* 荷官朝把自己的頭給打爆了, 是枚獨彈頭{RouletteShot.SLUG.value}"
                )
                self.dealer.take_shot(damage)
            elif damage == 1:
                self.game_logs.append(
                    f"* 荷官朝把實彈{RouletteShot.LIVE.value}打在了自己的臉上"
                )
                self.dealer.take_shot(damage)
            else:
                self.game_logs.append(
                    f"* 荷官朝自己扣了扳機, 是枚假彈{RouletteShot.BLANK.value}"
                )
                self.dealer.sanitize()
                self.dealers_turn()

    @property
    def empty(self):
        return len(self.bullets) == 0
