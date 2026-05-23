# kSpecial=5 ChineseFan 變種 — 設計文件

目的: unblock EOB1 ZH 物品名 / 怪物名 / intro narration 中文化。詳細背景見 [docs/future-work.md](../docs/future-work.md#15) §1.5。

> 撰寫日期: 2026-05-23
> Owner: claude (本 session)
> Status: **設計階段** — 待 iter2 tester 驗證 BUG-003 後再執行

## 為什麼需要

目前 EOB1 ZH 走 `kNoSpecial` (= 0)，與 EN/DE/IT 共用同一個 `eob1FloppyNeed[]` need-list。把 `kEoB1ItemNames` 加進 need-list 會 break EN/DE/IT build。所以中文翻譯被困在 PAK overlay 內無法取代。

引入 `kSpecial=5 kChineseFan` 讓 EOB1 ZH 走獨立 need-list，加 string 不影響其他語言。

## 牽涉的 codebase 區塊

### A. KYRA.DAT 建構工具側 (`devtools/create_kyradat/`)

| 檔案 | 改動 |
|---|---|
| `create_kyradat.h:1184` | enum `kSpecial` 加 `kChineseFan = 5` |
| `games.cpp:130` | EOB1 ZH 條目 `kNoSpecial` → `kChineseFan` |
| `games.cpp` (新) | 新增 `eob1ChineseFanNeed[]` (superset of `eob1FloppyNeed[]`) |
| `games.cpp:4635` 附近 | 新增 `{kEoB1, kPlatformDOS, kChineseFan, eob1ChineseFanNeed}` 至 `gameNeedTable` |
| `resources.cpp:~2014-2620` | 補 `{kEoB1IntroStringsTower/Orb/...}` 等 ZH_TWN 版本 provider |
| `eob1_dos_chinese.h` (新增 array) | 新增 `kEoB1IntroStringsTowerDOSChinese[]` `kEoB1IntroStringsOrbDOSChinese[]` `kEoB1ItemNamesDOSChinese[]` ... 等 |

### B. ScummVM 引擎側 (`engines/kyra/`)

兩個替代方案 — **強烈建議 B2**:

**B1. 結構改 (高入侵)**:
- `detection.h:50` GameFlags 加 `bool isChineseFan : 1;`
- `detection_tables.h:26` FLAGS macro 加參數
- 32 個 `FLAGS(...)` 全部加 `false,`
- 新增 `EOB_FLAGS_CHINESE_FAN` macro
- `detection_tables.h:2009` EOB1 ZH 條目 `EOB_FLAGS` → `EOB_FLAGS_CHINESE_FAN`
- `staticres.cpp:123` getSpecialID 加 `if (flags.isChineseFan) return 5;`

**B2. 最小入侵 (建議)**: 不動結構，純依靠 lang+gameID 推斷:
```cpp
// staticres.cpp:123
byte getSpecialID(const GameFlags &flags) {
    if (flags.gameID == GI_EOB1 && flags.lang == Common::ZH_TWN)
        return 5;
    if (flags.isOldFloppy)
        return 4;
    // ... rest unchanged
}
```
只動一個檔一個函式，零 macro 變動，無 detection_tables 漣漪。

唯一 trade-off: 邏輯把「kChineseFan = EOB1 + ZH_TWN」hard-code 進 engine。但 EOB1 沒其他 ZH_TWN 變種，且 ScummVM 既有 codebase 內這種 lang-based heuristic 滿坑滿谷 (例如 `text_rpg.cpp:39` 直接 lang check 設 `_isChinese`)，不違反 codebase 慣例。

## 實際的 strings 內容工作量

需新增 ZH 翻譯的 string ID (參考 [eob1FloppyNeed](../scummvm-source/devtools/create_kyradat/games.cpp#L1451)):

| String ID | 大小 | 翻譯難度 |
|---|---|---|
| kEoB1IntroStringsTower | ~10 段中等長度 narration | 高 (劇情) |
| kEoB1IntroStringsOrb | ~6 段 | 中 |
| kEoB1IntroStringsWdEntry / King / Hands / WdExit / Tunnel | 各 3-8 段 | 中 |
| kEoB1ItemNames | ~96 items | 中 (物品名) |
| kEoB1ItemInventoryStrings? | TBD | 待確認在 PAK 內 |
| kEoB1MainMenuStrings | 已翻 | — |

iter1 EXE-patch 路線的 `full_patches.json` 已含 402 條翻譯，其中可能涵蓋 intro 段落。需 cross-check。

## 執行步驟 (順序)

### Phase 1: 純基礎建設 (零內容)
1. `create_kyradat.h` 加 `kChineseFan`
2. `staticres.cpp` getSpecialID 加 EOB1+ZH_TWN 分支
3. 重 build engine — 應該沒變化 (沒有 special=5 的資源)
4. 跑 tester smoke test 確認沒 regression

### Phase 2: 加 need-list + 一個 provider (drycheck)
5. `games.cpp` 加 `eob1ChineseFanNeed[]` = `eob1FloppyNeed[]` + `kEoB1ItemNames`
6. `games.cpp` 加 gameNeedTable 條目
7. `resources.cpp` 加 `{kEoB1ItemNames, kEoB1, kPlatformDOS, kChineseFan, ZH_TWN, &kEoB1ItemNamesDOSChineseProvider}` (用空 array placeholder 或 alias 到 EN provider)
8. `eob1_dos_chinese.h` 加 `kEoB1ItemNamesDOSChinese[]` (先放英文 fallback)
9. 重 build KYRA.DAT，重 build engine
10. tester 跑 — 確認物品名顯示英文 (因為內容是英文 placeholder)，**但走的是新 special=5 路徑**

### Phase 3: 真的填中文
11. 翻譯 96 個物品名，填入 `kEoB1ItemNamesDOSChinese[]`
12. 重 build KYRA.DAT
13. tester 看物品名是否中文化

### Phase 4: 同樣節奏處理 intro narration
14. 加 `kEoB1IntroStringsTower/Orb/...` 到 need-list
15. 加 providers + arrays (英文 placeholder)
16. 翻譯 + 替換

## 風險

- **存檔相容**: 加新 string 不影響存檔格式，安全
- **PAK 資源**: 若引擎仍 fallback 讀 PAK，need-list 加 string 後可能繞過 PAK 完全讀 static — 須確認 fallback 路徑
- **特定 string 不存在於 static 而只在 PAK**: 例如 `LEVEL*.INF` 內 NPC 對話 — 這條路徑無法用 kChineseFan unblock，需另解 PAK
- **iter2 BUG-003 fix 若失敗** (`drawButton` Chinese 路徑對 EOB1 button 不適用): 應先 revert/調整再執行此 phase

## 看板狀態

- Phase 1: ✅ design done, enum kChineseFan added then reverted (clean state)
- Phase 2: ❌ **attempted 2026-05-23 reverted** — see "Lessons learned" below
- Phase 3: pending — 需翻譯內容 + 重新設計 Phase 2
- Phase 4: pending — 需翻譯內容

## Lessons learned (Phase 2 atomic flip 嘗試 2026-05-23)

實際 flip 步驟:
1. ✅ `staticres.cpp:123` getSpecialID 加 `if (EOB1 && ZH_TWN) return 5` (Plan B2 minimal)
2. ✅ `create_kyradat.h` enum kSpecial 加 `kChineseFan = 5`
3. ✅ `create_kyradat.cpp specialTable[]` 加 `{kChineseFan, 5}` entry (encoding byte)
4. ✅ `games.cpp:130` eob1Games[ZH_TWN] `kNoSpecial` → `kChineseFan`
5. ✅ `games.cpp:4635` gameNeedTable 加 `{kEoB1, kPlatformDOS, kChineseFan, eob1FloppyNeed}`
6. ✅ `resources.cpp` sed-replace 90 個 `kEoB1, kPlatformDOS, kNoSpecial, ZH_TWN` → `kEoB1, kPlatformDOS, kChineseFan, ZH_TWN`
7. ❌ **KYRA.DAT 生成失敗**: `ERROR: Could not find need 149 for game 305A`

## 為什麼失敗

resource lookup encoding = `(game<<24)|(platform<<20)|(special<<16)|(id<<4)|lang`。對於需 149 (e.g. kEoB1MainMenuStrings)，其 provider 註冊為 `kEoB1, kPlatformDOS, kNoSpecial, UNK_LANG` (lang-agnostic resource，e.g. CGA mapping tables / monster stats)。

當 game tuple `{kEoB1, DOS, kChineseFan, ZH_TWN}` 查需 149:
- 計算 filename = `3:0:5:0095:0` (special=5)
- 但 provider 註冊 filename = `3:0:0:0095:0` (special=0)
- 不匹配 → findEntry 失敗 → ERROR

## 規模量化

`grep "kEoB1, kPlatformDOS, kNoSpecial" resources.cpp` = **161 個 UNK_LANG providers** + 90 ZH_TWN providers = 251 entries 都要處理才能完整 wire 起來。

## 可行的 Plan B 修訂 (未來 attempt)

**方案 B3**: 不動 ZH_TWN tag 也不動 EOB1+DOS providers，改在 `outputAllResources` / lookup 加 fall-through:
- 如果 `(game, platform, kChineseFan, lang)` 找不到 → 退回 `(game, platform, kNoSpecial, lang)`
- 程式碼改 ~10 行，但要謹慎處理 hash key
- 對既有 EOB2 ZH (kNoSpecial+ZH_TWN) 不影響

**方案 B4**: duplicate 161 個 UNK_LANG providers 加 kChineseFan 條目，保留原 kNoSpecial 條目給 EN/DE/IT。
- 161 + 90 ZH_TWN + extra = ~250 entry edits
- 機械操作，但檔案膨脹 ~5K lines

**方案 B5 (最簡)**: 不做 kSpecial=5。改在 `eob1FloppyNeed` 加 `kEoB1ItemNames`。EN/DE/IT 需要新加 DOS provider (目前只有 PC98 + SegaCD)。
- 新增 4 個 provider: kEoB1ItemNamesDOSEnglish (從 PAK 抽出) / DOSGerman / DOSItalian / DOSChinese
- 每個 ~96 item names
- 需要從原版 EOB1 PAK 抽出 EN item name table 作 base

## 結論

Phase 2 atomic flip **比 design 預期複雜很多**。Plan B5 (per-resource opt-in) 比 Plan B (kSpecial=5) 更實際 — 一次只加一個資源，可獨立驗證。**Phase 2 + 3 + 4 都暫停**，未來資源增加用 Plan B5 漸進式。

## 已驗證 reverted state

- Source 全部 revert (engine + devtools 都還原)
- KYRA.DAT 重新生成 byte-level diff 390 bytes (不明原因，懷疑是 build artifact 或 hash map order)，**為了 portable bundle 不冒險，從 /root/eob1cht/ iter1 backup 還原 KYRA.DAT 到 game/**
- scummvm.exe rebuild from reverted source → SHA `444f3835e3e8a935821897bc70121f4d3a42bfaaf713c55861a32b03d87592aa` (Fix A/B/C/D/E intact)
