# 鯊魚
![鯊魚形象](/img/shark-discordbot.png "鯊魚形象")

![Built-with Python 3.10](https://img.shields.io/badge/Python-3.10-informational?style=plastic&logo=python)
![Disnake 2.7.0](https://img.shields.io/badge/disnake-2.7.0-informational?style=plastic)
![Version 2.2.479](https://img.shields.io/badge/version-2.2.479-informational?style=plastic)

## 關於我

### A self-use Discord Bot  
> 基於 Disnake 套件開發的 Discord Bot  
> Disnake 版本: 2.7.0  
> Python 版本 : 3.10 (不向下兼容)  

不是那隻迷因鯊魚、也不是亞特蘭提斯的後裔，只是在亞特蘭提斯的打工BOT。

## Changelog

* 2.2.479
	* FEAT: 防止使用者在 Bot 移除抽籤結果身分組時同時抽籤
	* TEST: 新增測試功能: 用於權限稽核的指令
* 2.2.386
	* FEAT: 新增抽籤統計指令 `/fortune statistics`
		* 可選選項 `group_by` 包含 `幸運天使`、`運氣`，可依不同選擇輸出不同統計數據
	* REFACTOR: 將抽籤指令整合至 `/fortune` 類別內，現在指令為 `/fortune draw`
* 2.2.352
	* REFACTOR: 重新調整檔案架構
		* 將個別功能的 Cog 檔案分為 extension、model、module 放在同一個資料夾底下
	* FEAT: 新增 Bot 運行時間(在 `/botinfo` 指令內)
	* FEAT: 從舊有 Bot 移植身分組分隔線功能、伺服器人數資訊顯示頻道
	* FEAT: 新增例外處理監聽
	* FEAT: 新增私訊監聽
* 2.1.338
	* FIX: 修復抽籤不會移除舊有抽籤結果身分組問題
* 2.1.333
	* FEAT: 抽籤會將抽籤結果加入身分組，在每日重置時一並移除
* 2.1.324
	* TEST: RPGame 新增攻略 Boss 機能
		* 預計將有 100 層，每層都有不同的 Boss
		* RPG models 底下新增 Boss 類別
		* 在戰鬥運算中增加對應的處理
		* 建立資料表 `boss_fight_stats` 用以未來紀錄 Boss 相關的數據統計
* 2.1.139
	* TEST: 開始 RPGame 的開發，建立基礎檔案架構及基本功能，指令前綴統一為 `/rpg`
		* 玩家間的互相切磋，包含獎勵
		* 商店購買、販賣功能
		* 行動功能，包含三種各自不同獎勵的行動
* 2.1.135
	* FEAT: 為 `/make_embed` 及 `moderation` 底下的管理指令群增加了 `copy` 可選選項，此選項會使 BOT 將訊息副本發送至指定頻道
* 2.1.53
	* FEAT: ~~新增 donothing 指令~~
* 2.1.39
	* FEAT: 新增建立 Embed 指令 `/make_embed`
		* 方便從 Discord 客戶端上建立 Discord embed
* 2.1.25
	* FEAT: 新增抽籤功能 `/draw`
		* 共有五種隨機結果、幸運色、幸運天使、幸運數字
		* 包含對應運勢的圖片
* 2.0.18
	* FEAT: 新增機器人資訊指令 `/botinfo`
* 2.0.14
	* FIX: 修正 `/warn add` 指令中 `warn_id` 參數超出整數範圍的問題
* 2.0.0
	* 發布，包含以下功能
		* 基礎管理指令
		* 半自動會員審核
		* 個人語音頻道管理
