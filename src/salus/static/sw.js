const STATIC_CACHE_NAME = 'salus-static-v8';
const DATA_CACHE_NAME = 'salus-data-v8';

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
            try {
                await cache.addAll(requests);
            } catch (err) {
                console.warn('[ServiceWorker] Pre-caching failed during install (likely offline):', err);
                throw err;
            }
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


// --------------------------------------------------------------------------
// Background Sync & IndexedDB Helper Functions
// --------------------------------------------------------------------------

function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('salus_db', 1);
        request.onupgradeneeded = (evt) => {
            const db = evt.target.result;
            if (!db.objectStoreNames.contains('sync_queue')) {
                db.createObjectStore('sync_queue', { keyPath: 'id' });
            }
        };
        request.onsuccess = (evt) => {
            resolve(evt.target.result);
        };
        request.onerror = (evt) => {
            reject(evt.target.error);
        };
    });
}

async function getQueuedActions(db) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['sync_queue'], 'readonly');
        const store = transaction.objectStore('sync_queue');
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result || []);
        request.onerror = () => reject(request.error);
    });
}

async function deleteQueuedAction(db, id) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['sync_queue'], 'readwrite');
        const store = transaction.objectStore('sync_queue');
        const request = store.delete(id);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

async function syncOfflineQueue() {
    console.log('[ServiceWorker] Background sync triggered for tag: salus-sync');
    try {
        const db = await openDatabase();
        const queue = await getQueuedActions(db);
        if (queue.length === 0) return;

        for (let item of queue) {
            try {
                let body = item.body;
                let headers = { ...item.headers };
                
                if (item.method !== 'GET' && typeof body === 'object') {
                    // Convert body object to URLSearchParams for application/x-www-form-urlencoded
                    const params = new URLSearchParams();
                    for (const [key, val] of Object.entries(body)) {
                        params.append(key, val);
                    }
                    if (item.client_updated_at) {
                        params.append('client_updated_at', item.client_updated_at);
                    }
                    body = params;
                    headers['Content-Type'] = 'application/x-www-form-urlencoded';
                }

                const response = await fetch(item.url, {
                    method: item.method,
                    headers: headers,
                    body: item.method !== 'GET' ? body : undefined
                });

                if (response.ok) {
                    await deleteQueuedAction(db, item.id);
                    console.log(`[ServiceWorker] Background sync succeeded for URL: ${item.url}`);
                    
                    // Notify active clients to update UI
                    const clientsList = await self.clients.matchAll();
                    for (let client of clientsList) {
                        client.postMessage({
                            type: 'salus:sync-item-completed',
                            itemId: item.id,
                            url: item.url,
                            status: response.status
                        });
                    }
                } else if (response.status === 409) {
                    await deleteQueuedAction(db, item.id);
                    console.warn(`[ServiceWorker] Background sync conflict (409) on URL: ${item.url}. Discarded.`);
                } else if (response.status >= 400 && response.status < 500) {
                    await deleteQueuedAction(db, item.id);
                    console.warn(`[ServiceWorker] Background sync rejected with status ${response.status} on URL: ${item.url}. Discarded.`);
                } else {
                    throw new Error(`Server returned status ${response.status}`);
                }
            } catch (err) {
                console.error(`[ServiceWorker] Failed to sync item ${item.id}:`, err);
                throw err; // Propagate error so browser SyncManager schedules retry
            }
        }
        
        // Notify all clients sync finished
        const clientsList = await self.clients.matchAll();
        for (let client of clientsList) {
            client.postMessage({ type: 'salus:sync-completed' });
        }
    } catch (err) {
        console.error('[ServiceWorker] Background sync failed:', err);
        throw err;
    }
}

// Register background sync handler
self.addEventListener('sync', event => {
    if (event.tag === 'salus-sync') {
        event.waitUntil(syncOfflineQueue());
    }
});
