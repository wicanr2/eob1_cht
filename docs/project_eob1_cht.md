---
name: 魔眼殺機 1 中文化評估
description: EOB1 英文版中文化可行性分析、文字資產位置、可重用的 EOB2 中文化資產
type: project
originSessionId: 65334092-a273-42ba-b37d-438e50371b86
---
**路徑**
- EOB1 英文: `D:\SteamLibrary\steamapps\common\Forgotten Realms The Archives - Collection One\games\Eye of the Beholder ENG\GAME\EYE`
- EOB2 繁中 (隱月傳奇): `E:\dos1866\eob2`（乾淨）
- EOB2 繁中（壞軌備用）: `D:\03_game_tmp\魔眼殺機2-隱月傳奇\eob2`（CHINFONT.COD 與 START.EXE 有 CRC error）
- 抽取工作目錄: `C:\Users\原來是個胖仔\eob_analysis\`

**關鍵格式（已驗證）**
- `TEXT.DAT`：N×uint16 LE offset table 開頭，第一個 offset = table 大小 → 推算條目數，字串 null-terminated。EOB1 51 條 16105 B、EOB2 中文 122 條 15974 B（同結構，可直接編輯）
- `CHINFONT.FNT` (410130 B)：13671 個 30-byte glyph，首 2 B = BIG5 codepoint LE，後 28 B XOR 加密（key = codepoint LE 交替）。**與 MM4 CHINFONT.FNT 完全同格式**，直接套用 `mm4/mm4/XEEN/decode_mm4_font.py`
- `CEOB.PAT` (46050 B, 1535 glyph)：30-byte/glyph 但 XOR 加密方式不同（待 RE），補充字模
- `EXTBIG5.COD` (20 B)：10 個 BIG5 codepoint 擴充表
- Westwood PAK：4-byte LE offset + null-terminated 檔名陣列 + raw 資料
- `TEXT.CMP`：Westwood Format80 LZW 壓縮（公開格式）

**EOB1 EOB.EXE 文字位置（已掃描）**
- 0x22831–0x22E54：UI/系統訊息（~70 條，~1.5KB）
- 0x2628E–0x269C0：屬性/種族/職業/陣營/咒語（~120 條）
- 0x269C7–0x2A310：戰鬥訊息/標題（~150 條）
- 0x2AE6D+：NPC 名與選項

**EOB1 文字總量 < 25 KB**（純翻譯）— 翻成 BIG5 後 ~12-15 KB

**已確認 EOB2 START.EXE (336864 B) 引用** `CHINFONT.FNT` (0x5B21) 與 `EXTBIG5` (0x5B3B) — 可作為 EOB1 字型 hook 的參考實作

**核心難關**：EOB1 EOB.EXE 是 264KB DOS real-mode exe，要 hook 字型繪製函式插入 BIG5 雙字節判斷 + glyph lookup，DOS 常規記憶體載不下 410KB 字型 → 需 EMS/XMS 或 disk-cached 設計

**反組譯成果 (2026-05-16, Python capstone)**
- **DGROUP base = paragraph 0x212E** (image 0x212E0)，由 reloc 分析得 (771 refs 最高)
- Font loader: image 0x1A475 (caller `lcall 0x1A47:0x0005`)，讀檔頭 0x102 取 width，0x103 取 height
- setActiveFont: image 0x1A5D9，把 font far ptr 存 [0xFE4E/FE50]，height [0x8100]，width [0x8101]
- Active font slots: Font8 在 [0xFE5A/5C]，Font6 在 [0xA9C0/C2]
- Print top-level: image 0x1E47A (`\r` 處理、multi-line)
- Print loop: image 0x1E222 (cursor 推進、viewport)
- Generic rect blit (clip): `lcall 0x19F3:0x000E` (image 0x19F3E)
- **實際 pixel blit: `lcall [0x806A]` 與 `lcall [0x8052]`** (indirect far ptr) ← 主要 hook 點
- FONT8.FNT 格式：2B filesize + 256B offset table (128 entries × 2B) + 2B (w,h) + 128 glyphs × 8B

**Big5 hook 策略 (建議)**
1. 在 0x1E222 入口 inject lead-byte 判斷 (0xA1-0xFE)
2. 是 Big5 → 讀次 byte 組 codepoint → 從 CHINFONT subset 取 16×14 bitmap → 自製 blit (或重用 [0x8052] 機制)
3. **準備 subset CHINFONT**：只含實際翻譯用到的字 (~3000 unique 字 × 30B = 90KB) 以避過 640KB 常規記憶體限制
4. 一般 ASCII byte → 原路徑

**字串 in-place patch 已驗證可行** (`patch_exe_strings.py`)
- 25/25 demo 翻譯成功 (休息隊伍/記憶法術/守序善良/戰士…) — Big5 每字 2B 比英文短，slot length 全部夠用
- 工具流程: JSON {file_off_hex: {orig, new, desc}} → 驗證 orig 符合 → 替換 + null pad

**檔案在** `C:\Users\原來是個胖仔\eob_analysis\`
- format80.py / decode_chinfont.py / mz_disasm.py / analyze_relocs.py / find_dgroup.py / patch_exe_strings.py
- demo_patches.json (25 條 POC 翻譯)
- EOB1_PATCHED.EXE (尚不可執行，需先做字型 hook)
- chinfont_sample.png (BIG5 Level 1 render 驗證)

**TEXT.CMP 是圖片不是文字！**（解壓出 64000B = 320×200 palette indexes）— 真實文字只在 EOB.EXE + TEXT.DAT (51 條) + ITEM.DAT (80 個物品名) + LEVEL*.INF (各關告示)

---

## Plan 3 (真 16×14 hook) 工程進度 (2026-05-16 晚)

**已 work 的階段 (Plan 1-2)**：EOB.EXE 文字 patch + FONT8 擴 256 字 + bit-OR fold 字模 + 4 個 OVL 內 strip 關閉 + INTRO/FONT6 配套修補 → 中文字確實有顯示但 8×8 太擠

**Plan 3 POC 卡關中** — 想用 5-byte far call + 短 jmp 從 image 0x1E498 攔截到注入的 15-byte hook，但**不論放 hook 在 image 0x067C 或 0x01F280，遊戲都會在 INTRO 後跳「unable to load font8.fnt」**

**POC hook 設計 (` apply_hook_poc.py`)**：
- 攔截點 image 0x1E498 (印字函式入口的 high-bit test) 寫 `9A off off seg seg EB 0C`
- 新增 1 條 MZ relocation entry (在 file 0x275E 寫 4 bytes, e_crlc 2504→2505) 讓 seg 載入時 fix-up
- 15-byte hook：A→Z 替換 (push ax / mov al,[bp-7] / cmp 'A' / jne+5 / mov al,'Z' / mov [bp-7],al / pop ax / retf)
- 首版 hook 有 off-by-one bug (`75 04` 跳到指令中間) 已修為 `75 05`
- 兩個放置位置都死：0x067C (paragraph 0x67) 與 0x01F280 (paragraph 0x1F28)

**待 debug 假設**：
1. MZ relocation 增加可能破壞 EXE 載入 (DOSBox 對非標準 reloc 數的容忍度?)
2. Hook 位置仍在 BSS init 區會被清零
3. Far call 後 retf 的 CS:IP 計算錯
4. 我寫的 lcall 編碼是 9A off_lo off_hi seg_lo seg_hi — 順序是否正確 (Intel real-mode lcall ptr16:16 immediate operand)？

**首要 debug 步驟 (下次)**：
1. 用 DOSBox `-conf` debug build 跑、或 DEBUG.COM 載入 EOB.EXE 設斷點到 image 0x1E498，看 lcall 後 CS:IP 實際指到哪
2. 先試「don't add reloc, just hardcode seg 假設 PSP+0x10」看是不是 reloc bug
3. 或先用 NEAR call (E8 rel16) 攔截到 image 同 segment 內的位置 — 不需 reloc
4. 終極備案：把 hook 寫進 EXE FILE 尾端，修 MZ header e_cp/e_cblp 讓 DOS 多載入 bytes (但需擴 min_alloc)

**檔案**：
- `EOB1_ORIG.EXE` — 純原版
- `EOB1_HOOK_POC.EXE` — POC v1/v2 far call + reloc (失敗,bytes count bug)
- `EOB1_HOOK_INLINE.EXE` — POC v3 inline (A→Z, 19-byte 原地替換)
- `EOB1_HOOK_ALL_Z.EXE` — POC v4 inline (每字→Z, 用來診斷哪些路徑用 0x1E47A)
- `apply_hook_poc.py`, `apply_hook_poc_inline.py`

---

## Plan 3 進度補充 (2026-05-17 凌晨)

**重大發現**：先前 POC「失敗」的真正原因 — **FONT6.FNT 沒還原回 1028 bytes**（之前擴成 2052 bytes 的版本還留著），不是 hook 機制問題。loader 拒收 → "Unable to load font Font8.fnt"（錯誤訊息固定顯示 Font8 即使實際失敗的是 FONT6）。

**POC v3 inline hook 證實 work**：
- 19-byte 原地替換在 0x1E498-0x1E4AA (純 inline, 不動 MZ reloc, 不動 segment)
- 遊戲正常啟動進到 dungeon view, 沒 crash
- BUT 角色名「ALLABAR/VALANAU」未被 A→Z 替換, intro 字幕「present」也未變 → **0x1E47A 不是這些 text 的渲染路徑**

**0x1E47A 範圍**：似乎是某種「高階格式化字串列印」(local 0xAC = 172 bytes 看像 sprintf buffer)，可能用於 TEXT.DAT 內 narrative dialog；character name / sidebar / intro 都走別的路徑

**正確 hook 點 (下次)**：MCGA.OVL 0x27F4 區的 per-char glyph blit loop
```
0x27F4  push cx
0x27F5  push bx
0x27F6  mov al, [es:si]      ; 從字串 buffer 讀下一字
0x27F9  and ax, 0x7F          ; ← 我們已 patch 成 0xFF (Plan 1-2)
0x27FC  push ax
0x27FD  call 0x261E           ; ← glyph blit 函式. Hook 前後攔 Big5
0x27FF  add sp, 2
0x2802  pop bx
0x2803  pop cx
0x2805  add bx, [cs:0x203F]   ; cursor advance
0x280A  inc si
0x280B  jmp 0x27AF             ; loop top
```
這個 loop 是 OVL 內所有 FONT8 文字共用的 dispatch。Hook 此處覆蓋所有 UI / 名稱 / 對話文字。

**OVL 內 free space**：MCGA.OVL = 11832 bytes, 末段可能有 padding (待確認)。或將 hook 放在 EOB.EXE 內，從 OVL 用 far call 跳過去 (need reloc 但這次 OVL 內,不是 EOB.EXE)

**DOSBox 自動化測試踩坑記錄** (省下次時間)：
- SendKeys / PostMessage 都被 DOSBox 吃掉 — 必須先 mouse click DOSBox window center 取得 focus
- 用 `..\pause6k` + `..\enter41y` 在 game.conf [autoexec] 可自動答 4/1/y 提示 (檔案在 GAME/ 目錄: PAUSE6K.COM, enter41Y.COM)
- PrintWindow(hwnd, hdc, 2) 可截 DOSBox 視窗即使不是 foreground

---

## Plan 3 系統性 bisect 進度 (2026-05-17 下午, 額度暫停前)

**Hook 機制完全驗證 OK**（call site patch + OVL extension + tail-jmp）：
- THUNK (3 bytes `E9 E3 F7` @ img 0x2C38) → menu 正常
- V2 (21 bytes: push bp + push 7 regs + pop 8 + jmp orig_blit @ 0x2C38) → menu 正常
- V_EXT_ONLY (擴充 OVL 但不打 call site) → menu 正常

**所有變大/換位置的 hook 都壞 menu**：
- V3b (25 bytes @ 0x2C38, V2 + `mov al,cs:[0x0100]`) → menu 黑
- V3c (25 bytes @ 0x2C38, V2 + 4 NOPs) → menu 黑（**證明跟 cs:mem 指令無關，純粹大小**）
- V_FAR (V2 21 bytes 但放到 img 0x3000) → menu 黑（**位置也要剛好在 0x2C38**）
- V_INSIDE (V2 21 bytes 放 pristine OVL 內部零區 img 0x020B, 不擴充) → menu 黑

**關鍵發現**：pristine OVL 在 img 0x0C4C 有 `mov bx, 0x2C38; shr bx, 4; inc bx` (image 0x0C4C-0x0C53)，計算 `bx = 0x2C4` 後 retf。這函式幾乎肯定回傳「end-of-image paragraph」給 EOB.EXE 用做 scratch buffer 起點。EOB 之後寫 (CS+0x2C4):0 onwards = 從 image 0x2C40 開始 → 蓋掉我們的 hook。

V2 (21 bytes, 0x2C38..0x2C4C) 之所以「剛好能跑」可能是 menu 已先 render 完才被覆寫；V3c 多 4 bytes 跨過某個臨界點。或者其他更深的原因尚未釐清。

**Patch 位置（不要再迷路）**：
- 攔截 `call 0x241E` (NEAR call 對 orig_blit) 在 OVL file offset **0x27FD** = image 0x25FD
- orig_blit 真正位址是 **image 0x241E**（不是先前筆記裡的 0x261E — 那是錯的）
- OVL 內**只有 1 個** 到 0x241E 的 call site，就是 0x27FD
- 原 OVL 11832 bytes, 全是 code, 沒有 padding tail; 287-byte 零區在 img 0x020B 但**疑似 runtime buffer**（V_INSIDE 證實放 hook 進去也壞）

**檔案** (`C:\Users\原來是個胖仔\eob_analysis\`)：
- `build_hook_peekahead.py` — 完整 Big5 hook builder (`hook_peekahead.bin` 1793 bytes)
- `build_thunk_hook.py` / `build_thunk_v2.py` / `build_v3.py` / `build_v3b.py` / `build_v3c.py` / `build_v_far.py` / `build_v_ext_only.py` / `build_v_inside.py` — bisect 變體
- `MCGA_THUNK.OVL` / `MCGA_THUNK_V2.OVL` / `MCGA_V3*.OVL` / `MCGA_VFAR.OVL` / `MCGA_EXT_ONLY.OVL` / `MCGA_INSIDE.OVL`
- `MCGA_CHT.OVL` (pristine + Plan 1-2 byte patch, 11832 bytes) — **恢復這個給遊戲就還原**
- `disasm_hook.py` / `find_callsites.py` / `inspect_csbase.py` / `disasm_0c40.py` / `trace_diff.py` / `verify_v_far.py` / `find_free_space2.py` — 分析工具

**下次接續做什麼**：
1. 用 DOSBox debug build / DEBUG.COM 設斷點到 image 0x0C3F 函式，trace caller 是誰、看它怎麼用回傳的 bx=0x2C4 — 確認「scratch buffer 從 image 0x2C40 開始」假設
2. 如果假設正確：把 hook 放在「EOB 不會碰」的位置 (e.g., 修 MZ header 騙 EOB 以為 image 更大讓 scratch 推到更後面；或把 0x0C3F 函式 patch 成回傳更大的 bx 值)
3. 替代路徑：放棄 OVL hook，改在 EOB.EXE 主 print 函式（image 0x1E222）做 inline 19-byte 替換（之前 POC v3 證實 work）— 但需重新分析該位址是否真的會收到全部文字（之前發現它不是 character name 路徑）
4. 已恢復遊戲為 Plan 1-2 OVL，遊戲現在可正常進選單（8x8 byte-pair 中文，但能玩）

---

## ✅ Plan 3 真 16x14 中文成功！(2026-05-17 深夜)

**架構**：const patch + orig_blit prefix hook + stateful Big5 detection

### 關鍵發現流程
1. Const patch (`mov bx, 0x2C38` → `mov bx, 0x4000` at file 0x0E4C) 把 EOB scratch buffer 推到 image 0x4000+ — 解決「hook 在 image 0x2C38+ 會被執行期覆寫」問題
2. Hook 點選 0x27FD call site 失敗：CAMP menu 走別條路徑，沒進 OVL per-char dispatch loop
3. 改 hook 在 **orig_blit prefix (image 0x241E)**：把首 3 bytes `55 8B EC` 改成 `E9 rel16` 跳到 hook，hook 處理完 fall through 時 jmp orig_blit+3
4. Stateful 設計：lead byte 進來 → save，set pending=1，return without render；trail byte 進來 → pending=1 觸發查 subset，render 16x14 at (x-8, y)，clear pending
5. Big5 codepoint endianness：subset 用 `struct.pack(">H", cp)` 存 BE bytes [lead, trail]，但 x86 `cmp word [si], bx` 是 LE-read = (trail<<8)|lead。所以 hook 要建 bx = ah:al where ah=trail, al=lead。**不要做 xchg al, ah**
6. Search loop：`je +8` (跳過 `add si, 30` + `loop` + `jmp normal_ascii` = 3+2+3=8 bytes 到 found)，`loop -10` (跳回 cmp 起點)
7. CAMP menu primary options blank 是 **baseline 就如此** (用 byte-pair Chinese 也一樣) — 跟 hook 無關

### 已驗證成果
- "祈禱法術"、"遊戲" 等已正確 render 成 16x14 中文 (Preferences submenu)
- "MACE TAKEN." 等英文系統訊息正常
- 角色名 (ALLABAR/ARIEL/VALANAU/TENMIYANA) 正常

### 剩餘 cosmetic 問題
- 中文字前面偶有 "J" 殘留字元 (約是 lead byte 走了某條未攔截路徑?)
- 某些 menu primary options 還是空白 (CAMP menu 主選單,跟 baseline 一樣)
- **SELECT CLASS 畫面字模疊到下一行** — 14 px 字模高度 > 10 px menu 行距,造成 "戰士"/"遊俠"/"聖騎"/"牧師" 各行重疊。Preferences 子選單(祈禱法術/遊戲選項等)行距夠寬,渲染正常
- 可能有 double-render: lead byte 透過某條路徑也 render 為 byte-pair 字模,跟 16x14 chinese 疊一起更糊
- 可能 fix 方向: 把 render 改成 8 rows (跟 FONT8 同高,擠但不疊),或者 dynamic 看 line spacing 決定 height

### 關鍵檔案
- `build_final_hook.py` — 完整 hook builder (用最終版)
- `MCGA_FINAL.OVL` — 安裝結果 (17408 bytes)
- `build_hook_peekahead.py` — 原舊版 (用 0x27FD call site,不通用所以放棄)
- `hook_peekahead.bin` / `hook_subset.bin` — subset 字模 (53 字)
- `extract_subset_font.py` + `build_hook_subset.py` — subset 生成工具
- 安裝步驟：
  1. 從 MCGA_CHT.OVL (pristine + Plan 1-2 byte) 開始
  2. Patch file 0x0E4C+1..+2: `38 2C` → `00 40` (const patch)
  3. Patch file 0x261E..0x2620 (= image 0x241E): `55 8B EC` → `E9 rel16` (跳到 hook image 0x2D80)
  4. Place hook bytes at file 0x2F80 (= image 0x2D80)
  5. 擴充 file 到 17408 bytes
  6. 更新 MZ header e_cp/e_cblp

### 下次再做的話
- 找 "J" 殘留是哪個 byte 沒攔到
- 擴充 subset 含全部 25 條翻譯需要的字 (目前缺 3 個標點: 0xA143 0xA147 0xBED0)
- 翻譯更多字串 (memory 提到 EOB.EXE 文字總量 <25KB, 目前只 patch 25 條)
- 處理 character name 路徑 (現在 ALLABAR 等是英文,要改中文需另外 hook EOB.EXE)

---

## ✅ Skill `eob1-cht` 建立 + 完整中文化 v1 (2026-05-18)

**Skill 位置**: `C:\Users\原來是個胖仔\.claude\skills\eob1-cht\`
- `SKILL.md` (主文件)
- `references/`: workflow.md, exe_strings.md, hook_internals.md, pitfalls.md
- `scripts/`: build_final_hook.py, patch_exe_strings.py, extract_subset_font.py, build_hook_subset.py, decode_chinfont.py, verify_full_hook.py, restore_baseline.py

**完整中文化 v1 成果**:
- 掃描 EOB.EXE 出 616 條可翻譯 ASCII 字串
- 翻譯字典 (`generate_patches.py`) 涵蓋 107 條，94 條 patch 成功
- Subset 從 53 字 → 149 字 (build_final_hook.py 改為動態讀 count)
- 已涵蓋: CAMP menu, 屬性, 種族×性別, 職業, 陣營, 主要法術, 部分 Preferences/NPC 訊息

**Pipeline** (完整 step-by-step 在 skill workflow.md):
```
scan_strings.py → strings_scan.json
generate_patches.py → full_patches.json (107 條翻譯字典)
patch_exe_strings.py EOB1_ORIG.EXE full_patches.json → EOB1_FULL_CHT.EXE
extract_subset_font.py CHINFONT.FNT full_patches.json → subset_font.bin
build_hook_subset.py → hook_subset.bin (149 entries)
build_final_hook.py → MCGA_FINAL.OVL (17408 bytes)
複製到 game dir
```

**v1 已知失敗 / TODO**:
- 13 條 `\r` 分隔複合字串 patch 失敗 (e.g., " Save game\r failure!" 是同一條 null-terminated)
- NPC 名字未翻 (Beohram/Kirath/Ileria 等, 保英文好辨識)
- 戰鬥訊息大多未翻 (281 條候選, 翻譯字典只涵蓋幾條範本)
- CAMP menu primary options baseline 就空白 (跟 hook 無關)
- "J" 殘留 / SELECT CLASS 行距字模疊問題待修

---

## 字模尺寸調整實驗紀錄 (2026-05-18)

build_final_hook.py 的 render 部分試過多種尺寸:

| Render | 結果 | 問題 |
|---|---|---|
| 16w × 14h (原版) | Preferences 子選單 OK | SELECT CLASS / 種族選單**字模疊到下一行** |
| 16w × 8h (取中段 rows 3-10) | 仍疊 (race menu 行距 < 8 px) | 種族還是糊 |
| 16w × 6h (取 rows 4-9) | 不疊但**字太扁** | 16:6 = 2.67:1 ratio,看不懂 |
| 12w × 6h (取 cols 2-13 rows 4-9) | 仍扁 | 2:1 ratio,看起來像橫條 |
| 8w × 6h (取 cols 4-11 rows 4-9) | 比例接近方塊但**太小** | 4:3 ratio,字模細節大量損失 |

**使用者建議**: 用 MM3 的縮字方式

### MM3 縮字 approach (見 skill `mm3-cht-font`)

MM3 用 **16x15 glyph** 完整存,但 render 時針對小字型用**降採樣** (subsampling),不是 crop. 具體做法:
- 對每個 row 取每 2 個 pixel 的 OR 結果 (preserves stroke continuity) 
- 或對每隔一 row 跳一 row (取奇/偶 rows)
- 最終 8x8 render 但保留主要筆畫

待研究: 看 mm3-cht-font skill 的 render 路徑,可能能直接套用。

### 下次接續做的事 (優先順序)

1. **改用 BoutiqueBitmap9x9 字模** (重要!) — `eob_analysis/BoutiqueBitmap9x9.ttf` (2.2MB, OFL 1.1 授權,12858 字含全 Big5 L1) 已下載。`extract_boutique9x9.py full_patches.json 9` 抽出 156 字 9x8 subset → `boutique_subset.bin` (3128 bytes, 20B/entry). Preview `boutique9x9_preview.png` 顯示字模清晰可辨。需要做的事:
   - 修 `build_final_hook.py`: subset 格式變了 (entry stride 從 30 改 20、bitmap 大小從 28 改 18 bytes、`add si, 30` 改 `add si, 20`)
   - render 改成 9 cols × 8 rows (or 8x8 簡化) 對應新 bitmap layout
   - 整個替換 CHINFONT.FNT-based pipeline 為 TTF-based
2. **動態高度** — 讀 cs:[0x2032] (font height) 決定 render 大小: Font8(8 tall) → 8x8 chinese, Font6(6 tall) → 6x6 chinese (可選用此替代 #1 或互補)
3. **修 13 條 CR-separated 失敗 patch** — 把 " Save game\r failure!" 當整條翻
4. **擴充翻譯** — 加戰鬥訊息 (281 條) 跟 NPC 對話 (81 條)。NPC 名字保留英文不翻
5. **trace "J" 殘留** — disasm 找哪個 lead byte 沒被攔到

### 字模選項對照

| 來源 | Glyph size | Subset 字數 | 整體判定 |
|---|---|---|---|
| MM4 CHINFONT.FNT (V1) | 16x14 (XOR 加密) | 149 字 | 太大,需 crop 但失真 |
| BoutiqueBitmap9x9 TTF (V2) | 9x8 (OFL) | 365 字 | **現用** |

新工具:
- `extract_boutique9x9.py` — TTF → binary subset (用 PIL,需 `pip install pillow`; freetype-py 可選更精準)
- `preview_boutique9x9.py` — 產生 PNG sprite sheet 視覺確認

---

## ✅ V2 完整中文化 (2026-05-18 凌晨)

**Skill `eob1-cht` 已更新** 包含完整 V2 流程。

### 翻譯成果
- **310 patches 全部成功** (V1 時 94 條, 增長 3.3x)
  - 245 singles + 31 compound (CR-separated)
  - 7 EXE strip patches (`25 7F 00` → `25 FF 00`, 不剝 Big5 高 bit)
- **365 字模 subset** (V1 時 149, 增長 2.5x)
- **9x8 BoutiqueBitmap9x9 字模** (OFL 1.1, 可商用)
- **大致內容**: CAMP / Preferences / 角色生成 (種族×性別 12 種, 屬性 6, 職業 7+, 陣營 9, 法術 ~50)、戰鬥訊息 (templates)、NPC dialog (Heal/Attack/Bribe/Leave 等)、Items (potion / scroll)、Title menu compound、UI 標籤、Status

### Pipeline 改善
**新 `install_full.py`** 一次跑全部 (generate → patch EXE → strip patches → extract subset → build hook → install). 整個流程 ~10 秒。

`generate_patches.py` 升級:
- 用 TR dict + COMPOUND dict 分別管理
- COMPOUND 先 patch (避免 singles overlap)
- 自動偵測 overlap，跳過 singles 在 compound range 內
- 統計 ok/overlap/missing/too_long

### 27 條 compound (CR-separated) 已 patch
特別重要的:
- 0x026B01 Title menu (52B): LOAD GAME IN PROGRESS\rSTART A NEW PARTY\rEXIT TO DOS
- 0x026A5C Preferences (90B): PREFERENCES\r\rRETURN TO GAME\r...
- 0x026A0C Options (34B): OPTIONS\r\rRE-ROLL\rMODIFY\rKEEP\rEXIT
- 0x0269C7 CharGen 標題 (69B): CHARACTER GENERATION\r\rUSE THE ARROW KEYS...
- 多條 dialog: "Are you sure", "Select a character", "Your party needs to rest" 等

### 檔案 (game-installed)
- `D:\...\GAME\EYE\MCGA.OVL` ← `eob_analysis\MCGA_V2_9x8.OVL` (19968 bytes, hook + 365 subset)
- `D:\...\GAME\EYE\EOB.EXE` ← `eob_analysis\EOB1_FULL_CHT.EXE` (含 310 patches + 8 strip patches)

### Backup
- `eob_analysis\backup_v1_0518_0103\` — 舊 V1 12x6 render 狀態
- `eob_analysis\backup_v2_0518_0139\` — V2 9x8 + 310 patches (最新)

### 還沒解的問題
- 剩 239 條 singles 沒翻 (主要是 NPC 名字、技術錯誤訊息、format strings 不適合翻)
- 字模疊行問題: 9x8 在 8+ px 行距 OK, 5-6 px 還是會疊一點
- CAMP menu primary options baseline 就空白 (跟我們無關,EOB 自己 bug 或路徑問題)
- "J" 殘留字符待 trace
- 角色名 (ALLABAR/ARIEL 等) 還是英文,要翻需另外 hook EOB 角色名渲染路徑

### 還可以做的
- 翻譯更多 NPC dialog 段 (用 patch_exe_strings.py + COMPOUND 加 0x02B... 段)
- 翻譯 LEVEL*.INF 各關卡告示 (另一個檔)
- 翻譯 TEXT.DAT (51 條 narrative dialog)
- 翻譯 ITEM.DAT (80 個物品名)
- 處理 V2 字模疊行的最後 case

---

## ✅ V2 完整中文化 (2026-05-18 凌晨 02:00) — FINAL state

**最終成果**: **402 patches 全部 OK** (V1 時 94, V2 早期 310, 持續加翻譯到 402)

### 翻譯統計
- 364 single-string patches (原 245)
- 30 compound CR-separated patches
- 8 EXE strip patches (`25 7F 00` x7, `24 7F` x1)
- 434 字模 subset (從 BoutiqueBitmap9x9 9x8 TTF)
- Hook 7488 bytes + 字模 = MCGA.OVL 21504 bytes

### 涵蓋翻譯內容
- ✅ CAMP menu compounds (Title menu, Preferences, Options, CharGen 標題, 10+ confirmation dialogs)
- ✅ 角色屬性 (力量/智力/智慧/敏捷/體質/魅力)
- ✅ 種族×性別 (人類/精靈/半精靈/矮人/地精/半人 × 男/女)
- ✅ 職業 (戰士/遊俠/聖騎/法師/牧師/盜賊 + 混合職業)
- ✅ 陣營 (9 種)
- ✅ 法術 (~50 個 + 大小寫雙形式)
- ✅ Inventory categories
- ✅ Combat templates (%s hits/misses/dies/casts...)
- ✅ Status (DEAD/UNCONSCIOUS/POISONED/PARALYZED 等)
- ✅ NPC dialog (Attack/Bribe/Leave/Heal Party/Resurrect Dead 等)
- ✅ Setup/intro prompts (Your party is complete, Entering game 等)
- ✅ Error messages (Memory error / file errors)
- ✅ Direction labels (北/南/東/西)
- ✅ Item types (Potion/Scroll/Ring/Wand/Key 等)

### 還沒翻 (intentionally 或 技術原因)
- NPC 名字 (Beohram/Kirath/Ileria/Tyrra/Tod Uphill/Taghor/Dohrum/Keirgar — 角色身份需保留辨識)
- 技術錯誤訊息 (Trying to ... unopened file 等)
- 檔名 (.DAT/.EXE/.OVL/.CMP/.PAK)
- Format-only strings (%lu:%lu, %s, etc.)
- 0x040000+ 區的隨機亂碼 (非真實字串)

### Pipeline
**單一指令完成全部 install**:
```bash
cd C:\Users\原來是個胖仔\eob_analysis
python install_full.py
```
- 從 generate_patches.py 生成 patches → patch EXE → 加 strip patches → 抽 subset → build hook → install

### 檔案備份
- `eob_analysis\backup_v1_0518_0103\` — V1 12x6 (MM4 CHINFONT, 94 patches)
- `eob_analysis\backup_v2_0518_0139\` — V2 早期 (310 patches)
- `eob_analysis\backup_v2_FINAL_0518_0148\` — **本次最終** (402 patches, 434 字模)

### Skill `eob1-cht` 完整內容 (24 files)
- SKILL.md (主)
- references/ (5 個 .md: workflow, exe_strings, hook_internals, pitfalls, v2_9x8_render)
- scripts/ (20+ python tools + TTF + bin)

### 已驗證
- DOSBox 啟動 OK (沒 crash)
- 進入 dungeon view 正常
- 角色名 ASCII 正常顯示
- (CAMP menu primary options 是 baseline 自帶空白問題,跟 hook 無關)
- 中文 Preferences submenu render OK (使用者前次 session 確認)

### 已知 cosmetic 待修
- 字模疊行: 9x8 在 8+ px line spacing OK；< 7 px (Font6) 還是會疊一點
- "J" 殘留 (某條 lead path 還沒攔到,待 trace)
- 字模看起來矮 (8 px tall) — 可考慮 dynamic height based on cs:[0x2032]
- 角色名 (ALLABAR/ARIEL) 仍是英文 — 要翻需另外 hook EOB.EXE 角色名渲染路徑

### 恢復 / 重裝指南

**重新安裝最新 V2** (從備份恢復 source files 後):
```bash
cd C:\Users\原來是個胖仔\eob_analysis
python install_full.py
```

**還原到無 hook 的 Plan 1-2 baseline** (8x8 byte-pair Chinese, 比 v2 更糊但 100% 穩):
```bash
copy MCGA_CHT.OVL "D:\..GAME\EYE\MCGA.OVL"
copy EOB1_RAW_BIG5.EXE "D:\..GAME\EYE\EOB.EXE"
```

**完全還原 pristine 英文版**:
```bash
copy EOB1_ORIG.EXE "D:\..GAME\EYE\EOB.EXE"
# MCGA.OVL 沒 pristine 備份, 用 MCGA_CHT.OVL (只多 Plan 1-2 byte patch)
```

**修改翻譯**:
1. 編 `generate_patches.py` 的 TR / COMPOUND dict
2. `python install_full.py`
3. 跑 `run-game.bat`

**新增字到 subset**:
- subset 自動從 full_patches.json 抽出所需字
- 不用手動管理

### 已驗證 final state (2026-05-18 02:00+)
- Game EOB.EXE: 264480 bytes, 含 402 patches, 8 EXE strip patches
- Game MCGA.OVL: 21504 bytes, hook + 434 字模 subset
- 0x022840 = A5 F0 (休) ✓
- 0x026B01 title compound = B8 FC A4 4A (Big5 start) ✓
- 0x020CA2 strip patch = FF (no high-bit strip) ✓
- orig_blit prologue = E9 (jmp to hook) ✓
- Const patch = 00 40 (scratch pushed to 0x4000) ✓
- Hook at 0x2D80 first bytes = 50 53 51 52 (push ax/bx/cx/dx) ✓
- Hook 含 robustness fix: lead-after-lead 自動 reset state
- build_v2_9x8.py 有 `RENDER_ROWS = 8` 常數 (4-8 可調,8 = 預設, 6 = 適合 Font6 緊行距)

### 一鍵 install / restore .bat (eob_analysis 根目錄)
- `INSTALL_V2.bat` — 跑 install_full.py 把最新 V2 裝到遊戲
- `RESTORE_BASELINE.bat` — 還原 Plan 1-2 baseline (Plan 1-2 OVL + RAW_BIG5 EXE)
- `RESTORE_ORIG.bat` — 完全還原英文 pristine

### Backup snapshots (eob_analysis/)
- backup_v1_0518_0103 — V1 12x6 MM4 (94 patches)
- backup_v2_0518_0139 — V2 早期 (310 patches)
- backup_v2_FINAL_0518_0148 — V2 stable (402 patches)
- backup_v2_robust_0518_0159 — V2 + robustness fix
- backup_v2_FINAL_robust_0518_0206 — V2 含 .bat installers

---

## 🐛 2 個重大 bug 修復 (2026-05-18 ~02:15)

### Bug 1: Robustness fix 反而破壞合法 Big5
之前加的 "lead-after-lead detect" 把 Big5 trail bytes 0xA1-0xFE 誤判為 lead (因為很多 Big5 字 trail 就在 0xA1-0xFE，例如「禱」=0xC3AB)。**移除整段 robustness 代碼**，回到單純 stateful design。

### Bug 2: Subset extract Big5 vs Unicode 混淆 (最致命!)
`extract_boutique9x9.py` 把 Big5 codepoint (如 0xA44F) 直接 `chr(cp)` 給 freetype。freetype 用 Unicode index，0xA44F Unicode 是某 Yi 文字不在 TTF 內 → 所有字都變 missing glyph (那個方框)！

**修法**: Big5 → cp950.decode → Unicode 字 → 再傳 freetype：
```python
hi, lo = cp >> 8, cp & 0xFF
unicode_char = bytes([hi, lo]).decode("cp950")
face.load_char(unicode_char, freetype.FT_LOAD_RENDER | ...)
```

PIL fallback 也有同樣 bug，一併修。

### freetype-py 安裝
原本沒裝，extract 自動 fallback PIL (PIL render TTF 9px 出來都是空白)。
- 裝 `pip install freetype-py` (815KB)
- freetype-py 不認 Unicode 檔案路徑 (`C:\Users\原來是個胖仔\...`) → 把 TTF copy 到 `C:\Temp\Boutique.ttf` 用 ASCII path

### Final state after 2 fixes
- Subset 434 字模 (全部真實 Big5 字模，不再 missing glyph)
- Hook 不再有 broken robustness code
- 402 EXE patches 不變
- 應該真正會看到中文了

### Files updated
- `extract_boutique9x9.py` — Big5→Unicode 轉換修復
- `build_v2_9x8.py` — 移除 robustness fix code
- `C:\Temp\Boutique.ttf` — TTF copy (ASCII path for freetype-py)
- Skill scripts/ 已同步
- Backup: `backup_v2_UNICODE_FIX_0518_0226`

### 驗證證據 (技術)
- `check_installed_subset.py` 確認 game's MCGA.OVL 內 subset:
  - Entry 0 (0xA141, "，"): 點在上左 ✓
  - Entry 1 (0xA143, "、"): 不同 ✓
  - Entry 2 (0xA147, "："): 又不同 ✓
- 之前 freetype 故障時所有 entry 都是同一張「方框」glyph
- 修復後每字模 distinct

### 需要 user 確認 next session
- 必須重啟 DOSBox 才會載入新 OVL
- 進 CAMP / 角色生成 race 選單看應該真的是中文 (不再方框)
- 如果還是方框 → trace 是否有 cache / 第 3 個 bug

### 一鍵 install / restore .bat (eob_analysis/)
- `INSTALL_V2.bat` — 安裝 V2
- `RESTORE_BASELINE.bat` — 還原 Plan 1-2 (相對穩定)
- `RESTORE_ORIG.bat` — 完全還原英文

### 目前可用版本

- `MCGA_FINAL.OVL` 在 game dir,目前是 12w x 6h render
- `EOB1_FULL_CHT.EXE` 在 game dir,有 94 條翻譯
- 翻譯字典 in `eob_analysis/generate_patches.py` (107 條)
- Subset 149 字模 in `hook_subset.bin`
- 還原 baseline: `python scripts/restore_baseline.py` (回 Plan 1-2 byte-pair 中文,可玩但小)

### Skill 完成

`C:\Users\原來是個胖仔\.claude\skills\eob1-cht\` 完整包含:
- SKILL.md
- references/{workflow.md, exe_strings.md, hook_internals.md, pitfalls.md}
- scripts/{build_final_hook.py, patch_exe_strings.py, extract_subset_font.py, build_hook_subset.py, decode_chinfont.py, restore_baseline.py, verify_full_hook.py, demo_patches.json, hook_subset_demo.bin}
