# 11. Food domain with a nutrition measurement bridge

- Status: Proposed
- Date: 2026-08-15

## Context

Meal tracking needs rich structure that the metric system cannot express: food
items form an open database (millions of products), meals are structured
(item × portions), and recipes are reusable templates. At the same time the data
must feed the existing dashboard, analytics, goals, insights and workout
autoregulation — all of which read `Measurement` rows. Without a bridge, every
consumer would need food-specific code.

## Decision

### 1. Dedicated domain model (not the metric system)

| Entity | Strategy | Purpose |
|---|---|---|
| `food_item` | `shared_nullable` | Open food database: system-seeded/verified items (`user_id=null`, `is_verified=true`) sync to everyone; user-created items sync only to the creator. Same pattern as `Exercise`. |
| `meal` | `user_scoped` | A logged meal: `log_date`, `meal_type`, optional name/notes. |
| `meal_item` | `user_scoped` | Junction meal × food_item with `servings`/`amount_g`. |
| `recipe` | `user_scoped` | Reusable template with servings, prep/cook time, `is_favorite`. |
| `recipe_ingredient` | `user_scoped` | Junction recipe × food_item with `amount_g`. |

The metric system stays for finite, code-defined metrics; food is explicitly
**not** one.

### 2. Nutrition measurement bridge

Every meal write maintains a single `Measurement` row per meal:

```
metric_code       = "nutrition"
source_data_type  = "nutrition"
source            = "meal"
external_id       = meal.id
start_time        = start of the meal's local day (User.timezone, ADR 009)
value_json        = { "calories": <float>, "protein_grams": <float>,
                      "carbs_grams": <float>, "fat_grams": <float> }
```

Meal lifecycle = measurement lifecycle (atomic in the command handler):

- create meal → create measurement
- update meal → delete old + create new
- delete meal → soft-delete measurement, items and meal
- cook recipe → create meal + items + measurement (scaled by servings)

`NutritionAnalysisService.daily_totals()` already filters
`source_data_type="nutrition"` and reads exactly these `value_json` keys, so the
bridge feeds analytics/dashboard/goals unchanged.

### 3. Canonical `value_json` schema

`calories`, `protein_grams`, `carbs_grams`, `fat_grams` is the single
convention. `Measurement.display_value` reads `calories` (fallback `total_kcal`)
and `*_grams` (fallback `*_g`) so legacy rows remain readable. The frontend
optimistic mirror writes the identical keys so client and server produce
deterministically equal rows (ADR 010).

### 4. Write path

Composed/verb writes go through command handlers (`create_meal`,
`update_meal`, `delete_meal`, `create_recipe`, `update_recipe`,
`delete_recipe`, `cook_recipe`), reached by both sync-push and the thin REST
routers. `food_item` is flat and written via auto-CRUD. Macros are computed in
one place (`commands/meal.py::_calc_macros`), including for `cook_recipe`.

### 5. Goal integration (note)

Nutrition goals use `metric_code="nutrition"` but the target refers to one of
four sub-fields. The goal evaluator currently compares a single `value_numeric`;
comparing against a `value_json` sub-field is a small extension that is
**deferred** and tracked here so it is not re-discovered later.

### 6. Deferred

- `meal_photo` (local + server file storage) — v2.
- Barcode scanner UI, external food data sources — see ADR 012.

## Consequences

- Dashboard/analytics/goals/insights consume nutrition data without changes.
- Food data is fully offline-capable via the standard sync strategies.
- One macro computation (DRY), deterministic client mirror (ADR 010).
- The status/gap document `docs/food-meal-logging-status.md` remains as a
  historical implementation log; this ADR is the normative record.
