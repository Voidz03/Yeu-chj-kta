@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
title 🖥️ CHAY IP THAT - KHONG PROXY - AUTO VOTE #74412 (KHONG DONG Y)
color 0b

set "SCRIPT_DIR=%~dp0"
set "TOOL_DIR=%SCRIPT_DIR%.."

REM ==== CAU HINH CO DINH ====
set "TABS=999999999999"
set "PARALLEL=16"
set "ANSWER=kdy"
set "RATE=5"

echo.
echo  ==============================================================
echo    🖥️ CHAY VOI IP THAT - KHONG DUNG PROXY
echo    Bat ke proxies.txt co gi cung KHONG dung - chay truc tiep
echo    Dap an  : KHONG DONG Y (b) - ID 249017
echo    So phieu: 999.999.999.999 (chay lien, dung bang Ctrl+C)
echo    Luong   : 16  ^|  Toc do: 5 phieu/s/IP
echo    Author  : _LeMinhVoid_VnxD ^| https://ngau.lol/leemin
echo    Only for Cppro Family ^<3
echo  ==============================================================
echo.

REM ================= BUOC 1: KIEM TRA / CAI PYTHON =================
echo [BUOC 1/3] Kiem tra Python...
where python >nul 2>nul
if %ERRORLEVEL%==0 (
    for /f "delims=" %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
    echo   [OK] Da co !PYVER!
    set "PYTHON_EXE=python"
    goto :CHECK_PIP
)

echo   [!] Khong tim thay Python - dang tu dong tai + cai dat...
where winget >nul 2>nul
if %ERRORLEVEL%==0 (
    echo   [*] Dang cai qua winget...
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent
    goto :REFRESH_PY
)

set "PYSETUP=%TEMP%\python-3.12.8-amd64.exe"
echo   [*] Dang tai Python 3.12 installer...
curl -L -o "%PYSETUP%" https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe
if not exist "%PYSETUP%" (
    echo   [X] Tai Python that bai - kiem tra ket noi Internet roi chay lai.
    pause
    exit /b 1
)
echo   [*] Dang cai dat Python (them vao PATH, cho 2-3 phut)...
"%PYSETUP%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
del /q "%PYSETUP%" >nul 2>nul

:REFRESH_PY
set "PYTHON_EXE="
for %%d in ("%LOCALAPPDATA%\Programs\Python\*", "C:\Python*") do (
    if exist "%%~d\python.exe" if not defined PYTHON_EXE set "PYTHON_EXE=%%~d\python.exe"
)
if not defined PYTHON_EXE where python >nul 2>nul && set "PYTHON_EXE=python"
if not defined PYTHON_EXE (
    echo   [X] Cai Python that bai - thu chay lai file nay hoac cai thu cong tu python.org
    pause
    exit /b 1
)
echo   [OK] Da cai Python: !PYTHON_EXE!

:CHECK_PIP
REM ================= BUOC 2: CAI THU VIEN =================
echo.
echo [BUOC 2/3] Cai thu vien requests...
"!PYTHON_EXE!" -m pip install --quiet --upgrade pip >nul 2>nul
"!PYTHON_EXE!" -m pip install --quiet requests
if not %ERRORLEVEL%==0 (
    echo   [X] Cai requests that bai - kiem tra Internet.
    pause
    exit /b 1
)
echo   [OK] requests da san sang

REM ================= BUOC 3: CHAY IP THAT (NO PROXY) =================
echo.
echo [BUOC 3/3] Chay voi IP THAT - --no-proxy...
echo.
echo   >> Dap an : KHONG DONG Y (kdy / b)
echo   >> So phieu: 999.999.999.999 - muon dung nhan Ctrl+C
echo   >> 16 luong - 5 phieu/s/IP - IP thuc cua may
echo.

"!PYTHON_EXE!" "%TOOL_DIR%\vote_74412.py" --tabs %TABS% --parallel %PARALLEL% --answer %ANSWER% --rate %RATE% --max-rate %RATE% --no-proxy

echo.
echo  [i] Tool da dung. Chay lai file nay de tiep tuc.
pause
