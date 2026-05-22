# EOB.EXE 字串地圖

已掃描的字串區段 (in EOB1_ORIG.EXE, 264480 bytes)。

## 區段一覽

| File offset | 內容 | 條數 (估) | 大小 |
|---|---|---|---|
| 0x22831-0x22E54 | UI/系統訊息 (CAMP / Preferences / dialog) | ~70 | 1.5 KB |
| 0x2628E-0x269C0 | 屬性/種族/職業/陣營/咒語名 (Character Generation) | ~120 | 1.8 KB |
| 0x269C7-0x2A310 | 戰鬥訊息/標題 | ~150 | ~3 KB |
| 0x2AE6D+ | NPC 名稱與對話選項 | varies | ~5 KB |
| **總計** | | ~340+ | ~12 KB |

中文翻譯後預期 ~12-15 KB Big5 (壓縮率與單詞長度相關)。

## 區段一: 0x22831 起 (CAMP menu / system)

已驗證 12 條，剩約 60 條待掃。Demo 範例:

```
0x022831  "Select Option:"       → "選擇："         (14B slot)
0x022840  "Rest Party"           → "休息隊伍"       (10B)
0x02284B  "Memorize Spells"      → "記憶法術"       (15B)
0x02285B  "Pray for Spells"      → "祈禱法術"       (15B)
0x02286B  "Scribe Scrolls"       → "謄寫卷軸"       (14B)
0x02287A  "Preferences"          → "偏好設定"       (11B)
0x022886  "Game Options"         → "遊戲選項"       (12B)
0x022898  "Load Game"            → "載入遊戲"       (9B)
0x0228A2  "Save Game"            → "儲存遊戲"       (9B)
0x0228AC  "Drop Character"       → "踢出角色"       (14B)
0x0228BB  "Quit Game"            → "離開遊戲"       (9B)
0x0228D7  "Game saved."          → "已存檔。"       (11B)
```

要掃完剩下 60 條，用:
```bash
python -c "
data = open('EOB1_ORIG.EXE','rb').read()
start, end = 0x22831, 0x22E54
i = start
while i < end:
    if data[i] < 0x20:
        i += 1; continue
    j = data.index(0, i, end)
    s = data[i:j].decode('latin1', errors='replace')
    if s.strip():
        print(f'0x{i:06X}: \"{s}\" (slot={j-i+1}B)')
    i = j + 1
"
```

## 區段二: 0x2628E 起 (Character Generation)

已驗證 13 條:

```
0x026363  "FIGHTER"        → "戰士"   (7B)
0x02636B  "RANGER"         → "遊俠"   (6B)
0x026372  "PALADIN"        → "聖騎"   (7B)
0x02637F  "CLERIC"         → "牧師"   (6B)

0x026438  "LAWFUL GOOD"    → "守序善良"  (11B)
0x026444  "NEUTRAL GOOD"   → "中立善良"  (12B)
0x026451  "CHAOTIC GOOD"   → "混亂善良"  (12B)
0x02645E  "LAWFUL NEUTRAL" → "守序中立"  (14B)
0x02646D  "TRUE NEUTRAL"   → "絕對中立"  (12B)
0x02647A  "CHAOTIC NEUTRAL"→ "混亂中立"  (15B)
0x02648A  "LAWFUL EVIL"    → "守序邪惡"  (11B)
0x026496  "NEUTRAL EVIL"   → "中立邪惡"  (12B)
0x0264A3  "CHAOTIC EVIL"   → "混亂邪惡"  (12B)
```

待掃: 屬性名 (STR/INT/WIS...), 種族 (HUMAN/ELF/DWARF...), MAGE/MAGIC USER, THIEF, 性別,  hit dice,  spell levels...

## 區段三: 0x269C7 起 (戰鬥訊息)

未掃。預計含: "Missed", "Killed", "X hits Y for Z damage", "Saving throw", "X dies"...

## 區段四: 0x2AE6D 起 (NPC)

未掃。預計含: NPC 名稱、對話選項、地圖描述。

## 翻譯建議優先順序

1. **CAMP menu (0x22831 區)** — 玩家最常見的 UI，影響感受最大
2. **Character Generation (0x2628E 區)** — 開新檔必看
3. **戰鬥訊息 (0x269C7 區)** — 遊玩中持續出現
4. **NPC 對話 (0x2AE6D+)** — 沉浸感與劇情

## 不可翻譯的東西

- TEXT.CMP — 是圖片不是文字 (320×200 palette indexes, Westwood Format80 LZW 壓縮)
- 各關卡告示 (LEVEL*.INF) — 另存於關卡檔，需另外處理
- 物品名稱 (ITEM.DAT 80 條) — 另一檔，可一起翻
- 對話 narrative (TEXT.DAT 51 條) — 另一檔，可一起翻
