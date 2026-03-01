@echo off
chcp 65001 >nul
echo ========================================
echo    Flutter 照片管理器 - 打包 APK
echo ========================================
echo.

REM 检查 Flutter
flutter --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Flutter 未安装，请先运行 初始化项目.bat
    pause
    exit /b 1
)

echo [*] 获取依赖...
flutter pub get

echo.
echo [*] 开始打包 APK (Release 模式)...
echo     这可能需要几分钟时间...
echo.

flutter build apk --release

if errorlevel 1 (
    echo.
    echo [错误] 打包失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo    打包成功！
echo ========================================
echo.
echo APK 文件位置:
echo   build\app\outputs\flutter-apk\app-release.apk
echo.
echo 将此文件复制到手机安装即可使用
echo.
pause
