# In-game 角色資訊 panel 中文 layout 設計 (Fix H 提案)

**Status**: design review, awaiting dev hand-off
**Date**: 2026-05-23
**Owner**: ux-designer subagent
**Severity**: high (panel 不可用 — 屬性無法判讀)
**Code path**: `engines/kyra/gui/gui_eob.cpp` `EoBCoreEngine::gui_drawCharacterStatsPage()`

---

## 1. 問題

### 症狀 (from user screenshot, win64-build 已套用 Fix A~G2)

User 在 in-game 點 portrait → 進入「角色資訊 panel」(`_currentControlMode == 2`)：

- 標題「角色資訊」黃色 (正常，已修)
- 中間 6 個 stat label (力/智/慧/敏/體/魅) **全部縱向疊在同一個 column**，黑色 shadow 連成一團
- 右側 6 個 stat 數值 (15/14/12/?/6/8) 也是縱向疊
- 底部 class label + XP 5000 + 鍵 button + 6 方向箭頭區，這部分視覺較鬆但仍縱排
- 整個 panel 寬度只用了 panel 右上角約 50px 寬，把所有 stat 擠在一行

→ **6 個 label 完全堆疊 + 6 個數字完全堆疊 → 完全無法閱讀**

### 對比：CharGen stats (Fix A，已 ship 且乾淨可讀)

`chargen.cpp::printStats()` 在 `_flags.lang == ZH_TWN` 走 line 1307~1338 的 inline ZH branch：
```cpp
// 2-col, 3-row layout
for (int i = 0; i < 6; i++)
    _screen->printShadedText(_chargenStatStrings[i],
        165 + (i / 3) * 75,   // X = 165 or 240 (col)
        64 + 16 * (i % 3),    // Y = 64/80/96 (row)
        ...);
```

→ 力/智/慧 @ X=165 Y=64/80/96；敏/體/魅 @ X=240 Y=64/80/96。**16px 行距能容納 16x15 BIG5 glyph**.

---

## 2. Root cause (RE 已定位)

### Path mapping

`gui_drawCharPortraitWithStats()` (gui_eob.cpp L99) →
  `_currentControlMode == 2` branch (L244-248) →
    `gui_drawCharacterStatsPage()` (L602-657)

該函式所有座標都讀自 `guiSettings()->statsPageCoords` (struct `KyraRpgGUISettings::StatsPageCoords`, kyra_rpg.h L166-202).

### Settings selector (smoking gun)

`engines/kyra/engine/darkmoon.cpp` L790-801 (EOB2):
```cpp
const KyraRpgGUISettings *DarkMoonEngine::guiSettings() const {
    ...
    else if (_flags.lang == Common::ZH_TWN)
        return &_guiSettingsDOS_ZH;        // ★ EOB2 有 ZH branch
    else
        return &_guiSettingsDOS;
}
```

`engines/kyra/engine/eob.cpp` L1277-1288 (EOB1):
```cpp
const KyraRpgGUISettings *EoBEngine::guiSettings() const {
    if (_flags.platform == Common::kPlatformAmiga) ...
    else if (... CGA / EGA) return &_guiSettingsEGA;
    else if (... PC98) return &_guiSettingsPC98;
    else if (... SegaCD) return &_guiSettingsSegaCD;
    else
        return &_guiSettingsVGA;            // ★ EOB1 沒 ZH branch → fallback 英文 VGA
}
```

**繼承 Fix B/D/E/G 完全同一個 pattern：EOB2 ZH 上游 ship 多年，EOB1 ZH 從未被 wire up**.

### Layout data (`statsPageCoords`) 對比

從 `engines/kyra/resource/staticres_eob.cpp` 萃取兩個 settings 的 `statsPageCoords` 35-field block：

| Field | EOB1 VGA (current EOB1 ZH 走) | EOB2 DOS_ZH (隱月已 ship) | 差異 |
|---|---|---|---|
| `headlineX/Y` | 183 / 42 | 180 / 37 | 微調 |
| `descStartX/Y/YInc` | 183 / 55 / 7 | 180 / 36 / 16 | EOB2 YInc=16 給中文用 |
| `statsGroup1StringsX/Y` | 183 / 82 | 180 / 100 | |
| `statsGroup2StringsX/Y` | **183 / 103** | **261 / 100** | EOB1 group2 跟 group1 同 X！中文擠在同一直行 |
| `statsStringsYInc` | **7** | **15** | EOB1 行距 7px 英文勉強 (8x8) — 中文 16x15 完全堆疊 |
| `statsGroup1StatsX/Y` | 275 / 82 | 219 / 104 | |
| `statsGroup2StatsX/Y` | **275 / 103** | **300 / 104** | 同樣 EOB1 數字疊在同一直行 |
| `statsStatsYInc` | **7** | **15** | 同 |
| `acStringX/Y, acStatsX/Y` | 183/124, 275/124 | 180/84, 236/88 | EOB2 把 AC row 移到上方 |
| `expStringX/Y...lvlStats...` | 239/138...278/138... | 254/51...287/51... | EOB2 全面重排 |
| `classStringsX/Y/XInc/YInc` | 180/145/0/7 | 180/148/38/0 | **EOB1 3 個 class 縱排 (YInc=7)；EOB2 橫排 (XInc=38)** |

