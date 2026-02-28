# 照片整理工具 - Android 版

直接在手机上操作手机存储卡的照片，无需网络。

## 功能

- 📁 浏览手机存储卡照片文件夹
- 📂 新建/管理子文件夹
- ✅ 批量选择照片（点击选择）
- 📦 移动照片到子文件夹
- 🗑️ 删除照片
- 📊 显示统计信息

## 开发环境

### 方式1: 在 Windows/Mac/Linux 开发

1. 安装 Python 3.8+
2. 安装 Kivy:
   ```bash
   pip install kivy
   ```

3. 运行测试:
   ```bash
   cd android
   python main.py
   ```

### 方式2: 打包成 APK

**推荐使用 Linux (WSL/Ubuntu)** 进行打包：

1. 安装 WSL (Windows Subsystem for Linux):
   ```powershell
   wsl --install -d Ubuntu
   ```

2. 在 WSL 中安装依赖:
   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-17-jdk
   pip install buildozer cython
   ```

3. 打包 APK:
   ```bash
   cd android
   buildozer init  # 如果没有 buildozer.spec
   buildozer -v android debug
   ```

4. 生成的 APK 在 `bin/` 目录

### 方式3: 使用 GitHub Actions 自动打包

1. 将代码上传到 GitHub
2. 添加 `.github/workflows/build.yml`:
   ```yaml
   name: Build Android APK
   on: [push]
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-python@v4
           with:
             python-version: '3.10'
         - run: pip install buildozer cython
         - run: cd android && buildozer -v android debug
         - uses: actions/upload-artifact@v3
           with:
             name: apk
             path: android/bin/*.apk
   ```

## 文件结构

```
android/
├── main.py           # 主程序
├── buildozer.spec    # 打包配置
└── README.md         # 说明文档
```

## 权限说明

应用需要以下权限：
- `READ_EXTERNAL_STORAGE` - 读取照片
- `WRITE_EXTERNAL_STORAGE` - 移动/删除照片
- `MANAGE_EXTERNAL_STORAGE` - Android 11+ 完整存储访问

## 注意事项

1. **Android 11+** 需要手动授予"所有文件访问"权限
2. 首次打开应用会请求存储权限
3. 建议在设置中授予完整存储访问权限
