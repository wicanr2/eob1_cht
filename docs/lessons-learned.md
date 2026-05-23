# Lessons Learned — EOB1 CHT iter1 → iter5

Consolidated insights from 2026-05-23 多 iter loop session。對應 design-reviews/ 與 test-reports/ 全套 artifacts。

## TL;DR — iter loop 戰績

| iter | 主修 bug | 新發現 | Binary SHA |
|---|---|---|---|
| iter1 | BUG-002 (stats blocker) + BUG-001/004 (major) | — | (lost) |
| iter2 | tester 驗證 iter1 PASS | BUG-013 + BUG-014 | (same as iter1) |
| iter3 | BUG-003/013 (Fix D/E) | INFRA-01 (WSL Xvfb 2/3 fail rate) | `f2d6766a...` |
| iter4 | BUG-007 (multi-class slash) + portable bundle | 啟動.bat encoding/CRLF bug | `444f3835...` |
| iter5 | Fix G (geometry consistency) + Fix G2 (3 OOB crashes) | — | `b4d9c31f...` |

**Net**: 13 個 iter1 bugs 解 6 個 + 解 iter4/5 新出 4 個。仍 open 5 cosmetic + 1 INFRA。

---

## 1. 跨平台 memory safety (最重要 — iter5)

**核心觀察**: WSL Linux scummvm 跑得很爽，user Windows 環境同個 binary 點兩下就 crash。

**根因**: Linux glibc heap 對 array OOB read 通常返回隨機 bytes (silent corruption)，行為「正常」；Windows MinGW heap 嚴格，OOB 直接 segfault。

**EOB1 vs EOB2 共用 array 是雷區**:
```cpp
// gui_eob.cpp 內 EOB2 ZH-only 字串 lookup 經常索引 [3], [6] etc
_screen->printShadedText(_characterGuiStringsHp[3], ...);  // 食 food
_screen->printShadedText(_characterGuiStringsSt[6], ...);  // petrified
```

但 provider 註冊 array size 不同:
- `eob1_dos_chinese.h:564`: `kEoB1CharacterGuiStringsHpDOSChinese[2]` (EOB1 size 2)
- `eob2_dos_chinese.h:510`: `kEoB2CharacterGuiStringsHpDOSChinese[4]` (EOB2 size 4)

EOB1 ZH 走到觸發 [3] 的 code path → OOB read。Linux 容忍，Windows 死。

**Action**: 把所有 `_characterGuiStrings*[idx]` 含 idx >= EOB1 array size 的存取**全部** gate `_flags.gameID == GI_EOB2`，EOB1 fallback 到合法 index。

**通用教訓**:
- Cross-platform 專案絕對不能只在 Linux WSL 驗證
- Memory-touch 類 bug (array OOB / null deref / use-after-free) 必須在 target platform 重測
- ScummVM 共用 string provider 設計 (kEoB1*/kEoB2* 不同 array size) 是潛在 OOB 來源，特別跨 game variant 共用 GUI code 時

---

## 2. 多 gate 一致性 (iter3 → iter5)

**核心觀察**: 修一個 `GI_EOB2 && ZH_TWN` gate (e.g. chargen Fix B/D/E) 常常漏掉**相關的**第二個 gate。

**Case study**: iter5 大黑塊 bug
- iter3 Fix E 改 `chargen.cpp:772` 把 name input position 從 lower (24,100) 放寬到 upper (19,81)
- BUT `gui_eob.cpp:1576-1580` 的 `_textInputHeight=9` (EN 默認) 仍 gated `EOB2 && ZH_TWN`
- 結果: EOB1 ZH 用 EN-高的 input strip 配 15-tall CJK 字 → getTextInput 內部 copyRegion 只備份 9 px → 字底 6 px 殘留 → cursor blink 累積 → 大黑塊

**修法 (Fix G)**: gui_eob.cpp:1576-1580 5 個 const 同步放寬。

**通用 audit pattern**:
```bash
grep -rn "GI_EOB2.*ZH_TWN\|ZH_TWN.*GI_EOB2" engines/kyra/
```
改 ZH gate 時，**列出全部相關 gate**，逐一評估是否要同步放寬。漏一個就是下一個 regression。

---

## 3. kSpecial=5 atomic flip 的陷阱 (iter4 → 5)

**Plan**: 引入 `kChineseFan = 5` special 變種，讓 EOB1 ZH 走獨立 KYRA.DAT need-list，unblock 物品名/intro 翻譯。

