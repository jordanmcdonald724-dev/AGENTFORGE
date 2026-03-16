@echo off
echo Installing AgentForge Local Bridge...
echo.

set BRIDGE_DIR=%USERPROFILE%\.agentforge
if not exist "%BRIDGE_DIR%" mkdir "%BRIDGE_DIR%"

echo Copying files...
copy /Y "%~dp0agentforge_bridge.py" "%BRIDGE_DIR%\" >nul
copy /Y "%~dp0agentforge_bridge.bat" "%BRIDGE_DIR%\" >nul

echo Creating config...
set MANIFEST_PATH=%BRIDGE_DIR%\com.agentforge.localbridge.json

(
echo {
echo   "name": "com.agentforge.localbridge",
echo   "description": "AgentForge Local Bridge",
echo   "path": "%BRIDGE_DIR:\=\\%\\agentforge_bridge.bat",
echo   "type": "stdio",
echo   "allowed_origins": [
echo     "chrome-extension://nmakkklbhdjmddeglkgaonikejnphaii/"
echo   ]
echo }
) > "%MANIFEST_PATH%"

echo Registering with Edge...
reg add "HKCU\SOFTWARE\Microsoft\Edge\NativeMessagingHosts\com.agentforge.localbridge" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f >nul 2>&1

echo.
echo ========================================
echo   INSTALLED!
echo ========================================
echo.
echo Location: %BRIDGE_DIR%
echo.
echo NOW: Close ALL Edge windows and reopen.
echo.
pause
