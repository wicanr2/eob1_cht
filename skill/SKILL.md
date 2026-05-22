---
name: eob1-cht
description: 接續 1991 Westwood/SSI 魔眼殺機 1 (Eye of the Beholder 1, EOB1) 繁體中文化 reverse engineering 與 patch 工作。當使用者提到 EOB1、魔眼殺機 1、Eye of the Beholder 1、EOB.EXE 字串翻譯、MCGA.OVL 字型 hook、Big5/cp950 in-place patch、CHINFONT.FNT 16x14 glyph、想翻譯 CAMP menu (休息隊伍/記憶法術)、角色生成 (戰士/守序善良)、咒語、戰鬥訊息、想加 16x14 真中文取代 8x8 byte-pair 中文，或處理同類 1991 年 Westwood DOS RPG (OVL+EXE 雙層架構) 字型 hook + 字串 in-place patch 時觸發。也涵蓋同類技術: x86 16-bit MZ overlay prefix-hook、Big5 endianness 對齊 (subset BE-stored / x86 LE-read)、stateful per-call Big5 detection (lead saves / trail renders)、const patch 把執行期 scratch buffer 推離 hook 區域、binary search 字模 subset 格式。**主動觸發**: 即使使用者只說「繼續做 EOB1」或「擴充翻譯」也要套用此 skill。
---

# EOB1 繁體中文化

1991 Westwood Studios / SSI 魔眼殺機 1 (Eye of the Beholder 1) 的 BIG5 in-place 翻譯 + 真 16x14 中文字模渲染 hook。這 skill 把破解流程包成可重用知識。

## 核心檔案位置

