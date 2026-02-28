/**
 * Service Worker - 离线缓存支持
 */

const CACHE_NAME = 'photo-organizer-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/index.html',
    '/css/style.css',
    '/js/fileSystem.js',
    '/js/photoGrid.js',
    '/js/app.js',
    '/manifest.json',
    '/icons/icon-192.png',
    '/icons/icon-512.png'
];

// 安装事件 - 缓存静态资源
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('缓存静态资源');
                return cache.addAll(ASSETS_TO_CACHE);
            })
            .then(() => {
                return self.skipWaiting();
            })
    );
});

// 激活事件 - 清理旧缓存
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((name) => name !== CACHE_NAME)
                        .map((name) => {
                            console.log('删除旧缓存:', name);
                            return caches.delete(name);
                        })
                );
            })
            .then(() => {
                return self.clients.claim();
            })
    );
});

// 请求事件 - 缓存优先策略
self.addEventListener('fetch', (event) => {
    // 只处理 GET 请求
    if (event.request.method !== 'GET') {
        return;
    }

    // 跳过非同源请求
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then((cachedResponse) => {
                if (cachedResponse) {
                    // 返回缓存，同时后台更新
                    fetchAndCache(event.request);
                    return cachedResponse;
                }

                // 没有缓存，从网络获取
                return fetchAndCache(event.request);
            })
            .catch(() => {
                // 网络失败，返回离线页面
                if (event.request.mode === 'navigate') {
                    return caches.match('/index.html');
                }
                return new Response('离线状态', { status: 503 });
            })
    );
});

// 从网络获取并缓存
async function fetchAndCache(request) {
    try {
        const response = await fetch(request);

        // 只缓存成功的响应
        if (response.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
        }

        return response;
    } catch (error) {
        throw error;
    }
}
