/**
 * 照片网格组件
 * 处理照片显示和选择逻辑
 */

class PhotoGrid {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.photos = [];
        this.selectedIndices = new Set();
        this.lastSelectedIndex = -1;
        this.isSelecting = false;
        this.selectStartIndex = -1;

        // 回调函数
        this.onSelectionChange = options.onSelectionChange || (() => {});
        this.onPhotoClick = options.onPhotoClick || (() => {});

        // 绑定事件
        this.bindEvents();
    }

    /**
     * 绑定事件处理
     */
    bindEvents() {
        // 键盘事件
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.deselectAll();
                this.render();
            }
        });
    }

    /**
     * 渲染照片网格
     */
    async render(photos) {
        if (photos) {
            this.photos = photos;
            this.selectedIndices.clear();
            this.lastSelectedIndex = -1;
        }

        if (!this.photos || this.photos.length === 0) {
            this.container.innerHTML = '';
            return;
        }

        const fragment = document.createDocumentFragment();

        for (let i = 0; i < this.photos.length; i++) {
            const photo = this.photos[i];
            const item = document.createElement('div');
            item.className = 'photo-item';
            item.dataset.index = i;

            // 创建缩略图
            const img = document.createElement('img');
            img.loading = 'lazy';
            img.alt = photo.name;

            // 使用 Promise 加载缩略图
            this.loadThumbnail(photo).then(url => {
                img.src = url;
            }).catch(() => {
                img.src = 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23E1E8ED" width="100" height="100"/><text x="50" y="50" text-anchor="middle" fill="%237F8C8D" font-size="30">📷</text></svg>');
            });

            // 创建复选框
            const checkbox = document.createElement('div');
            checkbox.className = 'checkbox';
            checkbox.innerHTML = `
                <svg viewBox="0 0 24 24">
                    <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-9.99-5.84L7.59 11l-1.41 1.41 4.24 4.24 8-8-1.41-1.41-6.59 6.59-1.42-1.42z"/>
                </svg>
            `;

            // 文件名
            const fileName = document.createElement('div');
            fileName.className = 'file-name';
            fileName.textContent = photo.name;

            item.appendChild(img);
            item.appendChild(checkbox);
            item.appendChild(fileName);

            // 绑定点击事件
            item.addEventListener('click', (e) => this.handleClick(e, i));

            // 触摸事件用于滑动多选
            item.addEventListener('touchstart', (e) => this.handleTouchStart(e, i), { passive: true });
            item.addEventListener('touchmove', (e) => this.handleTouchMove(e), { passive: false });
            item.addEventListener('touchend', (e) => this.handleTouchEnd(e));

            fragment.appendChild(item);
        }

        this.container.innerHTML = '';
        this.container.appendChild(fragment);

        // 应用已选中状态
        this.updateSelectedUI();
    }

    /**
     * 加载缩略图
     */
    async loadThumbnail(photo) {
        if (photo.thumbnailUrl) {
            return photo.thumbnailUrl;
        }

        return new Promise((resolve, reject) => {
            const url = URL.createObjectURL(photo.file);
            const img = new Image();

            img.onload = () => {
                photo.thumbnailUrl = url;
                resolve(url);
            };

            img.onerror = () => {
                URL.revokeObjectURL(url);
                reject(new Error('加载失败'));
            };

            img.src = url;
        });
    }

    /**
     * 处理点击事件
     */
    handleClick(e, index) {
        e.preventDefault();
        e.stopPropagation();

        const isShiftKey = e.shiftKey;
        const isCtrlKey = e.ctrlKey || e.metaKey;

        if (isShiftKey && this.lastSelectedIndex >= 0) {
            // Shift+点击: 范围选择
            this.selectRange(this.lastSelectedIndex, index);
        } else if (isCtrlKey) {
            // Ctrl+点击: 切换单个
            this.toggleSingle(index);
            this.lastSelectedIndex = index;
        } else {
            // 普通点击: 切换单个
            this.toggleSingle(index);
            this.lastSelectedIndex = index;
        }

        this.updateSelectedUI();
        this.onSelectionChange(this.getSelectedPhotos());
    }

    /**
     * 触摸开始
     */
    handleTouchStart(e, index) {
        // 长按检测
        this.longPressTimer = setTimeout(() => {
            this.isSelecting = true;
            this.selectStartIndex = index;
            this.toggleSingle(index);
            this.updateSelectedUI();
            this.showSelectionBadge();
        }, 300);

        this.touchStartIndex = index;
    }

    /**
     * 触摸移动
     */
    handleTouchMove(e) {
        // 清除长按计时器
        if (this.longPressTimer) {
            clearTimeout(this.longPressTimer);
            this.longPressTimer = null;
        }

        if (!this.isSelecting) return;

        e.preventDefault();

        // 获取触摸点下的元素
        const touch = e.touches[0];
        const element = document.elementFromPoint(touch.clientX, touch.clientY);

        if (element) {
            const photoItem = element.closest('.photo-item');
            if (photoItem) {
                const currentIndex = parseInt(photoItem.dataset.index);
                if (!isNaN(currentIndex) && currentIndex !== this.lastTouchedIndex) {
                    this.lastTouchedIndex = currentIndex;

                    // 选择范围内的所有照片
                    const start = Math.min(this.selectStartIndex, currentIndex);
                    const end = Math.max(this.selectStartIndex, currentIndex);

                    for (let i = start; i <= end; i++) {
                        this.selectedIndices.add(i);
                    }

                    this.updateSelectedUI();
                    this.updateSelectionBadge();
                    this.onSelectionChange(this.getSelectedPhotos());
                }
            }
        }
    }

    /**
     * 触摸结束
     */
    handleTouchEnd(e) {
        if (this.longPressTimer) {
            clearTimeout(this.longPressTimer);
            this.longPressTimer = null;
        }

        if (this.isSelecting) {
            this.isSelecting = false;
            this.hideSelectionBadge();
        }
    }

    /**
     * 切换单个选择状态
     */
    toggleSingle(index) {
        if (this.selectedIndices.has(index)) {
            this.selectedIndices.delete(index);
        } else {
            this.selectedIndices.add(index);
        }
    }

    /**
     * 选择单个照片
     */
    selectSingle(index) {
        this.selectedIndices.add(index);
    }

    /**
     * 范围选择
     */
    selectRange(start, end) {
        const minIndex = Math.min(start, end);
        const maxIndex = Math.max(start, end);

        for (let i = minIndex; i <= maxIndex; i++) {
            this.selectedIndices.add(i);
        }
    }

    /**
     * 全选
     */
    selectAll() {
        for (let i = 0; i < this.photos.length; i++) {
            this.selectedIndices.add(i);
        }
        this.updateSelectedUI();
        this.onSelectionChange(this.getSelectedPhotos());
    }

    /**
     * 取消全选
     */
    deselectAll() {
        this.selectedIndices.clear();
        this.updateSelectedUI();
        this.onSelectionChange(this.getSelectedPhotos());
    }

    /**
     * 反选
     */
    invertSelection() {
        const newSelection = new Set();
        for (let i = 0; i < this.photos.length; i++) {
            if (!this.selectedIndices.has(i)) {
                newSelection.add(i);
            }
        }
        this.selectedIndices = newSelection;
        this.updateSelectedUI();
        this.onSelectionChange(this.getSelectedPhotos());
    }

    /**
     * 更新选中状态的 UI
     */
    updateSelectedUI() {
        const items = this.container.querySelectorAll('.photo-item');
        items.forEach((item, index) => {
            if (this.selectedIndices.has(index)) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    /**
     * 获取选中的照片
     */
    getSelectedPhotos() {
        const selected = [];
        this.selectedIndices.forEach(index => {
            if (this.photos[index]) {
                selected.push(this.photos[index]);
            }
        });
        return selected;
    }

    /**
     * 获取选中数量
     */
    getSelectedCount() {
        return this.selectedIndices.size;
    }

    /**
     * 显示选中计数徽章
     */
    showSelectionBadge() {
        let badge = document.getElementById('selectionBadge');
        if (!badge) {
            badge = document.createElement('div');
            badge.id = 'selectionBadge';
            badge.className = 'selection-badge';
            document.body.appendChild(badge);
        }
        badge.classList.add('show');
        this.updateSelectionBadge();
    }

    /**
     * 更新选中计数徽章
     */
    updateSelectionBadge() {
        const badge = document.getElementById('selectionBadge');
        if (badge) {
            badge.textContent = `已选 ${this.selectedIndices.size} 张`;
        }
    }

    /**
     * 隐藏选中计数徽章
     */
    hideSelectionBadge() {
        const badge = document.getElementById('selectionBadge');
        if (badge) {
            badge.classList.remove('show');
        }
    }

    /**
     * 移除指定照片
     */
    removePhotos(photosToRemove) {
        const removeSet = new Set(photosToRemove);
        this.photos = this.photos.filter(p => !removeSet.has(p));

        // 重建选中索引
        const newSelection = new Set();
        let newIndex = 0;
        this.photos.forEach((photo, oldIndex) => {
            if (this.selectedIndices.has(oldIndex)) {
                newSelection.add(newIndex);
            }
            newIndex++;
        });
        this.selectedIndices = newSelection;

        return this.render();
    }

    /**
     * 清理资源
     */
    destroy() {
        this.photos.forEach(photo => {
            if (photo.thumbnailUrl) {
                URL.revokeObjectURL(photo.thumbnailUrl);
            }
        });
    }
}

// 导出
window.PhotoGrid = PhotoGrid;
