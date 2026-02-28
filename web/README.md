# 照片整理工具 - Web 版

在手机浏览器中操作电脑上的照片文件夹。

## 使用方法

### 1. 电脑端启动服务器

**方式A: 本地使用（仅电脑访问）**
```
双击 启动本地访问.bat
访问 http://localhost:8080
```

**方式B: 手机访问（需要 HTTPS）**
```
双击 启动手机访问.bat
手机浏览器访问显示的 HTTPS 地址
```

### 2. 手机访问步骤

1. 确保手机和电脑连接同一 WiFi
2. 电脑运行 `启动手机访问.bat`
3. 手机浏览器输入 `https://192.168.x.x:8443`
4. 提示"不安全"时，点击"高级"→"继续访问"
5. 选择电脑上的照片文件夹
6. 授权后即可操作

## 功能

- 📁 选择电脑上的照片文件夹
- 📂 新建/管理子文件夹
- ✅ 批量选择照片（点击、Shift范围选择、滑动多选）
- 📦 移动照片到子文件夹
- 🗑️ 删除照片
- 📊 显示统计信息
- 📱 支持添加到主屏幕 (PWA)

## 浏览器要求

| 浏览器 | 支持 |
|--------|------|
| Chrome 86+ | ✅ |
| Edge 86+ | ✅ |
| Safari | ❌ |
| Firefox | ❌ |

## 为什么需要 HTTPS？

File System Access API（用于直接操作文件）只能在安全上下文中工作：
- ✅ localhost
- ✅ HTTPS
- ❌ HTTP 局域网 IP

所以手机访问需要启动 HTTPS 服务器。

## 文件结构

```
web/
├── index.html           # 主页面
├── css/style.css        # 样式
├── js/
│   ├── app.js           # 主逻辑
│   ├── fileSystem.js    # 文件操作
│   └── photoGrid.js     # 照片网格
├── manifest.json        # PWA 配置
├── sw.js                # Service Worker
├── icons/               # 图标
├── https_server.py      # HTTPS 服务器
├── 启动本地访问.bat      # 本地启动
└── 启动手机访问.bat      # HTTPS 启动
```
