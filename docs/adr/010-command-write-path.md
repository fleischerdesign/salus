# 10. Command handlers as the single write path

- Status: Proposed
- Date: 2026-08-15

## Context

Domain writes had *two parallel implementations with divergent behavior*:

- **Sync-push** (the SPA's write channel, `mutate()` → `/sync/push`) handled flat
  entities generically (`WritePipeline` auto-CRUD) and domain verbs through
  command handlers (`services/commands/`). `lab`, `fasting`, `workout`, `exercise`
  and `plan` were command-only.
- **REST routers** (`api_meal`, `api_recipe`, `api_habit`, `api_medication`) plus
  their services (`MealService`, `RecipeService`, `HabitService`, `MedicationService`)
  re-implemented the same domain logic *only* on the server side.

This caused concrete defects:

- `createMeal`/`createRecipe` written via sync-push CRUD **dropped the composed
  children** (`meal_item`, `recipe_ingredient`) and the `nutrition` measurement
  bridge, because that logic lived only in the REST services.
- `createPlan` mirrored only `workout_plan`, not `workout_plan_exercise`.
- Habit `check` and medication `log` had two toggle implementations (REST action
  vs. client-side CRUD) that could diverge.
- REST writes via services did **not** publish SSE events (the sync-push
  `WritePipeline` does).

The SPA reads exclusively through Dexie (synced) and writes exclusively through
`mutate()`; the REST API is the public/integration/federation surface. Both must
produce identical results.

## Decision

### 1. Commands are the single source of truth for domain writes

All domain-verb and composed writes live in `services/commands/` and are reached
through exactly one implementation. Both transports invoke them:

- **Sync-push** `type=command` → `WritePipeline._handle_command` → handler.
- **REST routers** become thin adapters: parse the Pydantic request, build a
  `SyncOperation(type="command", …)`, run it through `WritePipeline.process`, and
  map the `CommandResult` to the response model (reads re-fetch through the
  read services/enrichers). This also gives REST writes the same SSE event as
  sync-push writes.

New/changed commands: `create_meal`/`update_meal`/`delete_meal`,
`create_recipe`/`update_recipe`/`delete_recipe`/`cook_recipe`,
`toggle_habit_check`, `log_medication`/`skip_medication_dose`/
`delete_medication_log`. `delete_plan` now removes orphaned
`workout_plan_exercise` rows.

The workout REST router (`/api/v1/workouts/*`) previously re-implemented the
plan/session/log writes through `WorkoutService`; it now delegates them to the
same commands, and `WorkoutService` (planner) is read-only. `delete_log_set`
resolves a log by id *or* `(session_id, exercise_id, set_number)`, and session
reads filter soft-deleted log entries out of the `logs` relationship.

### 2. Generic CRUD is the write path for flat entities only

Flat entities (`goal`, `mood_entry`, `journal_entry`, `measurement`, `habit`,
`medication`, `food_item`, `exercise`, `medication_schedule`,
`medication_inventory`, `dashboard_widget`, …) are written by auto-CRUD
(`WritePipeline` / `api_rest.py`), already shared by sync-push and REST.
Redundant per-entity write methods and routers were removed:

- `create_goal`/`delete_goal` and `create_exercise`/`delete_exercise` commands,
  plus the exercise write endpoints in `routers/workout.py` and
  `WorkoutService.create/update/delete_exercise`.
- `api_mood` POST and `MoodService.log`.
- `api_dashboard` widget POST/PUT/DELETE and `DashboardWidgetService` write methods
  (widgets via auto-CRUD; the `config_json` the client provides).
- `MedicationService` write methods (medication/schedule/inventory/log/toggle),
  with `medication_schedule`/`medication_inventory` moved to auto-CRUD and the
  REST schedule/inventory write endpoints removed.
- `MealService`/`RecipeService`/`HabitService` write methods (reads remain).

Exercise keeps its auto-CRUD name-dedup validator (`_validate_exercise_create`)
and system-row write protection (write_pipeline ownership denies writes to
`user_id=None` rows). `MedicationSchedule.start_date` defaults to today so the
generic create path needs no per-entity default logic.

### 3. Typed command payloads

Command payloads are validated once by Pydantic models in `schemas/commands.py`
(shared by both transports), replacing ad-hoc `.get()` validation.

### 4. Accepted local-first duplications (intentional)

Two duplications remain *by design* because the app must work fully offline:

- **Optimistic mirror**: the client predicts a command's server-side effect
  (children + measurement bridge + computed values) in `mutate()`. To prevent
  drift, client and server must produce **deterministically identical** results —
  client-supplied IDs (`measurement_id`, entity `id`) are honored by the handlers,
  and rounding/computation is mirrored exactly. The server stays authoritative and
  a later sync overwrites the mirror.
- **Read derivation**: streak/adherence/macros are derived on the server
  (enrichers/read models, for REST) and recomputed client-side (Dexie, for
  offline). This is the offline-first cost, not a bug.

## Consequences

- One implementation per domain write; REST and sync-push cannot diverge.
- REST writes publish SSE events (live-sync parity).
- Composed domains (meal, recipe, workout plan) work fully in local mode.
- Existing REST tests remain green (delegates return identical responses); new
  command tests cover the write path (`tests/test_food_commands.py`).
