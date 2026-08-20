# ADR-014: Training programming domain — terminology, structure, progression

**Status:** Proposed
**Date:** 2026-08-20

## Context

The workout domain models a training program as a flat list of exercises
(`WorkoutPlan` → `WorkoutPlanExercise`). Three capabilities are missing:

1. **No training-day layer** — a "Push Day" cannot be defined once and
   reused across programs.
2. **No time dimension** — training days cannot be scheduled (rotating /
   weekly / dated).
3. **No systematic progression** — the only load adjustment is
   autoregulation, which reacts *downward* to poor recovery but never
   progresses *upward* on successful sessions.

On top of this, the domain's **naming is inconsistent** and would block any
correct implementation:

- `WorkoutPlan` names a *single training day*, not a plan/program.
- "Workout" means three different things: the `/workouts` route, the act of
  starting a session (`startWorkout`), and — newly — a training day.
- The frontend `WorkoutPlan` type carries fields (`split`, `subtitle`,
  `estimatedDuration`, `targetVolume`) that do not exist in the backend model.
- **RPE vs RIR collision**: the plan editor stores `targetRir` (RIR, 0–N)
  while the backend and every other screen use `target_rpe`/`rpe` (RPE, 1–10).
  Different scales, mixed in one code path.
- "Set" (frontend) and `WorkoutLogEntry` (backend) name the same thing.
- "Split" exists only in the UI, with no representation in the data model.

## Decision

### Part A — Canonical terminology

| Concept | Was | Is (canonical) |
|---|---|---|
| Catalog exercise | `Exercise` | **`Exercise`** (unchanged) |
| Reusable training day | `WorkoutPlan` (misnomer) | **`Workout`** |
| Exercise prescription within a day | `WorkoutPlanExercise` | **`WorkoutExercise`** |
| Multi-day program with schedule | *(absent; UI "split")* | **`Program`** |
| Program → day slot with timing | *(absent)* | **`ProgramWorkout`** |
| Instance of performing a day | `WorkoutSession` | **`WorkoutSession`** (unchanged) |
| Logged set | `WorkoutLogEntry` | **`WorkoutSet`** |
| Perceived effort scale | RPE *and* RIR | **RPE (1–10)** only; RIR is display-only if ever needed |

The bridge-naming convention is `<Container><Item>` (`WorkoutExercise`,
`ProgramWorkout`), consistent with the existing `WorkoutPlanExercise`.

### Part B — Data model (three levels)

`Exercise → Workout → Program`.

- **`Workout`** — an ordered list of `WorkoutExercise`s with base targets
  (sets, reps, rpe, rest). Reusable across programs.
- **`Program`** — an ordered list of `ProgramWorkout`s. Each slot references
  a `Workout` and carries an optional timing rule:
  - none → rotation (next in sequence, wraps)
  - `day_of_week` → weekly
  - `date` → dated
- **`Program`** selects exactly one **progression scheme** (this replaces
  today's `autoreg_mode`).

### Part C — Progression

- Introduce a `ProgressionScheme` protocol with one entry point:
  `compute_targets(context) → targets`. This *proposes future load* and is
  distinct from the existing analytics `WorkoutProgressionStrategy`, which
  *reports past performance* (tonnage slope, 1RM regression).
  `LinearProgression` reuses the analytics building blocks
  (`get_exercise_progression`, 1RM regression) — never re-implements them.
- **Stateless**: targets are recomputed from history — the most recent
  completed session's performance of that exercise — never persisted as a
  "working weight". History stays the single source of truth; no state can
  drift, and nothing extra must be migrated or merged.
- **First scheme**: `LinearProgression` (progressive overload) — increments
  load when the previous session met its targets; holds when it missed.
- The existing `AutoregulationService` is refactored into a separate
  `AutoregulatedProgression` scheme behind the same interface.
- **Composition deferred**: the first slice supports exactly one scheme per
  program (`linear` | `autoregulated` | `none`). Composition (linear +
  deload + autoregulation) is a future ADR; the interface is designed so
  composition is an *implementation* detail behind one scheme, not a model
  change.

### Part D — Schema change (no data migration)

Salus is not in production — there is no user data to preserve. The schema
change is a straightforward rename + additive change, with **no
data-mapping migration**:

- Rename tables: `workout_plan` → `workout`,
  `workout_plan_exercise` → `workout_exercise`,
  `workout_log_entry` → `workout_set` (plus the `plan_id` → `workout_id`
  column rename on the bridge).
- Add tables: `program`, `program_workout`.
- Dev/seed data is re-seeded from `reference_data` into the new structure;
  no legacy-plan rows are mapped forward.
- **RPE fix**: `targetRir` in the plan editor is corrected to RPE semantics
  (the editor is changed to log RPE; values are not silently reinterpreted).

## Alternatives Considered

1. **Keep the flat model, add progression on top** (do nothing to structure).
   - Pros: minimal migration.
   - Cons: cannot express multi-day programs, reuse, or schedules;
     `WorkoutPlan` stays a misnomer; progression has no stable place to attach.
   - Rejected: the structural gap is the root cause the user identified.

2. **Rename only, no `Program` entity** (schedules attach directly to `Workout`).
   - Pros: one less table.
   - Cons: a `Workout` reused in two programs with different timing would
     duplicate schedule data on the `Workout` — violates DRY and single
     responsibility.
   - Rejected: reuse is a first-class requirement.

3. **Stateful progression** (persist a "current working weight" per exercise).
   - Pros: trivially answers "what's next"; implicit manual overrides.
   - Cons: a second source of truth that can drift from history; must be
     reconciled on delete/undo/sync; more state to migrate and merge.
   - Rejected: stateless recomputation keeps history authoritative and syncs
     for free.

## Consequences

- **Easier**: canonical naming makes the domain self-explanatory; `Workout`
  reuse removes duplication; new progression schemes are additive
  (open/closed); RPE is unambiguous across the boundary.
- **Harder**: a trivial schema migration (rename + create) must be written;
  frontend types and the plan editor must be aligned to the canonical model.
- **Next**: TDD implementation in two phases — (1) structure + schedule +
  migration, (2) linear progression — then update `docs/architecture/overview.md`.
