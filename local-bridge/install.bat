@echo off
REM One-click installer - Extension ID already configured

echo Installing AgentForge Local Bridge...

set BRIDGE_DIR=%USERPROFILE%\.agentforge
if not exist "%BRIDGE_DIR%" mkdir "%BRIDGE_DIR%"

copy "%~dp0agentforge_bridge.py" "%BRIDGE_DIR%\" >nul
copy "%~dp0agentforge_bridge.bat" "%BRIDGE_DIR%\" >nul

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

reg add "HKCU\SOFTWARE\Microsoft\Edge\NativeMessagingHosts\com.agentforge.localbridge" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f >nul 2>&1

echo.
echo DONE! Restart Edge now.
echo.
pause
