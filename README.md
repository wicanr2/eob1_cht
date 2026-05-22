# EOB1 繁體中文化 (魔眼殺機 1) — ScummVM 路線

一份 ScummVM 為基礎、把 1991 SSI/Westwood《Eye of the Beholder》(魔眼殺機 1) 改成繁體中文版的完整工作集。

不修原 DOS 二進位、不靠 DOSBox — 直接把 Big5 字模渲染與中文字串注入 ScummVM 的 KYRA engine，產出 Windows 原生 `scummvm.exe`。

## 現況一句話

主選單、角色生成、CAMP menu、屬性表、咒語表、各種訊息都中文化；過場 narration 與物品/怪物名仍英文。**Windows native (Win64) 可雙擊執行**。

## 目錄

```
eob1_cht/
├── README.md                    本檔
├── 中文化心得.md                  從 0 到 100 的逆向心路歷程
├── scummvm-source/              ScummVM 完整源碼 (含我們的修改)
├── win64-build/                 預編 Windows binary
│   ├── scummvm.exe              MinGW-w64 cross-compile
│   ├── SDL2.dll
│   ├── KYRA.DAT                 自製 (含中文字串)
│   ├── ceob.pat                 Big5 字模 (16x12 hybrid)
│   └── 啟動.bat                 雙擊執行
├── assets/
│   └── ceob.pat                 同 win64-build 內，但獨立放方便重產
├── tools/                       Python build/translation scripts
│   ├── build_ceob_combined.py   EOB2+BoutiqueBitmap 混合字模產生器
│   ├── gen_eob1_chinese.py      eob1_dos_chinese.h 生成器
│   ├── manual_overrides.json    手動翻譯覆寫表
│   ├── parse_chinfont_cod.py    EOB2 注音 IME 字典分析
│   └── ... (約 20 個工具)
├── wsl-scripts/                 WSL/Linux 端 build helper
│   ├── wsl_build_mingw.sh       cross-compile Windows binary
│   ├── wsl_rebuild_kyradat.sh   重產 KYRA.DAT
│   └── ...
├── skill/                       Claude Code skill (可放 ~/.claude/skills/)
│   └── SKILL.md
├── agents/                      Claude Code agent 定義
│   ├── game-tester.md
│   ├── ux-designer.md
│   └── developer.md
└── docs/
    ├── architecture.md          ScummVM CHT 架構解析
    ├── future-work.md           還沒做的（IME, 物品名等）
    └── pitfalls.md              踩過的雷
```

## 快速開始 (玩遊戲)

1. 確保 EOB1 ENG 已安裝於：
   ```
   D:\SteamLibrary\steamapps\common\Forgotten Realms The Archives - Collection One\games\Eye of the Beholder ENG\GAME\EYE\
   ```
   (其他路徑請改 `win64-build/啟動.bat` 內的 `GAMEDIR`)

2. 雙擊 `win64-build/啟動.bat`

3. 玩

## 開發 (改翻譯 / 字模 / engine 行為)

需要 WSL Ubuntu-22.04（含 MinGW-w64 + SDL2-mingw devel）。

```bash
# 一次性安裝 build env (WSL)
wsl bash wsl-scripts/wsl_install_mingw.sh

# 改 tools/ 內的 .py 或 scummvm-source/devtools/create_kyradat/resources/eob1_dos_chinese.h

# 重 build 全部
wsl bash wsl-scripts/wsl_build_kyradat.sh    # 重產 KYRA.DAT
wsl bash wsl-scripts/wsl_build_mingw.sh      # 重 build scummvm.exe
wsl bash wsl-scripts/wsl_package_win.sh      # 複製到 Windows
```

## ScummVM 改動摘要

3 個 commit，~1000 行 diff：

| 檔案 | 改動 |
|---|---|
| `engines/kyra/detection_tables.h` | 新增 EOB1 ZH_TWN 偵測 entry (`EOBDATA3.PAK md5 + ceob.pat 存在`) |
| `engines/kyra/graphics/screen_eob.cpp` | 把 GI_EOB2 only 的 Big5 wrapper 放寬到 GI_EOB1；EOB1 用 height=12（EOB2 維持 14）|
| `devtools/create_kyradat/games.cpp` | `eob1Games[]` 加 `{ kEoB1, kPlatformDOS, kNoSpecial, ZH_TWN }` |
| `devtools/create_kyradat/resources.cpp` | 90 個 ZH_TWN provider 註冊 + ManDef 別名 |
| `devtools/create_kyradat/resources/eob1_dos_chinese.h` | NEW 89 個 string provider，416/446 = 93% 覆蓋 |

Upstream branch: https://github.com/wicanr2/scummvm/tree/eob1-cht-fan-translation

## 字模

`ceob.pat` 是 **hybrid** 字模：
- 12,811 字從 EOB2 (隱月傳奇) `CHINFONT.FNT` 解密後 crop 成 16×12
- 940 字從 BoutiqueBitmap9x9 TTF 渲染到 12px 補缺 (覆蓋 EOB2 沒有的字如 `憶` `謄`)
- 總 13,751 字 / 357KB

格式 = ScummVM `Big5Font::loadPrefixedRaw`: `[2-byte BE codepoint][2*height bytes bitmap]...0xFFFF`

## 翻譯來源

主要：[EOB1 EXE patch 專案](C:\Users\原來是個胖仔\eob_analysis) 的 `full_patches.json`（402 條原始 byte-offset 翻譯），用 `tools/gen_eob1_chinese.py` 從 English 對譯。

短字標籤用 `tools/manual_overrides.json` 手動補。

## License

- ScummVM source: GPLv3+ (上游 license)
- 我們的 patches: GPLv3+ (同 ScummVM)
- BoutiqueBitmap9x9 字模: OFL 1.1
- EOB2 CHINFONT.FNT: SSI 1993 字模，從個人 EOB2 中文版抽取，僅限個人非商業用

## 已知限制

| 項目 | 為什麼沒做 | 解法概念 |
|---|---|---|
| 角色名輸入 IME | EOB2 CHINFONT.COD 結構非標 + 需寫 ScummVM widget | 詳見 docs/future-work.md |
| Intro narration 中文 | need-list 是 per-(game,plat,special) 不分語言，加進去會讓 EN build fail | 加 `kSpecial=5` Chinese-fan 變種 |
| 物品/怪物名中文 | 同上原因 | 同上 |
| 對話/關卡敘述 | 在 LEVEL*.INF PAK 內，要解 PAK | 加新 PAK 解碼器或 in-place patch |

詳細見 `docs/future-work.md`。
