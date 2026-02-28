/**
 * 照片整理工具 - 主应用逻辑
 */

class PhotoOrganizer {
    constructor() {
        // 状态
        this.fsManager = new FileSystemManager();
        this.photoGrid = null;
        this.subfolders = [];
        this.photos = [];
        this.currentSubfolder = null;
        this.deferredPrompt = null; // PWA 安装事件
        this.isIOS = this.detectIOS();
        this.isStandalone = this.checkStandalone();

        // DOM 元素
        this.elements = {
            currentFolder: document.getElementById('currentFolder'),
            btnSelectFolder: document.getElementById('btnSelectFolder'),
            stats: document.getElementById('stats'),
            subfolderList: document.getElementById('subfolderList'),
            btnNewFolder: document.getElementById('btnNewFolder'),
            photoGrid: document.getElementById('photoGrid'),
            emptyState: document.getElementById('emptyState'),
            loadingState: document.getElementById('loadingState'),
            actionBar: document.getElementById('actionBar'),
            btnSelectAll: document.getElementById('btnSelectAll'),
            btnDeselectAll: document.getElementById('btnDeselectAll'),
            btnMove: document.getElementById('btnMove'),
            moveDropdown: document.getElementById('moveDropdown'),
            btnDelete: document.getElementById('btnDelete'),
            newFolderModal: document.getElementById('newFolderModal'),
            newFolderName: document.getElementById('newFolderName'),
            btnCancelNewFolder: document.getElementById('btnCancelNewFolder'),
            btnConfirmNewFolder: document.getElementById('btnConfirmNewFolder'),
            confirmModal: document.getElementById('confirmModal'),
            confirmTitle: document.getElementById('confirmTitle'),
            confirmMessage: document.getElementById('confirmMessage'),
            btnCancelConfirm: document.getElementById('btnCancelConfirm'),
            btnConfirmAction: document.getElementById('btnConfirmAction'),
            toast: document.getElementById('toast'),
            installBanner: document.getElementById('installBanner'),
            btnInstallLater: document.getElementById('btnInstallLater'),
            btnInstallNow: document.getElementById('btnInstallNow'),
            iosInstallGuide: document.getElementById('iosInstallGuide'),
            closeIosGuide: document.getElementById('closeIosGuide')
        };

        // 初始化
        this.init();
    }

    /**
     * 检测是否为 iOS 设备
     */
    detectIOS() {
        const ua = navigator.userAgent;
        return /iPad|iPhone|iPod/.test(ua) ||
            (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    }

    /**
     * 检查是否已作为 PWA 运行
     */
    checkStandalone() {
        return window.matchMedia('(display-mode: standalone)').matches ||
            window.navigator.standalone === true;
    }

    /**
     * 初始化应用
     */
    async init() {
        // 初始化 PWA 安装
        this.initPWAInstall();

        // 检查浏览器兼容性
        if (!this.fsManager.isSupported()) {
            this.showBrowserWarning();
            return;
        }

        // 初始化照片网格
        this.photoGrid = new PhotoGrid('photoGrid', {
            onSelectionChange: (selected) => this.onSelectionChange(selected)
        });

        // 绑定事件
        this.bindEvents();

        // 显示空状态
        this.showEmptyState(true);

        // 如果已安装，不显示安装提示
        if (this.isStandalone) {
            this.hideInstallPrompts();
        }
    }

    /**
     * 初始化 PWA 安装功能
     */
    initPWAInstall() {
        // 监听 beforeinstallprompt 事件 (Android Chrome)
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;

            // 检查是否已安装或用户已拒绝
            if (!this.isStandalone && !this.hasUserDismissedInstall()) {
                // 延迟显示安装提示
                setTimeout(() => {
                    this.showInstallBanner();
                }, 2000);
            }
        });

