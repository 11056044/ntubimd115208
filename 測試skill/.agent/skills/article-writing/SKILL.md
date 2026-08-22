
Gemini
將聊天轉換為 PDF
將聊天轉換為 PDF
在 Acrobat 中開啟此聊天

即時通訊

Spark
Beta 版
新對話
搜尋對話
影片
媒體庫
Gem
新增筆記本
The Tehran Escalation: A Middle East in Turmoil
UBstore: Corporate Profile and Brand Portfolio
所有筆記本
育兒管理系統功能建議
POP 設計：黃色活動資訊
Takara Tomy Mall 訂購教學
Django 警告訊息與修正建議
使用案例圖修改與細化
AI Agent 系統開發規範
網路知識與實戰解析
簡報講稿生成與建議
生死課讀後感擴寫與潤飾
報告與文件修正待辦清單
報告內容建議與存取限制
生物科技與醫療知識問答
NAT 網路位址轉換快速入門
Unity APP 畫面串連設定教學
活潑字體，簡約素材設計
Unity 按鈕失效的除錯指南
Django REST Framework 實作指南
Unity C# 編譯錯誤：找不到名稱
APP首頁設計：運動場地預訂
檢定二母體變異數相等臨界值
PowerShell curl 錯誤解決方法
Gemini Features: Gems and Storybook
Gemini Gems & Storybook Demo
Bolt's Digital Forest Adventure
Storybook: Robot's Digital Forest Adventure
Short-Term Financing Needs Explained
Gemini Guided Learning Demonstration
DIY Desk Wood Selection Guidance
簡報製作與調整請求
簡報製作：Gemini 與 Storybook
Django 專案建置與問答系統
畢業專題系統功能介紹
Django DateTimeField 解決方案
Word 表目錄自動生成教學
孕產嬰兒管理系統 UML 程式碼
孕產婦角色稱呼與案例應用
和 Gemini 的對話
你覺得除了 歷史回顧、樹洞、個人化推薦，我們還可以開發什麼樣的功能?

這份系統手冊寫得非常完整且結構清晰！你們將一站式孕產育兒管理與 LINE、n8n 自動化流程及 Supabase RAG 向量資料庫結合，是一個技術落地且精準擊中新手父母痛點的優異專案。

針對你們提出的「除了歷史回顧、樹洞（可能對應目前的心情紀錄與 AI 分析）、個人化推薦」之外，站在評審、使用者體驗與功能完整性的角度，建議可以從「提升協同便利性」、「加強數據實用性」與「串接外部資源」三個維度，考慮開發以下功能：

1. 視覺化「神隊友分工儀表板」與動態給獎（遊戲化育兒）
你們目前已經做出了很棒的「協助者功能」與權限管理，解決了性別平等（SDG 5）的痛點。但往往伴侶「不知道自己能幫上什麼忙」。

功能概念： 系統根據待辦清單（T16）的完成狀態，產出一個「家庭分工雷達圖」或「貢獻度能量條」。例如：爸爸點選完成了「洗奶瓶」、「換尿布」，就能獲得點數或成就解鎖。

技術實作： 串接現有的 carerecord 表格，統計不同 user_id 在特定期間內完成的任務數量，並在前端以 Chart.js 繪製出趣味的分工圓餅圖或雷達圖。

加分點： 這能讓「點選完成」變成一種樂趣，用數據實質促進家庭和諧與伴侶參與。

2. 語音紀錄自動轉換與分類（極致的語音一站式輸入）
抱著小孩或肚子大起來的時候，打字是非常痛苦的。雖然 LINE 本身可以傳語音，但如果能直接「整合進紀錄」會非常貼心。

功能概念： 媽媽直接對 LINE 官方帳號發送語音訊息：「寶寶今天下午 2 點喝奶 120cc，大便一次，稍微有點稀。」系統自動幫她填好嬰幼兒紀錄。

技術實作： 透過 n8n 接收 LINE 語音檔案，串接 OpenAI Whisper API 進行語音轉文字（STT），再利用大語言模型（LLM）結構化提取關鍵資訊（時間、事件、數值），最後透過 Django 自動寫入 babyrecord（T07）資料庫。

