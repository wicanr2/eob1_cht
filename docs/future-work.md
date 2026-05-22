# EOB1 CHT — 未完成的工作

## Tier 1: 真正缺的（明顯影響體驗）

### 1.1 中文名字輸入 (IME)

**現況**: 角色名只能打 ASCII。EOB2 中文版可以用注音輸入中文角色名。

**為什麼難**:
- EOB2 `CHINFONT.COD` (8495B) 是 IME 字典，疑似 4-byte 注音碼 + 1-byte count + Big5 候選清單。檔頭看起來像 Zhuyin 鍵盤映射（"1***" "187*" "18**" 等），但後段資料對不上。
- 即便解出字典，ScummVM 沒有 IME widget 框架，需要從零寫：
  - Input handler 截到 ASCII keystroke
  - 維護組合中字串
  - 候選清單 popup
  - 確認/取消鍵綁定

**估計工程**: 字典解碼 ~4h + IME widget ~8h = 1.5 工作天。

### 1.2 物品 / 怪物名中文

**現況**: 顯示 "Cure Light Wounds" "Goblin" 等英文。

**為什麼難**:
- 名稱在 `EOBDATA*.PAK` 的 `ITEM.DAT` 內，read 時走 `EoBCoreEngine::getItemDefinitionFile`
- ScummVM 可走 static resource (`_itemNamesStatic` from `kEoB1ItemNames` provider) 取代 PAK 讀取
- 但要在 `eob1FloppyNeed[]` 加 `kEoB1ItemNames`，加了 EN/DE/IT build 會 fail
- 同 intro narration 的 need-list 問題

**解法**: 加 `kSpecial=5 ChineseFan` 變種 (詳 1.5)

**估計**: 翻譯 ~96 items × 5 min = 8h. 重構 need-list ~3h. 總 1.5 天。

### 1.3 過場 narration 中文

**現況**: "We, the Lords of Waterdeep..." 等英文。

**為什麼難**:
- 過場字串在 baked CPS 圖 (`TEXT.CMP`) 內，不是 string resource
- 引擎可走 `kEoB1IntroStringsTower` provider overlay，但同樣有 need-list 問題

**解法**: 同 1.2，加 kSpecial=5 ChineseFan + 寫翻譯（已草稿在 git history）

### 1.4 對話 / 關卡敘述中文

**現況**: NPC 對話、Beholder 解謎敘述等英文。

**為什麼難**: 在 `LEVEL*.INF` 內 (PAK 壓縮)，要解 PAK + 翻譯 + 重 pack。

**估計**: 1 週起跳，需要寫 LEVEL.INF 解碼器。

### 1.5 引入 kSpecial=5 ChineseFan 變種

unblock 1.2 / 1.3:

```cpp
// engines/kyra/resource/staticres.cpp
byte getSpecialID(const GameFlags &flags) {
    if (flags.isOldFloppy) return 4;
    if (flags.isChineseFan) return 5;  // NEW
    ...
}

// engines/kyra/detection_tables.h
struct GameFlags {
    ...
    bool isChineseFan : 1;  // NEW
    ...
};
#define EOB_CHINESE_FAN_FLAGS FLAGS(false, false, false, false, false, false, false, false, true, Kyra::GI_EOB1)
//                                                                                          ^^^^ isChineseFan

// devtools/create_kyradat/games.cpp
const Game eob1Games[] = {
    ...
    { kEoB1, kPlatformDOS, kChineseFan, ZH_TWN },  // CHANGED special
    ...
};

const int eob1ChineseFanNeed[] = {
    // copy of eob1FloppyNeed +
    kEoB1IntroStringsTower,
    kEoB1IntroStringsOrb,
    ...
    kEoB1ItemNames,
    ...
};

// And: gameNeedTable {kEoB1, kPlatformDOS, kChineseFan, eob1ChineseFanNeed}
```

**估計**: 半天。

## Tier 2: 體驗加分

### 2.1 翻譯 polish

剩 7% 未翻字串多數是格式碼。手動掃過 in-game 看哪些字串還是英文，補翻 manual_overrides.json。

### 2.2 字模選擇 UI

讓玩家在 ScummVM Options 切 12-row / 10-row / 14-row Big5 字模。需要：
- `loadPrefixedRaw` 高度從 config 讀
- 字模需多版本（或現場 crop）
- Options menu 加 ZH_TWN 專屬選項

### 2.3 EOB2 CHT 也升級到 16x12 hybrid

EOB2 ScummVM 現在用 14-row。如果 EOB1 12-row hybrid 體驗較好，可以 PR 上游改 EOB2 也用 12-row 並提供 hybrid `ceob.pat`。

## Tier 3: 純研究

### 3.1 反編譯 EOB2 IME

完整解出 `CHINFONT.COD` 格式，把它變成可重用的 Zhuyin lookup library。

### 3.2 完整 PAK 工具

Westwood PAK format 解 + 重 pack。可以用於：
- 翻譯 ITEM.DAT / LEVEL*.INF
- 替換 baked CPS 圖（過場中文）

### 3.3 Compare with 隱月傳奇 中文 EOB2

EOB2 中文版本身有些 ScummVM 還沒完美 render 的 corner case (字模缺、layout 衝突)。對照 EOB1 設計差異，看能否提取通用解。

## 已被打回票的方向

### 拒絕：原 EXE patch 路線

理由：見 中文化心得.md。不跨平台、難維護、字模塞不進。

### 拒絕：DOSBox + 注音掛載

理由：ScummVM 路線更乾淨。
