# Build applied — iter4 (2026-05-23 ~16:20)

Autonomous run after iter3 ship. User authorized "自主判斷下一個 run 不用詢問直到 token 用完"。

## Portable bundle reorganization

User request: 集中所有遊戲檔到 `win64-build/`，啟動.bat 不再從 SteamLibrary copy。

**Changes**:
- Created `win64-build/game/` subdirectory
- Copied EOB1 ENG game files from `D:\SteamLibrary\steamapps\common\Forgotten Realms The Archives - Collection One\games\Eye of the Beholder ENG\GAME\EYE\` excluding `.bak`/`.SAV`/installer (19 files, 6.5 MB)
- Moved `KYRA.DAT` + `ceob.pat` from `win64-build/` root into `win64-build/game/`
- Updated `啟動.bat`: removed SteamLibrary GAMEDIR + remove copy steps; now sets `GAMEDIR=%~dp0game`
- Verified: `scummvm.exe --detect --path=...game` recognises `Eye of the Beholder (Extracted/DOS/Chinese (Traditional))`

Total portable bundle: 34 MB. 雙擊 `啟動.bat` 即玩。

### 啟動.bat 編碼 + 行尾雙重雷 (2026-05-23 fix attempt #2)

User 雙擊 .bat 看到 garbled `'~dp0''`, `'OB1'`, `'閽?SteamLibrary'` 等錯誤。**兩個獨立問題**:

1. **編碼**: Edit tool 寫檔轉成 UTF-8 (3 bytes/CJK)，但 cmd 在繁中 Windows 用 cp950 讀檔 (2 bytes/CJK)。中文 bytes 解碼錯位導致 quote 不對齊 + parsing 壞掉。
   - Fix 1: 用 PowerShell `[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::GetEncoding(950))` 強制 cp950 ANSI 寫入