加分點： 在專題Demo時，現場錄音並直接在網頁上看到數據自動填入表格，對評審來說視覺震撼力極強。

3. 產檢與疫苗接種「一鍵行事曆同步」
紙本媽媽手冊和寶寶手冊最實用的功能之一就是「時程提醒」，但現代人常常忘記去看那本本子。

功能概念： 當養育者在 pregnancycase（T03）中輸入最後月經或預產期，或者在 babyinformation（T04）輸入出生日期後，系統自動推算「所有法定產檢週數」與「兒童常規疫苗接種時程」，並提供一個按鈕讓使用者直接匯入手機（Google Calendar 或 Apple Calendar）。

技術實作： 後端利用 Python 寫好固定時程演算法，前端提供一個生成 .ics 檔案的 API 或是 Google Calendar API 的跳轉連結。

加分點： 強化非功能性需求中的「可用性」與「易用性」，真正落實一站式管家的核心價值。

4. 產檢指標異常「紅字預警系統」
你們目前已經規劃了非常詳盡的 prenatalrecord 產檢紀錄表（T13），包含了血壓（sbp/dbp）、尿糖、尿蛋白、浮腫等。

功能概念： 這些數據對新手父母來說只是一堆數字。當使用者輸入產檢數據後，若血壓高於 140/90 mmHg，或者尿蛋白顯示異常，系統畫面不只留存紀錄，還會主動跳出紅字警告，並連動 Growth AI 提示這可能是妊娠毒血症的警訊，建議盡快就醫。

技術實作： 在 Django 後端邏輯寫入條件判斷（If-Else 醫學常規常數上限），當觸發異常時，發送 LINE Notify 或是前端彈出 Modal 警告。

加分點： 扣合 SDG 3（良好健康與福祉），讓系統從單純的「電子筆記本」升級為「主動式健康守護者」。

💡 專案調整小建議
看過你們的資料庫設計，表格結構非常嚴謹，欄位邏輯很清晰！如果決定要擴充上述功能，大部分都不需要大改現有的資料庫架構：

若做功能 1（分工儀表板）：現有的 carerecord 已經有 user_id 和 state（狀態），直接撈資料計算即可。

若做功能 3（行事曆）或功能 4（異常預警）：直接利用 pregnancycase 的日期與 prenatalrecord 的數值做後端運算即可。

你們這組的完成度已經非常高，挑選 1 個最契合你們目前 n8n / AI 工作流的功能來實作（例如功能 2），就能讓專案整體亮點更上一層樓！加油！

你覺得這網站系統還可以新增甚麼小功能?

這份 CoLoGrowth 的專案系統手冊內容已經非常完整且充實，從 LINE Login/Google Login 到 n8n 自動化流程、Supabase RAG 向量資料庫（Growth AI），以及跨足孕期與 0-3 歲嬰幼兒的完整關聯資料庫設計（包含產檢、心情、身體狀況、成長趨勢與里程碑），整體架構相當嚴謹！  
DOCX

如果希望在不大幅動到核心架構、不增加太多開發負擔前提下，新增幾個能「大幅提升使用者黏著度與貼心度」的小功能，可以考慮以下幾個切入點：

1. 產檢與疫苗接種「一鍵匯入手機行事曆」（Calendar Export）
應用場景： 媽媽或伴侶常忘記下一次產檢或寶寶打疫苗的時間。

做法： 系統根據 pregnancycase 中的預產期/最後月經，或 babyinformation 中的出生年月日，自動計算出台灣衛福部規定的 14 次常規產檢週數與 0-3 歲預防針時間表。在畫面上提供一個「匯入行事曆」按鈕，產出 .ics 檔或 Google Calendar API 連結，讓使用者一鍵把提醒加入個人手機行事曆。  
DOCX

優點： 實用性極高，技術成本低（後端純數學計算日期），能直接展現一站式管家的貼心度。

2. 產檢數據「異常指標紅字 Alert」（語意/數值警示）
應用場景： 使用者在填寫 prenatalrecord（收縮壓 sbp、舒張壓 dbp、尿糖、尿蛋白等）時，可能不清楚數字代表的健康意義。  
DOCX

