@echo off
cd /d "%~dp0"
python -u agentforge_bridge.py 2>> "%USERPROFILE%\.agentforge\error.log"
