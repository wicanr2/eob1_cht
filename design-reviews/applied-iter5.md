# Build applied — iter5 (2026-05-23 ~late afternoon)

接續 iter4 ship 後 user 雙擊 `win64-build\啟動.bat` 看到 CharGen name input 嚴重視覺異常 (大塊垂直黑色矩形覆蓋 input field) 的修補。Tester agent 並行做 visual confirm; developer 從 source 直接 diagnose 找根因。

## 根因分析 (hypothesis confirmed: input geometry consts gated to GI_EOB2)

iter3 Fix E (`chargen.cpp:771-789`) 把 ZH_TWN name input gate 從 `_vm->game() == GI_EOB2 && lang == ZH_TWN` **放寬到 `lang == ZH_TWN`** — 目的: EOB1 ZH 也走 EOB2 ZH 的 upper position 路徑 (prompt 149,66 / input 19,81)，避免 EOB1 ZH 在原 else branch (24,100) 顯示殘留。**Gate 放寬 OK**，input 位置也對齊。

但 EOB2 ZH 在 path 內 works 不只是 path 對，**還因為 `GUI_EoB` ctor 為 EOB2 ZH 特別設了 5 個 geometry 常數** (gui_eob.cpp:1576-1580)，把 input/dialog button 從 ASCII 8/9-tall 升到 CJK 15/16-tall:

```cpp
_textInputHeight        : GI_EOB2 && ZH_TWN ? 16 : 9
_textInputShadowOffset  : GI_EOB2 && ZH_TWN ?  1 : 0
_dlgButtonHeight1       : GI_EOB2 && ZH_TWN ? 16 : 14
_dlgButtonHeight2       : GI_EOB2 && ZH_TWN ? 17 : 14
_dlgButtonLabelYOffs    : GI_EOB2 && ZH_TWN ?  1 : 3
```

**問題**: 這 5 個 gate **沒** 隨 iter3 chargen gate 一起放寬到 EOB1 ZH。

**`_textInputHeight=9` 對 EOB1 ZH 的 effect**:
- `getTextInput` (gui_eob.cpp:2936) 用 `copyRegion((x-1)<<3, y, 0, 200-9, (n+2)<<3, 9, 0, 2, ...)` 把 input field 底圖**只備份 9 px tall** 到 page 2 暫存
- printShadedText 寫 input 字串到 (x<<3=152, y=81)，**字型是 EOB1 ZH 當前 font (FID_CHINESE_FNT, 15-tall, loadPCBIOSTall)** — 字佔 y=81..95
- Cursor blink loop (gui_eob.cpp:2965) 每 4 tick `copyRegion` 從 page 2 (0, 191) 抓 **9 tall** 寫回 (x+pos)<<3, y=81 復原 — 只蓋掉字頂 9 px，**字底 6 px (y=90..95) 永遠不被擦除，每 keystroke 與 cursor blink 累積**
- 加上 `chargen.cpp:779` 的 `fillRect(15, 80, 145, 95, guiColorBlack)` 在進入循環前清出黑底 + 同 y 範圍 80..95，視覺結果 = **80..95 的整條 130 px 寬 15 px 高黑底 + 上面殘留 cursor 區段** = "大塊黑色矩形覆蓋 input field"

**為何 EOB2 ZH 沒問題**: `_textInputHeight=16` 完整容納 15-tall 字 + 1 px shadow，copyRegion 復原範圍正確覆蓋整個字高，無殘留。

## Fix applied — iter5

### Fix G — `gui_eob.cpp:1576-1580` 5 個 ZH input/dialog geometry consts 放寬到任一 EOB

- **File**: `scummvm-source/engines/kyra/gui/gui_eob.cpp:1576-1580`
- **Edit**: 條件從 `vm->game() == GI_EOB2 && vm->gameFlags().lang == Common::Language::ZH_TWN` → `vm->gameFlags().lang == Common::Language::ZH_TWN`
- **Affects**: `_textInputHeight` (name input copyRegion height + cursor fillRect height), `_textInputShadowOffset` (cursor fillRect bottom margin), `_dlgButtonHeight1/2` (Yes/No dialog button heights), `_dlgButtonLabelYOffs` (button label baseline y offset)
- **Risk**: EOB1 ZH 跑同 path EOB2 ZH 已 ship 驗證的 geometry，最小 surprise。EOB1 ENG 與其他 lang/platform 完全不受影響 (gate by `lang == ZH_TWN`)。
- **NOT touched**: `chargen.cpp` (iter3 Fix E 已正確放寬 gate, fillRect 範圍 OK)，KYRA.DAT (純 source bug, 非資料問題)，ceob.pat，SDL2.dll

