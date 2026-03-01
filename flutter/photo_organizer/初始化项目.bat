@echo off
chcp 65001 >nul
echo ========================================
echo    Flutter 照片管理器 - 项目初始化
echo ========================================
echo.

REM 检查 Flutter 是否安装
flutter --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Flutter 未安装或未添加到 PATH
    echo.
    echo 请按以下步骤安装 Flutter:
    echo 1. 访问 https://docs.flutter.dev/get-started/install/windows
    echo 2. 下载 flutter_windows_x.x.x-stable.zip
    echo 3. 解压到 C:\flutter
    echo 4. 添加 C:\flutter\bin 到系统 PATH 环境变量
    echo 5. 重启命令行窗口后再次运行此脚本
    echo.
    pause
    exit /b 1
)

echo [√] Flutter 已安装
echo.

REM 检查 Windows 桌面支持
echo [*] 检查 Windows 桌面支持...
flutter config --enable-windows-desktop 2>nul

REM 检查 Visual Studio
echo [*] 检查 Visual Studio...
where cl.exe >nul 2>&1
if errorlevel 1 (
    echo [警告] 未检测到 Visual Studio C++ 编译器
    echo        Windows 桌面开发需要安装 Visual Studio 2022
    echo        并选择 "使用 C++ 的桌面开发" 工作负载
    echo.
) else (
    echo [√] Visual Studio 已安装
)

echo.
echo [*] 运行 Flutter doctor...
echo.
flutter doctor

echo.
echo ========================================
echo    初始化完成！
echo ========================================
echo.
echo 接下来请运行:
echo   1. flutter pub get     (获取依赖)
echo   2. flutter run -d windows  (运行 Windows 版)
echo.
echo 或者直接运行: 运行调试.bat
echo.
pause
