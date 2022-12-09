## 檔案架構說明

### cogs
*存放一些 commands.Cog 功能模組*

> * event
> 	* 一些監聽器
> * fortune
> 	* `/draw` - 抽籤指令
> * rpg
>	* RPGame
> * make_embed.py
> 	* 一個製作 Discord Embed 的方便指令
> * membership_assist.py
> 	* 半自動會員審核
> * misc.py
>	* 一些雜項指令
> 		* `/ping` - 單純用來檢查 Bot 連線機能的指令
> 		* `/donothing` - 這個指令什麼也不會做
> 		* `/botinfo` - 顯示 Bot 基本資訊
> * moderation.py
> 	* 基本的管理模組
> 		* 包含停權、踢出、禁言、警告功能
> * temporary_voice.py
> 	* 個人語音頻道管理

### data
*存放靜態資料的資料夾*

### database
*存放一些與資料庫有關的檔案*

> * db_manager.py
> 	* 包含一些操作資料庫的函式
> * rpg_db_manager.py
> 	* 供 RPGame 使用的資料庫操作函式庫
> * rpg_destroy.sql
> 	* 刪除RPGame資料庫的SQL語法
> * schema.sql
> 	* 用來初始化資料庫的資料表結構、SQL語法

### utils
*存放一些簡單的函式庫*

> * embed_builder.py
> 	* 協助建立 Discord Embed 的函式
> * gen.py
> 	* 一些字符生成器
> * roll.py
> 	* 一些擲骰函式
> * time_process.py
> 	* 處理一些與時間物件相關的函式

* bot.py
* config.py
* requirements.txt  