- **遊戲 ENG 版**: `D:\SteamLibrary\steamapps\common\Forgotten Realms The Archives - Collection One\games\Eye of the Beholder ENG\GAME\EYE\`
  - 關鍵檔: `EOB.EXE` (264KB)、`MCGA.OVL` (~12KB)、`CGA.OVL`/`EGA.OVL`/`TGA.OVL`、`FONT8.FNT`、`FONT6.FNT`、`TEXT.DAT`
- **工作目錄**: `C:\Users\原來是個胖仔\eob_analysis\`
- **EOB2 繁中（隱月傳奇）參考來源**: `E:\dos1866\eob2`
- **MM4 CHINFONT.FNT** (字模來源,跟 EOB2 同格式 16x14 13671 glyph): 從 EOB2 dir 取得，或 MM4 dir

## 兩種翻譯策略

### Plan 1-2 (byte-pair Chinese, 8x8 cramped)
- MCGA.OVL file 0x27FA: `25 7F 00` → `25 FF 00` (and ax, 0x7F → and ax, 0xFF) 不剝高 bit
- FONT8.FNT 擴充: 256B offset table + 128 glyphs → 512B table + 256 glyphs，高 128 索引塞 byte-pair Chinese (每 Big5 字拆 2 個 8x8 字模)
- 優點: 純資料 patch 不動 code,所有畫面都 work
- 缺點: 字小看不清楚

### Plan 3 (真 16x14 Chinese via orig_blit prefix hook) **✓ 已 work**
- MCGA.OVL 在 orig_blit (image 0x241E) 入口安裝 stateful hook
- Lead byte (0xA1-0xFE) 進來 → save+pending, return without render
- Trail byte 進來 → 查 subset → render 16x14 at (x-8, y), clear pending
- ASCII 直接 fall through 到 orig_blit
- 需要把 EOB 執行期 scratch buffer 從 image 0x2C40 推到 0x4000 才能安全放 hook (見 const patch)

### V2: BoutiqueBitmap9x9 9x8 render **✓ 推薦版**
- 改用 BoutiqueBitmap9x9 TTF 字模 (OFL 1.1, 12858 字)
- 字模 9 cols × 8 rows 較小，行距 8+ px 不會疊
- Render at (x-4, y) — 9-wide 對 16-px Font8 lead+trail 居中
- Subset entry 從 30B 縮成 20B (codepoint 2B + bitmap 18B)
- Search loop `add si, 30` → `add si, 20`
- 詳細在 `references/v2_9x8_render.md`

## Dependencies

```bash
pip install pillow freetype-py
```

**CRITICAL**: freetype-py 不認 Unicode 路徑 — TTF copy 到 `C:\Temp\Boutique.ttf` (extract script 自動處理).
**CRITICAL**: 必須 Big5 codepoint → cp950.decode → Unicode 再給 freetype，不然全部 missing glyph (方框).

## 完整流程 (V2, 推薦)

**所有步驟一次跑** (`install_full.py`):
```bash
cd C:\Users\原來是個胖仔\eob_analysis
python scripts\install_full.py
# 跑遊戲: D:\...\run-game.bat
```

或手動分步:
```
1. 取 pristine MCGA.OVL → 套 Plan 1-2 byte patch 得 MCGA_CHT.OVL (baseline)
2. python scan_strings.py → strings_scan.json (616 條 ASCII 字串)
3. 編輯 generate_patches.py 加翻譯到 TR / COMPOUND dict
4. python generate_patches.py → full_patches.json
5. python patch_exe_strings.py EOB1_ORIG.EXE full_patches.json EOB1_FULL_CHT.EXE
6. (加 EXE strip patches: install_full.py 內 patches `25 7F 00` → `25 FF 00` 共 7 處)
7. python extract_boutique9x9.py full_patches.json 9 → boutique_subset.bin
8. python build_v2_9x8.py → MCGA_V2_9x8.OVL (自動 copy 到 game)
9. 複製 EOB1_FULL_CHT.EXE → 遊戲 EOB.EXE
10. 跑 DOSBox 驗證
```

## V1 (16x14, 已 deprecated)

V1 用 MM4 CHINFONT.FNT (16x14 字模)。當 line spacing 太緊 (Font6) 會疊。已被 V2 取代但 V1 scripts 還在: `build_final_hook.py`, `extract_subset_font.py`, `build_hook_subset.py`.

詳細 step-by-step 在 `references/workflow.md`。

## 已知區段與翻譯目標

EOB.EXE 文字總量 <25KB (翻譯成 BIG5 ~12-15KB):
- **0x22831-0x22E54** UI/系統訊息 ~70 條 1.5KB (CAMP menu / Preferences / Load/Save)
- **0x2628E-0x269C0** 屬性/種族/職業/陣營/咒語 ~120 條 (Character Generation)
- **0x269C7-0x2A310** 戰鬥訊息/標題 ~150 條
- **0x2AE6D+** NPC 名與選項

詳細 offset table 在 `references/exe_strings.md`。

## 已知踩坑 (省下次時間)

### Big5 endianness (**最容易踩**)
Subset 用 `struct.pack(">H", cp)` 存 BE bytes `[lead, trail]`。x86 `cmp word cs:[si], bx` 是 LE-read = `(trail<<8) | lead`。所以 hook 建 bx 時:
- ❌ 錯: 先 `mov al, lead; mov ah, trail` 再 `xchg al, ah` 再 `mov bx, ax` (這變 BE 整數,跟 LE-read 不符)
- ✓ 對: `mov al, lead; mov ah, trail; mov bx, ax` (ax = ah:al = trail:lead = LE-read value)

### Const patch (不做的話 hook 被覆寫)
MCGA.OVL image 0x0C4C 有 `BB 38 2C` = `mov bx, 0x2C38`。後續 `shr bx, 4; inc bx` 算成 paragraph 數 (0x2C4)，回傳給 EOB.EXE。EOB 把 (CS_seg + 0x2C4):0 onwards 當 scratch buffer，從 image 0x2C40 開始寫。

**Fix**: patch file 0x0E4D..0x0E4E `38 2C` → `00 40`，scratch 推到 image 0x4000+。Hook 放在 image 0x2D80 就安全。

### Search loop 的 jump offset
```asm
search:
  cmp word cs:[si], bx     ; 3 bytes
  je found                  ; 2 bytes, +8 (跳過下面 3+2+3 bytes)
  add si, 30                ; 3 bytes  
  loop search               ; 2 bytes, -10 (跳回 cmp 起點 — 不是 -9)
  jmp normal_ascii          ; 3 bytes (rel16)
