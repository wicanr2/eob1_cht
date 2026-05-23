@echo off
chcp 950 >nul
title EOB1 中文版 - ScummVM Native Win64
cd /d "%~dp0"

REM === Portable: 所有檔案都在本目錄底下，不需要 SteamLibrary ===
set "GAMEDIR=%~dp0game"

if not exist "%GAMEDIR%\EOB.EXE" (
    echo.
    echo  錯誤: 找不到 EOB1 遊戲於 %GAMEDIR%
    echo.
    echo  game\ 子目錄損壞或缺檔。應有 EOB.EXE、EOBDATA*.PAK、KYRA.DAT、ceob.pat 等。
    echo.
    pause
    exit /b 1
)

echo  Launching ScummVM (Win64 native)...
scummvm.exe --extrapath="%GAMEDIR%" --path="%GAMEDIR%" --auto-detect