# Build applied — iter6 (2026-05-23 ~17:50)

User 玩到深處發現 4 個新 issue (見 user screenshots 4 連發):
1. 物品名 (Short sword) — content gap, PAK ITEM.DAT
2. 法術 panel 字形大小不一致 — font slot bug
3. 動作訊息 (als nothing.) — content gap, LEVEL.INF
4. 文件 (Commission and Letter of Marque) — content gap, LEVEL.INF

User 要求 1+2+3 (跳過 #4 LEVEL.INF 大坑 留給未來)。並行 spawn UX designer agent 處理另一個 user 早報的 in-game 角色資訊 panel 縱向堆疊 bug (本檔稱 Fix I)。

## Fixes applied

### Fix H — issue #2: 法術 panel `_bookFont` 漏設

- **File**: `scummvm-source/engines/kyra/engine/eobcommon.cpp:615`
- **Root cause**: `_bookFont = FID_6_FNT` 是 eobcommon.cpp:202 默認 init。ZH 分支只把 `_titleFont/_conFont/_invFont2/_invFont4` 設成 FID_CHINESE_FNT，**漏了 _bookFont**。法術 panel `gui_drawSpellbook()` (gui_eob.cpp:687) 用 `setFont(_bookFont)` → ZH 走 6-tall slot 渲染 15-tall CJK → 字看起來細小不一致 (酸液箭 vs 可用法術/清空/離開)。
- **Edit**: 加 `_bookFont` 到 FID_CHINESE_FNT 鏈
  ```diff
  -    _titleFont = _conFont = _invFont2 = _invFont4 = Screen::FID_CHINESE_FNT;
  +    _titleFont = _conFont = _invFont2 = _invFont4 = _bookFont = Screen::FID_CHINESE_FNT;
  ```
- **Reference**: `kyra_hof.cpp:146` 同 engine 對 _bookFont ZH 已正確設，EOB 漏了
- **Risk**: 低 — 純 font slot 補洞，EOB1+EOB2 ZH 都受惠
- **Verify**: 開法術選單 (memorize 或 spell book) 看 spell name 與 title/button 字體大小一致

### Fix I — in-game 角色資訊 panel layout

- **Designer doc**: `design-reviews/character-info-layout-design.md` (UX agent 寫的完整 design review)
- **Root cause**: `EoBEngine::guiSettings()` (eob.cpp:1277-1288) 沒 ZH branch → ZH 走 `_guiSettingsVGA`，`statsPageCoords` 的 `YInc=7` + `group2X = group1X = 183` → 15-tall CJK 完全堆疊。EOB2 `DarkMoonEngine` 早有 `_guiSettingsDOS_ZH` + ZH branch (上游 ship 7+ 年)。Pattern 同 Fix B/D/E/G — EOB1 ZH 從未 wire up。
- **Files** (3 處):
  - `engines/kyra/engine/eob.h:247-248`: declare `static const KyraRpgGUISettings _guiSettingsVGA_ZH;`
  - `engines/kyra/resource/staticres_eob.cpp:1704+`: define `_guiSettingsVGA_ZH` (~20 lines)。clone _guiSettingsVGA 大部分結構，**只覆寫 statsPageCoords** 借 EOB2 _guiSettingsDOS_ZH 數字
  - `engines/kyra/engine/eob.cpp:1284`: 加 `else if (_flags.lang == Common::ZH_TWN) return &_guiSettingsVGA_ZH;`
- **statsPageCoords 變化**:
  - YInc 7 → 15 (容 16x15 CJK glyph)
  - group2 X 183 → 261 (敏/體/魅 移到右 col)
  - group2 stat X 275 → 300
  - AC row 移 Y=84
  - exp/level row 移 Y=51 (改放最頂)
  - class XInc 0 → 38 (橫排 3 class)
- **Risk**: 低 — 只影響 `_currentControlMode == 2` (角色資訊 panel)，inventory mode 1 + spellbook + 戰鬥畫面不受影響
- **statsPageColors**: 保留 EOB1 VGA 原配色 (`{15, {12,12,12}, ...}`)，未切 EOB2 ZH 配色，conservative
- **Verify**: 進遊戲點 portrait → 進入角色資訊 panel → 6 個 stat 應該排成 2 col × 3 row (像 chargen Fix A) — 力/敏 智/體 慧/魅 + 防/命/級/AC/exp 區可讀

## Deferred — Issue #1 (物品名 Plan B5)

不在本 iter scope。需要的工作:
1. **PAK 抽取**: 從 EOBDATA*.PAK 抽 ITEM.DAT EN names (96 個)，需要 Westwood PAK reader (上游 ScummVM `getItemDefinitionFile` 已有 reader code 可借)
2. **EN DOS provider**: `resources.cpp` + `eob1_dos_english.h` 加 `kEoB1ItemNamesDOSEnglish[]`
3. **ZH DOS provider**: `eob1_dos_chinese.h` 加 `kEoB1ItemNamesDOSChinese[]` (96 條翻譯)
4. **DE/IT DOS providers**: optional — 若 EOB1 DE/IT PAK item names = EN (沒在地化)，可省。否則同 #1 抽 4 lang
5. **need-list**: `eob1FloppyNeed[]` 加 `kEoB1ItemNames`
6. **build + verify**: KYRA.DAT regen，遊戲內驗證 EN 玩家看到原英文，ZH 玩家看到中文

**估計**: 0.5 day 抽 + 1 day 翻譯 96 條 = **1.5 工作天**，不適合塞進 iter6。

## Deferred — Issue #3, #4 (LEVEL.INF 內容)

`LEVEL*.INF` 內 NPC 對話 + 文件文字 (Commission and Letter of Marque 等) 在 PAK 壓縮內。要解 Westwood PAK encoder/decoder (上游 ScummVM 有 decoder 但沒 encoder) → 翻譯 → 重 pack。

**估計**: 1+ 週工程級，是 milestone 級工作。

## Build status

| Target | Status | SHA-256 |
|---|---|---|
| Linux | OK (Fix H + Fix I) | rebuilt 17:45 |
| Windows (`win64-build/scummvm.exe`) | OK | `db4b583220454bccddd72141cbc499539d28151c755195b18268eaa66ce1c0ff` (Fix A/B/C/D/E/F/G/G2/H/I) |
| KYRA.DAT | unchanged | `fa2a8225...` (iter1 baseline) |

## 給 next iter / future

iter7 候選 (難度排序):
1. **Plan B5 Issue #1 物品名 (1.5 day)** — 從 PAK 抽 EN + 翻 96 條中文 + 加 4 個 DOS provider。是 user 最直觀感受到「中文化完整度」的指標
2. **BUG-009 CAMP `營：`** — 仍是 layout trade-off，需 design round (詳 bug-009-analysis.md)
3. **BUG-014 動作按鈕擋 `級`** — Fix A 副作用，需 col 2 X 調整或 button position 重設計
4. **BUG-005/006/010 字模 glyph** — ceob.pat 重生 (tools/build_ceob_combined.py 調 subset)
5. **LEVEL.INF 大坑 (1+ 週)** — Westwood PAK encoder + 翻譯 NPC 對話/文件

User 直觀感受角度，**Issue #1 物品名最值得做**，但工作量也大。
