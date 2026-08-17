# 13. Metric daily-aggregate cache + measurement write facade

- Status: Accepted
- Date: 2026-08-16

## Context

The metric detail page (e.g. Heart Rate) took ~20 s to render its trend chart,
changed its time range and pagination only after unrelated database events, and
froze while paginating deep pages. Root causes, verified against the code:

1. **`fetchTrend` streamed the whole requested window of raw measurements**
   (Heart Rate had ~174k rows, so a 90-day window was the entire dataset) and
   additionally built two discarded ~174k-element arrays.
2. **Offset pagination** (`.offset((page-1)*25)`) walks N×perPage index entries
   per page — unusable for high-volume metrics.
3. **Missing `useQuery` deps getters** everywhere: `range`/`date`/`page`/route
   params are external Svelte state that Dexie's `liveQuery` cannot observe, so
   range switches, page flips and param-driven detail pages never re-ran their
   queries (AGENTS.md rule violated in ~all 116 call sites).
4. **Unbounded `.toArray()` scans** on `db.measurement`
   (`local-achievements`, `fetchAnalytics`, goal measurements).

## Decision

### 1. Per-day aggregate cache (`metric_daily_stats`)

A device-local Dexie table keyed `[metric_code+day]` holding `{ count, sum }`
over non-deleted numeric measurements. Trend charts read per-day means
(`sum/count`), so their cost is independent of the raw measurement volume.

- **Maintenance contract:** the cache is deterministic *by construction* — every
  measurement write routes through a single write facade (see 2) which adjusts
  the buckets atomically with the row write. Drift therefore only occurs if a
  write path bypasses the facade, which is prevented by routing all four known
  write sites (mutate, sync-pull, health ingest, backup import) through it.
- **Backfill/repair:** `rebuildMetricDailyCache(metric)` re-derives one metric
  from raw rows (streamed, no full array). It runs lazily when a metric has data
  but no cache yet (first view after upgrade/import) and after a backup import.
- **Never synced** — like `system_stats`, it is derived, device-local state.
- Day strings are local days in the user's timezone (ADR-009).

### 2. Measurement write facade (`measurement-writes.ts`)

A single choke-point for measurement mutations. `createMeasurements`,
`upsertMeasurements`, `updateMeasurements`, `deleteMeasurements` and
`restoreMeasurements` write the row(s) and the cache adjustments in one Dexie
transaction. All four write sites route through it.

### 3. Cursor pagination + reactive queries

- Metric detail pagination uses cursor bounds on `[metric_code+start_time]`
  (`above`/`below` on the last/first item's timestamp) instead of offset —
  O(log n + page size) per page. The `Pagination` component gained a cursor mode
  (prev/next only, no numbered jump) for very large datasets.
- Every `useQuery` that reads external Svelte state (range, date, page, route
  params, other query results) now passes a deps getter, so Dexie live queries
  re-run when those inputs change.

### 4. Bounded scans

- `fetchAnalytics` streams per-metric windows instead of `.toArray()`.
- `evaluateLocalAchievements` aggregates count / UTC-hour buckets / distinct days
  in a single streamed `.each` pass instead of materializing all measurements.

## Consequences

- Trend charts load in <100 ms after the cache is warm, regardless of volume.
- Range switches and pagination react immediately.
- The pure bucket arithmetic is unit-tested (`daily-stats-core.test.ts`).
- The cache adds write-path integration points; the facade is the auditable
  single entry and the maintenance contract is documented here and in the module.
- Dexie's `between()` upper bound is unreliable for composite keys (it silently
  drops the upper day) — day-range reads use `aboveOrEqual` + a JS day filter.
