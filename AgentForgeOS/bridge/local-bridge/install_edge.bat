@echo off
REM AgentForge Local Bridge - Windows Installer for Edge
REM Run this as Administrator

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

REM Create .agentforge directory in user home
set BRIDGE_DIR=%USERPROFILE%\.agentforge
if not exist "%BRIDGE_DIR%" mkdir "%BRIDGE_DIR%"

REM Copy files
echo Copying bridge files...
copy "%~dp0agentforge_bridge.py" "%BRIDGE_DIR%\" >nul
copy "%~dp0agentforge_bridge.bat" "%BRIDGE_DIR%\" >nul

echo.
echo Go to edge://extensions and copy your AgentForge Extension ID
echo.
set /p EXT_ID=Paste Extension ID here: 

if "%EXT_ID%"=="" (
    echo ERROR: Extension ID required
    pause
    exit /b 1
)

REM Create manifest pointing to the BAT file (not .py directly)
set MANIFEST_PATH=%BRIDGE_DIR%\com.agentforge.localbridge.json

echo Creating config...
(
echo {
echo   "name": "com.agentforge.localbridge",
echo   "description": "AgentForge Local Bridge",
echo   "path": "%BRIDGE_DIR:\=\\%\\agentforge_bridge.bat",
echo   "type": "stdio",
echo   "allowed_origins": [
echo     "chrome-extension://%EXT_ID%/"
echo   ]
echo }
) > "%MANIFEST_PATH%"

REM Register for Edge
reg add "HKCU\SOFTWARE\Microsoft\Edge\NativeMessagingHosts\com.agentforge.localbridge" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f >nul 2>&1

echo.
echo ========================================
echo  DONE! Now restart Edge completely.
echo ========================================
echo.
pause