做法： 在前端或後端加入簡單的判斷邏輯（如：血壓 >140/90 mmHg 或尿蛋白為陽性），當數據超標時，系統除了儲存資料外，會在畫面上直接標記黃/紅字警告，並附帶一段溫馨提示（例如：「血壓偏高，建議多休息並諮詢您的婦產科醫師」），同時連動提示可向 Growth AI 詢問相關注意事項。

優點： 扣合系統目標中的 SDG 3（良好健康與福祉），將原本單純的「電子筆記本」升級為具備主動關懷能力的健康監測工具。  
DOCX

3. 「神隊友育兒任務卡」與神助攻提醒（遊戲化分工）
應用場景： 雖然有「協助者權限」與「待辦清單（carerecord）」，但伴侶常不知道自己能幫忙做什麼。  
DOCX

做法： 系統預設一套「新手爸爸/協助者今日任務庫」（如：幫媽媽準備葉酸、記錄今日胎動、清洗奶瓶）。養育者可一鍵指派任務給協助者，當協助者在 LINE 完成勾選時，發送一個歡呼通知或累積「神隊友點數」。

優點： 深入連結 SDG 5（性別平等與共同育兒），讓待辦清單變得更有趣味性與互動感。  
DOCX

4. 成長里程碑「快速生成圖文分享卡」（Social Sharing Card）
應用場景： 爸媽記錄了寶寶第一次翻身、第一次抬頭（babygrowthmap / babyrecord）或上傳超音波照片時，會想發朋友圈或給長輩看。  
DOCX

做法： 當使用者勾選完成某個成長里程碑並上傳照片時，系統提供一個「生成精美小卡」的功能，自動把寶寶暱稱、月齡、里程碑稱號與照片融合成一張微暖色調（馬卡龍色）的排版圖片，讓使用者能一鍵下載或分享到 LINE 聊天室/社交平台。  
DOCX

優點： 極佳的社群傳播效果，能自然為 CoLoGrowth 平台達到口碑行銷與推廣的作用。

5. Growth AI 的「快速常用提問卡（Prompt Chips）」
應用場景： 使用者打開 Growth AI 聊天室時，有時會因為焦慮或不知道如何精準提問而猶豫。  
DOCX

做法： 在聊天介面下方，根據使用者當前的「懷孕週數」或「寶寶月齡」，動態推播 3 個常見問題按鈕（例如孕期第 12 週顯示：「12週推薦補充什麼營養素？」、「這個階段孕吐正常嗎？」）。使用者點擊按鈕即可直接發送提問。

優點： 降低使用者打字的門檻，顯著提升 AI 功能的使用率與互動流暢度。

💡 總結建議
這些小功能大部分都不需要大幅改動現有的資料庫結構，主要是在後端運算邏輯與前端 UI 互動細節上做深化。如果時間有限，建議優先挑選 「行事曆一鍵匯入」 或 「Growth AI 常用提問卡」，這兩者在展示（Demo）與實際使用上都能帶來非常直觀且亮眼的加分效果！  
DOCX

那我想做歷史回顧的話，你覺得要怎麼呈現會比較好?

歷史回顧 常見呈現方式



時間軸（Timeline）：




依小時、日或周串聯碎片化紀錄。



左右滑動快速翻閱過去的日誌軌跡。






回顧牆（Memory

Wall）：




自動把照片或短片依月份與年份彙整。



以多格或卡片式排版一目了然。






年度總結（Year

in Review）：




類似音樂軟體的統計方式。



一鍵生成全年的精華回顧圖與影片。



這邊有參考的

你找的這三個方向（時間軸、回顧牆、年度/階段總結）非常經典且實用！

結合 CoLoGrowth 一站式（從孕期到 0-3 歲）與家庭共享的特性，我建議可以將這三種呈現方式依據「使用頻率」與「情境場景」做組合與細化，呈現效果會最有溫度也最符合使用者習慣：

1. 時間軸（Timeline）：定位為「每日成長軌跡」
對於頻繁記錄身體數據、心情與寶寶日常的使用者來說，時間軸是最好用、最不費力的切入點。

