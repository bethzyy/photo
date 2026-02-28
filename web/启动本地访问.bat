@echo off
chcp 65001 >nul
echo.
echo ══════════════════════════════════════════
echo   照片整理工具 Web版 - 本地访问
echo ══════════════════════════════════════════
echo.
echo 启动中...
echo.
echo 本地访问: http://localhost:8080
echo.
echo 按 Ctrl+C 停止
echo ══════════════════════════════════════════
cd /d "%~dp0"
python -m http.server 8080
pause
