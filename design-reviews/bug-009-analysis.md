# BUG-009 deeper analysis (for iter2 ux-designer)

`營：` 與 `休息隊伍` 的關係不是「上下垂直重疊」，是「左右同 Y 緊鄰」。

## 實測座標 (verified via source + screenshot iter1-03-camp-menu.png)

CAMP menu (`initMenu(0)` 進入時):
- `m->dim = 10` → `_screenDimTableZH[10] = {sx=0, sy=0, w=22, h=144}` (整個 dim 位於畫面左上原點)
- Title `營：` 來自 `_menuStringsHead[0]` (titleStrId 動態設為 56，見 `gui_eob.cpp:2415`)
- 繪製位置: `gui_eob.cpp:4569` `printShadedText(s, 3, 3, ...)` → 螢幕絕對 (3, 3)，高 12px → y=3..14
- 按鈕 0 (`休息隊伍`): `buttonDefsChineseEOB2[0] = {labelId=2, x=42, y=4, w=128, h=19}` → 螢幕絕對 (42, 4)，高 19px → y=4..23

兩者 Y 範圍 [3..14] vs [4..23] **有 11px 垂直重疊**，但 X 範圍 [3..28] vs [42..170] **完全分離** (隔 14px 空白)。

視覺呈現:
```
y=3..14:   營：              ███休息隊伍███   <- 第一個按鈕，反白
y=14..23:                    [按鈕底部框]
y=24..43:                    ░░░記憶法術░░░   <- 第二個按鈕
...
```

## 原 bug report 用「黏到」其實是描述視覺擁擠感:

- 標題 `營：` 在最左邊頂端 (x=3, y=3)
- 第一個按鈕 `休息隊伍` 反白底邊框在 (x=42, y=4)
- 兩者左右距離只有 14px，視覺上一行內標題+按鈕擠在一起
- **沒有實際 glyph pixel 重疊** (X 軸隔開)，但**視覺層次不對** — 標題該獨佔一行，現在像 column header

## 為什麼跟 BUG-001 不同根因

- BUG-001/Fix B: 真正的垂直重疊，全形冒號 `：` 點壓到下方第一個字頂端
- BUG-009: 純 X 軸佈局問題，標題與第一個按鈕同 Y

## 對應原 EOB2 ZH

EOB2 ZH 同樣用這個 `buttonDefsChineseEOB2` + `(3,3)` 標題位置。EOB2 ZH 既然 ship 過就代表這個 layout 玩家**可接受**，只是不漂亮。所以這是已知歷史問題不是 EOB1 新引入的 regression。

## 修法選項 (給 ux-designer)

| 選項 | 改動 | 副作用 |
|---|---|---|
| A. 標題下移到獨佔行 | `gui_eob.cpp:4569` 改 `(3, 3)` → `(3, -10)`...不行，會出 dim 邊界。或保留 (3, 3) 但 buttonDefsChineseEOB2[0..6].y 全部 +14 | 影響 EOB2 ZH，要 ux 看 EOB2 是否更糟 |
| B. ZH_TWN 並聯式 title row 改為 dim 上方 banner | `initMenu` 在 ZH_TWN 時把 title 畫進獨立的 banner region (跨 dim 邊界外) | 結構改動大 |
| C. 拉長 dim 10 高度 + buttonDefsChineseEOB2 全部 +14 | 改 `_screenDimTableZH[10].h` 從 144 → 158 + button y 偏移 | 容易超出 200px 畫面 |
| D. 維持現狀 (defer 到 polish iter) | — | 視覺仍不理想但可玩 |

**建議 D — 維持現狀**: BUG-009 由 tester 標為 minor (不是 blocker/major)，且 EOB2 ZH 也是這個 layout 已 ship 上游 fan-translation 多年。除非 ux-designer 看了真實截圖覺得不可接受，否則優先級低於 BUG-003 (英文按鈕) / BUG-005/006 (字 glyph)。

## 旁註

`gui_eob.cpp:2196` 的 `if (_vm->game() == GI_EOB2 && _vm->gameFlags().lang == Common::Language::ZH_TWN)` 是 `simpleMenu_setup` 內，與 BUG-009 無關 — 那是控制 sub-menu (sd=1/3) 的多欄 layout。不要混淆。
