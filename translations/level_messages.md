# LEVEL.INF 動作訊息中譯

來源: EOB1 DOS `EOBDATA3-6.PAK` 內 12 個 `LEVEL{1-12}.INF` (script bytecode + inline strings)
工具: [scan_level_inf.py](../tools/scan_level_inf.py)
落地: 直接 in-place patch INF 內 ASCII bytes (中文 cp950 bytes ≤ 原 EN bytes + null padding)
狀態: 🚧 **未 ship** — 等 patcher 寫好 + 測試

## 為什麼 LEVEL.INF 較難翻譯

EOB1 的關卡腳本 (LEVEL.INF) 是 **Westwood EMC2 script bytecode** + 內嵌 ASCII 字串。字串 inline 在 bytecode 中，**長度改變會破壞 bytecode offset**。所以中文翻譯**必須 ≤ 原 EN bytes** (含 null terminator)，多餘空間用 `\0` 填補。

中文 cp950 是 2 bytes/char，英文 1 byte/char，所以多數短訊息中文化會更短 (e.g. "going up..." 11B → "向上..." 7B)，符合限制。

## 共用動作訊息 (12 個 LEVEL.INF 多次重複)

| 原文 (摘要) | EN bytes | 中譯 | ZH bytes |
|---|---|---|---|
| going down / up... | 13 / 11 | 向下... / 向上... | 7 / 7 |
| you can't go (that way) | 22 / 12 | 無法那樣走。 | 13 |
| failed lock pick | 16 | 開鎖失敗 | 8 |
| (lock pick) s break! | 8 | 工具壞了！ | 9 ❌ over |
| appears jammed | 14 | 卡住了 | 6 |
| the lock has been picked! | 25 | 鎖已被打開！ | 12 |
| requires (a key/item) | 8 | 需要 | 4 |
| it doesn't fit. | 15 | 不合適。 | 8 |
| do not disturb | 14 | 請勿打擾 | 8 |
| stow yer weapons. | 17 | 請收武器。 | 10 |
| store weapons before... | 17+ | 請先收武器 | 10 |
| turn back, no tresspassing | 27 | 禁止進入。 | 10 |
| you were warned | 16 | 你已被警告 | 10 |
| get spiked! | 11 | 中尖刺！ | 8 |
| dead end? | 9 | 死路？ | 6 |
| failed (lock pick attempt) | 8 | 失敗 | 4 |

## 場景特有訊息

### LEVEL1.INF (Waterdeep 下水道入口)
- `it smells terrible here.` (24B) → `此處味道極差。` (14B) ✓
- `fallen rocks block the way.` (27B) → `落石擋路。` (10B) ✓

### LEVEL3.INF (矮人聖殿)
- `the key fits` (12B) → `鑰匙合適` (8B) ✓
- `feel dizzy` (?B) → `暈眩` (4B) ✓
- `opportunity...will yield great...sacrifice...` (剝離片段) → 翻成 `機會... / 必有大... / 獻祭` 各短句

### LEVEL5.INF (Dwarves' Hall)
- `please reset drain holes when finished` (33B) → `用畢請重設排水孔` (16B) ✓
- `'safe passage'` (15B) → `平安通行` (8B) ✓
- `greed will be` (truncated) → `貪婪將會` (8B) ✓

### LEVEL6.INF (Drow territory)
- `'fasten' and 'hammer'` (21B) → `緊扣 / 鎚` (8B) ✓
- `store weapons before...` → `先收武器` (8B) ✓

### LEVEL7-9.INF (Drow city)
- `room. no admittance` (20B) → `房間。禁入` (10B) ✓
- `acrifice made` (片段) → `獻祭完成` (8B) ✓
- `'s faith repaid` (16B) → `信念回報` (8B) ✓
- `front entr(y)` (truncated) → `正門入口` (8B) ✓

### LEVEL10-12.INF (Beholder lair)
- `keep an eye out` (15B) → `保持警戒` (8B) ✓
- `the hive` (8B) → `蜂巢` (4B) ✓
- `star of navigation.` (19B) → `導航之星。` (10B) ✓
- `alignment must be true` (truncated) → `陣營須真` (8B) ✓
- `reeks faintly of smoke` (24B) → `淡淡煙味` (8B) ✓
- `urn back, no tresspassing` (27B with leading 't' lost) → `禁止進入` (8B) ✓
- `light beam ha(s)` (truncated) → `光束已...` (8B) ✓
- `stone for substance` (19B) → `以石換實` (8B) ✓

## 未翻 (片段/上下文不足)

部分字串在 scan 中被 bytecode bytes 切碎，無法確定完整原文，先 skip:
- `this slimy,0)`, `y drain pipe r`, `age gratpi03`, `es deeper int`, `e floor0s`
- `gdom mark4S`, `e mountain R`, `ancient one W`
- `ngs are not al`, `ey appear`
- `word for 'clo`, `upboard q`
- `ourage!&`, `figh;%"I`
- `combination3`, `survive )`, `got some`, `a special0`, `generou$`

這些片段需要進一步 LEVEL.INF bytecode 反組譯 (找完整字串邊界) 才能翻。屬於 iter10+。

## Ship 狀態

- ✅ Tooling: scan_level_inf.py 已抽 168 strings
- ❌ Patcher: 尚未寫 (patch_level_inf.py 待做)
- ❌ Translated INF files: 未 deploy
- ❌ Tester verify: 待 patcher 完成

下一步: 寫 `patch_level_inf.py` 把上述短譯做 in-place patch + null padding，產 12 個新 LEVEL.INF，注入回 EOBDATA{3-6}.PAK。
