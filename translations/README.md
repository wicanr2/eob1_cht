# EOB1 中文化翻譯內容索引

此目錄收錄所有中文翻譯內容 + 對應原文的摘要 (短描述/分類)，做為 ScummVM 引擎 KYRA.DAT / 自製覆寫檔 (TEXT.DAT) 的內容來源。

> 註：基於版權考量，**原文完整段落不收錄於此 repo** — 玩家需要持有合法的 EOB1 安裝 (Steam Forgotten Realms: The Archives - Collection One 或同等)。本目錄只放**我們的中文翻譯**與**摘要分類**。

## 翻譯類別總覽

| 類別 | 檔案 | 條目數 | 來源 | 狀態 |
|---|---|---|---|---|
| CharGen 介面字串 | (KYRA.DAT internal) | ~30 | static resources | ✅ 全翻 |
| 物品名稱 (95 個) | [items.md](items.md) | 95 | EOBDATA6.PAK/ITEM.DAT | ✅ 全翻 |
| NPC 對話 / 文件 / 謎語 | [dialogue.md](dialogue.md) | 51 | EOBDATA3.PAK/TEXT.DAT | ✅ 全翻 |
| LEVEL.INF 動作訊息 | [level_messages.md](level_messages.md) | ~30 (短的) | EOBDATA3-6.PAK/LEVEL*.INF | 🚧 部分 (僅長度可塞 in-place) |
| 字體 (中文字模) | [../win64-build/game/ceob.pat](../win64-build/game/ceob.pat) | 12,811 glyphs | EOB2 CHINFONT.FNT 改造 | ✅ ship |

## 工具鏈

| 工具 | 功能 | 執行環境 |
|---|---|---|
| [extract_item_names2.py](../tools/extract_item_names2.py) | 從 EOBDATA6.PAK 抽 95 物品 EN 名 | WSL python3 |
| [gen_item_names.py](../tools/gen_item_names.py) | EN+ZH item 對照 → C array (Big5 encoded) | WSL python3 |
| [dump_text_dat.py](../tools/dump_text_dat.py) | 從 EOBDATA3.PAK 抽 TEXT.DAT 並解析 51 條對話 | WSL python3 |
| [gen_text_dat_v2.py](../tools/gen_text_dat_v2.py) | 重生 TEXT.DAT 含全中文 (51 條) | WSL python3 |
| [scan_level_inf.py](../tools/scan_level_inf.py) | 掃描 LEVEL*.INF 內的 ASCII 字串 | WSL python3 |
| [build_ceob_combined.py](../tools/build_ceob_combined.py) | 重生 ceob.pat 16×12 字模 | WSL python3 |

## 為什麼 translations/ 跟 tools/ 都用 WSL python3?

Windows Defender / AV 對「讀寫 EXE / 遊戲二進位檔案的 Python 腳本」常啟動 heuristic scan，可能誤判為威脅 (binary patching, packer-like behaviour)。

**Workaround**: 所有翻譯與打包工具都在 WSL Ubuntu-22.04 內跑:
```bash
wsl.exe -d Ubuntu-22.04 -- python3 /mnt/d/03_game_tmp/eob1_cht/tools/gen_text_dat_v2.py
```

腳本本身放 `D:\` (Windows 可見)，跑在 WSL (Windows AV 不掃)。輸入/輸出走 `/mnt/d/` 兩邊都看得到。Python 3.10 預設含 cp950 codec。

## 翻譯原則

1. **AD&D 2e 中文化慣例**: 沿用 1990s 中文 D&D 圈標準譯名 (e.g. 戰士/法師/牧師/盜賊；長劍/短劍/長弓)
2. **專有名詞 (Westwood IP)**: NPC 名 (Armun / Xanathar / Shindia / Tod / Beohram 等) 保留原文音譯
3. **地名**: 知名地名翻譯 (Waterdeep → 水深市)
4. **遊戲術語**: 簡潔 (擲鏢 vs 短矛投擲)，符合 36px 寬螢幕版面
5. **長度限制**:
   - 物品名 35 bytes max (cp950 17 字以內)
   - LEVEL.INF action messages 必須 ≤ 原文 bytes (in-place patch 不能擴張)
6. **語體**: 對話用文言/通俗混合 (符合奇幻 RPG 1991 原作氛圍)；UI / 訊息用現代簡潔白話
