# Build applied — iter3 (2026-05-23 ~13:00)

接續 iter2 baseline report (`test-reports/report-iter2-baseline.md`)。Fix A/B/C 全 PASS。本 iter 處理新出 BUG-013 + carry-over BUG-003。

## Fixes applied

### Fix D — BUG-003: CharGen 動作按鈕中文 overlay path

- **File**: `scummvm-source/engines/kyra/engine/chargen.cpp:604`
- **Edit**: 從
  ```cpp
  if (_vm->game() == GI_EOB2 && _vm->gameFlags().lang == Common::Language::ZH_TWN && _chineseButtonExtraData[index].type != -1) {
  ```
  改為
  ```cpp
  if (_vm->gameFlags().lang == Common::Language::ZH_TWN && _chineseButtonExtraData[index].type != -1) {
  ```
- **理由**: EOB2 ZH 已有完整中文 button render path (`_chineseButtonExtraData[]` 在 1842, `_chargenButtonDefsDOSChinese[]` 在 1862)，用 `printShadedText` 蓋掉英文 bitmap。EOB1 ZH 走同 path 應該也可以，因為 `_chineseButtonExtraData[index].mapping` (REROLL=27/MODIFY=28/FACES=29/KEEP=30) 在 EOB1's `_chargenButtonDefsDOS[]` 也是 action button slot 位置 (224,156 / 264,156 / 224,172 / 264,172)。
- **Risk**: 中文 label 位置依賴 EOB1 native button defs，未測。NOT 變更 line 180 (button defs swap)，因 EOB2 Chinese variant 的 button 座標 (e.g. index 27 → 144,64) 與 EOB1 chargen UI 不相容。
- **預期效果**: REROLL/MODIFY/FACES/KEEP/BACK/PLAY/+/-/刪除 改為中文 (骰子/修改/造型/接受/退回/完畢/十/一/刪除)
- **Risk if broken**: button label 位置錯或缺，但 click hitbox 不變 (button defs 沒換)

### Fix E — BUG-013: Name 輸入殘留 race-sex 字

- **File**: `scummvm-source/engines/kyra/engine/chargen.cpp:772-782`
- **Edit**: 兩處改動
  1. **放寬 gate** `_vm->game() == GI_EOB2 && _vm->gameFlags().lang == Common::Language::ZH_TWN` → `_vm->gameFlags().lang == Common::Language::ZH_TWN`，EOB1 ZH 也走 upper position (prompt 149,66 / input 19,81 8 chars wide)
  2. **加 clearRect** `fillRect(15, 80, 145, 95, guiColorBlack)` 在 prompt/input 前，清掉 input 條左半的殘留 (x 限制 < 150 避免擋到 stats 在 x=165+)
- **理由**:
  - Tester report 指出 EOB1 ZH (else branch) 的 input 在 (24, 100) 顯示 `名類男test1` 殘留
  - 統一到 EOB2 ZH 上方 position 後，input 位置變 (19, 81)，殘留來源不同但 clearRect 都覆蓋
  - EOB2 ZH 同樣可受惠 (即使原 iter2 tester 沒 flag EOB2-style)
- **Side effects**:
  - EOB1 ZH input field 從 10 char wide 變 8 char (跟 EOB2 ZH 一致)。`name[10]` buffer 仍夠
  - 字型從 `_invFont3` (FID_8_FNT) 改為 current font (可能 FID_CHINESE_FNT) — chars 變更寬，仍 fit
- **Risk**: clearRect 範圍 (15..145, 80..95) 計算為避開 stats grid (x>=165)；若 input 內容超出 x=145 視覺上會看到殘留 (8 char × 8px ASCII = 64px wide → 19..83，安全)
- **Risk if broken**: input area 可能被遮太多或太少。tester 截圖會看出

## Deferred

