@echo off
title AgentForge - Install Dependencies
color 0B

echo.
echo  Installing AgentForge Dependencies...
echo  =====================================
echo.

:: Install backend deps
echo [1/2] Installing Python packages...
cd /d "%~dp0backend"
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python packages
    pause
    exit /b 1
)
echo [OK] Python packages installed
echo.

:: Install frontend deps
echo [2/2] Installing Node packages...
cd /d "%~dp0frontend"
call yarn install
if %errorlevel% neq 0 (
    echo [WARN] Yarn failed, trying npm...
    call npm install
)
echo [OK] Node packages installed
echo.

echo ============================================================
echo  Dependencies installed! Run START_AGENTFORGE.bat to launch
echo ============================================================
pause
