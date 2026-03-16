@echo off
REM AgentForge Local Bridge - Windows Installer
REM This script installs the native messaging host for Chrome

echo.
echo ========================================
echo  AgentForge Local Bridge Installer
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

REM Create the native messaging host manifest
echo Creating native messaging manifest...
set MANIFEST_PATH=%BRIDGE_DIR%\com.agentforge.localbridge.json

REM Get Python path
for /f "delims=" %%i in ('where python') do set PYTHON_PATH=%%i

REM Create manifest with proper escaping
(
echo {
echo   "name": "com.agentforge.localbridge",
echo   "description": "AgentForge Local Bridge - Connect to local Unreal Engine and Unity projects",
echo   "path": "%BRIDGE_DIR:\=\\%\\agentforge_bridge.py",
echo   "type": "stdio",
echo   "allowed_origins": [
echo     "chrome-extension://EXTENSION_ID/"
echo   ]
echo }
) > "%MANIFEST_PATH%"

REM Register with Chrome
echo Registering with Chrome...
reg add "HKCU\SOFTWARE\Google\Chrome\NativeMessagingHosts\com.agentforge.localbridge" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f >nul 2>&1

REM Also register for Edge (Chromium)
reg add "HKCU\SOFTWARE\Microsoft\Edge\NativeMessagingHosts\com.agentforge.localbridge" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f >nul 2>&1

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo Bridge installed to: %BRIDGE_DIR%
echo.
echo NEXT STEPS:
echo 1. Install the AgentForge Local Bridge extension in Chrome
echo 2. Copy the extension ID from chrome://extensions
echo 3. Run update_extension_id.bat with your extension ID
echo.
pause
