@echo off
title AgentForge Local Server
color 0A

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║            AGENTFORGE v4.5 - LOCAL SERVER                 ║
echo  ║              AI Development Studio                         ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

:: Check if Node is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found! Install from https://nodejs.org
    pause
    exit /b 1
)

:: Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Install from https://python.org
    pause
    exit /b 1
)

echo [OK] Node.js found
echo [OK] Python found
echo.

:: Check MongoDB
echo [INFO] Checking MongoDB...
where mongod >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARN] MongoDB not in PATH - will try default location or use cloud
)

echo.
echo ============================================================
echo  Starting AgentForge Services...
echo ============================================================
echo.

:: Start Backend
echo [1/2] Starting Backend (FastAPI)...
cd /d "%~dp0backend"
start "AgentForge Backend" cmd /k "pip install -r requirements.txt >nul 2>nul && python server.py"

:: Wait for backend
timeout /t 5 /nobreak >nul

:: Start Frontend
echo [2/2] Starting Frontend (React)...
cd /d "%~dp0frontend"
start "AgentForge Frontend" cmd /k "yarn install >nul 2>nul && yarn start"

echo.
echo ============================================================
echo  AgentForge is starting up!
echo ============================================================
echo.
echo  Frontend: http://localhost:3000
echo  Backend:  http://localhost:8001
echo.
echo  Close this window to stop all services.
echo ============================================================
echo.

pause