### 路徑驗證 (Fix G 為何足夠)

- `_textInputHeight=16`: copyRegion 備份 16 tall, 復原也 16 tall, 完整覆蓋 15-tall 字 + 1 px shadow
- `_textInputShadowOffset=1`: cursor blink fillRect (line 2968) 範圍 `y..y+16-2+1=y..y+15` 對齊字高
- `_dlgButtonHeight1/2` 同步放寬避免 EOB1 ZH 後續走到 dialog button 路徑時又踩到同類雷
- `fillRect(15, 80, 145, 95)` (chargen.cpp:779) 範圍 15 tall — 與 new `_textInputHeight=16` 仍兼容 (黑底略小 1 px 但字 + cursor 復原全在 fillRect 區內，無視覺異常)

## Build status

| Target | Status | Path | Size | SHA-256 |
|---|---|---|---|---|
| Source (D:) | OK | `scummvm-source/engines/kyra/gui/gui_eob.cpp` | — | synced to 2× WSL trees |
| WSL Linux (`/root/scummvm_work/scummvm/`) | OK | `gui_eob.cpp`, `gui_eob.o`, `libkyra.a`, `scummvm` rebuilt | — | — |
| WSL Win64 (`/root/scummvm_work/scummvm-win64-build/`) | OK | `gui_eob.cpp`, `gui_eob.o`, `libkyra.a`, `scummvm.exe` rebuilt + stripped | 27,059,200 B | `a40be61e45353efc237587010b507706ca917ddae3889ac4c7cb4117db3b5fca` |
| **Deployed** (`win64-build/scummvm.exe`) | OK | copied from WSL | 27,059,200 B | `a40be61e45353efc237587010b507706ca917ddae3889ac4c7cb4117db3b5fca` |
| `KYRA.DAT` (`win64-build/game/`) | unchanged | — | 2,034,039 B | `8786c404810a8650a35d94b2c7605dee1aba378ba85ff7fa676a2c8e4731dc2c` |
| `ceob.pat` | unchanged | — | — | — |
| `SDL2.dll` | unchanged | — | — | — |

Detection 仍正常: `kyra:eob  Eye of the Beholder (Extracted/DOS/Chinese (Traditional))`.

## Source/build sanity (verified before fix)

- `/root/scummvm_work/scummvm/engines/kyra/engine/chargen.cpp` ≡ D:\ source ≡ `/root/scummvm_work/scummvm-win64-build/.../chargen.cpp` (all 92603 bytes, `diff` empty)
- iter4 ship binary SHA `444f3835...` 與 WSL Win64 build dir SHA 一致 → build pipeline 正確，bug 是 source 層
- gui_eob.o iter4 mtime 06:49 (未隨 chargen.o 13:09 rebuild) — iter4 改動沒 touch gui_eob.cpp，**這就是雷沒早被發現的原因**

## What iter5 changes for downstream

- Tester agent 應重新進 CharGen → name input field 應乾淨無大塊黑矩形，input 可正常輸入 1-8 character name (Chinese 全形字或 ASCII)
- 順帶 Yes/No 類 dialog button 在 EOB1 ZH 高度從 14 → 16/17，label y offset 從 3 → 1，**注意 regression**: 若 user 確認 EOB1 ZH 有任何 dialog button (e.g. quit confirm) 顯示異常，可能要把 `_dlgButtonHeight1/2` + `_dlgButtonLabelYOffs` 3 個 revert 為 EOB2-only，只放寬 `_textInputHeight` + `_textInputShadowOffset` 即可

## Hypotheses considered and rejected

| Hyp | Description | Rejected because |
|---|---|---|
| 1 | fillRect coord 失準 (textMargin/curDim offset 偏) | `Screen::fillRect` (screen.cpp:1217) 純 corner coords, 無 dim 偏移; assertion `x2<SCREEN_W && y2<_screenHeight` 也排除 |
| 3 | Build mismatch (source 變動但 .o/.exe 沒同步) | `diff` 3 處 chargen.cpp 完全一致; `sha256sum` win64-build/scummvm.exe ≡ WSL build dir ≡ iter4 SHA |
| 4 | `_textInputHeight` 在 ZH 模式被設成不合理值 | 接近但反方向: EOB1 ZH 沒進入 ZH ctor 分支, 仍是 default 9 → 對 15-tall 中文字過小, **這就是 Fix G 修的根因** |