### 推導用戶看到的座標

EOB1 ZH 走 `_guiSettingsVGA` 後實際畫出來的：

| 顯示元素 | 計算 | 結果 |
|---|---|---|
| 力 (`_chargenStatStrings[6]`) | (183, 82+0*7) | (183, 82) |
| 智 (`_chargenStatStrings[7]`) | (183, 82+1*7) | (183, 89) — **與「力」只差 7px，中文 15px 高完全壓上** |
| 慧 (`_chargenStatStrings[8]`) | (183, 82+2*7) | (183, 96) |
| 敏 (`_chargenStatStrings[9]`) | (183, 103+0*7) | (183, 103) ← **同 X**！ |
| 體 (`_chargenStatStrings[10]`) | (183, 110) | |
| 魅 (`_chargenStatStrings[11]`) | (183, 117) | |
| 力 value | (275, 82) | |
| ...同樣 6 個數字都疊在 X=275 | | |

完全對應 user screenshot 的「黑色 shadow 連成一團」+「6 個 stat 數字疊在另一個窄直行」。

---

## 3. EOB2 ZH (隱月傳奇) 現況

**EOB2 ZH 沒問題** — 上游有 `_guiSettingsDOS_ZH`，layout YInc=15, group2 移到 X=261 separate col, class strings 橫排. 玩家不會看到本 bug.

→ **fix 方向確定為 "把 EOB2 ZH 已有 layout 路由給 EOB1 ZH"** — Fix B/D/E/G pattern。

---

## 4. 候選方案

### 方案 A: 新增 `EoBEngine::_guiSettingsVGA_ZH` + 加 ZH branch (推薦)

**Concept**: 鏡像 EOB2 的做法。在 `eob.cpp::guiSettings()` 加 `else if (_flags.lang == ZH_TWN) return &_guiSettingsVGA_ZH;`，並在 staticres_eob.cpp 加 `EoBEngine::_guiSettingsVGA_ZH = { ... }`，**只覆寫 `statsPageCoords` 子結構**，其它 (buttons/colors/charBoxCoords/statsPageColors/spellbookCoords) 複製自 `_guiSettingsVGA`.

**直接借 EOB2 DOS_ZH 的 statsPageCoords 數字** (因為 panel clear region cm2X1/X2 = {179, 272, 301} / {271, 300, 318} 兩遊戲共用，X=180~300 範圍兩邊都安全)。

**預期視覺**:
- 6 stat label 變成 2-col 3-row, X=180/261, Y=100/115/130
- 6 數字同樣 2-col 3-row, X=219/300, Y=104/119/134
- AC label X=180 Y=84, 數字 X=236 Y=88
- 經驗/等級 row 在頂端 (Y=51) — 跟 chargen Fix A 視覺一致
- Class label 3 個橫排 X=180/218/256 Y=148 (中間 "/" 分隔已在 gui_eob.cpp L647-648 處理)

**Risk**:
- 中 — EOB1 跟 EOB2 的 sprite/dialog 不完全相同。例如 `_characterGuiStringsIn[]` (4 個字串) EOB1 ZH 跟 EOB2 ZH 都得有 4 個 (沒有 OOB 風險，line 627-629 用 index 0/1/2/3 全部 EOB1 也有)。
- 低 — `headlineX/Y` 改成 (180, 37) 後跟 line 184 ZH block 的 fillRect (216, 5, 300, 33) 不衝突 — 標題在 Y=37 是 panel 上方但 fillRect (`_screen->fillRect(216, 5, 300, 33, ...)`) 是 inventory mode 的 HP 文字背景，跟 stats page 不同 control mode (mode 2 走 `gui_drawCharacterStatsPage` 而不是 mode 1 的 inventory). 不衝突.
- 低 — `_invFont5` / `_invFont6` (line 631, 650) 是 EOB1 ZH 已 ship 用的字型，不需動.

**工作量**:
- staticres_eob.cpp: 加一個 `_guiSettingsVGA_ZH` (15 行，clone _guiSettingsVGA 然後改 statsPageCoords 那一行)
- eob.h: declare `_guiSettingsVGA_ZH` static
- eob.cpp guiSettings(): 加 1 個 else if branch (2 行)
- **共 ~20 行**

