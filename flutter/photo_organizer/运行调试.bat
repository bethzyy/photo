@echo off
chcp 65001 >nul
echo ========================================
echo    Flutter 照片管理器 - Chrome 调试
echo ========================================
echo.

REM 设置 Flutter 路径
set FLUTTER_PATH=C:\D\CAIE_tool\flutter\bin\flutter.bat

REM 检查 Flutter
%FLUTTER_PATH% --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Flutter 未安装或路径不正确
    echo 请检查: %FLUTTER_PATH%
    pause
    exit /b 1
)

REM 获取依赖
if not exist ".dart_tool\package_config.json" (
    echo [*] 首次运行，正在获取依赖...
    %FLUTTER_PATH% pub get
    echo.
)

echo [*] 启动 Chrome 浏览器调试...
echo.
echo 提示:
echo   - 按 r 热重载
echo   - 按 R 热重启
echo   - 按 q 退出
echo   - Web 版本仅用于界面调试
echo   - 文件操作功能需要在 Android 真机测试
echo.

%FLUTTER_PATH% run -d chrome

pause
