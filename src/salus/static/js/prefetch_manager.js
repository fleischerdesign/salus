/**
 * Salus PWA Cache-Warming Prefetch Manager
 * Asynchronously prefetches key dynamic user routes to warm the service worker cache.
 */
(function() {
    class PrefetchManager {
        constructor() {
            this.fetchedUrls = new Set();
            this.init();
        }

        init() {
            // Only prefetch if online and supported
            if (!navigator.onLine) return;

            window.addEventListener('load', () => {
                // Wait for the main thread to be idle
                if ('requestIdleCallback' in window) {
                    requestIdleCallback(() => this.startPrefetching());
                } else {
                    setTimeout(() => this.startPrefetching(), 2000);
                }
            });

            // Listen for reconnection to re-warm caches if needed
            window.addEventListener('online', () => {
                this.startPrefetching();
            });
        }

        async startPrefetching() {
            console.log('[PrefetchManager] Scanning for offline routes...');
            const urls = this.collectUrls();
            
            for (const url of urls) {
                if (this.fetchedUrls.has(url)) continue;
                
                try {
                    // Fetch with low priority and explicit Accept headers
                    const response = await fetch(url, {
                        headers: {
                            'Accept': 'text/html'
                        },
                        priority: 'low'
                    });
                    
                    if (response.ok) {
                        this.fetchedUrls.add(url);
                        console.log(`[PrefetchManager] Warmed cache for: ${url}`);
                    }
                } catch (e) {
                    console.warn(`[PrefetchManager] Failed to prefetch ${url}:`, e);
                }
                
                // Yield thread control
                await new Promise(r => setTimeout(r, 300));
            }
        }

        collectUrls() {
            const urls = new Set();
            
            // Add static pages
            urls.add('/workouts/plans');
            urls.add('/workouts/exercises');
            urls.add('/settings');
            urls.add('/entries');
            
            // Find all anchor links and card routes in the page
            document.querySelectorAll('a[href]').forEach(el => {
                const href = el.getAttribute('href');
                if (this.isValidRoute(href)) {
                    urls.add(href);
                }
            });

            // Find all hyperscript-based card click URLs
            document.querySelectorAll('[hyperscript]').forEach(el => {
                const hs = el.getAttribute('hyperscript') || '';
                const match = hs.match(/go to url\s+['"]([^'"]+)['"]/);
                if (match && match[1] && this.isValidRoute(match[1])) {
                    urls.add(match[1]);
                }
            });

            return Array.from(urls);
        }

        isValidRoute(href) {
            if (!href) return false;
            
            // Filter to local, non-action routes for plans and exercises
            return href.startsWith('/workouts/plans/') || 
                   href.startsWith('/workouts/exercises/') || 
                   href.startsWith('/entries/');
        }
    }

    // Initialize prefetch manager
    window.SalusPrefetchManager = new PrefetchManager();
})();
