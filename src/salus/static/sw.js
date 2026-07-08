const STATIC_CACHE_NAME = 'salus-static-v7';
const DATA_CACHE_NAME = 'salus-data-v7';

const FALLBACK_STATIC_ASSETS = [
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
    '/static/offline.html',
    '/login?pwa=true'
];

// Install Event - Precache core static shell (dynamic fetch + local fallback)
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(STATIC_CACHE_NAME).then(async cache => {
            let assets = FALLBACK_STATIC_ASSETS;
            try {
                const response = await fetch('/api/v1/pwa/static-assets');
                if (response.ok) {
                    assets = await response.json();
                }
            } catch (err) {
                console.warn('[ServiceWorker] Failed to fetch static assets list from server, using fallback:', err);
            }
            const requests = assets.map(url => new Request(url, { cache: 'reload' }));
            return cache.addAll(requests);
        }).then(() => self.skipWaiting())
    );
});

// Activate Event - Clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.map(key => {
                    if (key !== STATIC_CACHE_NAME && key !== DATA_CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch Event - Caching strategies
self.addEventListener('fetch', event => {
    // Skip non-GET requests (handled by sync queue)
    if (event.request.method !== 'GET') {
        return;
    }

    const url = new URL(event.request.url);

    // 1. Intercept offline logout
    if (url.pathname === '/auth/logout') {
        event.respondWith(
            caches.delete(DATA_CACHE_NAME).then(() => {
                console.log('[ServiceWorker] Logged out offline. Purged data cache.');
                return Response.redirect('/login', 303);
            })
        );
        return;
    }

    // 2. Serve /login offline using the precached PWA login shell
    if (url.pathname === '/login') {
        event.respondWith(
            fetch(event.request).then(networkResponse => {
                if (networkResponse && networkResponse.status === 200) {
                    const cacheCopy = networkResponse.clone();
                    caches.open(STATIC_CACHE_NAME).then(cache => {
                        cache.put('/login?pwa=true', cacheCopy);
                    });
                }
                return networkResponse;
            }).catch(() => {
                // Fallback to precached PWA login shell offline
                return caches.match('/login?pwa=true', { ignoreSearch: true });
            })
        );
        return;
    }

    // 3. Cache-First strategy for static assets
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(event.request, { ignoreVary: true, ignoreSearch: true }).then(cachedResponse => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                return fetch(event.request).then(networkResponse => {
                    if (networkResponse && networkResponse.status === 200) {
                        const cacheCopy = networkResponse.clone();
                        caches.open(STATIC_CACHE_NAME).then(cache => {
                            cache.put(event.request, cacheCopy);
                        });
                    }
                    return networkResponse;
                }).catch(() => {
                    return new Response('Asset Offline', { status: 404, statusText: 'Not Found' });
                });
            })
        );
        return;
    }

    // 4. Network-First falling back to Cache strategy for HTML pages (user data)
    event.respondWith(
        fetch(event.request).then(networkResponse => {
            // Cache page if it is a successful HTML response
            const acceptHeader = event.request.headers.get('accept') || '';
            if (networkResponse && networkResponse.status === 200 && acceptHeader.includes('text/html')) {
                const cacheCopy = networkResponse.clone();
                caches.open(DATA_CACHE_NAME).then(cache => {
                    cache.put(event.request, cacheCopy);
                });
            }
            return networkResponse;
        }).catch(() => {
            // Fallback to data cache on network failure (offline)
            return caches.match(event.request, { ignoreVary: true, ignoreSearch: true }).then(cachedResponse => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                // If requesting an HTML page, return the cached offline fallback
                const acceptHeader = event.request.headers.get('accept') || '';
                if (acceptHeader && acceptHeader.includes('text/html')) {
                    return caches.match('/static/offline.html');
                }
                // Return a basic offline response to avoid TypeError (resolving fetch with undefined)
                return new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
            });
        })
    );
});
