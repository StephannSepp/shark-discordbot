from utils import embed_builder

__all__ = [
    "fortune_embed",
    "remind_embed",
    "vchive_embed",
    "gacha_embed",
    "misc_embed",
    "action_embed",
    "banking_embed",
    "casino_embed",
    "embeds",
]

fortune_embed = embed_builder.information("運勢指令組")
fortune_embed.add_field("/fortune draw", "每日抽籤，於每日早上 8:00 重置", inline=False)
fortune_embed.add_field(
    "/fortune statistics",
    (
        "顯示個人抽籤統計。可接受`group_by`[運勢|幸運天使]參數決定統計分類類別\n"
        "｜group_by 運勢: 顯示抽籤各運勢的出現次數、機率\n"
        "｜group_by 幸運天使: 顯示前 9 出現次數最多的幸運天使、機率"
    ),
    inline=False,
)

remind_embed = embed_builder.information("提醒指令組")
remind_embed.add_field(
    "/remind me",
    (
        "新增一個提醒，需輸入`after`及`message`參數\n"
        "｜after: 參數為**指定時長後**執行，非指定特定時間，"
        "僅接受 d(日), h(小時), m(分鐘), s(秒) 格式，如`2d8h5m20s`\n"
        "｜message: 接受任何訊息，以兩個空格代替換行"
    ),
    inline=False,
)
remind_embed.add_field("/remind list", "列出個人以新增的提醒", inline=False)

vchive_embed = embed_builder.information("存檔備份系統")
vchive_embed.add_field(
    "/vchive archive",
    (
        "顯示所有存檔列表，依據存檔 VID 於`vid`參數取得存檔詳細資訊。"
        "可接受`vid`或`channel`參數\n"
        "｜channel: 顯示特定頻道的存檔列表\n"
        "｜vid: 輸入存檔 VID 來取得該存檔的詳細資訊"
    ),
    inline=False,
)
vchive_embed.add_field("/vchive channel", "顯示所有計畫存檔的頻道列表", inline=False)

gacha_embed = embed_builder.information("模擬抽卡指令組")
gacha_embed.add_field(
    "/gacha pure_rate",
    (
        "依隨機機率決定抽卡結果，`rate_percentage`為必填參數。可接受`spins`參數\n"
        "｜rate_percentage: 抽卡機率，百分比(%)\n"
        "｜spins: 抽卡次數，預設為 10 次，不可大於 1000 次"
    ),
    inline=False,
)

misc_embed = embed_builder.information("其他指令")
misc_embed.add_field("/ping", "顯示機器人連線延遲", inline=False)
misc_embed.add_field("/donothing", "這個指令不會做任何事", inline=False)
misc_embed.add_field("/botinfo", "機器人、系統資訊", inline=False)
misc_embed.add_field("/kuaikuai", "數位化乖乖", inline=False)

action_embed = embed_builder.information("行動指令")
action_embed.add_field("/action mining", "挖礦, CD 8 小時並獲得黃金")
action_embed.add_field("/action fishing", "釣魚, CD 4 小時並獲得金幣")

banking_embed = embed_builder.information("銀行指令")
banking_embed.add_field("/banking profile", "檢視自己的資產")
banking_embed.add_field("/banking atlantean_coin", "檢視亞特蘭提斯金幣相關資訊")
banking_embed.add_field("/banking sell_gold", "向銀行販賣黃金")

casino_embed = embed_builder.information("賭場指令")
casino_embed.add_field("/casino help", "賭場指令說明")
casino_embed.add_field("/casino blackjack", "二十一點遊戲")
casino_embed.add_field("/casino roulette", "惡魔賭輪盤遊戲")

lottery_embed = embed_builder.information("彩券指令")
lottery_embed.add_field("/lottery buy", "購買價值 100 金幣的彩券, 選擇任意 4 位數字, 每周三、日開獎")
lottery_embed.add_field("/lottery winning_number", "顯示上期頭獎號碼, 並兌換獎勵")

embeds = [
    fortune_embed,
    remind_embed,
    vchive_embed,
    gacha_embed,
    action_embed,
    banking_embed,
    casino_embed,
    misc_embed,
]
