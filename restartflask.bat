@echo off
echo "Iniciando sistema... Por favor espere."

setlocal enabledelayedexpansion

REM ================= CONFIG =================
set PORT=5000
set APP_PATH=D:\ProgramasTlapa\SyncFolder\ventaproductos
set URL=http://127.0.0.1:%PORT%
set LOG_FILE=%APP_PATH%\init_shell_log_PC.txt
set APP_FILE=app.py
REM ==========================================

REM Kill processes on port + Flask
call "%~dp0killport.bat" %PORT% "%LOG_FILE%" "%APP_PATH%"
timeout /t 3 >nul

call :logmsg "----- Clear log file -----"
REM Clear log file
echo "" > "%LOG_FILE%"
REM type nul > "%LOG_FILE%"

call :logmsg "----- Starting Flask -----"
REM Start Flask fully detached, log stdout+stderr
cd /d "%APP_PATH%"
REM START "" /b cmd /c "python %APP_FILE%" >> "%LOG_FILE%" 2>&1
REM START "" cmd /c "python %APP_FILE% >> \"%LOG_FILE%\" 2>&1"
START "" /B pythonw "%APP_FILE%" 
rem >> "%LOG_FILE%" 2>&1

call :logmsg "Flask started in background. Logging to %LOG_FILE%"
timeout /t 3 >nul
REM Open browser (Chrome if available, otherwise default)
REM taskkill /FI "WINDOWTITLE eq *VentaProductosInicio*" /IM msedge.exe /F >nul 2>&1
REM taskkill /FI "WINDOWTITLE eq *VentaProductos*" /IM msedge.exe /F >nul 2>&1

REM === DEBUG: All msedge.exe processes ===
call :logmsg "DEBUG: Listing all msedge.exe processes"
tasklist /v /fi "IMAGENAME eq msedge.exe" >> "%LOG_FILE%" 2>&1
call :logmsg "DEBUG: End msedge.exe list"

REM === DEBUG: Search for URL text in tasklist ===
call :logmsg "DEBUG: Finding URL match in msedge.exe processes"
tasklist /v /fi "IMAGENAME eq msedge.exe" /fo csv | findstr /I "VentaProductos" >> "%LOG_FILE%" 2>&1
call :logmsg "DEBUG: End URL matches"

REM === Kill only msedge.exe windows pointing to our URL ===
for /f "tokens=2 delims=," %%p in (
    'tasklist /fi "IMAGENAME eq msedge.exe" /fo csv /nh'
) do (
    for /f "tokens=*" %%c in (
        'tasklist /v /fi "PID eq %%~p" /fo csv ^| findstr /I "VentaProductos"'
    ) do (
        call :logmsg "Killing msedge PID %%~p"
        taskkill /F /PID %%~p >nul 2>&1
    )
)

REM start "localhost:5000" "%URL%"
start "" msedge.exe --app="http://127.0.0.1:5000" --profile-directory="AppVentaProductos" --start-maximized

timeout /t 3 >nul
exit /b 0


REM ================= FUNCTIONS =================
:logmsg
set MSG=%*
for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set DATE=%%c-%%a-%%b
set TIME=%time:~0,8%
echo [%DATE% %TIME%] [restart_flask.bat] %MSG% >> "%LOG_FILE%"
exit /b