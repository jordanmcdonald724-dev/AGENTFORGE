@echo off
setlocal enabledelayedexpansion
title AgentForge Local Bridge - One-Click Installer
color 0A

echo.
echo  ================================================
echo   AgentForge Local Bridge - ONE-CLICK INSTALLER
echo  ================================================
echo.
echo  This installer will:
echo    1. Check system requirements
echo    2. Install the native messaging host
echo    3. Register with Chrome AND Edge
echo    4. Configure everything automatically
echo.
echo  Press any key to continue or CTRL+C to cancel...
pause >nul

REM ============================================
REM CHECK PYTHON
REM ============================================
echo.
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python is not installed!
    echo.
    echo  Please install Python 3.8+ from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] Python %PYVER% found

REM ============================================
REM CREATE INSTALL DIRECTORY
REM ============================================
echo.
echo [2/5] Creating installation directory...
set BRIDGE_DIR=%USERPROFILE%\.agentforge
if not exist "%BRIDGE_DIR%" (
    mkdir "%BRIDGE_DIR%"
    echo  [OK] Created %BRIDGE_DIR%
) else (
    echo  [OK] Directory exists: %BRIDGE_DIR%
)

REM ============================================
REM COPY FILES
REM ============================================
echo.
echo [3/5] Installing bridge components...
set SCRIPT_DIR=%~dp0

REM Copy Python bridge script
copy /Y "%SCRIPT_DIR%agentforge_bridge.py" "%BRIDGE_DIR%\" >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Failed to copy agentforge_bridge.py
    pause
    exit /b 1
)
echo  [OK] Installed agentforge_bridge.py

REM Copy batch launcher
copy /Y "%SCRIPT_DIR%agentforge_bridge.bat" "%BRIDGE_DIR%\" >nul 2>&1
if not exist "%BRIDGE_DIR%\agentforge_bridge.bat" (
    REM Create it if missing
    echo @echo off > "%BRIDGE_DIR%\agentforge_bridge.bat"
    echo python "%%~dp0agentforge_bridge.py" >> "%BRIDGE_DIR%\agentforge_bridge.bat"
)
echo  [OK] Installed agentforge_bridge.bat

REM ============================================
REM CREATE MANIFEST WITH KNOWN EXTENSION ID
REM ============================================
echo.
echo [4/5] Creating native messaging manifests...

REM Known Extension ID from user's installation
set EXT_ID=nmakkklbhdjmddeglkgaonikejnphaii

set MANIFEST_PATH=%BRIDGE_DIR%\com.agentforge.localbridge.json

REM Escape backslashes for JSON
set "BRIDGE_PATH_ESCAPED=%BRIDGE_DIR:\=\\%"

REM Create manifest file
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

echo  [OK] Created manifest at %MANIFEST_PATH%

REM ============================================
REM REGISTER WITH BROWSERS
REM ============================================
echo.
echo [5/5] Registering with browsers...

REM Register with Chrome
reg add "HKCU\SOFTWARE\Google\Chrome\NativeMessagingHosts\com.agentforge.localbridge" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f >nul 2>&1
if errorlevel 0 (
    echo  [OK] Registered with Google Chrome
) else (
    echo  [WARN] Chrome registration may have failed
)

REM Register with Edge
reg add "HKCU\SOFTWARE\Microsoft\Edge\NativeMessagingHosts\com.agentforge.localbridge" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f >nul 2>&1
if errorlevel 0 (
    echo  [OK] Registered with Microsoft Edge
) else (
    echo  [WARN] Edge registration may have failed
)

REM Register with Chromium
reg add "HKCU\SOFTWARE\Chromium\NativeMessagingHosts\com.agentforge.localbridge" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f >nul 2>&1
if errorlevel 0 (
    echo  [OK] Registered with Chromium
)

REM ============================================
REM VERIFY INSTALLATION
REM ============================================
echo.
echo  ================================================
echo   INSTALLATION COMPLETE!
echo  ================================================
echo.
echo  Bridge Location: %BRIDGE_DIR%
echo  Extension ID:    %EXT_ID%
echo.
echo  NEXT STEPS:
echo  -----------------------------------------------
echo  1. Close ALL browser windows (Chrome/Edge)
echo  2. Reopen your browser
echo  3. Go to AgentForge website
echo  4. The bridge should connect automatically!
echo.
echo  If the extension ID is different, run:
echo  UpdateExtensionID.bat YOUR_EXTENSION_ID
echo.
echo  ================================================
echo.
pause
