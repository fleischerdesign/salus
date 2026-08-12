# 1. Metric terminology: canonical `metric_code` and `source_data_type`

- Status: Proposed
- Date: 2026-08-13

## Context

Three distinct concepts in the metric system share overlapping names. This has
already caused one user-visible bug — the entries trend chart queried by the
`DataType` enum value (`"number"`) instead of the metric code — and makes
queries harder to reason about.

The three concepts:

| Concept | Meaning | Example values |
|---|---|---|
| Metric identity | Canonical code of a metric definition | `"steps"`, `"systolic_bp"`, `"heart_rate"` |
| Source data type | Raw channel a value came from | `"steps"`, `"heart_rate"`, `"water"`, `"blood_pressure"`, `"workouts"` |
| Value data type | How a value is stored | `"number"`, `"text"` (`DataType` enum) |

Current field naming is inconsistent:

| Concept | Canonical name | Current fields |
|---|---|---|
| Metric identity | `metric_code` | `MetricDefinition.code` (PK), `Measurement.metric_code` — correct |
| Source data type | `source_data_type` | `MetricDefinition.source_data_type`, **`Measurement.data_type`**, **`LeaderboardGroup.metric_type_code`**, **`find_all(data_types=…)`** |
| Value data type | `data_type` | `MetricDefinition.data_type` (`DataType`) |

`data_type` is the collision point: `MetricDefinition.data_type` is the *value*
type (an enum), while `Measurement.data_type` is the *source* type (a string).
The trend chart passed `MetricDefinition.data_type` (the enum `"number"`) where a
`metric_code` was required — the exact confusion this ADR eliminates.

**Additional finding:** manual measurements are created with `data_type: "number"`
(the enum), while ingested measurements carry `data_type: "<source>"`. So
`Measurement.data_type` holds two different things depending on origin, and
`find_all(data_types=[…])` silently misses manual rows.

## Decision

Adopt two unambiguous names and migrate the colliding fields.

1. `metric_code` — unchanged; the authoritative metric identity. Metric-based
   filtering and display must use `metric_code`.
2. `source_data_type` — the source channel. Rename:
   - `Measurement.data_type` → `Measurement.source_data_type`
   - `LeaderboardGroup.metric_type_code` → `LeaderboardGroup.source_data_type`
   - `FederatedMeasurementCache.data_type` → `FederatedMeasurementCache.source_data_type`
   - `FederatedAccessLog.data_type` → `FederatedAccessLog.source_data_type`
   - `MeasurementRepository.find_all(data_types=…)` → `source_data_types=…`
3. `data_type` — retained *only* on `MetricDefinition` as the value storage type
   (`DataType` enum); unambiguous once `Measurement.data_type` is renamed.

Semantic rule: metric identity → `metric_code`; federation/sharing channel →
`source_data_type`; value storage → `data_type`.

Manual measurements must populate `source_data_type` with the metric's
`source_data_type` (or `None`), fixing the `"number"` vs source-type
inconsistency.

## Consequences

- **Migration**: Alembic migration renaming the `measurement.data_type` and
  `leaderboard_group.metric_type_code` columns; no seed-data change (the
  `metric_type_mapping.py` seed already uses `source_data_type` correctly).
- **API contract**: sync push/pull payloads and REST auto-CRUD rename the
  `data_type` / `metric_type_code` fields; frontend `types.ts`, Dexie schema, and
  the generated `schema.d.ts` are updated.
- **Sync protocol**: `X-Salus-Sync-Version` is bumped — clients must re-sync to
  rebuild the measurement table.
- **Frontend**: `Measurement.data_type` consumers (`useWellness`, federation
  views, mutations) and `LeaderboardGroup.metric_type_code` consumers are
  updated to the new names.
- **Rollout**: deployed backend first (with a short dual-read window if any
  external federation peers are affected), then clients.