呈現方式設計：
「孕期 ➔ 育兒」雙階段里程碑軸線：
頂部設有錨點標籤（如：孕早期 → 孕中期 → 產檢日 → 出生 → 滿月 → 周歲）。使用者向左右滑動時，不只是看日期，還能看到當時的「懷孕週數」或「寶寶月齡」。

多功能混合卡片：
將手冊中紀錄的資料類型（pregnancyrecord 體重/心情、prenatalrecord 超音波照片、babyrecord 身高體重） 整合在同一條時間軸上，用小圖示（如：🍼 喝奶、❤️ 心情、🩺 產檢）做視覺區隔。  
DOCX

協助者標示：
如果某筆紀錄是伴侶輸入的，卡片角落顯示伴侶的頭像，強調「這是我們一起完成的紀錄」。

2. 回顧牆（Memory Wall）：定位為「視覺化時光相簿」
相較於純文字與數據，爸媽最喜歡看的其實是照片與影音（例如超音波照、第一次抬頭、周歲照）。  
DOCX

呈現方式設計：
瀑布流 / 卡片式九宮格：
自動撈取 photo 欄位有照片的紀錄（如超音波影像、寶寶成長照片），預設以「月份」做大區塊分組（例如：2026年3月 寶寶滿3個月）。  
DOCX

「那年那天」同日對比（Flashback）：
在回顧牆頂部設計一個亮點區塊：「1年前的今天，你在產檢室第一次聽到胎心音」或「半年前的今天，寶寶學會了坐立」，隨機翻出舊照片，增加情感驚喜感（Surprise & Delight）。

3. 階段/年度總結（Year / Phase in Review）：定位為「儀式感週報與精華卡」
類似 Spotify / Apple Music 的年度總結，這部分是社群分享（Social Sharing）與情感共鳴最強的功能。

呈現方式設計：
「孕期畢業典禮」與「成長週歲卡」：
不用一定要等一整年，可以在關鍵節點主動推播：

孕期畢業報告： 當孕婦順利生產、進入育兒期時，生成「40週陪伴報告」（這期間記錄了多少次心情、拍了多少張超音波、體重變化的美麗曲線）。

寶寶 1 歲精華： 彙整過去 12 個月的身高體重成長曲線（growthrecord）與完成的里程碑（babygrowthmap）。  
DOCX

滿滿儀式感的數據統計：

「這一年，爸爸幫忙完成了 128 次育兒待辦事項！」（扣合神隊友/SDG 5）  
DOCX

「這一年，Growth AI 解答了你 35 個孕期小焦慮。」  
DOCX

一鍵導出一頁式圖片 / 短影片：
結合你們專案採用的柔和色調（馬卡龍色系），生成排版極具美感的高畫質圖卡，讓爸媽可以一鍵儲存或直接分享至 LINE 動態與 IG Story。

💡 建議的系統選單架構整合
在 LINE Login 開啟的 Web UI 介面中，歷史回顧可以這樣設計頁面層級：

Plaintext
[歷史回顧頂部 Tab]
 ├── 1. 時光軸 (Timeline)   ➔ 適合快速按日期/週數翻閱日常細節
 ├── 2. 照片牆 (Memory Wall) ➔ 適合純粹欣賞超音波與寶寶精美照片
 └── 3. 成長紀念冊 (Reports)  ➔ 觀看「孕期畢業」或「1歲里程碑」精華卡
這樣設計既能滿足日常數據查詢的實用性，又能滿足溫馨懷舊與社群分享的情感需求！

有辦法製作一張示意圖嗎?

太棒了！針對上面討論的三種歷史回顧呈現方式（時間軸、回顧牆、成長紀念冊），我用 Mermaid 繪圖語法 為你製作了三個介面 layout 的架構示意圖。

這能讓你更直觀地想像畫面排版，也很適合直接截圖放在專題簡報或系統手冊的 UI 設計章節中！

1. 時間軸 (Timeline) 介面示意圖
特點： 頂部有週數/月齡快速切換，中央為縱向時間軸，卡片混合顯示媽媽與寶寶的紀錄，並標示紀錄者頭像。  
DOCX

