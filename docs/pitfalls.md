# 踩過的雷 — Quick Reference

## ScummVM build

### Pitfall: `kEoB1ManDefDOSChineseProvider was not declared`

**原因**: register_chinese_providers.py 把所有 EN_ANY 的 provider 都 clone 成 ZH_TWN，但 ManDef 是 ByteProvider 不是 StringListProvider，且 EN 也只有一個 (各 lang 共用)。

**修復**: alias 英文 provider：
```cpp
{ kEoBBaseManDef, kEoB1, kPlatformDOS, kNoSpecial, ZH_TWN, &kEoB1ManDefDOSEnglishProvider },
```

### Pitfall: `ERROR: Could not find need 318 for game 300A`

**原因**: need-list 是 per-(game, platform, special) 不分 lang。加東西到 need-list 會讓 EN/DE/IT 也被檢查。

**修復**: 同上 — 為缺的 lang alias 英文 provider，或不加到 need-list。

### Pitfall: `KYRA.DAT INDEX 沒有 0x300A entry`

**症狀**: 遊戲啟動 "You're missing the 'KYRA.DAT' engine data file or it got corrupted"

**原因**: 沒在 `games.cpp` 的 `eob1Games[]` 加 ZH_TWN entry，create_kyradat 不知道要產 EOB1 ZH_TWN variant。

**修復**:
```c++
const Game eob1Games[] = {
    ...
    { kEoB1, kPlatformDOS, kNoSpecial, ZH_TWN },  // 加這行
    ...
};
```

### Pitfall: WSL 端 source 沒同步