**是否需要 KYRA.DAT regen**: 否 — 純 C++ static data + branch.

**Verify step (給 game-tester)**:
1. 啟動 win64-build/啟動.bat
2. 建立隊伍至少 1 個角色 (走 chargen Fix A 已 OK)
3. 進入冒險畫面，點 portrait → 進入 character info panel
4. 確認 6 個 stat label 排成 2 col x 3 row (像 chargen Fix A 那樣)
5. 確認 6 個數字也是 2 col x 3 row 對齊到 label 右邊
6. 確認 class label 橫排 (戰士) 或 (戰士/法師) 等多 class
7. 確認 AC / XP / Level 行可讀
8. 試 6 個角色都看一遍

---

### 方案 B: 在 `gui_drawCharacterStatsPage()` 內加 inline ZH branch (chargen Fix A pattern)

**Concept**: 不動 settings table，在 line 622-654 區段加 `if (_flags.lang == ZH_TWN)` 用 hardcoded 座標 (鏡像 chargen Fix A)，跳過 `cd.statsGroup1StringsX` 等。

**Risk**:
- 中 — 代碼分裂：chargen 有 inline ZH，in-game 也有 inline ZH，兩處要同步維護
- 高 — gui_drawCharacterStatsPage() ZH branch 還得處理 expStats/lvlStats/classStrings (L641-655 的 i 迴圈跟 class 數量有關)，比方案 A 麻煩

**工作量**: ~60 行 inline ZH branch + 必須複製 cl (colors) 變數

**結論**: 不推薦 — 比方案 A 散亂，且無法 reuse EOB2 ZH 已驗證的數字。

---

### 方案 C: 改字體大小 (FID_8_FNT 數字部分 → 6_FNT)

**Concept**: 行距 7px 容不下 16x15 中文 glyph，那能否縮字體？

**問題**:
- ZH 中文字根本沒有 6px 高的 glyph (BIG5 12x12 已是底線)
- 即使 stat 數字用 6_FNT，**label (力/智/慧) 仍是 16x15 中文**，照樣堆疊
- 不解決根本問題

**結論**: 否決。

---

### 方案 D: 移除 printShadedText 的 shadow

**Concept**: shadow 黑邊加重了「連成一團」的視覺。把 `printShadedText` → `printText`?

**問題**:
- 失去對比 (中文白字無 shadow 看不清楚)
- 不解決堆疊問題，只是把黑團變成糊團
- 違反 chargen Fix A 一致性 (chargen 用 printShadedText)

**結論**: 否決。

---

## 5. 推薦

### 首選：方案 A (新增 `_guiSettingsVGA_ZH`)

理由：
1. **與 Fix B/D/E/G pattern 完全一致** — pattern 是「EOB2 ZH 有 specific resource，EOB1 ZH 從未走到 → 加一個 EOB1 ZH branch」
2. **20 行改動**，不動演算法
3. **借用 EOB2 ZH 已驗證 7+ 年的 layout 數字**，視覺風險最低
4. **不需 regen KYRA.DAT**
5. 修法乾淨，未來想再調 layout 也只改 staticres 一個 table

### Fallback：方案 B (inline ZH)

僅當方案 A 在 build 時 link 出問題 (例如 `_guiSettingsVGA_ZH` 必須是 static const 但有循環依賴)，才退到 B.

---

## 6. 給 developer 的 hand-off

### Step 1: staticres_eob.cpp 加 `_guiSettingsVGA_ZH`

在 `_guiSettingsVGA` 定義之後 (line 1704 後) 加：