**Attempt**: 改了 enum + games.cpp + 90 個 resources.cpp ZH_TWN providers (kNoSpecial → kChineseFan) + getSpecialID。**KYRA.DAT 生成 fail**: `ERROR: Could not find need 149 for game 305A`。

**根因**: ScummVM resource lookup encoding 把 special 編進 filename hash:
```
(game<<24) | (platform<<20) | (special<<16) | (id<<4) | lang
```

當 game tuple 變 `{EOB1, DOS, kChineseFan, ZH_TWN}`，**lang-agnostic UNK_LANG providers** (e.g. CGA mapping tables, monster stats) 仍 tagged `kNoSpecial` — filename hash 不匹配 → lookup miss → ERROR。

`grep "kEoB1, kPlatformDOS, kNoSpecial" resources.cpp` = **161 個 UNK_LANG providers** + 90 個 ZH_TWN providers。要 fully wire 起來需 duplicate 那 161 entries 或加 fall-through。

**結論**: Phase 2 kSpecial=5 atomic flip 工作量比 design 預期大 5×。**REVERT 全部**，未來改用 **Plan B5 per-resource opt-in** — 一次只加一個資源 (e.g. kEoB1ItemNames)，給 EN/DE/IT 補 DOS provider (從 PAK 抽出英文)，加到 shared `eob1FloppyNeed[]`。

**詳**: `design-reviews/kSpecial-chinese-fan-design.md` "Lessons learned" 段。

---

## 4. WSL build hygiene (iter4 慘痛)

**核心觀察**: WSL 有**兩個獨立 in-tree clone**:
- `/root/scummvm_work/scummvm/` — Linux build
- `/root/scummvm_work/scummvm-win64-build/` — Win cross-build

兩邊**不共用 source**，各有 chargen.cpp 副本。改 source 只 cp 到 Linux clone → Win build 30 秒 "成功" link 出 binary，但其實沒重編 chargen.o (mtime 舊)，只 LINK 出 stale binary。

**症狀**: iter3 已 ship 的 Win binary 跟 iter1 行為一樣 (Fix D 沒生效)。

**修法**:
```bash
# 改 source 後 BOTH clone 都要 cp
cp /mnt/d/...src/foo.cpp /root/scummvm_work/scummvm/foo.cpp
cp /mnt/d/...src/foo.cpp /root/scummvm_work/scummvm-win64-build/foo.cpp
```

**Better**: 改成 out-of-tree build (Win build dir 直接讀 Linux source 樹)。

---

## 5. .bat 啟動腳本編碼 + 行尾雙雷 (iter4)

**核心觀察**: user 雙擊 cp950 Windows 上的 `啟動.bat` 看到 garbled 中文錯誤訊息，**兩個獨立問題疊加**:

1. **編碼**: Edit / Write tool 寫 UTF-8 (3 bytes/CJK)，cmd 用 cp950 (2 bytes/CJK) 讀 → quote 不對齊
2. **行尾**: PowerShell here-string `@'...'@` 保留 LF (Unix)，cmd 解析 LF-only `.bat` token 對不齊 → `@echo off` 變 `cho off`

