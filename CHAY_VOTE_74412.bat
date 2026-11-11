@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
title 🚀 AUTO VOTE VNEXPRESS #74412 (V5 PURE HTTP) - THI LỚP 10 CHUYÊN THEO KHỐI (_LeMinhVoid_VnxD)
color 0b

set "SCRIPT_DIR=%~dp0"
set TABS=1500
set PARALLEL=12
set ANSWER=dky
set RATE=4.5

:MENU
cls
echo.
echo  ======================================================================
echo    🚀 AUTO VOTE VNEXPRESS - KHẢO SÁT #74412 (V5 PURE HTTP)
echo    Tiêu đề  : "Quan điểm của bạn về việc thi lớp 10 chuyên theo khối?"
echo    Mục tiêu : "Đồng ý" (ID: 249016) - đổi được ở menu [4]
echo    Tốc độ   : ~16.000 phiếu/giờ được đếm thật (4.5 phiếu/s/IP)
echo    Author   : _LeMinhVoid_VnxD ^| https://printpf.netlify.app/
echo  ======================================================================
echo.
echo   KHÔNG cần Chrome/Chromium, KHÔNG captcha - chỉ cần Internet.
echo.
echo   CHỌN CHẾ ĐỘ CHẠY KHẢO SÁT #74412:
echo.
echo     [1] ⚡ CÀY 1.500 PHIẾU  (~6 phút)
echo     [2] ⚡ CÀY 3.000 PHIẾU  (~11 phút)
echo     [3] ⚡ CÀY 5.000 PHIẾU  (~19 phút)
echo     [4] 🛠️ TÙY CHỈNH SỐ LƯỢNG / LUỒNG / TỐC ĐỘ / ĐÁP ÁN
echo     [5] 🔄 BẬT TỰ ĐỘNG XOAY IP CLOUDFLARE WARP (Chạy song song)
echo     [6] 🧪 CHẠY THỬ 50 PHIẾU (kiểm tra trước khi cày lớn)
echo     [0] 🔙 Quay lại / Thoát
echo.
echo     Cấu hình hiện tại: !ANSWER! - !TABS! phiếu - !PARALLEL! luồng - !RATE! phiếu/s
echo.

set "OPT="
set /p OPT=">> Nhập lựa chọn của bạn [0-6, mặc định 1]: "
if "%OPT%"=="" set OPT=1

if "%OPT%"=="0" exit /b
if "%OPT%"=="1" goto :RUN
if "%OPT%"=="2" (
    set TABS=3000
    goto :RUN
)
if "%OPT%"=="3" (
    set TABS=5000
    goto :RUN
)
if "%OPT%"=="4" goto :CUSTOM
if "%OPT%"=="5" (
    start cmd /k "call \"%SCRIPT_DIR%AUTO_RESET_IP_CLOUDFLARE.bat\""
    goto :MENU
)
if "%OPT%"=="6" (
    set TABS=50
    goto :RUN
)
goto :MENU

:CUSTOM
echo.
echo   CHỌN ĐÁP ÁN MỤC TIÊU:
echo     [a] Đồng ý        - ID: 249016
echo     [b] Không đồng ý  - ID: 249017
set "ANSWER="
set /p ANSWER=">> Nhập a / b / dky / kdy / ID số [mặc định a]: "
if "%ANSWER%"=="" set ANSWER=a
if /i "%ANSWER%"=="a" set ANSWER=dky
if /i "%ANSWER%"=="b" set ANSWER=kdy
echo.
set "TABS="
set /p TABS=">> Nhập số lượng phiếu muốn buff [mặc định 1500]: "
if "%TABS%"=="" set TABS=1500
echo.
set "PARALLEL="
set /p PARALLEL=">> Nhập số luồng [mặc định 12, nên 8-16]: "
if "%PARALLEL%"=="" set PARALLEL=12
echo.
set "RATE="
set /p RATE=">> Nhập tốc độ phiếu/s mỗi IP [mặc định 4.5, tối đa nên 5]: "
if "%RATE%"=="" set RATE=4.5
goto :RUN

:RUN
echo.
echo  [*] Đang khởi động buff #74412 - %PARALLEL% luồng - %RATE% phiếu/s - đáp án: %ANSWER%...
echo.
python -c "import requests" >nul 2>nul
if not %ERRORLEVEL%==0 (
    echo  [*] Thiếu thư viện requests - đang cài...
    python -m pip install --quiet requests
)
if exist "%SCRIPT_DIR%proxies.txt" (
    python "%SCRIPT_DIR%vote_74412.py" --tabs %TABS% --parallel %PARALLEL% --answer %ANSWER% --rate %RATE% --proxy-file "%SCRIPT_DIR%proxies.txt"
) else (
    python "%SCRIPT_DIR%vote_74412.py" --tabs %TABS% --parallel %PARALLEL% --answer %ANSWER% --rate %RATE%
)
echo.
pause
goto :MENU