程式碼片段
graph TD
    subgraph UI_Timeline ["📱 時間軸 (Timeline) 畫面結構"]
        direction TB
        A["[頂部頁籤] 🕒 時光軸 | 🖼️ 相簿牆 | 🎓 紀念冊"]
        B["[階段快選] 孕早期 ➔ 孕中期 ➔ 孕晚期 ➔ 0-6個月 ➔ 6-12個月"]
        
        subgraph Line ["│ 縱向時間軸線 │"]
            direction TB
            C["📅 2026/03/15 (孕期 20 週)<br/>🩺 產檢紀錄：血壓 118/75，寶寶重 320g<br/>📷 超音波照 ｜ 👤 紀錄者：媽媽"]
            D["📅 2026/03/18 (孕期 20 週 +3)<br/>❤️ 今日心情：今天第一次感覺到明顯胎動！<br/>📝 備註：好神奇的感覺 ｜ 👤 紀錄者：媽媽"]
            E["📅 2026/03/20 (孕期 20 週 +5)<br/>✅ 完成待辦：組裝嬰兒床、準備產檢包<br/>💬 留言：老爸搞定囉！ ｜ 👤 紀錄者：爸爸"]
        end
        
        A --> B
        B --> C
        C --> D
        D --> E
    end
2. 回顧牆 (Memory Wall) 介面示意圖
特點： 頂部設有「同日對比」驚喜卡（Flashback），下方依月份將照片以卡片/瀑布流方式擺放。  
DOCX

程式碼片段
graph TD
    subgraph UI_MemoryWall ["📱 回顧牆 (Memory Wall) 畫面結構"]
        direction TB
        A["[頂部頁籤] 🕒 時光軸 | 🖼️ 相簿牆 | 🎓 紀念冊"]
        
        subgraph Flashback ["✨ 那年那天 (Flashback)"]
            B["🎉 1 年前的今天 (2025/07/24)<br/>『第一次聽到寶寶心跳聲 💓』<br/>[📷 點擊放大查看當時超音波照]"]
        end
        
        subgraph Wall ["📸 月份相簿區"]
            C["📅 2026年 7 月 (寶寶 3 個月)"]
            D1["🖼️ 首次抬頭成功"]
            D2["🖼️ 滿月禮拍照"]
            D3["🖼️ 與爸爸合照"]
            
            E["📅 2026年 6 月 (寶寶 2 個月)"]
            F1["🖼️ 打預防針小哭"]
            F2["🖼️ 睡覺萌樣"]
        end
        
        A --> B
        B --> C
        C --> D1 & D2 & D3
        D1 --> E
        E --> F1 & F2
    end
3. 階段/年度總結 (Reports & Review) 卡片示意圖
特點： 滿滿儀式感的數據統計卡片，搭配柔和馬卡龍配色風格，方便一鍵下載或分享至社群平台。

程式碼片段
graph TD
    subgraph UI_ReviewCard ["📱 孕期畢業 / 周歲精華卡 畫面結構"]
        direction TB
        
        subgraph Card ["🌸 柔色馬卡龍風 - 孕期 40 週畢業禮卡"]
            Header["🎓 CoLoGrowth 孕期全紀錄"]
            
            subgraph Stats ["📊 數據亮點"]
                S1["🤰 陪伴天數：280 天"]
                S2["📸 留下珍貴照片：48 張"]
                S3["👨‍👩‍👦 神隊友伴侶參與：156 次待辦"]
                S4["🤖 Growth AI 陪伴解答：42 次疑難雜症"]
            end
            
            Footer["✨ 『辛苦了媽媽，接下來一起陪寶寶長大吧！』"]
            Btn["📲 [一鍵生成圖片 / 分享至 LINE & IG]"]
        end
        
        Header --> Stats
        Stats --> S1 & S2 & S3 & S4
        S1 & S2 & S3 & S4 --> Footer
        Footer --> Btn
    end
💡 專案團隊討論建議
如果在報告或討論時展示：

時間軸 適合強打「資料整合與便利性」（同一頁看齊所有紀錄類型）。  
DOCX

回顧牆 適合強打「情感連結與照片溫存」。  
DOCX

階段總結 適合強打「遊戲化成果、神隊友分工（SDG 5）與社群擴散力」。  
DOCX

