# 照片整理工具

两个版本，分别用于不同场景：

## 📂 目录结构

```
photo/
├── web/          # Web 版 - 手机操作电脑照片
└── android/      # Android 版 - 手机操作手机照片
```

## 🔀 版本对比

| 版本 | 操作的照片 | 访问方式 | 适用场景 |
|------|-----------|---------|---------|
| **Web 版** | 电脑上的照片 | 浏览器访问 | 手机远程整理电脑照片 |
| **Android 版** | 手机上的照片 | 安装 APK | 直接整理手机存储照片 |

---

## 📱 Web 版 (`web/`)

**用途**: 在手机浏览器中操作电脑上的照片

**启动**:
```bash
# 本地访问（仅电脑）
web/启动本地访问.bat

# 手机访问（需要 HTTPS）
web/启动手机访问.bat
```

**详细说明**: [web/README.md](web/README.md)

---

## 🤖 Android 版 (`android/`)

**用途**: 直接在手机上操作手机存储卡的照片

**开发**:
```bash
cd android
pip install kivy
python main.py  # 测试运行
```

**打包 APK** (需要 Linux/WSL):
```bash
pip install buildozer
buildozer -v android debug
```

**详细说明**: [android/README.md](android/README.md)

---

## 🚀 快速选择

- **想在手机上整理电脑照片** → 使用 Web 版
- **想在手机上整理手机照片** → 使用 Android 版