**修法**:
```powershell
$content = @'...'@
$content = $content -replace "`n", "`r`n"  # LF → CRLF
[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::GetEncoding(950))
```

**驗證 checklist**:
- [ ] cp950 ANSI encoding (no BOM, no UTF-8/UTF-16)
- [ ] CRLF line endings (CR count == LF count)
- [ ] First byte ASCII (`@` 0x40 開頭最安全)
- [ ] Dry-run: 把最後 launch 行換 `echo TEST_OK` 後 `cmd /c "$bat"` 看 zero parsing error

---

## 6. Sub-agent loop 心得 (iter1 → 5)

**Workflow**: tester → ux-designer → developer → tester (新 iter)。

**有效**:
- Tester 寫詳細 report markdown，下游 ux-designer / developer 能精準對症
- ux-designer 提 fix 加 risk 分析 + 預期效果，developer 套用 + 加 build status
- 各 agent 工具邊界清楚 (tester 只跑 / 不改 source；developer 不跑 game tester)

**踩雷**:
- **3+ agent 並行潛在 race**: 改同一份 source 會互蓋。我做 iter5 時 spawn 3 agents (tester + name input dev + crash dev)，dev #2 (crash investigator) 動 gui_eob.cpp，dev #1 (name input) 也動 gui_eob.cpp 不同行 — 幸運不衝突，但若 review 沒 layout 區隔會 race。
- **WSL Xvfb 不穩**: iter3 tester 報 ENV-INFRA-01: scummvm 啟動 2/3 機率撞 `SDL_BlitSurface NULL` / `XIO fatal IO error`。Workaround (`-nolisten unix` + `--opl-driver=null` + 5s wait + retry) 寫在 `tools/agent-helpers/driver.sh` 留給後續 iter 用。
- **Linux ≠ Windows verification gap**: iter3 tester 跑遍但漏 BUG-014/Bug B 因 (a) coverage gap (沒進 inventory) (b) Linux glibc 容忍 silent OOB。iter5 user 實機 Windows 才 expose Bug B。

**Action items**:
- 多 agent 並行時，**明確劃分 file 邊界** (e.g. agent A 動 chargen.cpp，agent B 動 eobcommon.cpp，agent C 只動 docs)
- 高風險 memory bug **必 Windows-native 路徑驗證** (e.g. PowerShell 跑 scummvm.exe，stderr 抓 crash trace)，不能只信 WSL

---

## 7. Resource provider 結構速查 (devtools/create_kyradat)

每次想加新 string 翻譯都要先理解這個:

```
games[]               (devtools/create_kyradat/games.cpp:eob1Games)
  → {kEoB1, kPlatformDOS, kNoSpecial, ZH_TWN}    # 描述「這 game variant 存在」

gameNeedTable[]       (games.cpp:gameNeedTable)
  → {kEoB1, kPlatformDOS, kNoSpecial, eob1FloppyNeed}    # 此 game variant 要哪些 resource IDs

eob1FloppyNeed[]      (games.cpp:1451)
  → [kEoBBaseChargenStrings1, kEoB1MainMenuStrings, ...]    # resource IDs list

resources.cpp providers
  → {kEoB1MainMenuStrings, kEoB1, kPlatformDOS, kNoSpecial, ZH_TWN, &kEoB1MainMenuStringsDOSChineseProvider}
  → kEoB1MainMenuStringsDOSChineseProvider points to kEoB1MainMenuStringsDOSChinese[]

eob1_dos_chinese.h
  → static const char *const kEoB1MainMenuStringsDOSChinese[N] = { "中文字串", ... };
```

**加新翻譯資源 (e.g. kEoB1ItemNames)**:
1. 確認 `eob1FloppyNeed[]` 含這個 resource ID — 沒有就加 (但會 break EN/DE/IT build 若它們沒對應 provider)
2. 在 `eob1_dos_chinese.h` 加 `kEoB1ItemNamesDOSChinese[]` 字串陣列
3. 在 `resources.cpp` 加 provider entry tagged `kEoB1, kPlatformDOS, kNoSpecial, ZH_TWN`
4. 重 build devtools → regen KYRA.DAT
5. 引擎不需重 build (resource 是 data driven)

**踩雷**: 步驟 1 必 review EN/DE/IT/ZH 是否都有 provider — 沒有的 lang 要 alias 英文 provider (e.g. ManDef)。

---

## 8. iter3 design review pattern (推薦繼續用)

各 iter `applied-iter*.md` 標準段落:
```
# Build applied — iter<N> (date)

## Fixes applied (Fix A/B/C/...)
### Fix X — BUG-NNN: <title>
- File / lines
- Edit description
- Risk + verified expectation

## Build status
| Target | Status | SHA-256 |
|---|---|---|
| Linux | OK | ... |
| Windows | OK | ... |

## Deferred (bug, why deferred, doc ref)
## Recommendations for iter N+1
```

**為什麼 effective**: developer agent 給 tester / 下次 dev 的 context 直接拷貝就能繼續，零 ramp-up time。

---

## 引用文件

- 各 iter applied: `design-reviews/applied-iter1.md` (iter1 Fix A/B/C), `applied-iter3.md` (Fix D/E), `applied-iter4.md` (Fix F + portable + .bat 雙雷), `applied-iter5.md` (Fix G/G2)
- Design analysis: `bug-009-analysis.md` (CAMP 營：), `kSpecial-chinese-fan-design.md` (Phase 2 atomic flip failure + Plan B5)
- Test reports: `test-reports/report-iter1-baseline.md`, `report-iter2-baseline.md`, `report-iter3-baseline.md`
- 通用 pitfalls: `docs/pitfalls.md` (更新版含 iter4/5 教訓)
- Future work: `docs/future-work.md`
