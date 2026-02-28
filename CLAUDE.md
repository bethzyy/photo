# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Photo Organizer Tool** (照片整理工具) with two versions for different use cases:

| Version | Location | Purpose | Photos Location |
|---------|----------|---------|-----------------|
| Web | `web/` | Mobile browser controls PC photos | PC storage |
| Android | `android/` | Native app controls phone photos | Phone storage |

## Quick Commands

### Android Version (Kivy)
```bash
cd android
python main.py              # Run on desktop for testing
buildozer -v android debug  # Build APK (requires Linux/WSL)
```

### Web Version (PWA)
```bash
cd web
python -m http.server 8080           # Local access only
python https_server.py               # HTTPS for mobile access
```

## Architecture

### Android Version (`android/main.py`)

Single-file Kivy application with:

- **Custom Widgets**: `CLabel`, `CButton`, `CTextInput` - Wrap Kivy widgets with Chinese font support (msyh.ttc/simhei.ttf)
- **PhotoItem**: Displays photo thumbnail with selection state (blue overlay when selected)
- **PhotoGrid**: 3-column GridLayout for photo thumbnails
- **AppMain**: Main application class with Kivy properties (`folder`, `photos`, `selected`, `subs`)

Key implementation details:
- Window size: 360×640 (mobile portrait simulation)
- Config stored in `config.json` (last_folder)
- Chinese font must be set before Kivy initialization via `Config.set()`
- Touch handling uses `on_touch_down()` override, not event binding (required for ScrollView compatibility)
- Selection state passed to PhotoItem constructor for correct visual state on re-render

### Web Version (`web/`)

PWA using File System Access API:
- `js/fileSystem.js` - Directory picker, file operations
- `js/photoGrid.js` - Photo grid with selection
- `js/app.js` - Main application logic
- `https_server.py` - Self-signed certificate for HTTPS (required for File System Access API on mobile)

**Browser Support**: Chrome/Edge 86+ only (Safari/Firefox don't support File System Access API)

## Common Issues

### Android - Chinese Font (乱码)
Kivy requires explicit font configuration:
```python
Config.set("kivy", "default_font", ["YaHei", "C:/Windows/Fonts/msyh.ttc"])
```
All custom widgets (`CLabel`, `CButton`, `CTextInput`) must set `font_name` in `__init__`.

### Android - Selection State Not Updating
When calling `render()`, must pass selection state to PhotoItem:
```python
PhotoItem(path, callback, selected=(path in self.selected))
```

### Android - Touch Events in ScrollView
Use `on_touch_down()` method override on widget, not `bind(on_touch_down=...)`. The latter doesn't work correctly inside ScrollView.

### Web - HTTPS Required for Mobile
File System Access API only works in secure contexts:
- ✅ localhost
- ✅ HTTPS
- ❌ HTTP with LAN IP

## Build APK (Android)

Requires Linux environment (WSL on Windows):
```bash
sudo apt install -y git zip unzip openjdk-17-jdk
pip install buildozer cython
cd android
buildozer -v android debug
```

Output: `android/bin/*.apk`

## Permissions (Android)

- `READ_EXTERNAL_STORAGE` - Read photos
- `WRITE_EXTERNAL_STORAGE` - Move/delete photos
- `MANAGE_EXTERNAL_STORAGE` - Android 11+ full storage access