## 給下個 session

- iter5 ship Fix G。Tester agent 應 verify name input visual clean。
- Deferred bugs (BUG-005/006/008/009/010/011/014) 都未 touch — 字模/UX 問題，需 ceob.pat 重生或 layout 重設計。
- 若 EOB1 ZH 跑 Yes/No dialog 看起來變高/變位，按上面 "What iter5 changes" 段 partial revert dlg consts。

如果要再做:
1. EOB1 ZH dialog button 視覺 spot-check (本次 fix 順帶影響)
2. ceob.pat 字模 polish (BUG-005/006/010)
3. BUG-009 CAMP `營：` 的 dim 重設計或 button stride 調整

## Crash fix (Bug A + Bug B): portrait click crash

接續 iter5 ship 後 user 在 Win native 雙擊 `啟動.bat` 跑遊戲報的兩個 crash：
- **Bug A**: CharGen 流程中點人物選單會當機
- **Bug B**: 建立 4 人隊伍進遊戲後，點人物頭像 (portrait) 會當機

### Repro

- **WSL Linux** (Xvfb :88, isolated tester via `tools/agent-helpers/crash-flow.sh`): **NOT** reproducible — full chargen + 4-char party + in-game portrait click 全部 OK，無 crash trace、無 fatal error
- **Win64 native** (user 端): 確認 crash (per user report on `啟動.bat` 實機)
- 結論: bug 是 OOB read，**Linux glibc heap layout 之後緊鄰可讀記憶體 → silent garbage**；**MinGW Windows heap layout 之後可能撞到 guard page / 無效指標 → segfault**

### Root cause (Bug B)

`scummvm-source/engines/kyra/gui/gui_eob.cpp` 三處 `_characterGuiStrings*` array OOB read，**only EOB2 has 完整 provider; EOB1 ZH provider 比較短**：

| 存取點 | 索引 | EOB1 ZH 實際大小 | EOB2 ZH 實際大小 | 觸發條件 |
|---|---|---|---|---|
| `gui_eob.cpp:186` | `_characterGuiStringsHp[3]` | 2 (provider 564) | 4 (provider 510) | `_currentControlMode != 0` (portrait click in-game) + `lang == ZH_TWN` |
| `gui_eob.cpp:224` | `_characterGuiStringsSt[6]` | 6 (provider 587) | 7 (provider 536) | inventory mode + `c->flags & 8` (petrified) |
| `gui_eob.cpp:436` | `_characterGuiStringsHp[2]` | 2 | 4 | `_currentControlMode` + `!_configHpBarGraphs` (bar graph 關掉時) |

三處共同點: gate 是 `_flags.lang == Common::ZH_TWN` **而非** `gameID == GI_EOB2 && lang == ZH_TWN`。原作者 (iter1 之前的 upstream EOB2 CHT 補丁) 預設只有 EOB2 跑 ZH，所以 array size 配合 EOB2 排版設計 (4 strings: 命/HP fmt/HP-inv fmt/食)；EOB1 ZH 補丁加進來時 KYRA.DAT provider 只翻譯 EOB1 原本就有的 2 strings (命/HP fmt)，沒 mirror 加上 EOB2 才有的 inventory-mode HP 格式與「食」label，**因此 EOB1 ZH 走到同 gate 觸發 OOB**。

### Bug A 分析

WSL 完整重現 CharGen 流程 (race menu / class menu / alignment / FACES picker / KEEP / name input / 切換 box / 進 game) 全 OK。**沒在 chargen.cpp 找到 OOB**。

推測 Bug A 是 user 描述 Bug B 的另一個觸發點 — 可能 user 把 "在 CharGen 結束 → 進 game → 點選人物" 描述為 "CharGen 流程中"，或 user 之前實際 crash 是在「卡關 PLAY 不能進」的 perceived freeze。本 fix 完整解決 `_characterGuiStringsHp[3]` 等三處 OOB，**Bug A/B 同源**。若 user 後續仍報「CharGen 中某操作 crash」需另 iter 重新調查 (建議跑 game-tester agent 在 Windows native 下 step-by-step screenshot)。

### Fix (Fix G2)

`scummvm-source/engines/kyra/gui/gui_eob.cpp` 三處改動，把 OOB 索引存取 gate 到 `_flags.gameID == GI_EOB2`：