這些指令我可以怎麼呈現?

你拿到的這些 Mermaid 繪圖語法（Code Block），在專案報告或實體展示時有非常多靈活且漂亮的呈現方式！

根據你的發表情境（是簡報發表、書面文件、還是團隊討論），以下為你整理最適合的幾種呈現與轉化方式：

1. 轉化為實體 UI / Wireframe 視覺圖（最推薦用於簡報與專題手冊）
Mermaid 語法是用來定義「邏輯與區域結構」的，最直觀的做法是將它轉換為高保真（High-Fidelity）或低保真（Wireframe）的手機介面圖。

使用工具： Figma、Canva、Balsamiq 或 Stitch / Antigravity。  
DOCX

實作方式：

手機框 (Phone Mockup)： 畫一個 iPhone / Android 的外框。

套入配色： 配合你們專案的馬卡龍色系（淡粉、淡綠、溫柔紫）。  
DOCX

按圖擺放：

頂部放入 時光軸 | 相簿牆 | 紀念冊 的切換按鈕 (Tab bar)。

中間依據 Mermaid 裡寫的區域（如：縱向軸線、九宮格相簿、數據卡片）放上文字、卡片背景與圖示（🍼, 🩺, 📸）。

效果： 評審和老師能一眼看懂這是一個真實可運作的 App / Web 畫面。

2. 直接渲染成網頁互動式流程圖（適合團隊內部討論與 GitHub 文件）
如果你想在 GitHub README、Notion 專案頁面 或 簡報 中直接顯示這種區塊關係圖：  
DOCX

使用線上渲染工具：

開啟 Mermaid Live Editor。

把程式碼貼進去，右邊就會自動生成漂亮的向量架構圖。

可以直接導出為 PNG、SVG 圖片貼進 Word 系統手冊或 PowerPoint。  
DOCX

Notion / Markdown 支援：