        // 监听安装完成事件
        window.addEventListener('appinstalled', () => {
            this.hideInstallPrompts();
            this.showToast('应用已安装到主屏幕！', 'success');
            this.deferredPrompt = null;
        });

        // iOS 设备显示安装引导
        if (this.isIOS && !this.isStandalone && !this.hasUserDismissedInstall()) {
            setTimeout(() => {
                this.showIOSInstallGuide();
            }, 3000);
        }
    }

    /**
     * 检查用户是否已拒绝安装
     */
    hasUserDismissedInstall() {
        const dismissed = localStorage.getItem('pwa-install-dismissed');
        if (!dismissed) return false;

        // 7天后重新提示
        const dismissedTime = parseInt(dismissed, 10);
        const daysPassed = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24);
        return daysPassed < 7;
    }

    /**
     * 记录用户拒绝安装
     */
    setUserDismissedInstall() {
        localStorage.setItem('pwa-install-dismissed', Date.now().toString());
    }

    /**
     * 显示安装横幅 (Android)
     */
    showInstallBanner() {
        if (this.elements.installBanner) {
            this.elements.installBanner.style.display = 'flex';
            document.body.classList.add('has-install-banner');
        }
    }

    /**
     * 隐藏安装横幅
     */
    hideInstallBanner() {
        if (this.elements.installBanner) {
            this.elements.installBanner.style.display = 'none';
            document.body.classList.remove('has-install-banner');
        }
    }

    /**
     * 显示 iOS 安装引导
     */
    showIOSInstallGuide() {
        if (this.elements.iosInstallGuide) {
            this.elements.iosInstallGuide.style.display = 'flex';
        }
    }

    /**
     * 隐藏 iOS 安装引导
     */
    hideIOSInstallGuide() {
        if (this.elements.iosInstallGuide) {
            this.elements.iosInstallGuide.style.display = 'none';
        }
    }

    /**
     * 隐藏所有安装提示
     */
    hideInstallPrompts() {
        this.hideInstallBanner();
        this.hideIOSInstallGuide();
    }

    /**
     * 触发 PWA 安装
     */
    async installPWA() {
        if (!this.deferredPrompt) {
            // iOS 或已安装
            if (this.isIOS) {
                this.showIOSInstallGuide();
            }
            return;
        }

        // 显示安装对话框
        this.deferredPrompt.prompt();

        // 等待用户响应
        const { outcome } = await this.deferredPrompt.userChoice;

        if (outcome === 'accepted') {
            console.log('用户接受安装');
        } else {
            console.log('用户拒绝安装');
            this.setUserDismissedInstall();
        }

        this.deferredPrompt = null;
        this.hideInstallBanner();
    }

    /**
     * 显示浏览器不兼容警告
     */
    showBrowserWarning() {
        this.elements.emptyState.innerHTML = `
            <div class="empty-icon">⚠️</div>
            <p>浏览器不支持</p>
            <p class="empty-hint">
                请使用 <strong>Chrome</strong> 或 <strong>Edge</strong> 浏览器<br>
                Safari 和 Firefox 暂不支持此功能
            </p>
            <div style="margin-top: 20px; font-size: 13px; color: var(--text-secondary);">
                ${this.isIOS ? 'iOS 用户请使用 Safari 添加到主屏幕后使用' : ''}
            </div>
        `;
        this.showEmptyState(true);

        // 隐藏操作栏
        this.elements.actionBar.style.display = 'none';
    }

    /**
     * 绑定事件处理
     */
    bindEvents() {
        // 选择文件夹
        this.elements.btnSelectFolder.addEventListener('click', () => this.selectFolder());

        // 新建文件夹
        this.elements.btnNewFolder.addEventListener('click', () => this.showNewFolderModal());
        this.elements.btnCancelNewFolder.addEventListener('click', () => this.hideModal('newFolderModal'));
        this.elements.btnConfirmNewFolder.addEventListener('click', () => this.createFolder());
        this.elements.newFolderName.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.createFolder();
        });

        // 全选/反选
        this.elements.btnSelectAll.addEventListener('click', () => this.photoGrid.selectAll());
        this.elements.btnDeselectAll.addEventListener('click', () => this.photoGrid.invertSelection());

        // 移动
        this.elements.btnMove.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleMoveDropdown();
        });

        // 点击其他地方关闭下拉菜单
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.move-dropdown')) {
                this.elements.moveDropdown.classList.remove('show');
            }
        });

        // 删除
        this.elements.btnDelete.addEventListener('click', () => this.confirmDelete());

        // 确认对话框
        this.elements.btnCancelConfirm.addEventListener('click', () => this.hideModal('confirmModal'));
        this.elements.btnConfirmAction.addEventListener('click', () => this.executeConfirmAction());

        // 点击模态框背景关闭
        [this.elements.newFolderModal, this.elements.confirmModal].forEach(modal => {
            if (modal) {
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        this.hideModal(modal.id);
                    }
                });
            }
        });

        // PWA 安装相关
        if (this.elements.btnInstallLater) {
            this.elements.btnInstallLater.addEventListener('click', () => {
                this.hideInstallBanner();
                this.setUserDismissedInstall();
            });
        }

        if (this.elements.btnInstallNow) {
            this.elements.btnInstallNow.addEventListener('click', () => {
                this.installPWA();
            });
        }

        if (this.elements.closeIosGuide) {
            this.elements.closeIosGuide.addEventListener('click', () => {
                this.hideIOSInstallGuide();
                this.setUserDismissedInstall();
            });
        }

        // 点击 iOS 引导背景关闭
        if (this.elements.iosInstallGuide) {
            this.elements.iosInstallGuide.addEventListener('click', (e) => {
                if (e.target === this.elements.iosInstallGuide) {
                    this.hideIOSInstallGuide();
                    this.setUserDismissedInstall();
                }
            });
        }
    }

    /**
     * 选择文件夹
     */
    async selectFolder() {
        try {
            this.showLoading(true);

            const handle = await this.fsManager.selectFolder();
            if (!handle) {
                this.showLoading(false);
                return;
            }

            // 更新文件夹名称
            this.elements.currentFolder.textContent = this.fsManager.getFolderName();

            // 加载数据
            await this.loadFolder();

        } catch (error) {
            console.error('选择文件夹失败:', error);
            this.showToast(error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * 加载文件夹内容
     */
    async loadFolder() {
        try {
            this.showLoading(true);

            // 并行加载子文件夹和照片
            const [subfolders, photos] = await Promise.all([
                this.fsManager.getSubFolders(),
                this.fsManager.getPhotos()
            ]);

            this.subfolders = subfolders;
            this.photos = photos;

            // 渲染子文件夹
            this.renderSubfolders();

            // 渲染照片网格
            await this.photoGrid.render(photos);

            // 更新统计信息
            this.updateStats();

            // 显示/隐藏空状态
            this.showEmptyState(photos.length === 0);

        } catch (error) {
            console.error('加载文件夹失败:', error);
            this.showToast('加载文件夹失败: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * 渲染子文件夹列表
     */
    renderSubfolders() {
        const list = this.elements.subfolderList;

        if (this.subfolders.length === 0) {
            list.innerHTML = '<span class="no-subfolders" style="color: var(--text-secondary); font-size: 13px;">暂无子文件夹</span>';
            return;
        }

        list.innerHTML = this.subfolders.map(folder => `
            <button class="subfolder-tag ${this.currentSubfolder === folder.name ? 'selected' : ''}"
                    data-name="${folder.name}">
                📁 ${folder.name}
                <span class="photo-count">(${folder.photoCount})</span>
            </button>
        `).join('');

        // 绑定点击事件
        list.querySelectorAll('.subfolder-tag').forEach(tag => {
            tag.addEventListener('click', () => this.showSubfolderMenu(tag.dataset.name));
        });
    }

    /**
     * 显示子文件夹菜单（移动到该文件夹）
     */
    showSubfolderMenu(folderName) {
        // 直接移动选中的照片到该文件夹
        const selectedPhotos = this.photoGrid.getSelectedPhotos();
        if (selectedPhotos.length === 0) {
            this.showToast('请先选择要移动的照片', 'error');
            return;
        }

        this.confirmAction(
            '移动照片',
            `确定要将 ${selectedPhotos.length} 张照片移动到 "${folderName}" 文件夹吗？`,
            async () => {
                await this.moveSelectedToFolder(folderName);
            }
        );
    }

    /**
     * 更新统计信息
     */
    updateStats() {
        const selectedCount = this.photoGrid.getSelectedCount();
        const totalSize = this.photos.reduce((sum, p) => sum + p.size, 0);

        this.elements.stats.innerHTML = `
            <span class="stat-item">📊 ${this.photos.length}张照片</span>
            <span class="stat-item">已选 ${selectedCount}张</span>
            <span class="stat-item">${FileSystemManager.formatSize(totalSize)}</span>
        `;
    }

    /**
     * 选择变化回调
     */
    onSelectionChange(selected) {
        this.updateStats();
    }

    /**
     * 显示新建文件夹对话框
     */
    showNewFolderModal() {
        if (!this.fsManager.directoryHandle) {
            this.showToast('请先选择照片文件夹', 'error');
            return;
        }

        this.elements.newFolderName.value = '';
        this.showModal('newFolderModal');
        setTimeout(() => this.elements.newFolderName.focus(), 100);
    }

    /**
     * 创建文件夹
     */
    async createFolder() {
        const name = this.elements.newFolderName.value.trim();
        if (!name) {
            this.showToast('请输入文件夹名称', 'error');
            return;
        }

        try {
            const newFolder = await this.fsManager.createSubfolder(name);
            this.subfolders.push(newFolder);
            this.subfolders.sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));
            this.renderSubfolders();
            this.hideModal('newFolderModal');
            this.showToast(`已创建文件夹 "${name}"`, 'success');
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    /**
     * 切换移动下拉菜单
     */
    toggleMoveDropdown() {
        const selectedPhotos = this.photoGrid.getSelectedPhotos();
        if (selectedPhotos.length === 0) {
            this.showToast('请先选择要移动的照片', 'error');
            return;
        }

        // 填充目标文件夹列表
        if (this.subfolders.length === 0) {
            this.showToast('暂无子文件夹，请先创建', 'error');
            return;
        }

        this.elements.moveDropdown.innerHTML = this.subfolders.map(folder => `
            <button class="dropdown-item" data-name="${folder.name}">
                📁 ${folder.name} (${folder.photoCount})
            </button>
        `).join('');

        // 绑定点击事件
        this.elements.moveDropdown.querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const folderName = item.dataset.name;
                this.elements.moveDropdown.classList.remove('show');
                this.confirmAction(
                    '移动照片',
                    `确定要将 ${selectedPhotos.length} 张照片移动到 "${folderName}" 文件夹吗？`,
                    async () => {
                        await this.moveSelectedToFolder(folderName);
                    }
                );
            });
        });

        this.elements.moveDropdown.classList.toggle('show');
    }

    /**
     * 移动选中的照片到指定文件夹
     */
    async moveSelectedToFolder(folderName) {
        const selectedPhotos = this.photoGrid.getSelectedPhotos();
        if (selectedPhotos.length === 0) return;

        const folder = this.subfolders.find(f => f.name === folderName);
        if (!folder) {
            this.showToast('目标文件夹不存在', 'error');
            return;
        }

        let successCount = 0;
        let failCount = 0;

        try {
            this.showLoading(true);
            this.showToast(`正在移动 ${selectedPhotos.length} 张照片...`, 'info');

            for (const photo of selectedPhotos) {
                try {
                    await this.fsManager.movePhoto(photo.handle, folder.handle);
                    successCount++;
                } catch (error) {
                    console.error(`移动 ${photo.name} 失败:`, error);
                    failCount++;
                }
            }

            // 刷新数据
            await this.loadFolder();

            if (failCount === 0) {
                this.showToast(`成功移动 ${successCount} 张照片`, 'success');
            } else {
                this.showToast(`移动完成: 成功 ${successCount} 张, 失败 ${failCount} 张`, 'warning');
            }

        } catch (error) {
            console.error('移动照片失败:', error);
            this.showToast('移动照片失败: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * 确认删除
     */
    confirmDelete() {
        const selectedPhotos = this.photoGrid.getSelectedPhotos();
        if (selectedPhotos.length === 0) {
            this.showToast('请先选择要删除的照片', 'error');
            return;
        }

        this.confirmAction(
            '删除照片',
            `确定要删除选中的 ${selectedPhotos.length} 张照片吗？此操作不可撤销！`,
            async () => {
                await this.deleteSelected();
            }
        );
    }

    /**
     * 删除选中的照片
     */
    async deleteSelected() {
        const selectedPhotos = this.photoGrid.getSelectedPhotos();
        if (selectedPhotos.length === 0) return;

        let successCount = 0;
        let failCount = 0;

        try {
            this.showLoading(true);
            this.showToast(`正在删除 ${selectedPhotos.length} 张照片...`, 'info');

            for (const photo of selectedPhotos) {
                try {
                    await this.fsManager.deletePhoto(photo.handle);
                    successCount++;
                } catch (error) {
                    console.error(`删除 ${photo.name} 失败:`, error);
                    failCount++;
                }
            }

            // 刷新数据
            await this.loadFolder();

            if (failCount === 0) {
                this.showToast(`成功删除 ${successCount} 张照片`, 'success');
            } else {
                this.showToast(`删除完成: 成功 ${successCount} 张, 失败 ${failCount} 张`, 'warning');
            }

        } catch (error) {
            console.error('删除照片失败:', error);
            this.showToast('删除照片失败: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * 显示确认对话框
     */
    confirmAction(title, message, callback) {
        this.elements.confirmTitle.textContent = title;
        this.elements.confirmMessage.textContent = message;
        this.confirmCallback = callback;
        this.showModal('confirmModal');
    }

    /**
     * 执行确认操作
     */
    async executeConfirmAction() {
        this.hideModal('confirmModal');
        if (this.confirmCallback) {
            await this.confirmCallback();
            this.confirmCallback = null;
        }
    }

    /**
     * 显示模态框
     */
    showModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.classList.add('show');
    }

    /**
     * 隐藏模态框
     */
    hideModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.classList.remove('show');
    }

    /**
     * 显示空状态
     */
    showEmptyState(show) {
        this.elements.emptyState.style.display = show ? 'flex' : 'none';
        this.elements.photoGrid.style.display = show ? 'none' : 'grid';
    }

    /**
     * 显示加载状态
     */
    showLoading(show) {
        this.elements.loadingState.style.display = show ? 'flex' : 'none';
    }

    /**
     * 显示 Toast 通知
     */
    showToast(message, type = 'info') {
        const toast = this.elements.toast;
        toast.textContent = message;
        toast.className = 'toast show';

        if (type === 'success') {
            toast.classList.add('success');
        } else if (type === 'error') {
            toast.classList.add('error');
        }

        // 自动隐藏
        clearTimeout(this.toastTimer);
        this.toastTimer = setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.photoOrganizer = new PhotoOrganizer();
});

// 注册 Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('sw.js')
            .then(registration => {
                console.log('Service Worker 注册成功:', registration.scope);
            })
            .catch(error => {
                console.log('Service Worker 注册失败:', error);
            });
    });
}
