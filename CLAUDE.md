# Claude Code 入口說明

當 Claude 在這個 repo 工作時，先讀這個檔。

## 這個 repo 是什麼

EOB1 (魔眼殺機 1) 繁體中文化工作集。基於 ScummVM 修改，產出 Windows native binary。

完整說明見 `README.md`，技術細節見 `中文化心得.md`、`docs/architecture.md`。

## 可用的 sub-agents

`agents/` 內 3 個 agent 定義：

| Agent | 用途 | 何時 spawn |
|---|---|---|
| `game-tester` | 跑 scummvm.exe 找 bug，寫 test-reports | 改動後驗證 |
| `ux-designer` | 看 test report 提 UI 修改建議，寫 design-reviews | 收到 [UX] 標記的 bug |
| `developer` | 套用 design review 的 fix，重 build | 收到 design-review |

Loop: tester → ux-designer → developer → tester → ...

## 重要路徑

- `scummvm-source/` — ScummVM 完整源碼（可改）
- `win64-build/scummvm.exe` — 預編 Windows binary（developer agent 重 build 時更新）
- `tools/` — Python build/translation scripts
- `wsl-scripts/` — WSL 端 build helper
- `test-reports/` — game-tester 產出
- `design-reviews/` — ux-designer 產出
- `skill/SKILL.md` — Claude Code skill (此專案的領域知識)

## 不要做的事

- 不要把 `.git/` 加進 `scummvm-source/`（保持 source dir 乾淨）
- 不要動 `D:\SteamLibrary\...\GAME\EYE\` 內的原始遊戲檔（只 copy ceob.pat / KYRA.DAT 進去）
- 不要 commit `test-reports/*.png`（gitignore 已排除）
- 不要在 .bat 內 inline 多行 PowerShell（cmd.exe `^` 接行不穩，見 docs/pitfalls.md）

## 常見任務的入口

| 任務 | 入口 |
|---|---|
| 改翻譯 | `tools/manual_overrides.json` 或 `scummvm-source/devtools/create_kyradat/resources/eob1_dos_chinese.h` |
| 改字模 | `tools/build_ceob_combined.py` |
| 改 engine 行為 | `scummvm-source/engines/kyra/graphics/screen_eob.cpp` |
| 改偵測規則 | `scummvm-source/engines/kyra/detection_tables.h` |
| 重 build | `wsl-scripts/wsl_rebuild_kyradat.sh` + `wsl_build_mingw.sh` |
| 測試 | spawn `game-tester` agent |
| UI 設計 | spawn `ux-designer` agent |
