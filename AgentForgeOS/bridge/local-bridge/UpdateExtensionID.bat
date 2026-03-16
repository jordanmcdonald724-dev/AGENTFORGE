@echo off
setlocal enabledelayedexpansion
title AgentForge - Update Extension ID
color 0B

echo.
echo  ==========================================
echo   AgentForge - Update Extension ID
echo  ==========================================
echo.

REM Check if ID was provided as argument
if "%~1"=="" (
    echo  No Extension ID provided as argument.
    echo.
    echo  HOW TO FIND YOUR EXTENSION ID:
    echo  1. Open your browser
    echo  2. Go to chrome://extensions or edge://extensions
    echo  3. Find "AgentForge Local Bridge"
    echo  4. Copy the ID (looks like: nmakkklbhdjmddeglkgaonikejnphaii)
    echo.
    set /p EXT_ID="Enter your Extension ID: "
) else (
    set EXT_ID=%~1
)

REM Validate ID length (should be 32 characters)
set "ID_LEN=0"
for /l %%a in (0,1,31) do if "!EXT_ID:~%%a,1!" neq "" set /a ID_LEN+=1
if !ID_LEN! neq 32 (
    echo.
    echo  [ERROR] Invalid Extension ID length!
    echo  Extension IDs should be exactly 32 characters.
    echo  You entered: !ID_LEN! characters
    echo.
    pause
    exit /b 1
)

echo.
echo  Using Extension ID: %EXT_ID%
echo.

REM Update the manifest file
set BRIDGE_DIR=%USERPROFILE%\.agentforge
set MANIFEST_PATH=%BRIDGE_DIR%\com.agentforge.localbridge.json

if not exist "%BRIDGE_DIR%" (
    echo  [ERROR] Bridge not installed!
    echo  Please run OneClickInstaller.bat first.
    pause
    exit /b 1
)

REM Escape backslashes for JSON
set "BRIDGE_PATH_ESCAPED=%BRIDGE_DIR:\=\\%"

REM Create updated manifest
(
echo {
echo   "name": "com.agentforge.localbridge",
echo   "description": "AgentForge Local Bridge - Connect to local Unreal Engine and Unity projects",
echo   "path": "%BRIDGE_PATH_ESCAPED%\\agentforge_bridge.bat",
echo   "type": "stdio",
echo   "allowed_origins": [
echo     "chrome-extension://%EXT_ID%/"
echo   ]
echo }
) > "%MANIFEST_PATH%"

echo  [OK] Updated manifest with new Extension ID
echo.
echo  ==========================================
echo   UPDATE COMPLETE!
echo  ==========================================
echo.
echo  IMPORTANT: Close ALL browser windows and reopen!
echo.
pause
