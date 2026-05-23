# win64-build/game/

ScummVM 偵測 EOB1 用的遊戲資料夾。**`啟動.bat` 預設用 `--path=%~dp0game --extrapath=%~dp0game`** 從這裡讀。

## 目錄內容

### Git 追蹤 (本 repo 衍生資料)

- `KYRA.DAT` — ScummVM static resources (含中文化字串)
- `ceob.pat` — 16×12 hybrid Big5 字模 (EOB2 CHINFONT 解密 crop + BoutiqueBitmap9x9 補缺)
- `README.md` (本檔)

### 不在 git 內 (需自備，版權)

要玩需自行從合法 EOB1 安裝來源 copy 進來:

| 來源 | 路徑 |
|---|---|
| Steam (Forgotten Realms: The Archives Collection One) | `<Steam>\steamapps\common\Forgotten Realms The Archives - Collection One\games\Eye of the Beholder ENG\GAME\EYE\` |
| GOG / 原版 5.25" 軟碟 | `<EOB安裝路徑>\` |

要 copy 的檔案 (~5.8 MB total):
```
EOB.EXE
INTRO.EXE
START.EXE
EOBDATA1.PAK
EOBDATA2.PAK
EOBDATA3.PAK
EOBDATA4.PAK
EOBDATA5.PAK
EOBDATA6.PAK
EYE.PAK
CGA.OVL
EGA.OVL
MCGA.OVL
TGA.OVL
FONT6.FNT
FONT8.FNT
LEVELS.TMP
```

不需要 copy:
- `EOB_org.EXE` (backup 不需要)
- `EOBDATA.SAV` (原版存檔不相容)
- `INSTALL.BAT` (DOS 安裝腳本不需要)
- `INTRO.EXE.bak`
- `backup/` (子目錄)

## 驗證

放好後，從 `win64-build/` 根目錄跑:
```
scummvm.exe --detect --path=.\game
```
應顯示:
```
kyra:eob   Eye of the Beholder (Extracted/DOS/Chinese (Traditional))   ...\game\
```

雙擊 `啟動.bat` 即玩。
