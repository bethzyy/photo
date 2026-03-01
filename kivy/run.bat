@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo ══════════════════════════════════════════
echo   照片整理工具 - Android 版 (桌面测试)
echo ══════════════════════════════════════════
echo.
python main.py
pause
