# 8. Lab results & fasting: domain models with a metric-system bridge

- Status: Proposed
- Date: 2026-08-13

## Context

Two new health domains need tracking:

1. **Blood work / lab results** — periodic lab panels (lipid, CBC, thyroid, …)
   with per-marker reference ranges and abnormal flags.
2. **Fasting** — intermittent/extended fasts as sessions with target durations
   and saved protocols.

The question is how to fit them into the existing architecture so that they are
*fully consumable* by the analytics, goals, dashboard, and insight systems
without duplicating those systems.

## Decision

### Lab results — metric system, extended

Lab markers are **full metric-system citizens** (they appear in the logbook,
analytics, and goals). This is achieved with three layers, mirroring the Food
hybrid pattern:

1. **Metric system** — each marker is a `metric_definition` (`source_data_type=
   "lab"`, `group_key="laboratory"`). Analytics/goals/dashboard work unchanged.
2. **Lab reference** — `lab_marker` (a `global`, code-defined reference keyed by
   `metric_code`) carries only the lab-specific metadata: `category`,
   `reference_low/high`, `optimal_low/high`, `description`. Seeded and synced
   like `mood_tag`/`achievement_definition`.
3. **Domain + bridge** — `lab_panel` (one draw) + `lab_result` (per marker),
   where each `lab_result` also writes a `Measurement` bridge
   (`source="lab"`, `source_data_type="lab"`, `external_id=lab_result.id`) so the
   marker's history flows into the metric system. Deleting a result deletes the
   bridged measurement.

This keeps the marker set finite and code-defined (DRY) and gives lab values a
single representation for trend/goal/insight consumption.

### Fasting — session domain model, with a bridge

`fasting_session` (start/end, `target_hours`, `type`) and `fasting_protocol`
(saved presets like 16:8) are a session-like domain model (analogous to
`workout_session`). On completion a `fasting_hours` metric measurement is
written (`source="manual"`, `source_data_type="fasting"`,
`external_id=session.id`), so fasting duration also feeds trends/analytics.

## Consequences

- `metric_definition` gains ~40 lab markers plus `fasting_hours`; the
  `laboratory` `metric_group` and `lab_marker` reference are seeded and exported
  to `reference.json` (frontend bundle) and synced (`global`).
- Lab markers default to `widget_enabled=False` (dashboard) but appear in the
  logbook, analytics, and goal selection.
- `lab_result`/`lab_panel`/`fasting_session`/`fasting_protocol` are `user_scoped`
  sync entities; `lab_marker` is `global`.
- The `lab` source is new to `Measurement.source`; the source-resolution system
  (`UserSourcePreference`) treats it like any other provenance source.

## Alternatives considered

- **Lab as standalone domain model (no metric bridge)** — rejected: analytics,
  goals, and trends would need duplicated consumption paths.
- **Lab markers as a separate `lab_marker` reference without `metric_definition`**
  — rejected: two finite, code-defined sets would drift and duplicate the metric
  machinery.
- **Fasting as a pure metric** — rejected: sessions/protocols have structure
  (start/end, target, type) that a scalar measurement cannot express.
