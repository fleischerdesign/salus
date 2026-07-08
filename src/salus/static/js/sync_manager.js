/**
 * Salus Unified Sync Manager
 * Resilient, transaction-oriented queue manager for offline-first actions.
 */
(function() {
    class SalusDatabase {
        constructor() {
            this.dbName = 'salus_db';
            this.dbVersion = 1;
            this.db = null;
        }

        open() {
            return new Promise((resolve, reject) => {
                if (this.db) {
                    resolve(this.db);
                    return;
                }
                const request = indexedDB.open(this.dbName, this.dbVersion);

                request.onupgradeneeded = (evt) => {
                    const db = evt.target.result;
                    if (!db.objectStoreNames.contains('sync_queue')) {
                        db.createObjectStore('sync_queue', { keyPath: 'id' });
                    }
                };

                request.onsuccess = (evt) => {
                    this.db = evt.target.result;
                    resolve(this.db);
                };

                request.onerror = (evt) => {
                    reject(evt.target.error);
                };
            });
        }

        async getQueue() {
            const db = await this.open();
            return new Promise((resolve, reject) => {
                const transaction = db.transaction(['sync_queue'], 'readonly');
                const store = transaction.objectStore('sync_queue');
                const request = store.getAll();

                request.onsuccess = () => {
                    resolve(request.result || []);
                };

                request.onerror = () => {
                    reject(request.error);
                };
            });
        }

        async enqueue(action) {
            const db = await this.open();
            return new Promise((resolve, reject) => {
                const transaction = db.transaction(['sync_queue'], 'readwrite');
                const store = transaction.objectStore('sync_queue');
                const request = store.add(action);

                request.onsuccess = () => {
                    resolve();
                };

                request.onerror = () => {
                    reject(request.error);
                };
            });
        }

        async dequeue(id) {
            const db = await this.open();
            return new Promise((resolve, reject) => {
                const transaction = db.transaction(['sync_queue'], 'readwrite');
                const store = transaction.objectStore('sync_queue');
                const request = store.delete(id);

                request.onsuccess = () => {
                    resolve();
                };

                request.onerror = () => {
                    reject(request.error);
                };
            });
        }

        async clearQueue() {
            const db = await this.open();
            return new Promise((resolve, reject) => {
                const transaction = db.transaction(['sync_queue'], 'readwrite');
                const store = transaction.objectStore('sync_queue');
                const request = store.clear();

                request.onsuccess = () => {
                    resolve();
                };

                request.onerror = () => {
                    reject(request.error);
                };
            });
        }
    }

    class SyncManager {
        constructor() {
            this.db = new SalusDatabase();
            this.isSyncing = false;
            this.isOnline = navigator.onLine;

            this.initListeners();
            
            // Try to sync on load if online
            setTimeout(() => this.processQueue(), 500);

            // Update badge and re-hydrate optimistic UI placeholders on page load (Durable Offline State)
            window.addEventListener('DOMContentLoaded', () => {
                this.updateBadge();
                this.checkServerHealth();
                this.rehydrateOptimisticUI();
            });
            if (document.readyState === 'interactive' || document.readyState === 'complete') {
                this.updateBadge();
                this.checkServerHealth();
                this.rehydrateOptimisticUI();
            }

            // React to HTMX swaps resetting the badge element in the DOM
            document.addEventListener('htmx:afterSwap', () => {
                this.updateBadge();
            });

            // Listen to messages from the Service Worker
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.addEventListener('message', (event) => {
                    if (event.data) {
                        if (event.data.type === 'salus:sync-item-completed') {
                            this.handleSyncItemCompleted(event.data.itemId, event.data.url, event.data.status);
                        } else if (event.data.type === 'salus:sync-completed') {
                            this.handleSyncCompleted();
                        }
                    }
                });
            }
        }

        initListeners() {
            window.addEventListener('online', () => {
                this.checkServerHealth().then(() => {
                    if (this.isOnline) {
                        this.processQueue();
                    }
                });
            });

            window.addEventListener('offline', () => {
                this.isOnline = false;
                this.updateBadge();
            });

            // React to HTMX swaps resetting the badge element in the DOM
            document.addEventListener('htmx:afterSwap', () => {
                this.updateBadge();
            });
        }

        async checkServerHealth() {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 2000); // 2s timeout
                
                const response = await fetch('/api/v1/pwa/health', {
                    method: 'GET',
                    signal: controller.signal,
                    headers: { 'Cache-Control': 'no-cache' }
                });
                clearTimeout(timeoutId);
                
                if (response.ok) {
                    this.isOnline = true;
                } else {
                    this.isOnline = false;
                }
            } catch (err) {
                this.isOnline = false;
            }
            this.updateBadge();
        }

        async rehydrateOptimisticUI() {
            const queue = await this.db.getQueue();
            queue.forEach(item => {
                if (typeof renderOptimisticUI === 'function') {
                    renderOptimisticUI(item, item.id);
                }
            });

            // Special Case: Rehydrate the entire Active Workout Session offline from the plan details!
            if (!navigator.onLine && window.location.pathname === '/workouts/sessions/active') {
                const planId = localStorage.getItem('salus_offline_active_plan');
                if (planId) {
                    await this.rehydrateOfflineActiveSession(planId);
                }
            }
        }

        async rehydrateOfflineActiveSession(planId) {
            console.log(`[SyncManager] Rehydrating active session layout for plan ${planId} offline...`);
            
            try {
                const queue = await this.db.getQueue();
                const cacheKeys = await caches.keys();
                const dataCacheName = cacheKeys.find(k => k.startsWith('salus-data-')) || 'salus-data-v7';
                
                const cache = await caches.open(dataCacheName);
                const planResponse = await cache.match(`/workouts/plans/${planId}`);
                if (!planResponse) {
                    console.warn(`[SyncManager] Cached plan detail page not found for plan ${planId}`);
                    return;
                }
                
                const htmlText = await planResponse.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(htmlText, 'text/html');
                const planTitle = doc.querySelector('h1')?.innerText.trim() || 'Offline Workout';
                
                const exercises = [];
                const cards = doc.querySelectorAll('.card');
                
                cards.forEach(card => {
                    const header = card.querySelector('div[style*="font-weight:700"]');
                    if (header) {
                        const name = header.innerText.trim();
                        const targetTextEl = card.querySelector('div[style*="text-align:right"]');
                        let sets = 3;
                        let reps = 10;
                        let rpe = 8;
                        
                        if (targetTextEl) {
                            const text = targetTextEl.innerText;
                            const setsMatch = text.match(/(\d+)\s*sets?/i);
                            const repsMatch = text.match(/(\d+)\s*reps?/i);
                            const rpeMatch = text.match(/RPE\s*(\d+(\.\d+)?)/i);
                            if (setsMatch) sets = parseInt(setsMatch[1], 10);
                            if (repsMatch) reps = parseInt(repsMatch[1], 10);
                            if (rpeMatch) rpe = parseFloat(rpeMatch[1]);
                        }
                        
                        const hsAttr = card.getAttribute('hyperscript') || card.getAttribute('_') || '';
                        const idMatch = hsAttr.match(/\/exercises\/(\d+)/) || card.outerHTML.match(/\/exercises\/(\d+)/);
                        const exerciseId = idMatch ? parseInt(idMatch[1], 10) : Math.floor(Math.random() * 1000);
                        
                        exercises.push({
                            id: exerciseId,
                            name: name,
                            suggested_sets: sets,
                            suggested_reps: reps,
                            suggested_rpe: rpe
                        });
                    }
                });

                if (exercises.length === 0) {
                    console.warn('[SyncManager] No target exercises scraped from plan detail page.');
                    return;
                }
                
                const mainForm = document.querySelector('form[action="/workouts/sessions/complete"]') || document.body;
                if (!mainForm) return;

                let exercisesContainer = document.querySelector('form-stack') || document.querySelector('.form-stack');
                if (!exercisesContainer) {
                    exercisesContainer = document.createElement('div');
                    exercisesContainer.className = 'form-stack';
                    exercisesContainer.style.display = 'flex';
                    exercisesContainer.style.flexDirection = 'column';
                    exercisesContainer.style.gap = '24px';
                    mainForm.insertBefore(exercisesContainer, mainForm.firstChild);
                } else {
                    exercisesContainer.innerHTML = '';
                }

                const h1 = document.querySelector('h1');
                if (h1) {
                    h1.innerText = `${planTitle} (Offline Active)`;
                }

                exercises.forEach(target => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.setAttribute('data-variant', 'flat');
                    card.style.border = '1px solid var(--color-slate-200)';
                    card.style.padding = '16px';
                    card.style.borderRadius = '8px';
                    card.style.backgroundColor = 'var(--color-surface-container-lowest)';
                    card.style.marginBottom = '24px';
                    
                    let rowsHtml = '';
                    for (let setNum = 1; setNum <= target.suggested_sets; setNum++) {
                        const isLogged = queue.some(item => 
                            item.method === 'POST' && 
                            item.url.includes('/sessions/log') && 
                            item.body?.exercise_id == target.id && 
                            item.body?.set_number == setNum
                        );
                        
                        const loggedWeight = queue.find(item => 
                            item.method === 'POST' && 
                            item.url.includes('/sessions/log') && 
                            item.body?.exercise_id == target.id && 
                            item.body?.set_number == setNum
                        )?.body?.weight || 40.0;
                        
                        const loggedReps = queue.find(item => 
                            item.method === 'POST' && 
                            item.url.includes('/sessions/log') && 
                            item.body?.exercise_id == target.id && 
                            item.body?.set_number == setNum
                        )?.body?.reps || target.suggested_reps;

                        rowsHtml += `
                            <div id="row-${target.id}-${setNum}" 
                                 data-pr-weight="0.0"
                                 data-pr-est-1rm="0.0"
                                 style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;background:var(--color-slate-50);padding:8px 12px;border-radius:6px;margin-bottom:8px;${isLogged ? 'opacity:0.75;' : ''}transition:opacity var(--duration-fast)">
                                <span style="font-weight:700;font:var(--font-body-sm);color:var(--color-slate-500);min-width:40px">Set ${setNum}</span>

                                <div class="input" style="flex-direction:row;align-items:center;gap:6px;margin:0">
                                    <label class="input__label" style="font:var(--font-caption);font-weight:600">Weight:</label>
                                    <div style="display:flex;align-items:center;background:var(--color-surface-container-lowest);border:1px solid var(--color-slate-200);border-radius:var(--radius-sm);overflow:hidden">
                                        <button type="button" style="background:none;border:none;padding:6px 10px;cursor:pointer;font-weight:bold;color:var(--color-slate-600)" onclick="adjustValue('weight-${target.id}-${setNum}', -2.5, 0, false, ${target.id}, ${setNum})" ${isLogged ? 'disabled' : ''}>-</button>
                                        <input type="number" id="weight-${target.id}-${setNum}" step="0.5" value="${loggedWeight}" placeholder="kg" class="input__field" style="width:65px;border:none;text-align:center;padding:6px 0;height:auto;font-size:13px" oninput="update1RM(${target.id}, ${setNum})" ${isLogged ? 'disabled' : ''}>
                                        <button type="button" style="background:none;border:none;padding:6px 10px;cursor:pointer;font-weight:bold;color:var(--color-slate-600)" onclick="adjustValue('weight-${target.id}-${setNum}', 2.5, 0, false, ${target.id}, ${setNum})" ${isLogged ? 'disabled' : ''}>+</button>
                                    </div>
                                </div>

                                <div class="input" style="flex-direction:row;align-items:center;gap:6px;margin:0">
                                    <label class="input__label" style="font:var(--font-caption);font-weight:600">Reps:</label>
                                    <div style="display:flex;align-items:center;background:var(--color-surface-container-lowest);border:1px solid var(--color-slate-200);border-radius:var(--radius-sm);overflow:hidden">
                                        <button type="button" style="background:none;border:none;padding:6px 10px;cursor:pointer;font-weight:bold;color:var(--color-slate-600)" onclick="adjustValue('reps-${target.id}-${setNum}', -1, 0, true, ${target.id}, ${setNum})" ${isLogged ? 'disabled' : ''}>-</button>
                                        <input type="number" id="reps-${target.id}-${setNum}" value="${loggedReps}" class="input__field" style="width:50px;border:none;text-align:center;padding:6px 0;height:auto;font-size:13px" oninput="update1RM(${target.id}, ${setNum})" ${isLogged ? 'disabled' : ''}>
                                        <button type="button" style="background:none;border:none;padding:6px 10px;cursor:pointer;font-weight:bold;color:var(--color-slate-600)" onclick="adjustValue('reps-${target.id}-${setNum}', 1, 0, true, ${target.id}, ${setNum})" ${isLogged ? 'disabled' : ''}>+</button>
                                    </div>
                                </div>

                                <div class="input" style="flex-direction:row;align-items:center;gap:6px;margin:0">
                                    <label class="input__label" style="font:var(--font-caption);font-weight:600">RPE:</label>
                                    <select id="rpe-${target.id}-${setNum}" class="input__field" style="padding:6px 8px;font-size:13px;border:1px solid var(--color-slate-200);border-radius:var(--radius-sm);height:auto" ${isLogged ? 'disabled' : ''}>
                                        <option value="10" ${target.suggested_rpe === 10 ? 'selected' : ''}>10</option>
                                        <option value="9.5" ${target.suggested_rpe === 9.5 ? 'selected' : ''}>9.5</option>
                                        <option value="9" ${target.suggested_rpe === 9 ? 'selected' : ''}>9</option>
                                        <option value="8.5" ${target.suggested_rpe === 8.5 ? 'selected' : ''}>8.5</option>
                                        <option value="8" ${target.suggested_rpe === 8 ? 'selected' : ''}>8</option>
                                        <option value="7.5" ${target.suggested_rpe === 7.5 ? 'selected' : ''}>7.5</option>
                                        <option value="7" ${target.suggested_rpe === 7 ? 'selected' : ''}>7</option>
                                        <option value="6.5" ${target.suggested_rpe === 6.5 ? 'selected' : ''}>6.5</option>
                                        <option value="6" ${target.suggested_rpe === 6 ? 'selected' : ''}>6</option>
                                    </select>
                                </div>

                                <span id="est1rm-${target.id}-${setNum}" style="font:var(--font-caption);color:var(--color-slate-400);min-width:70px">e1RM: 0kg</span>

                                <button id="btn-${target.id}-${setNum}" type="button" class="btn" data-variant="secondary" style="padding:6px 12px;font-size:13px;height:auto;margin-left:auto" 
                                        onclick="logOfflineSet(${target.id}, ${setNum})" ${isLogged ? 'disabled' : ''}>
                                    ${isLogged ? 'Logged' : 'Log Set'}
                                </button>
                            </div>
                        `;
                    }

                    card.innerHTML = `
                        <div style="display:flex;justify-content:between;align-items:center;margin-bottom:12px">
                            <span style="font-weight:700;font:var(--font-body-md);color:var(--color-slate-800)">${target.name}</span>
                            <span style="font:var(--font-caption);color:var(--color-slate-400);margin-left:auto">Target: ${target.suggested_sets}x${target.suggested_reps} @ RPE ${target.suggested_rpe}</span>
                        </div>
                        <div style="display:flex;flex-direction:column">
                            ${rowsHtml}
                        </div>
                    `;
                    exercisesContainer.appendChild(card);
                });

                document.querySelectorAll("[id^='est1rm-']").forEach(span => {
                    const idParts = span.id.split("-");
                    if (idParts.length === 3) {
                        update1RM(idParts[1], idParts[2]);
                    }
                });

                const sessIdInput = document.querySelector('input[name="session_id"]');
                if (sessIdInput) {
                    sessIdInput.value = "0";
                }

                console.log('[SyncManager] Dynamic offline session rehydration complete.');
            } catch (err) {
                console.error('[SyncManager] Error in offline session rehydration:', err);
            }
        }

        enqueue(request) {
            const tempId = 'sync-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
            const queueItem = {
                id: tempId,
                method: request.method || 'POST',
                url: request.url,
                body: request.body || null,
                headers: request.headers || {},
                meta: request.meta || {},
                client_updated_at: Date.now()
            };

            // Write asynchronously to IndexedDB
            this.db.enqueue(queueItem).then(() => {
                this.updateBadge();
                this.registerBackgroundSync();
            });

            console.log('[SyncManager] Enqueued transaction into IndexedDB:', queueItem);
            return tempId;
        }

        async registerBackgroundSync() {
            if ('serviceWorker' in navigator && 'SyncManager' in window) {
                try {
                    const reg = await navigator.serviceWorker.ready;
                    await reg.sync.register('salus-sync');
                    console.log('[SyncManager] Registered background sync tag: salus-sync');
                } catch (err) {
                    console.warn('[SyncManager] Background sync registration failed, falling back to processQueue:', err);
                    this.processQueue();
                }
            } else {
                this.processQueue();
            }
        }

        async processQueue() {
            if (this.isSyncing) return;
            if (!this.isOnline) {
                this.updateBadge();
                return;
            }

            const queue = await this.db.getQueue();
            if (queue.length === 0) {
                this.updateBadge();
                return;
            }

            this.isSyncing = true;
            this.updateBadge();

            console.log(`[SyncManager] Starting sync of ${queue.length} items...`);

            for (let item of queue) {
                try {
                    let body = item.body;
                    let headers = { ...item.headers };
                    
                    if (item.method !== 'GET' && typeof body === 'object') {
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

                    const fetchOptions = {
                        method: item.method,
                        headers: headers,
                        body: item.method !== 'GET' ? body : undefined
                    };

                    const response = await fetch(item.url, fetchOptions);

                    if (response.ok) {
                        await this.db.dequeue(item.id);
                        console.log('[SyncManager] Sync success for item:', item.id);
                        
                        let htmlContent = '';
                        const contentType = response.headers.get('content-type') || '';
                        if (contentType.includes('text/html')) {
                            htmlContent = await response.text();
                        }

                        window.dispatchEvent(new CustomEvent('salus:sync-completed', {
                            detail: { item: item, response: response, html: htmlContent }
                        }));
                    } else if (response.status === 409) {
                        await this.db.dequeue(item.id);
                        console.warn(`[SyncManager] Sync conflict (409) for item: ${item.id}. Discarded.`);
                    } else if (response.status >= 400 && response.status < 500) {
                        await this.db.dequeue(item.id);
                        console.warn(`[SyncManager] Client error ${response.status} for item: ${item.id}. Discarded.`);
                        window.dispatchEvent(new CustomEvent('salus:sync-failed', {
                            detail: { item: item, error: `Client error: ${response.status}` }
                        }));
                    } else {
                        console.error(`[SyncManager] Server error ${response.status} for item: ${item.id}. Pausing sync.`);
                        this.isOnline = false;
                        break;
                    }
                } catch (err) {
                    console.error('[SyncManager] Network error during sync:', err);
                    this.isOnline = false;
                    break;
                }
            }

            this.isSyncing = false;
            
            const finalQueue = await this.db.getQueue();
            if (finalQueue.length === 0) {
                localStorage.removeItem('salus_offline_active_plan');
            }

            this.updateBadge();
        }

        handleSyncItemCompleted(itemId, url, status) {
            console.log('[SyncManager] Sync item completed from Service Worker:', itemId);
            const optimisticEl = document.querySelector(`[data-optimistic-id="${itemId}"]`);
            if (optimisticEl) {
                if (url.includes('/delete') || (url.includes('/sessions/log') && status === 200)) {
                    const row = document.getElementById(itemId);
                    if (row) {
                        row.style.opacity = '1';
                        const checkbox = row.querySelector('.workout-set-checkbox');
                        if (checkbox) {
                            checkbox.setAttribute('data-logged', 'true');
                            const icon = checkbox.querySelector('.material-symbols-outlined');
                            if (icon) icon.innerText = 'done';
                        }
                    }
                } else {
                    optimisticEl.remove();
                }
            }
        }

        handleSyncCompleted() {
            console.log('[SyncManager] All sync items completed from Service Worker.');
            localStorage.removeItem('salus_offline_active_plan');
            this.updateBadge();
            if (typeof showToast === 'function') {
                showToast('Synchronisierung abgeschlossen!', 'success');
            }
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }

        async updateBadge() {
            let badge = document.getElementById('global-sync-badge');
            if (!badge) {
                const actionsContainer = document.querySelector('.top-app-bar__actions');
                if (actionsContainer) {
                    badge = document.createElement('div');
                    badge.id = 'global-sync-badge';
                    badge.className = 'global-sync-badge';
                    badge.style.display = 'none';
                    const refEl = actionsContainer.querySelector('.notifications-bell') || actionsContainer.firstChild;
                    actionsContainer.insertBefore(badge, refEl);
                } else {
                    return;
                }
            }

            const queue = await this.db.getQueue();
            const count = queue.length;
            
            console.log('[SyncManager] updateBadge called. isOnline:', this.isOnline, 'queue count:', count, 'badge:', badge);

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

            // Special Case: Starting a workout session offline
            if (evt.detail.path.includes('/workouts/sessions/start')) {
                const urlParams = new URLSearchParams(evt.detail.path.split('?')[1] || '');
                const planId = urlParams.get('plan_id') || body.plan_id;
                if (planId) {
                    localStorage.setItem('salus_offline_active_plan', planId);
                    setTimeout(() => {
                        window.location.href = '/workouts/sessions/active';
                    }, 150);
                    return;
                }
            }

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

        // Invalidate PWA route manifest ETag cache and check cooldown on data changes
        localStorage.removeItem('salus_routes_etag');
        sessionStorage.removeItem('salus_last_manifest_check');

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

    // ── Offline Submit Interceptor (HTMX + Standard Forms) ───────────────────
    document.addEventListener('submit', function(evt) {
        if (!navigator.onLine) {
            const form = evt.target;
            const action = form.getAttribute('action') || form.action || '';
            const method = (form.getAttribute('method') || 'POST').toUpperCase();
            
            if (method !== 'GET') {
                evt.preventDefault(); // Stop standard form submission
                
                // Clear cached route manifest ETag and check cooldown client-side
                if (action.includes('/auth/logout')) {
                    localStorage.removeItem('salus_routes_etag');
                    sessionStorage.removeItem('salus_last_manifest_check');
                    window.SalusSyncManager.enqueue({
                        method: 'POST',
                        url: '/auth/logout',
                        body: {},
                        headers: {},
                        meta: { action: 'logout' }
                    });
                    window.location.href = '/auth/logout';
                    return;
                }

                // Handle starting a workout offline
                if (action.includes('/workouts/sessions/start')) {
                    const urlParams = new URLSearchParams(action.split('?')[1] || '');
                    const planId = urlParams.get('plan_id') || form.querySelector('[name="plan_id"]')?.value;
                    if (planId) {
                        localStorage.setItem('salus_offline_active_plan', planId);
                        
                        window.SalusSyncManager.enqueue({
                            method: 'POST',
                            url: `/api/v1/workouts/sessions/start?plan_id=${planId}`,
                            body: {},
                            headers: {},
                            meta: { action: 'start-session', planId: planId }
                        });
                        
                        setTimeout(() => {
                            window.location.href = '/workouts/sessions/active';
                        }, 150);
                        return;
                    }
                }

                // General Form enqueuing
                const body = Object.fromEntries(new FormData(form));
                window.SalusSyncManager.enqueue({
                    method: method,
                    url: action,
                    body: body,
                    headers: {},
                    meta: { target: form.id || null, swap: 'outerHTML' }
                });
                
                if (typeof showToast === 'function') {
                    showToast('Action saved offline.', 'warning');
                }
            }
        }
    });

    document.addEventListener('click', function(evt) {
        const link = evt.target.closest('a[href="/auth/logout"]');
        if (link && !navigator.onLine) {
            evt.preventDefault();
            
            // Clear cached route manifest ETag and check cooldown client-side
            localStorage.removeItem('salus_routes_etag');
            sessionStorage.removeItem('salus_last_manifest_check');

            window.SalusSyncManager.enqueue({
                method: 'GET',
                url: '/auth/logout',
                body: {},
                headers: {},
                meta: { action: 'logout' }
            });
            
            window.location.href = '/auth/logout';
        }
    });
})();