在 Notion 或支援 Markdown 的編輯器中，輸入 /mermaid 或使用 ```mermaid 程式碼區塊，將語法貼入，頁面就會直接動態渲染出圖表。

3. 簡報發表時的「分步動畫呈現」（PPT / Keynote 技巧）
如果在進行專題提報或系統 Demo 時，不要一次把一整張圖丟出來，建議利用動畫層層遞進：

頁面 1（總覽）： 先展示手機外框與頂部切換 Tab（時光軸 / 相簿牆 / 紀念冊）。

頁面 2（細節拆解 - 以時間軸為例）：

動畫點擊「時光軸」→ 展開縱向時間線。

強調特色標籤：「媽媽記錄了產檢」、「爸爸完成了待辦」，展示家庭共享概念。  
DOCX
+ 1

頁面 3（亮點卡片 - 以階段總結為例）：

點擊「孕期畢業」→ 彈出一張漂亮的成果圖卡（包含陪伴天數、神隊友參與次數）。  
DOCX

💡 總結建議呈現搭配表
呈現情境	建議使用的呈現方式	工具推薦
專題系統手冊 (Word/PDF)

  
DOCX

轉化為柔色調的高保真 UI 設計圖 (Wireframe)	
Figma / Canva  
DOCX

評審簡報 (PowerPoint)

  
DOCX

手機 Mockup 圖 + 數據亮點卡片排版	
PPT / Canva  
DOCX

GitHub / Notion 文件

  
DOCX

直接渲染 Mermaid 程式碼區塊為 SVG 圖檔	
Mermaid Live Editor  
DOCX

組內工程師溝通	保留原始 Mermaid 語法或流程關係圖	
Notion / PlantUML  
DOCX

我想要設定antigratity skills 可以讓我順利製作專題的專案，你可以幫我寫一份完整的SKILL.md的內容嗎?

Your Markdown (SKILL.md) file is ready

「MD」圖示
SKILL
 MD 
開啟
這份 SKILL.md 是專門為你在 Antigravity / Agentic IDE 中開發 CoLoGrowth 專案所客製化設定的技能定義檔，已整合以下關鍵要素：

📌 技能設定核心重點：
專案規格與情境對齊：完整收錄專案目標、三大 SDGs 目標（SDG 3, 4, 5）及核心使用者角色（養育者、協助者）。  
DOCX

精準技術棧規範：包含 Python / Django 後端架構、Supabase PostgreSQL + pgvector 向量檢索、n8n 工作流程自動化與 Tailwind CSS (馬卡龍柔和粉/綠/紫配色) 規範。  
DOCX

14 張資料庫實體表字典 (Schema)：直接寫入 userprofile、pregnancycase、babyrecord、prenatalrecord、docs_vectors 等標準欄位型態與 PK/FK 關聯，避免 AI 在生成 Model、SQL 或 API 時產生幻覺或欄位不一致。  
DOCX

開發與文檔標準：要求 AI 隨時遵循北商資管專題手冊規格，並具備輸出標準 Django ORM、n8n Webhook 處理邏輯及 UML (PlantUML / Mermaid) 圖表的能力。  
DOCX

你可以將此檔案放置於專案根目錄的 .antigravity/skills/ 或相應的技能資料夾中，即可讓 AI Agent 在後續編碼與撰寫文件時自動進入 CoLoGrowth 的專屬開發模式！




Gemini 是 AI，有時可能會出錯。

---
name: cologrowth-project-assistant
description: "Specialized assistant for developing, designing, and maintaining the CoLoGrowth (一站式孕產育兒管理系統) graduation project. Enforces Django backend standards, Supabase DB & pgvector integration, n8n workflow orchestrations, LINE Login/Bot interactions, Tailwind CSS/HTML frontend styling with macaron/pastel aesthetics, and UML/System Manual documentation standards."
---

# CoLoGrowth Project Assistant Skill (`SKILL.md`)

## 1. Project Overview & System Context
* **Project Name**: CoLoGrowth (一站式孕產期與嬰幼兒成長管理系統)
* **Target Audience**: Expecting mothers, partners/helpers (協助者), and caregivers managing pregnancy through infant stages (0–3 years).
* **Core Values & SDGs**:
  - **SDG 3 (Good Health & Well-being)**: Comprehensive tracking of maternal prenatal metrics (`prenatalrecord`), mood/symptoms, and infant growth curves (`babyrecord`).
  - **SDG 4 (Quality Education)**: RAG-driven knowledge assistant (`Growth AI`) backed by verified pediatric/obstetric health data.
  - **SDG 5 (Gender Equality)**: Helper co-parenting role assignment, shared tasks (`carerecord`), and partner engagement tracking.

---

## 2. Technical Stack & Architectural Rules

### 2.1 Backend Architecture
* **Language & Framework**: Python 3.10+, Django Framework.
* **Database**: Supabase (PostgreSQL with `pgvector` extension for RAG embeddings).
* **Workflow Automation & Agent Layer**: **n8n** for handling webhook events from LINE, triggering RAG embeddings, and interacting with OpenAI API / LangChain / RAG endpoints.
* **Authentication**: LINE Login API & Google OAuth2.

### 2.2 Frontend & UI/UX Standards
* **Framework / Styling**: HTML5, CSS3, JavaScript (ES6+), **Tailwind CSS**.
* **Responsive Design**: Mobile-First Responsive Web Design (RWD) optimized for LINE in-app browser (LIFF) and mobile viewports.
* **Color Palette & Visual Tone**:
  - **Primary Colors**: Soft pastel & macaron hues (柔和馬卡龍色系 — light lavender `#E8E0F0` / primary purple `#8E72A7`, light pink `#FCE7EC`, soft mint green `#E2F3ED`, gentle cream `#FDFBF7`).
  - **Contrast & Text**: Clear slate grey / black text for readability. Avoid harsh neon colors.
  - **Layout**: Clean cards, rounded corners (`rounded-2xl`), subtle shadows (`shadow-sm` / `shadow-md`), and mobile-friendly touch targets (min 44px height).

---

## 3. Database Schema & Models Reference

When generating SQL, Django models, or migration scripts, strictly adhere to the project metadata definitions:

