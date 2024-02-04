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
        "* group_by 運勢: 顯示抽籤各運勢的出現次數、機率\n"
        "* group_by 幸運天使: 顯示前 9 出現次數最多的幸運天使、機率"
    ),
    inline=False,
)

remind_embed = embed_builder.information("提醒指令組")
remind_embed.add_field(
    "/remind me",
    (
        "新增一個提醒，需輸入`after`及`message`參數\n"
        "* after: 參數為**指定時長後**執行，非指定特定時間，"
        "僅接受 [d(日), h(小時), m(分鐘), s(秒)] 格式，如`2d8h5m20s`\n"
        "* message: 接受任何訊息，使用兩個空格可換行"
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
        "* channel: 顯示特定頻道的存檔列表\n"
        "* vid: 輸入存檔 VID 來取得該存檔的詳細資訊"
    ),
    inline=False,
)
vchive_embed.add_field("/vchive channel", "顯示所有計畫存檔的頻道列表", inline=False)

gacha_embed = embed_builder.information("模擬抽卡指令組")
gacha_embed.add_field(
    "/gacha pure_rate",
    (
        "依隨機機率決定抽卡結果，`rate_percentage`為必填參數。可接受`spins`參數\n"
        "* rate_percentage: 抽卡機率，百分比(%)\n"
        "* spins: 抽卡次數，預設為 10 次，不可大於 1000 次"
    ),
    inline=False,
)

misc_embed = embed_builder.information("其他指令")
misc_embed.add_field("/ping", "顯示機器人連線延遲", inline=False)
misc_embed.add_field("/donothing", "這個指令不會做任何事", inline=False)
misc_embed.add_field("/botinfo", "機器人、系統資訊", inline=False)
misc_embed.add_field("/kuaikuai", "數位化乖乖", inline=False)

action_embed = embed_builder.information("行動指令")
action_embed.add_field(
    "/action mining",
    "挖礦 CD 為 7 小時, 獲得的是黃金, 時間結束時再次輸入指令即可領取工酬",
    inline=False,
)
action_embed.add_field(
    "/action fishing",
    "釣魚 CD 為 2 小時, 獲得的是金幣, 時間結束時再次輸入指令即可領取工酬",
    inline=False,
)

banking_embed = embed_builder.information("銀行指令")
banking_embed.add_field("/banking profile", "檢視自己的資產", inline=False)
banking_embed.add_field(
    "/banking atlantean_coin",
    "檢視亞特蘭提斯金幣相關資訊、匯率，匯率於每日早上 8:00 更新",
    inline=False,
)
banking_embed.add_field("/banking sell_gold", "向銀行以當前匯率販賣黃金", inline=False)

casino_embed = embed_builder.information("賭場指令")
casino_embed.add_field("/casino help", "賭場指令說明", inline=False)
casino_embed.add_field(
    "/casino blackjack",
    (
        "二十一點遊戲，遊戲流程如下\n"
        "1. 以一副牌遊玩, 遊戲開始時玩家獲得 2 張牌, 莊家 1 張\n"
        "2. 若玩家獲得 21 點時則獲得 1.5 倍籌碼\n"
        "3. 玩家可決定是否加倍籌碼, 若加倍籌碼玩家將只再獲得 1 張牌\n"
        "4. 玩家停牌後, 輪到莊家拿牌, 莊家需到 17 點才能停牌\n"
        "5. 若玩家勝利則獲得 2 倍籌碼\n"
        "※ 並無五張勝利的規則"
    ),
    inline=False,
)
casino_embed.add_field(
    "/casino roulette",
    (
        "霰彈槍輪盤遊戲\n"
        "遊戲圍繞在一把隨機裝入假彈與實彈的霰彈槍, 玩家與荷官輪流決定要朝自己擊發或是"
        "對方擊發, 直到有一方生命值耗盡."
        "每回合開始時會顯示本回合裝入的彈藥, "
        "紅色<:Shotgun_Shell:1202947684877471774>為實彈, "
        "黑色<:Shotgun_Shell_Black:1203509902782369792>為獨彈頭, 能造成雙倍傷害, "
        "綠色<:Shotgun_Shell_Green:1202947686911844433>為假彈, "
        "且每回合一定是由玩家開始.\n"
        "* 若選擇向自己擊發並安然無恙時則繼續該回合, 若沒有霰彈槍則會交給對方.\n"
        "* 玩家每次遊戲時有兩次機會將彈藥退出, 並告知玩家退出的彈藥是實彈或是假彈.\n"
    ),
    inline=False,
)

lottery_embed = embed_builder.information("彩券指令")
lottery_embed.add_field(
    "/lottery buy",
    (
        "以 100 金幣購買任意 4 位數字彩券, 彩券在每周三、日開出頭獎號碼.\n"
        "獎項有 4 等賞 至 1 等賞, 由個位數檢查至千位數(由左至右), 若數字符合則往下個位數檢查.\n"
        "* 如頭獎為 1234, 若玩家挑選了 7654, 僅個位數符合則為 4 等賞.\n"
        "* 如頭獎為 1235, 若玩家挑選了 1234, 因為個位數不符合前面三碼符合也無效, 因此沒有獲得"
        "任何獎金.\n"
    ),
    inline=False,
)
lottery_embed.add_field(
    "/lottery winning_number",
    (
        "顯示上期頭獎號碼, 並兌換獎勵\n"
        "１等賞｜A€183,000\n"
        "２等賞｜A€18,300\n"
        "３等賞｜A€3,660\n"
        "４等賞｜A€915\n"
    ),
    inline=False,
)

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
