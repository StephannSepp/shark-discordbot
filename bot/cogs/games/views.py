import math
import random
from collections import deque

import disnake
from disnake import ButtonStyle
from disnake import Colour
from disnake import Embed
from disnake import MessageInteraction
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

    # pylint: disable=W0237
    async def interaction_check(self, inter: MessageInteraction) -> bool:
        return inter.user.id == self.user.uid

    async def build_embed(self, end_of_game=False) -> Embed:
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
            await self.user.bank_transaction(
                coin_change_to_player=math.floor(self.bet * 1.5),
                note="Casino consumption.",
            )
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
                await self.user.bank_transaction(
                    coin_change_to_player=math.floor(self.bet * 2),
                    note="Casino consumption.",
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
                await self.user.bank_transaction(
                    coin_change_to_player=math.floor(self.bet * 1),
                    note="Casino consumption.",
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

    async def dealer_round(self) -> Embed:
        while self.calc_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.cards.pop())
        embed = await self.build_embed(end_of_game=True)
        return embed

    @disnake.ui.button(label="要牌", emoji="🔼", style=ButtonStyle.green)
    async def player_hit(self, button: Button, inter: MessageInteraction):
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
            embed = await self.dealer_round()
        else:
            # Player busted, no need to continue.
            embed = await self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="停牌", emoji="⏸️", style=ButtonStyle.gray)
    async def player_stop(self, button: Button, inter: MessageInteraction):
        self.first_hand = False
        self._disable_all_child()
        embed = await self.dealer_round()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="雙倍下注", emoji="⏫", style=ButtonStyle.blurple)
    async def player_double(self, button: Button, inter: MessageInteraction):
        await self.user.bank_transaction(
            coin_change_to_player=-self.bet, note="Casino consumption."
        )
        self.bet *= 2
        self.first_hand = False
        self._disable_all_child()
        self.player_hand.append(self.cards.pop())
        if self.calc_value(self.player_hand) > 21:
            # Player busted, no need to continue.
            self._disable_all_child()
            embed = await self.build_embed()
        else:
            embed = await self.dealer_round()
        await inter.response.edit_message(embed=embed, view=self)