| Bug | Why deferred | 對應 doc |
|---|---|---|
| BUG-009 CAMP `營：` | 實測非 pixel overlap 是同 Y 緊鄰 (`bug-009-analysis.md`)；4 個 fix 選項皆 trade-off (動 EOB2 ZH 或結構改) | `design-reviews/bug-009-analysis.md` |
| BUG-014 動作按鈕擋 `級` | Fix A col 2 X=240 與 EOB1 native button area (x=224..302) 衝突；只能透過 (a) shrink col stride 但會擠壓 stat label/value (b) 把 buttons 移開但要改 bitmap (c) 在 button 顯示時 hide col 2 — 都需 architecture 級重設計 | (inline 此 doc) |
| BUG-005 `色` glyph | tester 未驗證；待 iter3 tester re-test | — |
| BUG-006 `沒` glyph | 待 tester re-confirm 是否仍 broken | — |
| BUG-007 multi-class 斜線 | cosmetic；未驗證 | — |
| BUG-008 BACK button 漏字 | cosmetic redraw bleed | — |
| BUG-010 alignment spacing | cosmetic | — |
| BUG-011 multi-class header clip | 未驗證 | — |
| Inventory regression | Coverage gap from iter2；tester 進不去 inventory；iter3 tester 重試 | — |

## Build status

| Target | Status | Binary | Size | SHA-256 |
|---|---|---|---|---|
| Linux (`/root/scummvm_work/scummvm/scummvm`) | OK | scummvm | ~43 MB | (rebuilt 13:06; only chargen.o incremental) |
| Windows (MinGW cross, stripped, `win64-build/scummvm.exe`) | OK | scummvm.exe | 27,059,712 B | `f2d6766a528b7e9b275de709a51c0dd29203c5b774f2295ba44465fb03865b3e` |

兩個 build 都 incremental (只 chargen.o + libkyra.a + final LINK)。**踩到雷**: Win 用獨立 in-tree clone 在 `/root/scummvm_work/scummvm-win64-build/`，初次只 cp 到 Linux source dir 沒有同步到 Win clone，導致 Win first build 用了 stale chargen.o → 30 秒 finish 但 binary 還是 iter1 的。第二次手動 cp chargen.cpp 到 Win build dir 才正確 rebuild。下次 build script 應該同步兩處或 Win 改 out-of-tree。

- **KYRA.DAT / ceob.pat**: unchanged (no resource changes)

## What changed for downstream (next tester run)

- scummvm (Linux): rebuilt, picks up Fix D + Fix E
- scummvm.exe (Windows): rebuilt
- Test priorities for iter3 baseline:
  1. **BUG-003 verify**: REROLL/MODIFY/FACES/KEEP/BACK/PLAY buttons 應該變中文
  2. **BUG-013 verify**: name input field 應該乾淨 (`test1` 沒有 `名類男` 殘留)
  3. **Fix E side-effect check**: name input 位置移到 (19, 81) 而非 (24, 100)；input 寬度從 10 → 8 char
  4. **Regression check**: stats screen (Fix A 仍正常), menu titles (Fix B 仍正常), portrait names (Fix C 仍正常)
  5. **iter2 coverage gap re-test**: Inventory screen (Fix C 副作用 — _invFont1 revert 對中文物品名是否影響)
  6. **iter2 deferred**: BUG-005 (色 glyph), BUG-006 (沒 glyph) 確認狀態

## Open questions

- BUG-003 fix 是否真的 work? EOB1 chargen button 索引與 EOB2 是否一致 (REROLL=4, MODIFY=7, FACES=8, KEEP=6, BACK=5, PLAY=9...)
- 若 BUG-013 clearRect 寬度太大遮到 EOB2 ZH 既有可見內容，要 narrow 範圍
- iter3 tester 若還 flag BUG-009 / BUG-014，需 ux-designer round 設計 layout 大改

## 給 iter3 tester 的指示 (excerpt for the agent)

進 CharGen → 看 race menu (BUG-001 verify Fix B 仍 OK)
→ 過 race/class/alignment menu → stats roll (BUG-002 Fix A 仍 OK, BUG-014 cosmetic 確認仍存在)
→ FACE picker 時看 button label (BUG-003 verify) — 應是中文
→ KEEP → name input (BUG-013 verify) — 應乾淨無殘留
→ 完成 4 角色進遊戲 → portrait name 中文化 OK (Fix C)
→ 點 portrait 進 inventory (iter2 coverage gap)
→ 進 CAMP (BUG-009 仍存在，cosmetic)
→ 偏好設定 → 踢出角色 (BUG-005 `色` 確認)
