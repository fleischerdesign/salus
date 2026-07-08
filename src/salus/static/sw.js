const CACHE_NAME = 'salus-cache-v3';
const STATIC_ASSETS = [
    '/static/vendor/htmx.min.js',
    '/static/vendor/hyperscript.min.js',
    '/static/components.css',
    '/static/components.js',
    '/static/tokens.css',
    '/static/vendor/fonts.css',
    '/static/js/sync_manager.js',
    '/static/js/prefetch_manager.js',
    '/static/manifest.json',
    '/static/vendor/icon-192.png',
    '/static/offline.html'
];

// Install Event - Precache core static shell
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS);
        }).then(() => self.skipWaiting())
    );
});

// Activate Event - Clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.map(key => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch Event - Caching strategies
self.addEventListener('fetch', event => {
    // Skip non-GET requests (e.g. POST for logging sets - handled by sync queue)
    if (event.request.method !== 'GET') {
        return;
    }

    const url = new URL(event.request.url);

    // Cache-First strategy for static assets
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(event.request, { ignoreVary: true, ignoreSearch: true }).then(cachedResponse => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                return fetch(event.request).then(networkResponse => {
                    if (networkResponse && networkResponse.status === 200) {
                        const cacheCopy = networkResponse.clone();
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, cacheCopy);
                        });
                    }
                    return networkResponse;
                });
            })
        );
        return;
    }

    // Network-First falling back to Cache strategy for HTML pages
    event.respondWith(
        fetch(event.request).then(networkResponse => {
            // Cache page if it is a successful HTML response
            const acceptHeader = event.request.headers.get('accept') || '';
            if (networkResponse && networkResponse.status === 200 && acceptHeader.includes('text/html')) {
                const cacheCopy = networkResponse.clone();
                caches.open(CACHE_NAME).then(cache => {
                    cache.put(event.request, cacheCopy);
                });
            }
            return networkResponse;
        }).catch(() => {
            // Fallback to cache on network failure (offline)
            return caches.match(event.request, { ignoreVary: true, ignoreSearch: true }).then(cachedResponse => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                // If requesting an HTML page, return the cached offline fallback
                const acceptHeader = event.request.headers.get('accept') || '';
                if (acceptHeader && acceptHeader.includes('text/html')) {
                    return caches.match('/static/offline.html');
                }
            });
        })
    );
});
