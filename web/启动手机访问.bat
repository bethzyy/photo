@echo off
chcp 65001 >nul
cd /d "%~dp0"
python https_server.py
pause
