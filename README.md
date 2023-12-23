# 鯊魚
![鯊魚形象](/img/shark-discordbot.png "鯊魚形象")

![Built-with Python 3.10](https://img.shields.io/badge/Python-3.10-informational?style=plastic&logo=python)
![Disnake 2.9.0](https://img.shields.io/badge/disnake-2.9.0-informational?style=plastic)
![Version 2.5.8](https://img.shields.io/badge/version-2.5.8-informational?style=plastic)

## 關於我

### A self-use Discord Bot  
> 基於 Disnake 套件開發的 Discord Bot  
> Disnake 版本: 2.9.0  
> Python 版本 : 3.10 (不向下兼容)  

不是那隻迷因鯊魚、也不是亞特蘭提斯的後裔，只是在亞特蘭提斯的打工BOT。

## Changelog

* 2.5.8
	* 增加 Help 指令
* 2.5.2
	* Vchive 直播備份/存檔系統
* 2.4.16
	* 部分指令i18n在地化；增加 gacha 系列指令模擬抽卡機率
* 2.4.4
	* 沒什麼改變，只是換了個伺服器
* 2.3.715
	* 抽籤圖片資源改用 URL 而非上傳本機檔案
* 2.3.613
	* Reminder
	* 暫時停用 vxtwitter 轉換
* 2.2.571
	* 將 Twitter 網址轉換為 vxtwitter
* 2.2.532
	* 增加乖乖
* 2.2.531
	* 修正含有 `copy` 副本參數的指令發生 interaction timeout 的問題
* 2.2.520
	* 新增 `/tablat_text` 指令，用於產生文字圖片
* 2.2.504
	* 新增管理用指令，用於檢查身分組對應所有頻道、類別的權限
* 2.2.480
	* 防止使用者在抽籤重置後至 Bot 移除運勢身分組期間或之前使用抽籤指令
* 2.2.386
	* 新增抽籤統計指令 `/fortune statistics`
	* 將抽籤指令整合至 `/fortune` 類別內，現在指令為 `/fortune draw`
* 2.2.352
	* 重新調整檔案架構
	* 新增 Bot 運行時間(在`/botinfo`指令內)
	* 從舊有 Bot 移植身分組分隔線功能、伺服器人數資訊顯示頻道
	* 新增錯誤監聽
	* 新增私訊監聽
* 2.1.338
	* 修復抽籤不會移除舊有抽籤結果身分組問題
* 2.1.333
	* 抽籤會將抽籤結果加入身分組
* 2.1.135
	* 為 make-embed 及管理指令群增加了 copy 可選選項，此選項會使 BOT 將訊息副本發送至指定頻道
* 2.1.53
	* ~~新增 donothing 指令~~
* 2.1.39
	* 新增建立 Embed 指令
* 2.1.25
	* 新增抽籤功能
* 2.0.18
	* 新增機器人資訊指令
* 2.0.14
	* 修正"warn add"指令中"warn_id"參數超出整數範圍的問題
* 2.0.0
	* 發布
