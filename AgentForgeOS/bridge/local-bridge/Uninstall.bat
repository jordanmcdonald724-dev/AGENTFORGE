@echo off
title AgentForge Local Bridge - Uninstaller
color 0C

echo.
echo  ==========================================
echo   AgentForge Local Bridge - UNINSTALLER
echo  ==========================================
echo.
echo  This will remove the AgentForge Local Bridge
echo  from your system.
echo.
set /p CONFIRM="Are you sure? (Y/N): "

if /i not "%CONFIRM%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo [1/3] Removing registry entries...

REM Remove Chrome registration
reg delete "HKCU\SOFTWARE\Google\Chrome\NativeMessagingHosts\com.agentforge.localbridge" /f >nul 2>&1
echo  [OK] Removed Chrome registration

REM Remove Edge registration
reg delete "HKCU\SOFTWARE\Microsoft\Edge\NativeMessagingHosts\com.agentforge.localbridge" /f >nul 2>&1
echo  [OK] Removed Edge registration

REM Remove Chromium registration
reg delete "HKCU\SOFTWARE\Chromium\NativeMessagingHosts\com.agentforge.localbridge" /f >nul 2>&1
echo  [OK] Removed Chromium registration

echo.
echo [2/3] Removing bridge files...

set BRIDGE_DIR=%USERPROFILE%\.agentforge

if exist "%BRIDGE_DIR%\agentforge_bridge.py" del "%BRIDGE_DIR%\agentforge_bridge.py"
if exist "%BRIDGE_DIR%\agentforge_bridge.bat" del "%BRIDGE_DIR%\agentforge_bridge.bat"
if exist "%BRIDGE_DIR%\com.agentforge.localbridge.json" del "%BRIDGE_DIR%\com.agentforge.localbridge.json"
echo  [OK] Removed bridge files

echo.
echo [3/3] Keeping logs for reference...
echo  Log files are still at: %BRIDGE_DIR%\bridge.log
echo.
echo  ==========================================
echo   UNINSTALL COMPLETE!
echo  ==========================================
echo.
echo  You can now remove the browser extension manually
echo  from chrome://extensions or edge://extensions
echo.
pause