**症狀**: 改了 `D:\03_game_tmp\eob1_cht\scummvm-source\` 但 WSL build 用舊版

**原因**: WSL build 跑在 `/root/scummvm_work/scummvm/`，要手動 cp。

**修復**: 寫 sync script (見 developer.md)。

### Pitfall (iter4 慘痛): WSL 兩個 ScummVM clone 不共用 source

**症狀**: Win cross-build 跑完 30 秒「成功」link 出 scummvm.exe，但行為跟 iter1 一樣 (新 patch 沒生效)

**原因**: WSL 有兩個獨立 in-tree clone:
- `/root/scummvm_work/scummvm/` (Linux build)
- `/root/scummvm_work/scummvm-win64-build/` (Win cross-build)

它們**不共用 source** — 兩邊都有自己的 chargen.cpp 副本。改 source 只 cp 到 Linux clone，Win clone 仍是 iter1 版 → Win build incremental "succeeds" 但其實沒重編 chargen.o，只 LINK 出 stale binary。

**修復**: 改 source 後 **兩個 clone 都要 cp**:
```bash
cp /mnt/d/...src/foo.cpp /root/scummvm_work/scummvm/foo.cpp
cp /mnt/d/...src/foo.cpp /root/scummvm_work/scummvm-win64-build/foo.cpp
```
或改成 out-of-tree build (Win build 改成 `cd /tmp/winbld && /path/configure ...` 直接讀 /root/scummvm_work/scummvm/ 源碼)。

## Cross-compile

### Pitfall: `--disable-curl` not recognized

**原因**: ScummVM configure 不支援 disable libcurl 直接，需要不裝 libcurl-dev 即可。

**修復**: skip `--disable-curl`，沒裝 libcurl 自動 disable。

### Pitfall: MinGW build 缺 SDL2 header

**修復**: 下載 https://github.com/libsdl-org/SDL/releases/.../SDL2-devel-X-mingw.tar.gz，解到 `/opt/sdl2-mingw/`，configure 加 `--with-sdl-prefix=/opt/sdl2-mingw/SDL2-X/x86_64-w64-mingw32`。

## Run-time

### Pitfall: WSLg `[WARN:COPY MODE]` 視窗黑屏

**症狀**: scummvm 跑著，msrdc.exe hwnd 存在，但 Windows desktop 看不到

**原因**: WSLg graphics bridge fallback 到 software rendering

**修復**: `wsl --shutdown` 重啟 WSL，重 launch scummvm。或乾脆換 native Windows scummvm.exe。

### Pitfall: PrintWindow 回傳黑圖

**原因**: WSLg msrdc.exe 視窗不支援 PrintWindow content capture（Direct3D）

**修復 1**: 用 WSL 內 `import -window <id>` 從 X server 直接抓
**修復 2**: 用 Windows native scummvm.exe — PrintWindow 正常

### Pitfall: 字模缺字顯示 "?"

**症狀**: e.g., 顯示 "記?法術" 而非 "記憶法術"

**原因**: EOB2 CHINFONT.FNT 只有 12,811 字，有些字（如 `憶` 0xBED0）不在內

**修復**: build_ceob_combined.py 用 BoutiqueBitmap9x9 fallback 補

### Pitfall: 名字輸入欄看似空白

**原因**: 不是空白 — Chinese font 把輸入欄蓋住了（14-row 時）

**修復**: 換 12-row 字模

### Pitfall: PowerShell 在 .bat 內 ^ 接行炸開

**症狀**:
```
'?' 不是內部或外部命令
'Where-Object' 不是內部或外部命令
```

**原因**: cmd.exe 對 `^` 多行 PowerShell here-string 處理不穩

**修復**: 不要 inline PowerShell。寫成獨立 `.ps1` 或單行字串。

### Pitfall (iter4 慘痛): .bat 啟動腳本編碼 + 行尾雙雷

**症狀**: User 雙擊 `啟動.bat` cmd 報 garbled 中文錯誤如:
```
'~dp0''  不是內部或外部命令
'閽?SteamLibrary' 不是內部或外部命令
'OB1' 不是內部或外部命令
```

**根因 (兩個獨立問題疊加)**:

1. **編碼錯誤**: Edit tool / Write tool 寫 `.bat` 預設 UTF-8 (3 bytes/CJK)，但繁中 Windows cmd 用 cp950 (2 bytes/CJK) 讀檔。bytes 解碼錯位 → quote 不對齊 → parsing 壞掉
2. **行尾錯誤**: PowerShell here-string `@'...'@` 保留 LF (Unix 行尾)，cmd.exe 解析 LF-only `.bat` token 對不齊 → `@echo off` 變成 `cho off`，`set "GAMEDIR=..."` 變 unknown command

**修復**:
```powershell
$content = @'
...bat content...
'@
# 1. 把 LF 轉 CRLF
$content = $content -replace "`n", "`r`n"
# 2. 用 cp950 ANSI 寫 (不要 UTF-8/UTF-16/BOM)
[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::GetEncoding(950))
```

**驗證 checklist**:
- [ ] `(Get-Item $bat).Length` 合理 (cp950 < UTF-8)
- [ ] First 4 bytes ASCII (`@ech` 開頭最安全)
- [ ] CR count == LF count (CRLF)
- [ ] cp950 decode 中文正常: `[System.Text.Encoding]::GetEncoding(950).GetString((Get-Content $bat -Encoding Byte))`
- [ ] Dry-run: 把最後 launch 行換 `echo TEST` 後 `cmd /c "$bat"` 看 exit code + 輸出

## Cross-platform memory safety (iter5 慘痛教訓)

### Pitfall: Linux glibc 容忍 OOB，Windows MinGW 直接 crash

**症狀**: WSL Xvfb tester 跑遍 CharGen 流程沒 crash，user 雙擊 Windows .bat 點人物頭像/選單會當機

**原因**: ScummVM array OOB read (e.g. `_characterGuiStringsHp[3]` when size==2) 在 Linux glibc heap 通常返回隨機 bytes 不 crash (silent corruption)；同個 binary 在 Windows MinGW heap 嚴格 → segfault

**修復策略**:
- **Code review 階段**: 改 ZH_TWN gate 時 grep **所有** array 索引含 [2]/[3]/[6]/etc — 確認對應 EOB1 ZH provider array size 是否足夠
- **Test 階段**: 不能只 trust WSL Xvfb 結果。Memory-touch 類 bug 必須 Windows native 驗證
- **Defensive fix**: gate 加 `_flags.gameID == GI_EOB2`，EOB1 fallback 到合法 index

**具體案例 (Fix G2 in gui_eob.cpp)**:
- `:186` (now :192): `_characterGuiStringsHp[3]` (食 food) — EOB1 size 2, EOB2 size 4
- `:224` (now :228): `_characterGuiStringsSt[6]` (petrified) — EOB1 size 6, EOB2 size 7
- `:425` (now :439): `_characterGuiStringsHp[2]` (inv HP fmt) — EOB1 size 2, EOB2 size 4

### Pitfall: 放寬 `GI_EOB2 && ZH_TWN` gate 容易漏關聯 gate

**症狀**: iter3 Fix E 把 `chargen.cpp:772` name input gate 放寬，name input 出現視覺異常 (大黑色累積殘像)

**原因**: input position 由 chargen.cpp 控制，但 input **strip 高度** (`_textInputHeight=9` for EN / `=16` for EOB2 ZH) 由 `gui_eob.cpp:1576-1580` 另一組 `GI_EOB2 && ZH_TWN` gate 控制。chargen.cpp 改了但 gui_eob.cpp 沒改 → EOB1 ZH 用 9-px strip 配 15-tall CJK 字 → cursor blink copyRegion 只 backup 字頂 → 字底 6 px 殘留累積

**修復**: 改 ZH_TWN gate 時做關聯 audit:
```bash
# 列所有 EOB2 ZH 專屬常數 / 函式行為
grep -rn "GI_EOB2.*ZH_TWN\|ZH_TWN.*GI_EOB2" engines/kyra/
# 評估每一處是否該同步放寬
```

## Source code

### Pitfall: ScummVM `loadStrings(id, count)` returns nullptr

**原因**: 沒在當前 game variant 的 need-list 內

**修復**: 加進 need-list (但同時可能 break 其他 langs，見上)

### Pitfall: getNeedList 只比對 (game, platform, special)

**原因**: ScummVM 設計 — need-list 是 build-time check，per-lang 不同的應該用 `langSpecific=true` 的 ExtractFilename，但不解決 "ZH_TWN 想多翻一個 string 但 EN_ANY 沒對應" 的問題。

**修復**: 同前 — kSpecial=5 ChineseFan 變種。

## 字模

### Pitfall: BoutiqueBitmap9x9 在 9px 模糊

**症狀**: 用 freetype-py 渲染 BoutiqueBitmap9x9 at 9px，中文字筆畫糊掉

**修復**: 改用 12px (or 11px)。或改用 EOB2 16x14 crop 為主，Boutique 只補缺。

### Pitfall: 14-row 字模在 CAMP menu 疊行

**症狀**: 行間 overlap

**修復**: crop 成 16x12（去掉 top/bottom 1 row 各）

### Pitfall: freetype-py 不認 Unicode 路徑

**修復**: copy TTF 到 `C:\Temp\Boutique.ttf` (ASCII path) 再 load

### Pitfall: cp950 → Unicode 對應錯

**症狀**: BoutiqueBitmap 渲染出來全是方框

**原因**: Big5 codepoint 不能直接當 Unicode codepoint 傳給 freetype

**修復**: `bytes([hi, lo]).decode("cp950")` → Unicode char → freetype `load_char(unicode_char, ...)`
