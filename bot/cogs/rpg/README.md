## 速度公式
$$ Player's Spd =  (Player's Mana * 16) + Player's Crystal $$ 

> 當以下條件發生時，為該玩家回合：  

$$(Player's Spd + Target's Spd) - Player's Spd <= 0$$

## 傷害公式

數值初始調整：

$$ Mana = Mana + 1 $$

> ###### By default both players' mana are added  by 1, so that divide by zero situation will never happen.

$$ DamageModifier = \sqrt{{Player's Crystal + Target's Crystal \over (Player's Mana + Target's Mana) * 87}} $$  

$$ DamageLow = [(69 * Player's Mana * {Player's Luk \over 255}) - ((Target's Mana - 1) * 5)] * DamageModifier  $$  

$$ DamageHigh = [(87 * Player's Mana) - ((Target's Mana - 1) * 6)] *  DamageModifier $$  

> ###### The max luck value is 255.
> ###### If the player has 0 mana, then the defense from that player will be ignored.

$$ FinalDamage = Random[DamageLow, DamageHigh] $$