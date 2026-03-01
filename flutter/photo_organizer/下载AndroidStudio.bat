@echo off
chcp 65001 >nul
echo ========================================
echo    下载 Android Studio
echo ========================================
echo.

echo 请选择下载方式：
echo.
echo [1] 打开官网下载页面（推荐）
echo [2] 使用国内镜像（更快）
echo [3] 查看安装说明
echo.

set /p choice="请输入选择 (1/2/3): "

if "%choice%"=="1" (
    echo 正在打开 Android Studio 官网...
    start https://developer.android.google.cn/studio
) else if "%choice%"=="2" (
    echo 正在打开国内镜像下载页面...
    start https://www.androiddevtools.cn/
) else if "%choice%"=="3" (
    echo.
    echo ========================================
    echo Android Studio 安装说明
    echo ========================================
    echo.
    echo 1. 运行下载的 .exe 安装程序
    echo 2. 选择安装路径（建议默认）
    echo 3. 选择 "Standard" 安装类型
    echo 4. 等待 SDK 组件下载完成
    echo 5. 安装完成后，运行以下命令验证：
    echo.
    echo    flutter doctor
    echo.
    echo ========================================
    pause
) else (
    echo 无效选择
)

echo.
pause
