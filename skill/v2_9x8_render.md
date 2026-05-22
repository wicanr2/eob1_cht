# V2: 9x8 BoutiqueBitmap9x9 Render

當 16x14 字模太大蓋到下一行時，改用 BoutiqueBitmap9x9 (9x9 design, 抽出實際 9x8 glyph)。

## Why v2

V1 用 MM4 CHINFONT.FNT (16x14) 字模，問題:
- Font6 行距 6-8 px，14 px 字模蓋下一行
- Crop 到 8/6 rows 失真嚴重
- Crop 寬度也失真

V2 用 BoutiqueBitmap9x9 字模:
- TTF 設計就是 9x9，光柵化在 PIL/freetype-py 為 9x8 (字本來就 8 高)
- OFL 1.1 授權自由使用
- 涵蓋 12858 字含整個 Big5 Level 1
- Render 9 cols × 8 rows，剛好不重疊大部分行距

## Files

- `scripts/BoutiqueBitmap9x9.ttf` — TTF 字型 (2.2MB)
- `scripts/extract_boutique9x9.py` — TTF → binary subset 抽取
- `scripts/preview_boutique9x9.py` — 渲染 PNG sprite sheet 視覺確認
- `scripts/build_v2_9x8.py` — orig_blit prefix hook builder for 9x8

## Subset 格式 (boutique_subset.bin)

Header (8 bytes):
- `CHST` magic (4 bytes)
- uint16 LE count
- uint16 LE glyph_size_bytes (= 18 for 9x8)

Each entry (20 bytes):
- 2 bytes BE codepoint (matches x86 LE-read pattern)
- 18 bytes bitmap = 8 rows × 2 bytes (only 9 bits used per row, MSB first)

9-bit row layout per byte pair:
- Byte 0: bits 7..0 → cols 0..7
- Byte 1: bit 7 only → col 8 (bits 6..0 unused)

## Hook 變更 from V1

### Subset 相關
- `mov cx, COUNT` 從 `B9 35 00` (53) 改成 `B9 XX YY` (動態 count)
- `add si, 30` (V1) → `add si, 20` (V2) — 每 entry 20 bytes

### Render 變更
V1 (16x14):
```
mov cx, 14
row:
  mov ah, cs:[si]
  mov dl, cs:[si+1]
  add si, 2
  mov cx, 8; left loop (shl ah, plot)
  mov cx, 8; right loop (shl dl, plot)
  add di, 304
  loop row
```

V2 (9x8):
```
mov cx, 8     ; 8 rows
row:
  mov ah, cs:[si]
  mov dl, cs:[si+1]
  add si, 2
  mov cx, 8; loop 8 cols from ah (shl ah, plot)
  ; Now single bit from dl (col 8)
  shl dl, 1
  jae +3
  mov es:[di], al
  inc di
  add di, 311   ; 320 - 9
  loop row
```

### Position
- V1: `sub ax, 8` (16 wide centered in 16 px lead+trail span)
- V2: `sub ax, 4` (9 wide centered)

## 完整流程

```bash
cd C:\Users\原來是個胖仔\eob_analysis
# 1. Scan EXE strings
python scripts/scan_strings.py  # → strings_scan.json

# 2. Build translation dict + generate patches
python scripts/generate_patches.py  # → full_patches.json

# 3. Patch EXE
python scripts/patch_exe_strings.py EOB1_ORIG.EXE full_patches.json EOB1_FULL_CHT.EXE

# 4. Extract subset using Boutique TTF
python scripts/extract_boutique9x9.py full_patches.json 9  # → boutique_subset.bin

# 5. Build + install hook
python scripts/build_v2_9x8.py  # → MCGA_V2_9x8.OVL + copies to game

# 6. Install patched EXE
copy EOB1_FULL_CHT.EXE "<game>\EOB.EXE"

# 7. Test
"<game>\..\run-game.bat"
```

## Compound strings (CR-separated)

EOB.EXE 有 27 個 CR-separated 字串需當「整條」翻譯：
- Title menu (0x026B01): "LOAD GAME IN PROGRESS\rSTART A NEW PARTY\rEXIT TO DOS"
- Options (0x026A0C): "OPTIONS\r\rRE-ROLL\rMODIFY\rKEEP\rEXIT"
- Preferences (0x026A5C): "PREFERENCES\r\rRETURN TO GAME\r..."
- CharGen header (0x0269C7): "CHARACTER GENERATION\r\rUSE THE ARROW KEYS..."
- 多條 CAMP submenu dialogs

`generate_patches.py` 用 `COMPOUND` dict 分開管理，**先 patch compound，再 patch singles 並跳過 overlap**。

```python
def in_compound(off):
    for start, end in compound_ranges:
        if start <= off < end:
            return True
    return False
```
