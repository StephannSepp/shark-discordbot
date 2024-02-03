from utils import embed_builder

__all__ = [
    "blackjack_embed",
    "roulette_embed",
    "embeds",
]

description = (
    "以一副牌遊玩, 遊戲開始時玩家獲得兩張牌, 莊家一張\n"
    "在玩家停牌後, 莊家需到 17 點才能停牌\n"
    "玩家若拿到「21點」時直接勝利, 獲得 1.5 倍籌碼\n"
    "若玩家牌面比莊家大或是莊家爆牌時玩家獲勝, 獲得 2 倍籌碼\n"
)
blackjack_embed = embed_builder.information("二十一點", description)

description = (
    "回合開始時會顯示本回合的彈藥, 綠色為假彈, 紅色為實彈\n"
    "荷官隨機裝入實彈與假彈至霰彈槍, 由玩家開始輪流選擇對自己或對方開槍\n"
    "若選擇對自己開槍且安然無恙, 你將會獲得額外的機會選擇\n"
    "獎勵表如下\n"
)
roulette_embed = embed_builder.information("惡魔輪賭盤", description)
roulette_embed.add_field("活過回合數", "A€50/回合")
roulette_embed.add_field("剩餘生命數", "A€100/個")
roulette_embed.add_field("向荷官開槍", "A€250/次")
roulette_embed.add_field("向自射擊安然無恙", "A€400/次")
roulette_embed.add_field("被荷官開槍懲罰", "A€100/次(落敗時 A€600/次)")
roulette_embed.add_field("向自己開槍懲罰", "A€800/次(落敗時 A€1,200/次)")
roulette_embed.add_field("退出彈藥懲罰", "A€50/次(落敗時 A€200/次)")

embeds = [blackjack_embed, roulette_embed]
