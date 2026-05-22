@echo off
chcp 950 >nul
title EOB1 中文版 - ScummVM Native Win64
cd /d "%~dp0"

REM === 設定遊戲目錄 (改這裡) ===
set "GAMEDIR=D:\SteamLibrary\steamapps\common\Forgotten Realms The Archives - Collection One\games\Eye of the Beholder ENG\GAME\EYE"

if not exist "%GAMEDIR%\EOB.EXE" (
    echo.
    echo  錯誤: 找不到 EOB1 遊戲於 %GAMEDIR%
    echo.
    echo  請編輯本 .bat 把 GAMEDIR 改成你的 EOB1 ENG 安裝路徑。
    echo  該目錄底下要有 EOB.EXE、EOBDATA*.PAK 等檔。
    echo.
    pause
    exit /b 1
)

REM 複製 ceob.pat + KYRA.DAT 到遊戲目錄 (覆寫，確保版本一致)
copy /Y "ceob.pat" "%GAMEDIR%\ceob.pat" >nul
copy /Y "KYRA.DAT" "%GAMEDIR%\KYRA.DAT" >nul

echo  Launching ScummVM (Win64 native)...
scummvm.exe --extrapath="%GAMEDIR%" --path="%GAMEDIR%" --auto-detect
