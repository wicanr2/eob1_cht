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
