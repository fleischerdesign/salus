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

            // Re-hydrate optimistic UI placeholders on page load (Durable Offline State)
            window.addEventListener('DOMContentLoaded', () => this.rehydrateOptimisticUI());
            if (document.readyState === 'interactive' || document.readyState === 'complete') {
                this.rehydrateOptimisticUI();
            }
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

        rehydrateOptimisticUI() {
            const queue = this.getQueue();
            queue.forEach(item => {
                if (typeof renderOptimisticUI === 'function') {
                    renderOptimisticUI(item, item.id);
                }
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
                        
                        let htmlContent = '';
                        const contentType = response.headers.get('content-type') || '';
                        if (contentType.includes('text/html')) {
                            htmlContent = await response.text();
                        }

                        window.dispatchEvent(new CustomEvent('salus:sync-completed', {
                            detail: { item: item, response: response, html: htmlContent }
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

    // ── HTMX Offline Mutation Interceptor ─────────────────────────────────────
    document.addEventListener('htmx:confirm', function(evt) {
        // If offline and it's a mutation (POST, PUT, DELETE), queue it!
        if (!navigator.onLine && evt.detail.verb !== 'GET') {
            evt.preventDefault(); // Halt HTMX request execution

            // Extract request body parameters
            let body = {};
            if (evt.detail.elt instanceof HTMLFormElement) {
                body = Object.fromEntries(new FormData(evt.detail.elt));
            } else {
                const form = evt.detail.elt.closest('form');
                if (form) {
                    body = Object.fromEntries(new FormData(form));
                }
            }

            const request = {
                method: evt.detail.verb.toUpperCase(),
                url: evt.detail.path,
                body: body,
                headers: evt.detail.headers || {},
                meta: {
                    target: evt.detail.target ? evt.detail.target.id : null,
                    trigger: evt.detail.elt ? evt.detail.elt.id : null,
                    swap: evt.detail.swap || 'innerHTML'
                }
            };

            const itemId = window.SalusSyncManager.enqueue(request);

            // Optimistic UI updates
            renderOptimisticUI(request, itemId);

            if (typeof showToast === 'function') {
                showToast('Action queued. Will sync when online.', 'info');
            }
        }
    });

    // Helper to render immediate local placeholder states
    function renderOptimisticUI(request, itemId) {
        // Optimistic rendering for new plan cards
        if (request.method === 'POST' && request.url.includes('/workouts/plans')) {
            const grid = document.getElementById('plans-grid');
            if (grid) {
                const tempCard = document.createElement('div');
                tempCard.id = itemId;
                tempCard.className = 'card';
                tempCard.setAttribute('data-variant', 'flat');
                tempCard.style.opacity = '0.75';
                tempCard.style.border = '1.5px dashed var(--color-primary)';
                tempCard.style.display = 'flex';
                tempCard.style.flexDirection = 'column';
                tempCard.style.justifyContent = 'space-between';
                tempCard.style.gap = '12px';
                tempCard.innerHTML = `
                    <div>
                        <div class="card__header" style="display:flex;justify-content:space-between;align-items:center;">
                            <h3 class="card__title" style="margin:0;font:var(--font-headline-sm);">${request.body.name || 'New Plan'}</h3>
                            <span class="material-symbols-outlined" style="animation: spin 1.5s linear infinite;color:var(--color-primary);">sync</span>
                        </div>
                        <p style="font:var(--font-body-sm);color:var(--color-slate-500);margin:8px 0 0 0;">
                            ${request.body.description || 'Queued for sync...'}
                        </p>
                    </div>
                    <div style="margin-top:12px;font:var(--font-caption);color:var(--color-warning-600);font-weight:600;display:flex;align-items:center;gap:4px;">
                        <span class="material-symbols-outlined" style="font-size:14px;">cloud_off</span>
                        Syncing once online...
                    </div>
                `;
                
                // Hide empty state if visible
                const empty = grid.querySelector('.empty-state');
                if (empty) empty.style.display = 'none';

                grid.appendChild(tempCard);
            }
        }
    }

    // ── Reconnection DOM Reconciliation & Hydration ─────────────────────────
    window.addEventListener('salus:sync-completed', function(evt) {
        const item = evt.detail.item;
        const html = evt.detail.html;

        // Delete optimistic UI placeholder
        const tempCard = document.getElementById(item.id);
        if (tempCard) {
            tempCard.remove();
        }

        // Hydrate live DOM if the sync server-returned HTML content is present
        if (item.meta.target && html) {
            const targetEl = document.getElementById(item.meta.target);
            if (targetEl) {
                if (item.meta.swap === 'beforeend') {
                    targetEl.insertAdjacentHTML('beforeend', html);
                } else if (item.meta.swap === 'outerHTML') {
                    const wrapper = document.createElement('div');
                    wrapper.innerHTML = html.trim();
                    targetEl.replaceWith(wrapper.firstChild);
                } else {
                    targetEl.innerHTML = html;
                }

                // Process DOM fragment so HTMX attributes and triggers are compiled
                if (window.htmx) {
                    window.htmx.process(targetEl);
                }
            }
        }
    });

    window.addEventListener('salus:sync-failed', function(evt) {
        const item = evt.detail.item;
        const error = evt.detail.error;

        // Discard optimistic card placeholder
        const tempCard = document.getElementById(item.id);
        if (tempCard) {
            tempCard.remove();
        }

        if (typeof showToast === 'function') {
            showToast(`Sync failed: ${error}`, 'error');
        }
    });
})();
