# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flutter 照片管理器 - 跨平台照片管理工具，用于批量整理手机/电脑上的照片。

**主要功能：** 选择源文件夹 → 网格展示照片 → 批量选择 → 移动/删除/分类

## Commands

### 开发调试
```bash
# 获取依赖
flutter pub get

# Chrome 浏览器调试（界面预览，文件功能受限）
flutter run -d chrome

# Android 模拟器调试（需要先启动模拟器）
flutter run -d emulator-5554

# 热重载: r | 热重启: R | 退出: q
```

### 打包发布
```bash
# 打包 Release APK
flutter build apk --release

# 输出位置: build/app/outputs/flutter-apk/app-release.apk
```

### 批量脚本
- `运行调试.bat` - Chrome 调试
- `打包APK.bat` - 打包 Android APK

## Architecture

### 平台适配（重要）

项目使用条件导入实现跨平台支持：

```
lib/services/
├── file_service.dart          # 跨平台接口 + Web 桩实现
├── file_service_native.dart   # 原生平台实现 (dart:io)
└── file_service_web.dart      # Web 平台桩实现
```

**关键模式：**
```dart
// 条件导入
import 'file_service_native.dart' if (dart.library.html) 'file_service_web.dart';

// 平台判断
if (kIsWeb) {
  // Web 逻辑
} else {
  // 原生逻辑
}
```

### 核心文件

| 文件 | 职责 |
|------|------|
| `lib/main.dart` | 应用入口、主题配置 |
| `lib/screens/home_screen.dart` | 主界面（所有UI和业务逻辑） |
| `lib/services/file_service.dart` | 文件操作抽象层 |
| `lib/widgets/photo_item.dart` | 照片网格项组件 |

### 数据模型

```dart
class PhotoFile {
  final String path;        // 文件路径
  final String name;        // 文件名
  final Uint8List? bytes;   // Web平台使用
  final DateTime modifiedTime;
}
```

## Android 配置

### 权限 (AndroidManifest.xml)
- `READ_EXTERNAL_STORAGE` / `WRITE_EXTERNAL_STORAGE`
- `READ_MEDIA_IMAGES` / `READ_MEDIA_VIDEO` (Android 13+)
- `MANAGE_EXTERNAL_STORAGE` (Android 11+)

### compileSdk
当前使用 `compileSdk = 35`，位于 `android/app/build.gradle`

## Known Issues

### Android 14 文件选择器
`file_picker` 在 Android 14 上可能显示 "cannot use this folder" 错误。
**解决方案：** 使用快捷按钮直接加载 `/sdcard/Pictures` 或 `/sdcard/Download`

### 模拟器黑屏
GPU 加速在某些机器上不稳定。
**解决方案：** 使用 `-gpu swiftshader_indirect` 软件渲染

```bash
emulator -avd test_phone -no-snapshot -gpu swiftshader_indirect -no-audio
```
