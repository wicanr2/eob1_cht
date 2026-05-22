# 完整翻譯流程 (Plan 3, 真 16x14 Chinese)

從 pristine 開始到能玩中文版的全部步驟。

## 0. 準備來源檔

確認以下 known-good 檔在 `C:\Users\原來是個胖仔\eob_analysis\`:
- `MCGA_CHT.OVL` (11832 bytes, pristine + Plan 1-2 byte patch 在 file 0x27FA)
- `EOB1_ORIG.EXE` (264480 bytes, 純原版)
- `CHINFONT.FNT` (來自 MM4 或 EOB2，410130 bytes, 13671 個 16x14 字模)
- `EOB1_RAW_BIG5.EXE` (含 25 條 demo 翻譯,可作 baseline 對照)

## 1. 翻譯字串 (擴充 patches.json)

從 `demo_patches.json` 開始，加入更多翻譯。格式:
```json
{
  "0x022840": {"orig": "Rest Party", "new": "休息隊伍", "desc": "Camp menu"},
  ...
}
```

**重要規則**:
- `orig` 必須跟 EXE 該位置 bytes (decode as ASCII) 完全相符 — 工具會驗證
- `new` 用 Big5 (cp950) 編碼後 bytes ≤ orig 長度。padding 用 0x00 (null) — 不夠長就空字串
- slot 長度由「字串起點到下個 null byte」決定，必要時可看 raw bytes 確認

詳細可翻譯區段見 `exe_strings.md`。

## 2. 套用字串翻譯

```bash
cd C:\Users\原來是個胖仔\eob_analysis
python scripts\patch_exe_strings.py EOB1_ORIG.EXE EOB1_PATCHED.EXE patches.json
```

工具輸出每條 patch 結果 (OK / FAIL with reason)。所有 OK 才繼續。

## 3. 抽取字模 subset

```bash
python scripts\extract_subset_font.py CHINFONT.FNT patches.json
```

產生:
- `subset_font.bin` — XOR 解密後的字模 (sorted by codepoint, header "CFST")
- `subset_codepoints.txt` — 人類可讀字模清單

## 4. 重排成 hook 用 binary

```bash
python scripts\build_hook_subset.py
```

讀 `subset_font.bin` (CFST 格式) → 寫 `hook_subset.bin` (CHST 格式, BE codepoint):
- Header: `CHST` + uint16 LE count + uint16 LE glyph_size(=28)
- Records: 2 BE codepoint + 28 bitmap (14 rows × 2 bytes MSB-first)
- Sorted ascending (binary search 可用,但目前 hook 用 linear)

## 5. 編譯 + 注入 hook

```bash
python scripts\build_final_hook.py
```

`build_final_hook.py` 做這幾件事:
1. 讀 `MCGA_CHT.OVL` 當 source
2. Patch file 0x0E4D..0x0E4E: `38 2C` → `00 40` (const patch, EOB scratch 推到 image 0x4000)
3. Patch file 0x261E..0x2620 (= image 0x241E orig_blit 入口): `55 8B EC` → `E9 rel16` 跳到 hook
4. 擴充檔到至少 17408 bytes (e_cp = 0x22)
5. Hook bytes 放在 file 0x2F80 (= image 0x2D80): 含完整 stateful Big5 邏輯 + subset data
6. 同步更新 MZ header e_cp / e_cblp
7. 寫 `MCGA_FINAL.OVL` (17408 bytes)

## 6. 安裝到遊戲

```bash
copy MCGA_FINAL.OVL "D:\SteamLibrary\steamapps\common\Forgotten Realms The Archives - Collection One\games\Eye of the Beholder ENG\GAME\EYE\MCGA.OVL"
copy EOB1_PATCHED.EXE "D:\SteamLibrary\steamapps\common\Forgotten Realms The Archives - Collection One\games\Eye of the Beholder ENG\GAME\EYE\EOB.EXE"
```

## 7. 測試

```bash
cd "D:\SteamLibrary\steamapps\common\Forgotten Realms The Archives - Collection One\games\Eye of the Beholder ENG"
run-game.bat
```

啟動時答 `4 / 1 / y` 過 VGA / AdLib / Mouse 提示。進到 dungeon 後點 CAMP → Preferences 可看翻譯。

## 8. 還原 (如果壞了)

```bash
python scripts\restore_baseline.py
```

恢復 MCGA.OVL 跟 EOB.EXE 為 baseline (Plan 1-2 byte-pair Chinese 還是 work)。

## 同步其他 OVL (待做)

只 hook MCGA 的話 EGA/CGA/TGA 用戶看不到中文。重複 step 5 的邏輯為其他 3 個 OVL 各自建一份 (它們的 image offset 可能不同，要重新分析)。
