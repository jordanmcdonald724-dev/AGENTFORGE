@echo off
REM AgentForge Local Bridge - Windows Installer for Edge
REM This script installs the native messaging host for Microsoft Edge

echo.
echo ========================================
echo  AgentForge Local Bridge Installer
echo  (Microsoft Edge Version)
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Create .agentforge directory in user home
set BRIDGE_DIR=%USERPROFILE%\.agentforge
if not exist "%BRIDGE_DIR%" mkdir "%BRIDGE_DIR%"

REM Copy the bridge script
echo Copying bridge script...
copy "%SCRIPT_DIR%agentforge_bridge.py" "%BRIDGE_DIR%\agentforge_bridge.py" >nul

echo.
echo Enter your Extension ID (from edge://extensions):
set /p EXT_ID=

if "%EXT_ID%"=="" (
    echo ERROR: Extension ID is required
    pause
    exit /b 1
)

REM Create the native messaging host manifest
echo Creating native messaging manifest...
set MANIFEST_PATH=%BRIDGE_DIR%\com.agentforge.localbridge.json

REM Create manifest with the extension ID
(
echo {
echo   "name": "com.agentforge.localbridge",
echo   "description": "AgentForge Local Bridge",
echo   "path": "%BRIDGE_DIR:\=\\%\\agentforge_bridge.py",
echo   "type": "stdio",
echo   "allowed_origins": [
echo     "chrome-extension://%EXT_ID%/"
echo   ]
echo }
) > "%MANIFEST_PATH%"

REM Register with Edge
echo Registering with Microsoft Edge...
reg add "HKCU\SOFTWARE\Microsoft\Edge\NativeMessagingHosts\com.agentforge.localbridge" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f >nul 2>&1

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo Bridge installed to: %BRIDGE_DIR%
echo Extension ID: %EXT_ID%
echo.
echo NOW: Restart Microsoft Edge completely
echo.
pause