class RouletteView(View):
    round_start = False
    total_shot = 0

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

    # pylint: disable=W0237
    async def interaction_check(self, inter: MessageInteraction) -> bool:
        return inter.user.id == self.user.uid

    def _start_round(self) -> None:
        self.round_start = False
        self.game_round += 1
        self.bullets = deque(maxlen=8)
        bullets: list[RouletteShot] = []
        k = random.randint(2, 8)
        white_round_chance = (1 - (math.exp(3 - self.game_round) ** 0.1) / 1 + 1) * 0.1
        if random.random() < white_round_chance:
            bullets.append(RouletteShot.RANDOM)
            if self.game_round >= 3 and k > 3:
                bullets.append(RouletteShot.RANDOM)
        if k >= 6:
            bullets.extend(
                [
                    RouletteShot.BLANK,
                    RouletteShot.BLANK,
                    RouletteShot.LIVE,
                    RouletteShot.LIVE,
                ]
            )
        elif k >= 3:
            bullets.extend([RouletteShot.BLANK, RouletteShot.LIVE])
        bullets.extend(
            random.choices(
                (RouletteShot.BLANK, RouletteShot.LIVE, RouletteShot.SLUG),
                weights=(50, 47, 3),
                k=(k - len(bullets)),
            )
        )
        random.shuffle(bullets)
        self.bullets.extend(bullets)
        self.game_logs.append(f"第 {self.game_round} 回合")
        self.game_logs.append("".join(b.value for b in sorted(bullets)))

    def _fire_once(self) -> tuple[int, RouletteShot]:
        shot = self.bullets.pop()
        if shot == RouletteShot.RANDOM:
            damage = random.choices((0, 1, 2), (50, 40, 10))[0]
            if damage > 0:
                self.total_shot += 1
            return damage, shot
        if shot == RouletteShot.SLUG:
            self.total_shot += 1
            return 2, shot
        if shot == RouletteShot.LIVE:
            self.total_shot += 1
            return 1, shot
        return 0, shot

    def _get_score(self) -> tuple[int, str, bool]:
        game_round = self.game_round
        remaining_life = self.player.life
        shot_dealer = self.player.shot_at_dealer
        self_attampt = self.player.shoot_self_attampt
        self_shot = self.player.shot_at_self
        self_blank = self_attampt - self_shot
        shot_taken = self.player.shot_taken_from_dealer
        shot_pop = self.player.pop_shot
        total_shot = self.total_shot
        reward = 0
        if remaining_life == 0:
            reward += shot_dealer * 100
            reward += self_blank * 200
            reward -= self.dealer.life * 50
            reward -= shot_taken * 300
            reward -= self_shot * 1200
            reward -= shot_pop * 400
            reward -= total_shot * 30
            if self.dealer.life == self.dealer.max_life:
                reward -= 1200
            reward = min(reward, 0)
            win = False
        else:
            reward += 2100
            reward += (game_round - 1) * 50
            reward += remaining_life * 100
            reward += shot_dealer * 200
            reward += self_blank * 600
            reward -= shot_taken * 100
            reward -= self_shot * 800
            reward -= shot_pop * 200
            if remaining_life == self.player.max_life:
                reward += 2400
            if self_attampt > 8 and self_shot == 0:
                reward += 3200
            if game_round >= 10:
                reward += 1000
            reward = max(reward, 0)
            win = True
        if remaining_life == 0:
            text = (
                f"{shot_dealer} 次向荷官開槍 x 100 = {shot_dealer * 100:,}\n"
                f"{self_blank} 次向自射擊安然無恙 x 200 = {self_blank * 200:,}\n"
                f"{self.dealer.life} 荷官剩餘生命 x -100 = {self.dealer.life * -100:,}\n"
                f"{shot_taken} 次被荷官開槍 x -300 = {shot_taken * -300:,}\n"
                f"{self_shot} 次向自己開槍 x -800 = {self_shot * -800:,}\n"
                f"{shot_pop} 次退出彈藥 x -400 = {shot_pop * -400:,}\n"
                f"{total_shot} 彈藥費用 x -30 = {total_shot * -30:,}\n"
                "== 其他獎懲 ==\n"
                f"善後費用 = -2,100\n"
            )
            if self.dealer.life == self.dealer.max_life:
                text += "滿身瘡痍 = -1,200\n"
        else:
            text = (
                f"活過 {game_round - 1} 回合 x 50 = {(game_round - 1) * 50:,}\n"
                f"{remaining_life} 剩餘生命 x 100 = {remaining_life * 100:,}\n"
                f"{shot_dealer} 次向荷官開槍 x 200 = {shot_dealer * 200:,}\n"
                f"{self_blank} 次向自己射擊安然無恙 x 600 = {self_blank * 600:,}\n"
                f"{shot_taken} 次被荷官開槍 x -100 = {shot_taken * -100:,}\n"
                f"{self_shot} 次向自己開槍 x -600 = {self_shot * -600:,}\n"
                f"{shot_pop} 次退出彈藥 x -200 = {shot_pop * -200:,}\n"
                "== 其他獎懲 ==\n"
                f"押金返還 = 2,100\n"
            )
            if remaining_life == self.player.max_life:
                text += "全身而退 = 2,400\n"
            if self_attampt > 8 and self_shot == 0:
                text += "天選之人 = 3,200\n"
            if game_round > 9:
                text += "長壽 = 1,000\n"
        return reward, text, win

    def _disable_all_child(self):
        for child in self.children:
            child.disabled = True

    async def build_embed(self) -> Embed:
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
            await self.user.bank_transaction(
                coin_change_to_player=reward, note="Casino consumption."
            )
            field_name = "勝利獎金" if win else "失敗罰金"
            if reward >= 0:
                embed.add_field(field_name, f"A€{reward:,}")
            else:
                if win:
                    embed.add_field(field_name, f"-A€{abs(reward):,}")
                else:
                    embed.add_field(field_name, f"-A€{abs(reward - 2400):,}")
            if self.user.coin >= 0:
                embed.add_field("金幣餘額", f"A€{self.user.coin:,}")
            else:
                embed.add_field("金幣餘額", f"-A€{abs(self.user.coin):,}")
        else:
            embed.add_field("玩家生命", self.player.lives)
            embed.add_field("荷官生命", self.dealer.lives)
        return embed

    @disnake.ui.button(label="對荷官開槍", style=ButtonStyle.green)
    async def shoot_at_dealer(self, button: Button, inter: MessageInteraction):
        if not self.round_start:
            self.game_logs.pop()
            self.round_start = True
        self.player.shoot_dealer_attampt += 1
        damage, shot = self._fire_once()
        if damage == 2:
            self.dealer.take_shot(damage)
            self.player.shot_at_dealer += 1
            self.game_logs.append(
                f"* {inter.author.mention}把獨彈頭{shot.value}送進了荷官的腦門裡"
            )
        elif damage == 1:
            self.dealer.take_shot(damage)
            self.player.shot_at_dealer += 1
            self.game_logs.append(
                f"* {inter.author.mention}把實彈{shot.value}打在了荷官的臉上"
            )
        else:
            self.game_logs.append(
                f"* {inter.author.mention}朝荷官扣動了扳機, 但是一枚假彈{shot.value}"
            )
        self.dealers_turn()
        embed = await self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="對自己開槍", style=ButtonStyle.blurple)
    async def shoot_at_self(self, button: Button, inter: MessageInteraction):
        if not self.round_start:
            self.game_logs.pop()
            self.round_start = True
        self.player.shoot_self_attampt += 1
        damage, shot = self._fire_once()
        if damage == 2:
            self.player.take_shot(damage)
            self.player.shot_at_self += 1
            self.game_logs.append(
                f"* {inter.author.mention}朝自己的腦袋賞了一發獨彈頭{shot.value}"
            )
            self.dealers_turn()
        elif damage == 1:
            self.player.take_shot(damage)
            self.player.shot_at_self += 1
            self.game_logs.append(
                f"* {inter.author.mention}朝自己扣了扳機, 是枚貨真價實的實彈{shot.value}"
            )
            self.dealers_turn()
        else:
            self.game_logs.append(
                f"* {inter.author.mention}朝自己扣動了扳機, 是一枚假彈{shot.value}"
            )
        embed = await self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="退出一發彈藥", style=ButtonStyle.blurple)
    async def pop_one_shot(self, button: Button, inter: MessageInteraction):
        if not self.round_start:
            self.game_logs.pop()
            self.round_start = True
        shot = self.bullets.pop()
        self.player.pop_shot += 1
        if shot == RouletteShot.RANDOM:
            self.game_logs.append(
                f"* {inter.author.mention}退出了一發彈藥, 是枚隨機彈{shot.value}"
                f"(剩餘 {2 - self.player.pop_shot} 次)"
            )
        elif shot == RouletteShot.SLUG:
            self.game_logs.append(
                f"* {inter.author.mention}退出了一發彈藥, 是枚獨彈頭{shot.value}"
                f"(剩餘 {2 - self.player.pop_shot} 次)"
            )
        elif shot == RouletteShot.LIVE:
            self.game_logs.append(
                f"* {inter.author.mention}退出了一發彈藥, 是枚實彈{shot.value}"
                f"(剩餘 {2 - self.player.pop_shot} 次)"
            )
        else:
            self.game_logs.append(
                f"* {inter.author.mention}退出了一發彈藥, 是枚假彈{shot.value}"
                f"(剩餘 {2 - self.player.pop_shot} 次)"
            )
        if self.player.pop_shot >= 2:
            for child in self.children:
                if child.label == "退出一發彈藥":
                    child.disabled = True
        embed = await self.build_embed()
        await inter.response.edit_message(embed=embed, view=self)

    def dealers_turn(self) -> bool:
        if self.player.life == 0 or self.dealer.life == 0:
            return
        if self.empty:
            self._start_round()
            return
        if (next_shot := self.dealer.check_next_shot(self.bullets)) is not None:
            self.game_logs.append(
                f"* 荷官檢查了槍膛裡的彈藥(剩餘 {2 - self.dealer.next_shot_checked} 次)"
            )
            if next_shot == RouletteShot.BLANK:
                aim_at_player = False
            elif next_shot == RouletteShot.RANDOM:
                aim_at_player = random.random() < 0.5
            else:
                aim_at_player = True
        else:
            aim_at_player = self.dealer.aim_at_player(self.bullets)
        if aim_at_player:
            damage, shot = self._fire_once()
            if damage == 2:
                self.player.take_shot(damage)
                self.player.shot_taken_from_dealer += 1
                self.game_logs.append(f"* 荷官將獨彈頭{shot.value}送進了你的頭顱")
            elif damage == 1:
                self.player.take_shot(damage)
                self.player.shot_taken_from_dealer += 1
                self.game_logs.append(f"* 荷官朝你的臉上開了一槍實彈{shot.value}")
            else:
                self.game_logs.append(f"* 荷官朝你扣動了扳機, 是一枚假彈{shot.value}")
        else:
            damage, shot = self._fire_once()
            if damage == 2:
                self.game_logs.append(
                    f"* 荷官朝把自己的頭給打爆了, 是枚獨彈頭{shot.value}"
                )
                self.dealer.take_shot(damage)
            elif damage == 1:
                self.game_logs.append(f"* 荷官朝把實彈{shot.value}打在了自己的臉上")
                self.dealer.take_shot(damage)
            else:
                self.game_logs.append(f"* 荷官朝自己扣了扳機, 是枚假彈{shot.value}")
                self.dealers_turn()

    @property
    def empty(self):
        return len(self.bullets) == 0
