# 7. Data quality: plausibility checks with shared bounds

- Status: Proposed
- Date: 2026-08-14

## Context

Salus ingests health data from heterogeneous sources — manual entries, wearable
sync (Health Connect / Apple Health), webhooks, and domain bridges (meal, lab,
fasting). A typo, a misconfigured unit, or a sensor glitch can inject a
nonsensical value (e.g. a 900 bpm heart rate) that then pollutes analytics,
goals, and insights without the user noticing.

We need a way to surface questionable data. The requirement is explicitly
**plausibility and UX**, not anti-cheat or adversarial integrity: the user is the
one entering or syncing their own data, and legitimate outliers (a pathological
lab value, a marathon step count) must never be silently rejected.

## Decision

### 1. Bounds are shared on `metric_definition`

Hard plausibility bounds (`min_value`/`max_value`) live on `metric_definition`
itself — the single, code-defined source of truth — not in a server-only table.
They are seeded via `metric_type_mapping.py`, exported into `reference.json`
(bundled by the SPA), and synced `global`, so the frontend can render inline
hints and the backend can check at write time from one representation.

### 2. Three checks, three channels

| Check | Trigger | Cost | Outcome |
|---|---|---|---|
| **Hard bounds** | write time (after-write hook) | O(1) metric lookup | `data_quality_flag` (`hard_bound`) |
| **Cross-source** | write time + recheck sweep | O(k) same-day sources | `data_quality_flag` (`cross_source`) |
| **Anomaly / z-score** | scheduled + manual recheck | O(n·window) per metric | `data_quality_flag` (`anomaly`) **+ Notification** |

All checks are **advisory**: they never block a write. A value outside bounds is
still stored; it produces a flag (and, for anomalies, a notification) the user
can act on. This is the key consequence of the "not anti-cheat" stance.

- **Hard bounds** cover the continuous/body metrics (steps, heart rate, weight,
  blood pressure, …). Lab markers carry *no* bounds: their reference ranges are
  clinical, and pathological values are the whole point of a test.
- **Cross-source** compares same-day values of *discrete* aggregate metrics
  (steps, sleep, water, calories, distance, floors, elevation, exercise,
  active calories) across the sources that reported them. A >25 % disagreement
  between sources flags a likely duplicate/mis-mapped ingestion.
- **Anomaly / z-score** flags values that jump a conservative threshold
  (`|z| > 3.5`) against the user's rolling personal baseline. It is the only
  check that *notifies*, because it is the strongest signal of bad data. The
  baseline is the *preceding* window (look-behind, not the current point), so a
  single outlier among stable data is not absorbed into its own window's
  variance. This is a **documented heuristic**, not a statistical test: health
  data is irregularly sampled, so the z-score is a conservative plausibility
  signal rather than a rigorous outlier test.

### 3. Findings are append-only `data_quality_flag`

All three checks write to one `data_quality_flag` entity (`append_only`,
`owner_field=user_id`, `no_soft_delete`). It is read-only to the client and
synced down, so the „Datenqualität" settings tab lists every finding without any
write path. Deduplication is per `(user_id, measurement_id, kind)` — a recheck
or a re-write of the same measurement does not re-flag it.

### 4. A reusable scheduler runs the expensive check

The anomaly check needs a personal baseline and is not O(1), so it cannot run at
write time. A small, dependency-free asyncio scheduler (`services/scheduler.py`)
runs the `DataQualityRecheckJob` periodically (plus a manual „Jetzt prüfen"
action in the settings tab). The scheduler is generic on purpose: future
periodic work (refill reminders, stale-sync detection, backups) reuses it.

## Consequences

- `metric_definition` gains `min_value`/`max_value`; `seed_definitions` repairs
  them; `reference.json` exports them.
- A new `data_quality_flag` entity (append-only) and a `data_quality` service
  with `run_checks()`.
- The `WritePipeline` gains a small after-write hook (per-entity callbacks after
  commit) used today only by `measurement` for the hard-bound + cross-source
  checks.
- Anomalies create `Notification` rows (`category="data_quality"`), surfacing in
  the existing notification bell. Hard-bound and cross-source findings notify
  only for non-manual sources (manual entry already shows the inline hint).
- No Play Integrity, no attestation, no rejection of user data.

## Follow-up decisions (remediation)

- **Flag kinds and severity are an enum** (`DataQualityKind`,
  `DataQualitySeverity`) — no stringly-typed kinds in the service.
- **`SAFE_PROFILE_FIELDS`** is the single source of truth for user-profile
  fields writable via sync-push and the `update_profile` command (the previous
  duplication between `entity_meta` and `commands/account` is removed).
- **Webhook upsert** runs the checks against the actually-persisted rows (the
  upsert returns them), so the flag's `measurement_id` is always correct and
  stale flags are cleaned on re-ingestion.
- **`Notification` stays generic**: notifications deep-link via a generic
  `link` route field and carry a `severity` field — no metric-domain coupling
  (`metric_code` on `Notification` was rejected as rigid; only `data_quality_flag`
  carries `metric_code`, because a flag *is* about a metric). Notification
  categories are enum-typed (`NotificationCategory`).
- **Notification coalescing uses a UTC day boundary**; per-user timezone bucketing
  is a possible future refinement, not required for correctness.
- **`check_measurement` re-evaluates idempotently**: a flag is added when a value
  violates, kept on re-writes while still violating (dedup), and removed when the
  value is corrected.
- **The write-hook is registered in the wiring layer** (`main.create_app`) rather
  than via an import side-effect in the generic `WritePipeline`; the anomaly
  z-score is a shared stat in `analytics/stats` (`zscore_vs_baseline`); the domain
  is a package (`services/data_quality/` with `checks`, `service`, `jobs`).

## Alternatives considered

- **Server-only bounds (config table)** — rejected: drifts from the client and
  breaks the open-source/Local-Mode "single source of truth" guarantee.
- **Reject writes outside bounds** — rejected: legitimate outliers exist; this
  is plausibility UX, not integrity enforcement.
- **Blocking write-time anomaly detection** — rejected: needs personal history
  and is O(n); would couple the write path to analytics.
- **Third-party scheduler dependency (APScheduler)** — rejected: a 40-line
  asyncio scheduler suffices and keeps the dependency surface minimal.