found:
  ...
```

### 不同 hook 位置都會壞
- Hook 放 OVL 內任何「閒置」位置 (e.g., img 0x020B 287-byte 零區) 都會被執行期覆寫
- 放在 image 0x2C38 + 21 bytes 大小剛好不會被覆寫 (歷史巧合,不可靠)
- 放在 image 0x3000 也壞
- **可靠做法**: const patch + hook 放在 image 0x2D80 (在 EOB scratch boundary 推走後安全)

### MZ header 改 e_cp 要同步 e_cblp
```python
new_ecp = (len(data) + 511) // 512
data[4:6] = new_ecp.to_bytes(2, 'little')
e_cblp = len(data) - (new_ecp - 1) * 512
if e_cblp == 512: e_cblp = 0
data[2:4] = e_cblp.to_bytes(2, 'little')
```
否則 DOS 不正確載入。

### Hook 路徑 vs 0x27FD 路徑
- OVL 的 per-char dispatch (0x27FD `call orig_blit`) 只走 Plan 1-2 樣式 menu
- EOB.EXE 自己也直接 far-call orig_blit (CAMP/角色生成等)
- 所以 hook 一定要裝 orig_blit prefix，不要裝 0x27FD call site (會漏 EOB-direct 路徑)

### Cosmetic 限制
- 14-row 字模高度有時蓋下一行 (e.g., SELECT CLASS menu 行距 10 px)。可改 render 高度 8 rows 試試
- 字模前偶有「J」殘留 (某條 lead byte 路徑沒被攔到 — 待 trace)
- 某些 menu primary options (CAMP 主選單) baseline 就空白，不是 hook 問題

### DOSBox 自動化
- SendKeys/PostMessage 都被 DOSBox 吃 — mouse 必須先 click window center 取得 focus
- `PAUSE6K.COM` + `enter41Y.COM` 在 game.conf [autoexec] 可自動答 4=VGA / 1=AdLib / y=Mouse 啟動提示
- `PrintWindow(hwnd, hdc, 2)` 可截 DOSBox 視窗即使不是 foreground
- EOB palette 不是標準 VGA: color 4 顯示為綠色 (不是紅), color 5 不容易看，color 14/15 醒目易見

詳細踩坑分析在 `references/pitfalls.md`。

## 工具腳本 (scripts/)

- `patch_exe_strings.py` — JSON-driven EOB.EXE 字串 in-place patcher (Big5 encode + null pad + verify orig)
- `build_final_hook.py` — 完整 Plan 3 hook builder (orig_blit prefix + stateful Big5 + 16x14 render + const patch + extension)
- `extract_subset_font.py` — 從 MM4/EOB2 CHINFONT.FNT 抽出 patches.json 用到的字模
- `build_hook_subset.py` — subset binary 打包 (BE codepoint + bitmap, sorted)
- `decode_chinfont.py` — CHINFONT.FNT XOR 解密 + render preview
- `restore_baseline.py` — 把遊戲還原成 MCGA_CHT.OVL + RAW_BIG5 EOB.EXE (測試完畢恢復用)
- `verify_install.py` — disassemble 已安裝 OVL，確認 hook bytes / const patch / call site 都正確

## 重要參考

- `references/workflow.md` — step-by-step 完整流程
- `references/exe_strings.md` — EOB.EXE 字串 offset 表 (已掃描的區段)
- `references/hook_internals.md` — orig_blit prefix hook 組合語言細節
- `references/pitfalls.md` — 完整踩坑清單與 fix

## Demo: 25 條 POC 翻譯

`demo_patches.json` 範例已驗證 work:
```json
{
  "0x022840": {"orig": "Rest Party", "new": "休息隊伍", "desc": "Rest menu"},
  "0x02284B": {"orig": "Memorize Spells", "new": "記憶法術", "desc": "..."},
  "0x026363": {"orig": "FIGHTER", "new": "戰士", "desc": "Class"},
  "0x026438": {"orig": "LAWFUL GOOD", "new": "守序善良", "desc": "Alignment"}
}
```

擴充完整翻譯時把所有要翻的字串加進去，subset 會自動跟著擴。
