/**
 * Salus Unified Sync Manager
 * Resilient, transaction-oriented queue manager for offline-first actions.
 */
(function() {
    class SyncManager {
        constructor() {
            this.queueKey = 'salus_sync_queue';
            this.isSyncing = false;
            this.isOnline = navigator.onLine;

            this.initListeners();
            // Try to sync on load if online
            setTimeout(() => this.processQueue(), 500);
        }

        initListeners() {
            window.addEventListener('online', () => {
                this.isOnline = true;
                this.processQueue();
            });

            window.addEventListener('offline', () => {
                this.isOnline = false;
                this.updateBadge();
            });
        }

        getQueue() {
            try {
                return JSON.parse(localStorage.getItem(this.queueKey)) || [];
            } catch (e) {
                console.error('[SyncManager] Error reading queue from localStorage:', e);
                return [];
            }
        }

        saveQueue(queue) {
            try {
                localStorage.setItem(this.queueKey, JSON.stringify(queue));
            } catch (e) {
                console.error('[SyncManager] Error saving queue to localStorage:', e);
            }
            this.updateBadge();
        }

        /**
         * Enqueue a new request action.
         * @param {Object} request - The request payload
         * @param {string} request.method - GET | POST | DELETE | PUT
         * @param {string} request.url - API endpoint URL
         * @param {Object} [request.body] - Optional request payload body
         * @param {Object} [request.headers] - Custom request headers
         * @param {Object} [request.meta] - Custom target element bindings and descriptors
         */
        enqueue(request) {
            const queue = this.getQueue();
            const queueItem = {
                id: 'sync-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9),
                method: request.method || 'POST',
                url: request.url,
                body: request.body || null,
                headers: request.headers || {},
                meta: request.meta || {},
                timestamp: Date.now()
            };

            queue.push(queueItem);
            this.saveQueue(queue);

            console.log('[SyncManager] Enqueued transaction:', queueItem);
            
            // Trigger background queue execution
            this.processQueue();
            return queueItem.id;
        }

        async processQueue() {
            if (this.isSyncing) return;
            if (!this.isOnline) {
                this.updateBadge();
                return;
            }

            const queue = this.getQueue();
            if (queue.length === 0) {
                this.updateBadge();
                return;
            }

            this.isSyncing = true;
            this.updateBadge();

            console.log(`[SyncManager] Starting sync of ${queue.length} items...`);

            while (queue.length > 0) {
                const item = queue[0];
                try {
                    const fetchOptions = {
                        method: item.method,
                        headers: {
                            'Content-Type': 'application/json',
                            ...item.headers
                        }
                    };
                    if (item.body && item.method !== 'GET' && item.method !== 'HEAD') {
                        fetchOptions.body = JSON.stringify(item.body);
                    }

                    const response = await fetch(item.url, fetchOptions);

                    if (response.ok) {
                        // Success: remove from queue and notify listeners
                        queue.shift();
                        this.saveQueue(queue);

                        console.log('[SyncManager] Sync success for item:', item.id);
                        window.dispatchEvent(new CustomEvent('salus:sync-completed', {
                            detail: { item: item, response: response }
                        }));
                    } else if (response.status >= 400 && response.status < 500) {
                        // Client error (400, 404, 409 etc.): discard item and dispatch error event to unblock queue
                        queue.shift();
                        this.saveQueue(queue);

                        console.warn(`[SyncManager] Client error ${response.status} for item: ${item.id}. Discarded.`);
                        window.dispatchEvent(new CustomEvent('salus:sync-failed', {
                            detail: { item: item, error: `Client error: ${response.status}` }
                        }));
                    } else {
                        // Server error (500, 503 etc.): pause queue and try again later
                        console.error(`[SyncManager] Server error ${response.status} for item: ${item.id}. Pausing sync.`);
                        this.isOnline = false; // Treat server error as offline temporarily
                        break;
                    }
                } catch (err) {
                    // Network / timeout error: pause queue
                    console.error('[SyncManager] Network error during sync:', err);
                    this.isOnline = false;
                    break;
                }
            }

            this.isSyncing = false;
            this.updateBadge();
        }

        updateBadge() {
            const badge = document.getElementById('global-sync-badge');
            if (!badge) return;

            const queue = this.getQueue();
            const count = queue.length;

            if (this.isSyncing) {
                // Syncing state: Show spinning icon
                badge.style.display = 'inline-flex';
                badge.className = 'global-sync-badge global-sync-badge--syncing';
                badge.innerHTML = `
                    <span class="material-symbols-outlined global-sync-badge__icon" style="animation: spin 1s linear infinite">sync</span>
                    <span class="global-sync-badge__text">Syncing...</span>
                `;
            } else if (!this.isOnline || count > 0) {
                // Offline or pending changes: Show amber indicator
                badge.style.display = 'inline-flex';
                badge.className = 'global-sync-badge global-sync-badge--offline';
                badge.innerHTML = `
                    <span class="material-symbols-outlined global-sync-badge__icon">cloud_off</span>
                    <span class="global-sync-badge__text">${count > 0 ? count + ' pending' : 'Offline'}</span>
                `;
            } else {
                // Online & idle / fully synced: Hide entirely (per user feedback!)
                badge.style.display = 'none';
            }
        }
    }

    // Initialize globally
    window.SalusSyncManager = new SyncManager();
})();