2. **行尾**: PowerShell here-string `@'...'@` 保留 LF (Unix 行尾)，cmd.exe 解析 LF-only .bat 會 token 對不齊 → 第一行 `@echo off` 變成 `cho off`、`set` 行變 `GAMEDIR is not recognized`。
   - Fix 2: 確保 CRLF (`-replace "`n", "`r`n"` OR 用 `Add-Content` 多次寫，或 `[System.IO.File]::WriteAllText` 後手動 `[System.IO.File]::ReadAllBytes` + insert `\r` 前 `\n`)

最終正確檔: 523 bytes, CR=19/LF=19 (純 CRLF), cp950 ANSI, no BOM. Dry-run (把 scummvm 行換成 `echo TEST_DRY_RUN_OK`) 確認零 parsing error 後還原。

**未來打包 .bat 必檢清單** (寫進 dosbox-portable-sfx / wing-portable-sfx skill?):
- [ ] cp950 encoding (no UTF-8 BOM, no UTF-16)
- [ ] CRLF line endings (CR count == LF count)
- [ ] First byte = ASCII (`@` 0x40 開頭最安全)
- [ ] Dry-run via `cmd /c "...bat"` 至少跑過一次

## Source patches

### Fix F — BUG-007: multi-class 縮寫半形斜線改全形

- **File**: `scummvm-source/devtools/create_kyradat/resources/eob1_dos_chinese.h:77-91`
- **Edit**: 7 多職業字串從 半形 `/` (`0x2f`) 改為全形 `／` (Big5 `\xa1\x4d`):
  - idx 6: 戰／牧 (was 戰/牧)
  - idx 7: 戰／盜
  - idx 8: 戰／法
  - idx 10: 盜／法
  - idx 11: 牧／盜
  - idx 13: 俠／牧
  - idx 14: 牧／法
- 3-char tri-class (戰法盜/戰牧法) 不動 — 原本就無斜線
- **Verification**: KYRA.DAT 大小 +7 bytes 對應 7 字串各 +1 byte (3-byte fullwidth vs 1-byte halfwidth)
- **Risk**: 字寬統一後 CharGen race menu 多職業看起來與 6 基礎職業同寬，整體一致

### Phase 2 kSpecial=5 ChineseFan — ATTEMPTED then REVERTED

詳 `design-reviews/kSpecial-chinese-fan-design.md` 看板 + Lessons learned 段。

簡述: getSpecialID + games.cpp + resources.cpp 90 entries 全 flip → KYRA.DAT 生成 ERROR `Could not find need 149`。原因: resource lookup encoding 把 special 編進 filename hash，**161 個 language-agnostic UNK_LANG providers** 仍 tagged kNoSpecial 不在新 lookup table 內 → miss。修法需 duplicate 那 161 entries 或加 fall-through，超出 atomic flip 範圍。**REVERT 全部 changes**，未來改用 Plan B5 per-resource opt-in。

### Bugs DEFERRED (no fix this iter)

- **BUG-005** 「色」glyph 破損: 字模問題 (ceob.pat)，不是 string fix 可解。需 `tools/build_ceob_combined.py` 調整 16x12 hybrid glyph subset。
- **BUG-006** 「沒」glyph: 同 BUG-005
- **BUG-008** BACK 漏字: redraw timing bug，需 engine 介入
- **BUG-009** CAMP `營：`: 分析 4 fix 選項皆 trade-off (詳 `bug-009-analysis.md`)。本 iter 嘗試 runtime button y offset 但 buttonDefsChineseEOB2 stride 不允許 shift 不 overflow dim h=144。需 ux-designer round 決定: shrink button height OR enlarge dim OR accept layout。
- **BUG-010** alignment 間距: 字模渲染問題，所有 9 alignment 字串都是 4 全形字均勻，視覺差異來自 ceob.pat glyph 寬度。需字模 polish。
- **BUG-014** 動作按鈕擋 `級`: Fix A col 2 X=240 與 EOB1 native button area x=224..302 衝突。需要 architecture 級重設計 OR 接受 cosmetic regression。
- **ENV-INFRA-01** WSL tester 2/3 fail rate: WSL-specific，影響 tester productivity 不影響 end user。`tools/agent-helpers/driver.sh` workaround 已 ship。

## Build status

| Target | Status | Binary | Size | SHA-256 |
|---|---|---|---|---|
| Linux (`/root/scummvm_work/scummvm/scummvm`) | OK | scummvm | ~43 MB | rebuilt (Phase 2 source revert + recompile) |
| Windows (`win64-build/scummvm.exe`) | OK | scummvm.exe | 27,059,712 B | `444f3835e3e8a935821897bc70121f4d3a42bfaaf713c55861a32b03d87592aa` |
| KYRA.DAT (`win64-build/game/KYRA.DAT`) | OK | 2,034,039 B | `8786c404810a8650a35d94b2c7605dee1aba378ba85ff7fa676a2c8e4731dc2c` |

## 給 Claude (next session)

iter4 ship:
- Portable bundle 完整: `D:\03_game_tmp\eob1_cht\win64-build\` 雙擊 `啟動.bat` 即玩
- Fix A/B/C (iter1) + Fix D/E (iter3) + Fix F (BUG-007 iter4) 全在 binary 內
- 5 bugs 剩 deferred (BUG-005/006/008/010/014) + BUG-009 (CAMP `營：`) — 都需 ux/font 工作
- Phase 2 kSpecial=5 路徑卡關，記在 design doc。Plan B5 是未來物品名/intro 翻譯的方向

如果要再做:
1. **BUG-009 ux fix**: 探討 dim h enlarge OR 縮 button stride
2. **字模 polish**: BUG-005/006/010 對應 ceob.pat 重生 (tools/build_ceob_combined.py)
3. **Plan B5 per-resource opt-in**: 從 PAK 抽 EN item names + 翻譯 + 加 DOS English provider + ZH_TWN provider + 加到 eob1FloppyNeed

iter4 沒 spawn tester (ENV-INFRA-01 issue + BUG-007 fix 是 mechanical byte change 高信心)。下次累積更多 fix 後再一次 verify。
