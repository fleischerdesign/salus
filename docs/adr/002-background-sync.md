# 2. Background sync: native Health Connect worker with direct push

- Status: Proposed
- Date: 2026-08-13

## Context

`HealthSyncWorker.kt` existed only as a stub (`doWork()` returned `Result.success()`
with a comment) and was never scheduled. The `AndroidManifest.xml` declared
`RECEIVE_BOOT_COMPLETED` and `androidx.work:work-runtime-ktx` was a dependency,
but no `PeriodicWorkRequest` enqueued the worker. AGENTS.md claimed
"WorkManager background sync" as if functional.

The goal: harvest Health Connect metrics while the app is closed and get them to
the server without requiring the user to open the app.

Two constraints shape the design:

1. **Dexie is WebView-only.** The outbox lives in IndexedDB inside the Capacitor
   WebView; a native `CoroutineWorker` running while the WebView is closed cannot
   read or write it. Any durable queue the worker touches must be native.
2. **The JWT lives in WebView `localStorage`.** The worker cannot authenticate a
   push unless the token is also available natively.

## Decision

The worker harvests natively and pushes directly to `/api/v1/sync/push`, with the
token and a durable pending queue stored in hardware-backed encrypted preferences.

1. **Shared harvest logic** — `HealthConnectHarvester` is the single source of
   truth for the Health Connect → Salus metric mapping (32 record types). Both the
   foreground `HealthConnectPlugin.fetchDelta` and the background worker call it.
2. **`SecureStorage`** — `EncryptedSharedPreferences` (AES256-GCM, MasterKey in the
   hardware keystore) stores the JWT, server URL, `last_harvest_at`, and the pending
   push queue. The SPA persists the token/server URL on login via the
   `SecureStoragePlugin` Capacitor bridge and clears them on logout.
3. **Idempotent push** — each harvested metric becomes a queue entry with a fixed
   `id` + `client_id`, persisted *before* the push and cleared only after a
   confirmed success. The server dedups on `client_id` within the `sync_push_log`
   TTL, so retries (after a dropped response) do not duplicate rows.
4. **Scheduling** — `PeriodicWorkRequest` (15 min) with
   `setRequiresBatteryNotLow(true)` + `setRequiredNetworkType(CONNECTED)`,
   enqueued as unique work with `ExistingPeriodicWorkPolicy.KEEP` from
   `MainActivity.onCreate`. Boot rescheduling is handled by WorkManager itself
   (`RECEIVE_BOOT_COMPLETED` is already declared).
5. **Pull is deferred to the foreground.** A background worker cannot write into
   the WebView's IndexedDB while the app is closed, and no UI consumes a pull
   anyway. The existing foreground `syncAll()` already performs a delta pull on
   launch, so a background pull would be redundant work.

## Consequences

- **Single write path is preserved in spirit but not in mechanism:** foreground
  writes flow through `mutate()` → outbox → push; background writes flow through
  the native queue → push. Both converge on the same `/api/v1/sync/push` endpoint
  and the same server-side dedup/pipeline.
- **Known limitation (follow-up):** the worker and the foreground
  `healthSyncService.syncNow()` maintain *independent* harvest cursors
  (`last_harvest_at` vs Dexie `health_connect:last_sync`). There is a small window
  where the same Health Connect record could be pushed twice with different
  `client_id`s (server dedup is keyed on `client_id`, not `external_id`). A
  server-side unique dedup on `measurement.external_id` (or a shared native
  harvest cursor consumed by the foreground) eliminates this. Not required for
  correctness of this change.
- **401 handling:** the worker treats `401`/`403` as terminal (keeps the queue,
  does not retry with an expired token). The queue flushes on the next run after
  re-login refreshes the stored token.
- **Battery:** the `CONNECTED` constraint means no harvesting happens offline;
  offline harvesting (harvest + queue, push later) is a possible future
  enhancement.

## Alternatives considered

- **Harvest-only worker, foreground flush (Decision 1 in
  `docs/native-apk-bundling.md` recommended Option A):** the worker stores the
  harvested payload in native storage and the SPA consumes it on next foreground
  via `mutate()`. Rejected: server-side data would only arrive when the app is
  opened, defeating the purpose of background sync.
- **Duplicate the harvest inside the worker:** rejected — violates DRY; the
  mapping is a single authoritative representation in `HealthConnectHarvester`.