```cpp
const KyraRpgGUISettings EoBEngine::_guiSettingsVGA_ZH = {
    // buttons: copy from _guiSettingsVGA (line 1693)
    { _dlgButtonPosX_Def, _dlgButtonPosY_Def, 9, 15, false, 95, 9, 2, 7, { 285, 139 }, { 189, 162 }, { 31, 31 } },
    // colors: copy from _guiSettingsVGA (line 1694)
    { 135, 130, 132, 180, 133, 17, 23, 20, 184, 177, 180, 184, 177, 180, 15, 6, 8, 9, 2, 11, 5, 4, 3, 1, 7, 12 },
    // charBoxCoords: copy from _guiSettingsVGA (line 1695-1700) — 6 portrait box 不變
    {	{ 184, 256, -1}, { 2, 54, 106 }, 64, 50,
        { 8, 80, -1 }, { 11, 63, 115 }, { 181, -1, -1 }, { 3, -1, -1 },
        { 40, 112, -1 }, { 11, 27, 63, 79, 115, 131 },
        { 23, 95, -1}, { 46, 98, 150 }, 38, 3, { 250, 250, -1}, { 16, 25, -1 }, { 51, 51 }, 5,
        2, 2, 2, 2, 13, 30
    },
    // statsPageCoords: ★ 借自 EOB2 _guiSettingsDOS_ZH (staticres line 2050)
    { 180, 37, 180, 36, 16, 180, 100, 261, 100, 15, 219, 104, 300, 104, 15, 180, 84, 236, 88, 254, 51, 270, 67, 0, 7, 287, 51, 301, 67, 0, 7, 180, 148, 38, 0 },
    // statsPageColors: 借自 EOB2 _guiSettingsDOS_ZH 配色 (line 2051) — 比 EOB1 VGA 對比更高，適合中文 ★ 註：如果 EOB1 ZH 已有自家色系偏好，改回 EOB1 VGA L1702 `{ 15, { 12, 12, 12 }, 12, 12, 12, 12, 15, { 15, 15, 15 } }`
    { 15, { 4, 5, 6 }, 1, 2, 7, 15, 15, { 4, 5, 6 } },
    // spellbookCoords: copy from _guiSettingsVGA (line 1703)
    { 56, 5, 71, 122, 21, 9, 2, 1, 6, 73, 132, 44, 0, 0, 0, 0, 73, 168, 0, { 0x44, 0x62, 0x80, 0x90 }, { 0x82, 0x92, 0x98 } }
};
```

**Color note**: `statsPageColors` 我建議 dev **先 commit EOB1 VGA 原配色** (line 1702)，再玩一輪看 OK 才嘗試切 EOB2 配色。降低同 commit 風險。

### Step 2: eob.h declare

找到現有 `_guiSettingsVGA` declaration (應該在 EoBEngine class private section)，旁邊加：

```cpp
static const KyraRpgGUISettings _guiSettingsVGA_ZH;
```

### Step 3: eob.cpp `guiSettings()` 加 branch

L1277-1288 改成：

```cpp
const KyraRpgGUISettings *EoBEngine::guiSettings() const {
    if (_flags.platform == Common::kPlatformAmiga)
        return _useMainMenuGUISettings ? &_guiSettingsAmigaMainMenu : &_guiSettingsAmiga;
    else if (_configRenderMode == Common::kRenderCGA || _configRenderMode == Common::kRenderEGA)
        return &_guiSettingsEGA;
    else if (_flags.platform == Common::kPlatformPC98)
        return &_guiSettingsPC98;
    else if (_flags.platform == Common::kPlatformSegaCD)
        return &_guiSettingsSegaCD;
    else if (_flags.lang == Common::ZH_TWN)   // ★ Fix H: EOB1 ZH stats page layout
        return &_guiSettingsVGA_ZH;
    else
        return &_guiSettingsVGA;
}
```

**Caveat**: 注意 ZH branch **必須放最後一個 else if** (在 SegaCD 之後 / 在 fallback 之前)。如果放最前面，會吃掉 Amiga/EGA/PC98 path (雖然 EOB1 ZH 不會跑那些 platform，但 defensively 放最後)。

### Step 4: build + iterate

依 iter5 工作流 (wsl-scripts/ + win64-build/ rsync + Steam emu link)。

**Side-effect 預警**:
- `guiSettings()` 也被 `gui_drawCharPortraitWithStats()` (L99) 自己用 — 但只取 `charBoxCoords` 跟 `colors`，這兩個我們複製自 VGA 沒動。**6 portrait 不會變**.
- `gui_drawWeaponSlot`, `gui_drawFaceShape`, `gui_drawHitpoints` 也用 `guiSettings()` 取 `charBoxCoords` — 同樣不變.
- 唯一視覺變化集中在 `_currentControlMode == 2` (角色資訊 panel) — 命中正是 user 報的 bug.

### Step 5: 確認 game-tester verify checklist 全 pass (見方案 A verify step)

---

## 7. 提案後續 Fix 編號

承接 Fix G2，本提案編號為 **Fix H** (character info layout)。
建議 commit message: `Fix H: route EOB1 ZH stats page through _guiSettingsVGA_ZH (mirror EOB2 ZH layout)`.

## 8. 已知未涵蓋

- 本 fix **只修 `_currentControlMode == 2` (stats page)**.
- `_currentControlMode == 1` (inventory page) 在 gui_eob.cpp L205-243 走另一條 path — 已有 ZH 處理 (line 207 JPN, line 212-229 ZH labels)，**未報壞**.
- spellbook (line 754+) 已有大量 ZH-specific code，**未報壞**.
- 戰鬥畫面、地圖畫面、save/load 等 **未報壞** (與本 fix 無關).

若 game-tester 後續再報 inventory / spellbook layout 壞，那是另一個 fix 不在本 design 範圍。
