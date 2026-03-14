@echo off
REM Update the extension ID in the native messaging manifest

if "%~1"=="" (
    echo Usage: update_extension_id.bat YOUR_EXTENSION_ID
    echo.
    echo Get your extension ID from chrome://extensions after installing the extension
    pause
    exit /b 1
)

set EXT_ID=%~1
set MANIFEST_PATH=%USERPROFILE%\.agentforge\com.agentforge.localbridge.json

if not exist "%MANIFEST_PATH%" (
    echo ERROR: Native messaging manifest not found
    echo Please run install_windows.bat first
    pause
    exit /b 1
)

REM Update the manifest
set BRIDGE_DIR=%USERPROFILE%\.agentforge

(
echo {
echo   "name": "com.agentforge.localbridge",
echo   "description": "AgentForge Local Bridge - Connect to local Unreal Engine and Unity projects",
echo   "path": "%BRIDGE_DIR:\=\\%\\agentforge_bridge.py",
echo   "type": "stdio",
echo   "allowed_origins": [
echo     "chrome-extension://%EXT_ID%/"
echo   ]
echo }
) > "%MANIFEST_PATH%"

echo.
echo Extension ID updated successfully!
echo Manifest: %MANIFEST_PATH%
echo Extension ID: %EXT_ID%
echo.
echo Please restart Chrome for changes to take effect.
echo.
pause
