@echo off
setlocal enabledelayedexpansion

REM Args
set PORT=%1
set APP_PATH=%3
set LOG_FILE=%APP_PATH%\init_shell_log_PC_kill.txt
set APP_FILE=app.py

if "%PORT%"=="" (
    echo Usage: kill_port.bat PORT LOG_FILE APP_PATH
    exit /b 1
)

echo "" > "%LOG_FILE%"

call :logmsg "Checking processes on port %PORT%"

REM === Kill processes using the port ===
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :%PORT%') do (
    call :logmsg "Killing PID %%p on port %PORT%"
    taskkill /PID %%p /F >nul 2>&1
)

call :logmsg "Port %PORT% cleared"

REM === Kill Flask app.py processes ===
for %%I in (python.exe pythonw.exe) do (
    tasklist /V /FI "IMAGENAME eq %%I" /FO CSV | findstr /I "%APP_FILE%" >nul
    if not errorlevel 1 (
        for /f "tokens=2 delims=," %%P in (
            'tasklist /V /FI "IMAGENAME eq %%I" /FO CSV ^| findstr /I "%APP_FILE%"'
        ) do (
            set PID=%%~P
            echo "Killing %%I PID !PID!"
            call :logmsg "Killing %%I PID !PID!"
            taskkill /PID !PID! /F >nul 2>&1
        )
    )
)

call :logmsg "Flask processes cleared"

exit /b 0


REM ================= FUNCTIONS =================
:logmsg
set MSG=%*
for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set DATE=%%c-%%a-%%b
set TIME=%time:~0,8%
echo [%DATE% %TIME%] [kill_port.bat] %MSG% >> "%LOG_FILE%"
exit /b