1. **`userprofile` (T01)**: `user_id` (PK, int), `line_id` (varchar 100, unique), `email` (varchar 100, unique), `avatar` (varchar 255), `name` (varchar 20), `birthday` (date), `create_time` (datetime).
2. **`familymember` (T02)**: `familymember_id` (PK), `pregnancycase_id` (FK), `user_id` (FK), `role` (varchar 5), `join_time` (datetime).
3. **`pregnancycase` (T03)**: `pregnancycase_id` (PK), `user_id` (FK), `menstruation` (date), `expecteddate` (date), `code` (varchar 10, unique invite code), `create_time` (datetime).
4. **`babyinformation` (T04)**: `baby_id` (PK), `pregnancycase_id` (FK), `name` (varchar 20), `birthdaytime` (datetime), `baby_height` (float), `baby_weight` (float), `babyheadcircumference` (float), `chestcircumference` (float), `production_method` (varchar 4).
5. **`babygrowthmap` (T05)**: `babygrowthmap_id` (PK), `timecourse` (int), `growthrecord` (varchar 50).
6. **`babystatus` (T06)**: `babystatus_id` (PK), `babyrecord_id` (FK), `babygrowthmap_id` (FK).
7. **`babyrecord` (T07)**: `babyrecord_id` (PK), `baby_id` (FK), `date` (date), `record` (text), `weight` (float), `height` (float), `headcircumference` (float), `chestcircumference` (float), `photo` (varchar 255), `update_time` (datetime).
8. **`pregnancyrecord` (T08)**: `pregnancyrecord_id` (PK), `user_id` (FK), `check_date` (date), `record` (text), `weight` (float).
9. **`feeling` (T09) & `userfeeling` (T10)**: Feelings dictionary (`feeling_id`, `feeling_name`) and mapping to `pregnancyrecord_id`.
10. **`physicalcondition` (T11) & `userphysicalcondition` (T12)**: Symptoms dictionary (`physicalcondition_id`, `physicalcondition_name`) and mapping to `pregnancyrecord_id`.
11. **`prenatalrecord` (T13)**: `prenatalrecord_id` (PK), `user_id` (FK), `sbp` (int), `dbp` (int), `fetal_heart_rate` (int), `urine_glucose` (varchar 4), `urine_protein` (varchar 4), `edema` (varchar 4), `photo` (varchar 255).
12. **`qaconversation` (T14) & `qamessage` (T15)**: Multi-turn chat session (`qaconversation_id`, `title`) and messages (`serno`, `role`, `message`, `create_time`).
13. **`carerecord` (T16) & `carestatus` (T17)**: Care tasks/todo items (`carerecord_id`, `user_id`, `carestatus_id`, `record_time`, `content`, `state` [boolean]).
14. **`docs_vectors` (T18)**: Supabase vector store (`id`, `content` [text], `metadata` [jsonb], `embedding` [vector]). Model: `text-embedding-3-small`.

---

## 4. Development Workflow Guidelines

### 4.1 Django Code Guidelines
* All view logic should be modularized into apps (e.g., `users`, `pregnancy`, `baby`, `ai_agent`, `tasks`).
* Use Django REST Framework (DRF) serializers or standard Django JSON responses where API communication with n8n/frontend is required.
* Ensure database transactions (`transaction.atomic`) when modifying multiple relational tables (e.g., creating a baby + milestone mapping).

### 4.2 n8n & RAG Workflows
* Webhooks from LINE Bot should parse text/voice/images, perform token validation, and route to corresponding n8n nodes.
* RAG queries must execute vector similarity search on `docs_vectors` using Supabase RPC functions (`match_documents`) before feeding context to OpenAI models.

### 4.3 Documentation & UML Standards
* Keep all UML diagrams (Use Case, Activity, Sequence, Class, Component, Deployment, State) consistent with the 14 database tables and user roles (`養育者`, `協助者`).
* Generate PlantUML or Mermaid syntax whenever architectural or flow changes are discussed.

---

## 5. Tone & Personality
* **Role**: Senior Full-Stack Technical Mentor & IM Project Specialist.
* **Tone**: Professional, encouraging, highly structured, adhering strictly to information management graduation project standards (國立臺北商業大學 資訊管理系專案規格).
* **Language**: Traditional Chinese (繁體中文 - 台灣) for explanations, documentation, and comments.
SKILL.md
目前顯示的是「SKILL.md」。