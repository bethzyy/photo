/**
 * 文件系统操作封装
 * 使用 File System Access API 进行文件操作
 */

class FileSystemManager {
    constructor() {
        this.directoryHandle = null;
        this.dbName = 'PhotoOrganizerDB';
        this.dbStore = 'directoryHandles';
        this.db = null;
    }

    /**
     * 初始化 IndexedDB
     */
    async initDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, 1);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(this.dbStore)) {
                    db.createObjectStore(this.dbStore, { keyPath: 'id' });
                }
            };
        });
    }

    /**
     * 保存目录句柄到 IndexedDB
     */
    async saveDirectoryHandle(handle) {
        if (!this.db) await this.initDB();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.dbStore], 'readwrite');
            const store = transaction.objectStore(this.dbStore);
            const request = store.put({ id: 'lastDirectory', handle });

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * 从 IndexedDB 加载目录句柄
     */
    async loadDirectoryHandle() {
        if (!this.db) await this.initDB();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.dbStore], 'readonly');
            const store = transaction.objectStore(this.dbStore);
            const request = store.get('lastDirectory');

            request.onsuccess = () => {
                if (request.result && request.result.handle) {
                    resolve(request.result.handle);
                } else {
                    resolve(null);
                }
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * 检查浏览器是否支持 File System Access API
     */
    isSupported() {
        return 'showDirectoryPicker' in window;
    }

    /**
     * 选择文件夹
     */
    async selectFolder() {
        if (!this.isSupported()) {
            throw new Error('您的浏览器不支持文件系统访问功能。请使用 Chrome 或 Edge 浏览器。');
        }

        try {
            // 尝试加载之前保存的句柄
            const savedHandle = await this.loadDirectoryHandle();

            if (savedHandle) {
                // 检查是否有权限
                const permission = await savedHandle.queryPermission({ mode: 'readwrite' });
                if (permission === 'granted') {
                    this.directoryHandle = savedHandle;
                    return savedHandle;
                }
                // 请求权限
                const requestPermission = await savedHandle.requestPermission({ mode: 'readwrite' });
                if (requestPermission === 'granted') {
                    this.directoryHandle = savedHandle;
                    return savedHandle;
                }
            }

            // 弹出文件夹选择器
            const handle = await window.showDirectoryPicker({
                mode: 'readwrite',
                startIn: 'pictures'
            });

            this.directoryHandle = handle;
            await this.saveDirectoryHandle(handle);
            return handle;

        } catch (error) {
            if (error.name === 'AbortError') {
                // 用户取消了选择
                return null;
            }
            throw error;
        }
    }

    /**
     * 获取当前文件夹名称
     */
    getFolderName() {
        return this.directoryHandle ? this.directoryHandle.name : '';
    }

    /**
     * 获取子文件夹列表
     */
    async getSubFolders() {
        if (!this.directoryHandle) {
            return [];
        }

        const subfolders = [];
        for await (const entry of this.directoryHandle.values()) {
            if (entry.kind === 'directory') {
                // 获取子文件夹中的照片数量
                const photoCount = await this.countPhotosInFolder(entry);
                subfolders.push({
                    name: entry.name,
                    handle: entry,
                    photoCount: photoCount
                });
            }
        }

        // 按名称排序
        subfolders.sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));
        return subfolders;
    }

    /**
     * 统计文件夹中的照片数量
     */
    async countPhotosInFolder(folderHandle) {
        let count = 0;
        try {
            for await (const entry of folderHandle.values()) {
                if (entry.kind === 'file' && this.isPhotoFile(entry.name)) {
                    count++;
                }
            }
        } catch (error) {
            console.warn(`无法读取文件夹 ${folderHandle.name}:`, error);
        }
        return count;
    }

    /**
     * 创建子文件夹
     */
    async createSubfolder(name) {
        if (!this.directoryHandle) {
            throw new Error('请先选择照片文件夹');
        }

        // 验证文件夹名称
        const sanitizedName = this.sanitizeFolderName(name);
        if (!sanitizedName) {
            throw new Error('文件夹名称无效');
        }

        // 检查是否已存在
        try {
            await this.directoryHandle.getDirectoryHandle(sanitizedName);
            throw new Error('文件夹已存在');
        } catch (error) {
            if (error.message === '文件夹已存在') {
                throw error;
            }
            // 文件夹不存在，可以创建
        }

        const newHandle = await this.directoryHandle.getDirectoryHandle(sanitizedName, { create: true });
        return {
            name: sanitizedName,
            handle: newHandle,
            photoCount: 0
        };
    }

    /**
     * 清理文件夹名称
     */
    sanitizeFolderName(name) {
        // 移除不允许的字符
        return name
            .replace(/[<>:"/\\|?*\x00-\x1f]/g, '')
            .replace(/^\.+/, '')
            .replace(/\.+$/, '')
            .trim()
            .substring(0, 100);
    }

    /**
     * 判断是否为照片文件
     */
    isPhotoFile(filename) {
        const ext = filename.toLowerCase().split('.').pop();
        return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'heic', 'heif', 'raw', 'tiff', 'tif'].includes(ext);
    }

    /**
     * 获取所有照片（仅当前文件夹，不包括子文件夹）
     */
    async getPhotos() {
        if (!this.directoryHandle) {
            return [];
        }

        const photos = [];
        for await (const entry of this.directoryHandle.values()) {
            if (entry.kind === 'file' && this.isPhotoFile(entry.name)) {
                const file = await entry.getFile();
                photos.push({
                    name: entry.name,
                    handle: entry,
                    file: file,
                    size: file.size,
                    lastModified: file.lastModified
                });
            }
        }

        // 按修改时间排序（最新的在前）
        photos.sort((a, b) => b.lastModified - a.lastModified);
        return photos;
    }

    /**
     * 生成照片缩略图 URL
     */
    async getPhotoThumbnail(photo, maxSize = 200) {
        if (photo.thumbnailUrl) {
            return photo.thumbnailUrl;
        }

        const url = URL.createObjectURL(photo.file);
        photo.thumbnailUrl = url;
        return url;
    }

    /**
     * 移动照片到目标文件夹
     */
    async movePhoto(photoHandle, destFolderHandle) {
        if (!this.directoryHandle) {
            throw new Error('请先选择照片文件夹');
        }

        try {
            // 读取原文件内容
            const file = await photoHandle.getFile();

            // 在目标文件夹创建新文件
            await destFolderHandle.getFileHandle(photoHandle.name, { create: true });
            const newFileHandle = await destFolderHandle.getFileHandle(photoHandle.name, { create: true });

            // 写入文件内容
            const writable = await newFileHandle.createWritable();
            await writable.write(file);
            await writable.close();

            // 删除原文件
            await this.directoryHandle.removeEntry(photoHandle.name);

            return true;
        } catch (error) {
            console.error(`移动照片失败: ${photoHandle.name}`, error);
            throw new Error(`移动 ${photoHandle.name} 失败: ${error.message}`);
        }
    }

    /**
     * 删除照片
     */
    async deletePhoto(photoHandle) {
        if (!this.directoryHandle) {
            throw new Error('请先选择照片文件夹');
        }

        try {
            await this.directoryHandle.removeEntry(photoHandle.name);
            return true;
        } catch (error) {
            console.error(`删除照片失败: ${photoHandle.name}`, error);
            throw new Error(`删除 ${photoHandle.name} 失败: ${error.message}`);
        }
    }

    /**
     * 释放资源
     */
    releasePhotoUrls(photos) {
        photos.forEach(photo => {
            if (photo.thumbnailUrl) {
                URL.revokeObjectURL(photo.thumbnailUrl);
            }
        });
    }

    /**
     * 格式化文件大小
     */
    static formatSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
}

// 导出
window.FileSystemManager = FileSystemManager;
