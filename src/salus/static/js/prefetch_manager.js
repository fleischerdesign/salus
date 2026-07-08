/**
 * Salus PWA Server-Driven Route Prefetch Manager (ETag-Match + 30s Cooldown + Delta Caching)
 * Fetches the dynamic list of navigable routes from the server and warms the cache incrementally.
 */
(function() {
    class PrefetchManager {
        constructor() {
            this.fetchedUrls = new Set();
            this.cooldownMs = 30000; // 30-second navigation cooldown
            this.init();
        }

        init() {
            if (!navigator.onLine) return;

            window.addEventListener('load', () => {
                // Wait for browser idle to warm the cache without blocking UI threads
                if ('requestIdleCallback' in window) {
                    requestIdleCallback(() => this.startPrefetching());
                } else {
                    setTimeout(() => this.startPrefetching(), 2000);
                }
            });

            window.addEventListener('online', () => {
                this.startPrefetching();
            });
        }

        async startPrefetching() {
            // 1. Navigation Cooldown Check
            const lastCheck = sessionStorage.getItem('salus_last_manifest_check');
            const now = Date.now();
            if (lastCheck && (now - parseInt(lastCheck, 10) < this.cooldownMs)) {
                console.log('[PrefetchManager] Manifest checked recently. Skipping prefetch.');
                return;
            }

            console.log('[PrefetchManager] Querying route manifest from server...');
            
            try {
                const storedEtag = localStorage.getItem('salus_routes_etag');
                const headers = { 'Accept': 'application/json' };
                if (storedEtag) {
                    headers['If-None-Match'] = storedEtag;
                }
                
                const manifestResponse = await fetch('/api/v1/pwa/manifest-routes', { headers });
                
                // Update check timestamp
                sessionStorage.setItem('salus_last_manifest_check', now.toString());

                if (manifestResponse.status === 304) {
                    console.log('[PrefetchManager] Route manifest unchanged (304). Skipping cache warming.');
                    return;
                }
                
                if (!manifestResponse.ok) {
                    if (manifestResponse.status === 401) {
                        console.log('[PrefetchManager] User is not logged in. Skipping prefetch.');
                    } else {
                        console.warn(`[PrefetchManager] Server returned status ${manifestResponse.status} for manifest routes.`);
                    }
                    return;
                }
                
                // Get ETag header (handling both native 304 and browser-converted 200)
                const responseEtag = manifestResponse.headers.get('ETag');
                if (responseEtag) {
                    if (storedEtag && responseEtag === storedEtag) {
                        console.log('[PrefetchManager] Route manifest unchanged (ETag match). Skipping cache warming.');
                        return;
                    }
                    localStorage.setItem('salus_routes_etag', responseEtag);
                }
                
                const urls = await manifestResponse.json();
                console.log(`[PrefetchManager] Server-driven route manifest loaded: ${urls.length} routes found.`);
                
                // Get list of currently cached URLs for Delta Caching
                const cacheKeys = await caches.keys();
                const dataCacheName = cacheKeys.find(k => k.startsWith('salus-data-')) || 'salus-data-v5';
                const cache = await caches.open(dataCacheName);
                const cachedRequests = await cache.keys();
                const cachedPaths = new Set(cachedRequests.map(req => new URL(req.url).pathname));
                
                for (const url of urls) {
                    const resolvedPath = new URL(url, window.location.origin).pathname;
                    
                    // Skip caching if already present in data cache (Incremental Caching)
                    if (cachedPaths.has(resolvedPath)) {
                        continue;
                    }
                    if (this.fetchedUrls.has(url)) continue;
                    
                    try {
                        const response = await fetch(url, {
                            headers: { 'Accept': 'text/html' },
                            priority: 'low'
                        });
                        
                        if (response.ok) {
                            this.fetchedUrls.add(url);
                            console.log(`[PrefetchManager] Delta prefetch cached: ${url}`);
                        }
                    } catch (err) {
                        console.warn(`[PrefetchManager] Failed to prefetch route ${url}:`, err);
                    }
                    
                    // Throttle requests slightly
                    await new Promise(r => setTimeout(r, 150));
                }
                
            } catch (err) {
                console.warn('[PrefetchManager] Failed to fetch PWA route manifest:', err);
            }
        }
    }

    // Initialize globally
    window.SalusPrefetchManager = new PrefetchManager();
})();
