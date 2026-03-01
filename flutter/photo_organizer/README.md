# Photo Organizer - Flutter 版照片管理器

跨平台照片管理工具，支持 Windows 桌面和 Android 手机。

## 功能特性

- 📁 选择源文件夹和目标文件夹
- 🖼️ 3 列网格展示照片
- ✅ 单选/全选/反选照片
- 📦 批量移动照片到目标文件夹
- 🗑️ 批量删除照片
- 📂 在目标文件夹下新建子文件夹
- 💾 自动记忆上次使用的目录

## 开发环境

### 前置要求

1. **Flutter SDK 3.0+**
2. **Windows 开发**: Visual Studio 2022 (C++ 桌面开发工作负载)
3. **Android 开发**: Android Studio / Android SDK

### 环境配置

```powershell
# 1. 下载 Flutter SDK
# 访问 https://docs.flutter.dev/get-started/install/windows
# 解压到 C:\flutter

# 2. 添加到环境变量 PATH
# C:\flutter\bin

# 3. 启用 Windows 桌面支持
flutter config --enable-windows-desktop

# 4. 验证环境
flutter doctor
```

## 运行项目

### Windows 桌面调试

```powershell
cd C:\D\CAIE_tool\MyAIProduct\photo\flutter\photo_organizer

# 首次运行需要获取依赖
flutter pub get

# 运行 Windows 桌面应用
flutter run -d windows
```

### 热重载

- 按 `r` 热重载
- 按 `R` 热重启
- 按 `q` 退出

## 打包 APK

```powershell
# 1. 确保依赖已安装
flutter pub get

# 2. 打包 release APK
flutter build apk --release

# 3. 输出位置
# build/app/outputs/flutter-apk/app-release.apk
```

## 项目结构

```
photo_organizer/
├── lib/
│   ├── main.dart              # 应用入口
│   ├── screens/
│   │   └── home_screen.dart   # 主界面
│   ├── widgets/
│   │   └── photo_item.dart    # 照片组件
│   └── services/
│       └── file_service.dart  # 文件操作服务
├── android/                   # Android 平台代码
├── windows/                   # Windows 平台代码 (需要 flutter create 生成)
└── pubspec.yaml              # 依赖配置
```

## 依赖说明

| 包名 | 用途 |
|------|------|
| `file_picker` | 文件夹选择器 |
| `shared_preferences` | 本地存储 (记忆目录) |
| `path_provider` | 路径工具 |
| `permission_handler` | Android 权限管理 |

## 注意事项

1. **首次运行**: 需要 `flutter pub get` 获取依赖
2. **Windows 平台**: 需要安装 Visual Studio 的 C++ 桌面开发组件
3. **Android 权限**: 首次打开 App 需要授予存储权限
4. **Android 11+**: 可能需要授予"所有文件访问"权限

## 从 Kivy 迁移

此项目是从 Kivy 版本照片管理器迁移而来，功能保持一致：

| Kivy | Flutter |
|------|---------|
| `main.py` | `lib/main.dart` |
| `gui.kv` | `lib/screens/home_screen.dart` |
| `fileops.py` | `lib/services/file_service.dart` |
