@echo off
:: ==============================================================================
:: Author : _LeMinhVoid_VnxD
:: Profile: https://printpf.netlify.app/
:: ==============================================================================

chcp 65001 >nul
setlocal EnableDelayedExpansion
title AUTO ROTATE IP - CLOUDFLARE WARP

set "WARP_CLI=C:\Program Files\Cloudflare\Cloudflare WARP\warp-cli.exe"

cls
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║             AUTO RESET IP - CLOUDFLARE WARP ENGINE               ║
echo ║       Tu dong xoay IP lien tuc de khong bao gio bi Rate-Limit    ║
echo ║                                                                  ║
echo ║  Author : _LeMinhVoid_VnxD                                       ║
echo ║  Profile: https://printpf.netlify.app/                          ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

if not exist "!WARP_CLI!" (
    where warp-cli >nul 2>nul
    if errorlevel 1 (
        echo  [X] Khong tim thay warp-cli.exe! Vui long cai Cloudflare WARP.
        echo.
        pause
        exit /b 1
    )
    set "WARP_CLI=warp-cli"
)

echo  [!] Da tim thay Cloudflare WARP CLI.
echo.
set "INTERVAL="
set /p INTERVAL=  [?] Thoi gian tu dong reset IP moi lan (giay) [Mac dinh 30]: 
if "%INTERVAL%"=="" set INTERVAL=30

echo.
echo ────────────────────────────────────────────────────────────────────
echo  [*] Bat dau vong lap Auto Reset IP moi %INTERVAL% giay...
echo  [*] Nhan Ctrl+C de dung bat cu luc nao.
echo ────────────────────────────────────────────────────────────────────
echo.

set /a COUNT=0

:LOOP
set /a COUNT+=1
echo [%time:~0,8%] [#%COUNT%] Dang ngat ket noi va doi IP moi...

"!WARP_CLI!" disconnect >nul 2>&1
timeout /t 1 >nul
"!WARP_CLI!" connect >nul 2>&1
timeout /t 1 >nul

echo [%time:~0,8%] [#%COUNT%] [OK] Da ket noi IP Cloudflare moi! Nghi %INTERVAL%s truoc lan doi tiep theo...
echo.

timeout /t %INTERVAL% >nul
goto LOOP