1. **Line 186-192** (portrait inventory mode HP/food label): `_characterGuiStringsHp[3]` (食) 改 gate `if (_flags.gameID == GI_EOB2)` 內。EOB1 ZH 無 inline "食" label (gui_drawFoodStatusGraph 仍 render bar，僅 cosmetic 少一個字符 label)。
2. **Line 223-230** (status "petrified" string): `_characterGuiStringsSt[6]` 改 gate `if (_flags.gameID == GI_EOB2)` 內。EOB1 無原始 status[6] (provider 只 6 elements)，gate 後與原 EOB1 行為一致。
3. **Line 435-437** (inventory mode HP format string): `_characterGuiStringsHp[2]` 用三元運算選 — EOB2 用 `[2]` (緊湊格式 `%2d/%-2d`)、EOB1 fallback 到 `[1]` (`%3d / %-3d`)。EOB1 ZH inventory HP display 跟 normal mode 同格式 (cosmetic but no crash)。

Diff摘:
```cpp
// gui_eob.cpp:186 (was)
_screen->printShadedText(_characterGuiStringsHp[3], 272, 20, ...);
// (now)
if (_flags.gameID == GI_EOB2)
    _screen->printShadedText(_characterGuiStringsHp[3], 272, 20, ...);

// gui_eob.cpp:224 (was)
else if (c->flags & 8)
    _screen->printShadedText(_characterGuiStringsSt[6], 232, statusTxtY, ...);
// (now)
else if (c->flags & 8) {
    if (_flags.gameID == GI_EOB2)
        _screen->printShadedText(_characterGuiStringsSt[6], 232, statusTxtY, ...);
}

// gui_eob.cpp:436 (was)
tmpString = Common::String::format(_characterGuiStringsHp[2], c->hitPointsCur, c->hitPointsMax);
// (now)
tmpString = Common::String::format(_flags.gameID == GI_EOB2 ? _characterGuiStringsHp[2] : _characterGuiStringsHp[1], c->hitPointsCur, c->hitPointsMax);
```

### Build status

| Target | Status | Path | Size | SHA-256 |
|---|---|---|---|---|
| Source (D:) | OK | `scummvm-source/engines/kyra/gui/gui_eob.cpp` | — | `3f890012f4f3b0a18a1a2d02bafaf148e975b613df5642775d2e0c6d4cded1ba` |
| WSL Linux (`/root/scummvm_work/scummvm/`) | OK rebuilt | only `gui_eob.o` + libkyra.a + LINK | — | — |
| WSL Win64 (`/root/scummvm_work/scummvm-win64-build/`) | OK rebuilt + stripped | `scummvm.exe` | 27,059,712 B | `b4d9c31f1f62e6e58cbf1a945f4aa48664bb0fab1d1bbf76d8b0d5385f8eb6d4` |
| **Deployed** (`win64-build/scummvm.exe`) | OK | — | 27,059,712 B | `b4d9c31f1f62e6e58cbf1a945f4aa48664bb0fab1d1bbf76d8b0d5385f8eb6d4` |
| `KYRA.DAT` | unchanged | — | 2,034,039 B | `8786c404810a8650a35d94b2c7605dee1aba378ba85ff7fa676a2c8e4731dc2c` (no resource changes) |
| `ceob.pat` | unchanged | — | — | — |

Detection still recognises Chinese (Traditional): `kyra:eob  Eye of the Beholder (Extracted/DOS/Chinese (Traditional))`.

WSL repro confirms no regression in normal flow (chargen → 4-char party → in-game portrait click 全 OK, 無 crash)。Win 端 user 端驗證待 user 雙擊 `啟動.bat` 跑一次確認 portrait click 不再 crash。

### Helpers added (留給未來 iter)

- `tools/agent-helpers/crash-repro.sh` — isolated driver (DISPLAY :88, log /tmp/eob1-crash/) 避免跟 iter5 tester (:99) 互踩
- `tools/agent-helpers/crash-flow.sh` — all-in-one flow: boot → CharGen (1 char) → +3 chars → PLAY → in-game portrait click → screenshot at each step

### 未來改進建議

長期解 (建議下 iter)：
1. 把 EOB1 ZH provider 在 `eob1_dos_chinese.h` 補齊到 4-Hp / 7-St 元素 (添加 食 / 石化 等 string)，重生 KYRA.DAT，**revert Fix G2** — 這樣 EOB1 ZH 跑同 EOB2 ZH 的 inventory layout 視覺一致，不再是 EOB2-only feature
2. 或直接接受 Fix G2 — EOB1 ZH inventory mode 缺 inline 食 label (圖形 bar 仍在)，但 100% 不會 crash，零 KYRA.DAT 風險
