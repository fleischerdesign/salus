/**
 * Salus PWA Agnostic Cache-Warming Prefetch Manager
 * Dynamically crawls all local GET routes in the DOM and pre-warms the service worker cache.
 */
(function() {
    class PrefetchManager {
        constructor() {
            this.fetchedUrls = new Set();
            this.init();
        }

        init() {
            if (!navigator.onLine) return;

            window.addEventListener('load', () => {
                // Fetch everything in the background once main page is loaded
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
            console.log('[PrefetchManager] Agnostically scanning for offline routes...');
            const urls = this.collectUrls();
            
            for (const url of urls) {
                if (this.fetchedUrls.has(url)) continue;
                
                try {
                    const response = await fetch(url, {
                        headers: {
                            'Accept': 'text/html'
                        },
                        priority: 'low'
                    });
                    
                    if (response.ok) {
                        this.fetchedUrls.add(url);
                        console.log(`[PrefetchManager] Prefetched and cached: ${url}`);
                    }
                } catch (e) {
                    console.warn(`[PrefetchManager] Failed to prefetch ${url}:`, e);
                }
                
                // Yield thread control to prevent page jank
                await new Promise(r => setTimeout(r, 200));
            }
        }

        collectUrls() {
            const urls = new Set();
            
            // 1. Scan standard anchor tags (ignoring HTMX write mutations)
            document.querySelectorAll('a[href]').forEach(el => {
                if (el.hasAttribute('hx-post') || el.hasAttribute('hx-delete') || el.hasAttribute('hx-put') || el.hasAttribute('hx-patch')) {
                    return;
                }
                try {
                    const resolved = new URL(el.href, window.location.origin);
                    if (resolved.origin === window.location.origin) {
                        const path = resolved.pathname + resolved.search;
                        if (this.isValidRoute(resolved.pathname)) {
                            urls.add(path);
                        }
                    }
                } catch (e) {}
            });

            // 2. Scan HTMX GET requests (for tab changes, modals, overlays)
            document.querySelectorAll('[hx-get]').forEach(el => {
                const path = el.getAttribute('hx-get') || '';
                try {
                    const resolved = new URL(path, window.location.origin);
                    if (resolved.origin === window.location.origin) {
                        const cleanPath = resolved.pathname + resolved.search;
                        if (this.isValidRoute(resolved.pathname)) {
                            urls.add(cleanPath);
                        }
                    }
                } catch (e) {}
            });

            // 3. Scan Hyperscript navigation patterns (e.g. go to url '/...')
            document.querySelectorAll('[hyperscript]').forEach(el => {
                const hs = el.getAttribute('hyperscript') || '';
                const match = hs.match(/go to url\s+['"]([^'"]+)['"]/);
                if (match && match[1]) {
                    try {
                        const resolved = new URL(match[1], window.location.origin);
                        if (resolved.origin === window.location.origin) {
                            const cleanPath = resolved.pathname + resolved.search;
                            if (this.isValidRoute(resolved.pathname)) {
                                urls.add(cleanPath);
                            }
                        }
                    } catch (e) {}
                }
            });

            return Array.from(urls);
        }

        isValidRoute(path) {
            if (!path) return false;
            
            // Blacklisted URL prefixes that should never be prefetched
            const excludedPrefixes = ['/static/', '/api/', '/auth/', '/docs', '/redoc', '/openapi.json'];
            if (excludedPrefixes.some(prefix => path.startsWith(prefix))) {
                return false;
            }

            // Blacklist static files and extensions
            if (path.match(/\.(png|jpg|jpeg|gif|svg|webp|ico|css|js|json|xml|zip|pdf|csv|xlsx)$/i)) {
                return false;
            }

            return true;
        }
    }

    window.SalusPrefetchManager = new PrefetchManager();
})();
