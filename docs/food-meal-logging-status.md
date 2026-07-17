# Food / Meal Logging — Implementation Status & Gap Analysis

> **Date:** 2026-07-17
> **Branch:** `develop` (commit `c2de5e3` — backend, plus frontend WIP)
> **Overall:** Backend complete + tested. Frontend scaffolded — Core Happy-Path works, 8 gaps block production use.

---

## 1. Architecture Decisions (final)

| Decision | Rationale |
|---|---|
| **Dedicated domain model** (NOT metric system) | Food items are an open database (millions via OpenFoodFacts). Meals have structure (items × portions). Recipes are templates. None of this fits the finite metric-definition model. |
| **Measurement bridge** | Every meal CRUD writes/updates a `Measurement(metric_code="nutrition", source="meal", external_id=meal.id)` row. This feeds dashboard/analytics/goals without any changes to those layers. |
| **food_item = `shared_nullable` sync** | System-seeded items (`user_id=null`, `is_verified=true`) sync to all users. User-created items (`user_id=set`) sync only to creator. Exact same pattern as `Exercise`. |
| **meal / recipe / children = `user_scoped`** | Personal data, standard sync. |
| **meal_photo deferred** | File storage + IndexedDB blob complexity pushed to v2. |
| **No individual macro metrics** | Existing `nutrition` metric with `value_json` is sufficient. Analytics reads that unchanged. |

---

## 2. Integration Architecture — How Food Connects to Everything

### 2.1 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FOOD DOMAIN MODEL                           │
│                                                                     │
│  food_item (shared_nullable)          recipe (user_scoped)           │
│  ┌──────────────────────┐            ┌──────────────────┐           │
│  │ name, macros, brand  │            │ name, servings    │           │
│  │ barcode, serving_size│            │ instructions      │           │
│  │ is_verified, source  │            │ prep/cook time     │           │
│  └─────────┬────────────┘            └────────┬─────────┘           │
│            │                                  │                     │
│            ├── meal_item ──┐      recipe_ingredient                │
│            │   (servings)  │         (amount_g)                    │
│            │               │            │                          │
│            │         ┌─────▼────┐       │                          │
│            │         │   meal   │◄──────┘ (via cook endpoint)      │
│            │         │ user_id  │                                   │
│            │         │ log_date │                                   │
│            │         │ meal_type│                                   │
│            │         └────┬─────┘                                   │
│            │              │                                         │
│            └──────────────┘                                         │
│                           │                                         │
│              ┌────────────▼────────────┐                            │
│              │   _calc_macros()        │  ← pure function           │
│              │   calories, P, C, F     │                            │
│              └────────────┬────────────┘                            │
│                           │                                         │
│  ─ ─ ─ ─ ─ ─ ─ ─ BRIDGE ─▼─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
│                           │                                         │
│              ┌────────────▼────────────┐                            │
│              │   Measurement           │                            │
│              │   metric_code=nutrition │                            │
│              │   data_type=nutrition    │                            │
│              │   source="meal"          │                            │
│              │   external_id=meal.id    │                            │
│              │   value_json={           │                            │
│              │     calories: 420,       │                            │
│              │     protein_grams: 12,   │                            │
│              │     carbs_grams: 65,     │                            │
│              │     fat_grams: 9         │                            │
│              │   }                      │                            │
│              │   start_time=<meal_time> │                            │
│              └────────────┬─────────────┘                            │
│                           │                                         │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┼ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
│                           │                                         │
│     ┌─────────────────────┼─────────────────────────────┐           │
│     │                     ▼                             │           │
│     │  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │           │
│     │  │ Dashboard│  │ Analytics│  │    Goals      │    │           │
│     │  │          │  │          │  │               │    │           │
│     │  │ Widget:  │  │ daily_   │  │ "180g Protein │    │           │
│     │  │ nutrition│  │ totals() │  │  pro Tag"     │    │           │
│     │  │ chart    │  │ tdee()   │  │ → Progressbar │    │           │
│     │  └──────────┘  │ trend()  │  └──────────────┘    │           │
│     │                │ correl() │                       │           │
│     │  ┌──────────┐  └──────────┘  ┌──────────────┐    │           │
│     │  │ Insights │                │  Workout     │    │           │
│     │  │ AI Coach │                │  Autoreg.    │    │           │
│     │  │          │                │  TDEE-based  │    │           │
│     │  │ "Ernäh-  │                │  recovery    │    │           │
│     │  │ rungs-   │                │  score       │    │           │
│     │  │ coaching"│                └──────────────┘    │           │
│     │  └──────────┘                                    │           │
│     │                                                  │           │
│     │    ALLE lesen Measurements OHNE Änderung         │           │
│     │    NutritionAnalysisService.daily_totals()       │           │
│     │    liest value_json → NutritionDay dataclass     │           │
│     └──────────────────────────────────────────────────┘           │
│                                                                     │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
│                                                                     │
│  SYNC / OFFLINE                                                     │
│  ┌────────────────────────────────────────────────────┐             │
│  │  Dexie v16  │  Outbox (mutate)  │  Entity Meta     │             │
│  │  ───────────┼──────────────────┼───────────────── │             │
│  │  food_item  │  createFoodItem  │  shared_nullable  │             │
│  │  meal       │  createMeal      │  user_scoped      │             │
│  │  meal_item  │  (implicit via   │  user_scoped      │             │
│  │  recipe     │   meal create)   │  user_scoped      │             │
│  │  recipe_ing │  createRecipe    │  user_scoped      │             │
│  └────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Integration Points — Detailed

#### A. Measurement Bridge (the core integration)

**How it works:**
Every `MealService.create()`, `MealService.update()`, and `RecipeService.cook()` writes a `Measurement` row with `metric_code="nutrition"`, `data_type="nutrition"`, `source="meal"`, and `external_id=meal.id`. The `value_json` column stores `{calories, protein_grams, carbs_grams, fat_grams}`.

**Meal lifecycle = Measurement lifecycle (atomic via UoW):**
```
Create meal → Create Measurement(external_id=meal.id)
Update meal → Delete old Measurement + Create new
Delete meal → Soft-delete Measurement + Meal + MealItems (one transaction)
Recipe cook → Create Meal + Items + Measurement (one transaction)
```

**Why Measurement, not custom analytics tables:**
The Measurement table is the universal data sink. Dashboard widgets, the analytics pipeline, goal progress evaluation, and the AI coach ALL read Measurements. By writing a `nutrition` Measurement, food data flows into every existing system without a single line of code changed in those systems.

**Code references:**
- `MealService._measurement_for_meal()` — creates Measurement from meal + items
- `MealService._delete_measurement_for_meal()` — finds by `external_id` + `source` and soft-deletes
- `MeasurementRepository.find_by_external_id()` — added specifically for this pattern
- `Measurement.display_value` — already formats nutrition JSON as `"2100 kcal (140g P, 210g C, 70g F)"`

#### B. Dashboard Integration

**What already works:**
Dashboard widgets fetch measurements via `IMeasurementRepository.find_all(data_types=["nutrition"])`. Our bridge creates measurements with `data_type="nutrition"`, so nutrition data appears in the dashboard automatically.

**Widget rendering:**
- The existing `NutritionSummary` widget (if any) reads the most recent `nutrition` measurements
- Or a new dashboard widget can be added that filters `source="meal"` measurements
- The `Measurement.display_value` property renders macro totals in a readable format

#### C. Analytics Pipeline Integration

**Services that consume nutrition data unchanged:**

| Service | Method | What it reads |
|---|---|---|
| `NutritionAnalysisService` | `daily_totals(user_id, since, until)` | `Measurement` rows with `data_types=["nutrition"]` → aggregates per day → returns `list[NutritionDay]` |
| `NutritionAnalysisService` | `today(user_id)` | Today's nutrition measurements → single `NutritionDay` |
| `AnalyticsOrchestrator` | `_compute_tdee()` | Reads nutrition measurements for TDEE calculation (thermic effect of food) |
| `CorrelationAnalysis` | `compute_correlations()` | Cross-references `nutrition` measurements with `sleep`, `exercise`, `weight`, `mood` for pattern detection |

**The NutritionDay dataclass** (`src/salus/models/analytics.py:96-102`):
```python
class NutritionDay:
    date: date
    total_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
```
This is already the exact shape our measurement bridge produces — zero translation needed.

#### D. Goals Integration

**How it works:**
The goal system tracks progress via `Measurement` rows for a given `metric_code`. A user can set a goal like:
- "180g protein per day" — `Goal(metric_code="nutrition", target_value=180 ...)`
- "2200 kcal bulk phase" — `Goal(metric_code="nutrition", target_value=2200 ...)`
- "< 50g fat" — `Goal(metric_code="nutrition", target_value=50 ...)`

The goal evaluator reads today's `nutrition` measurement, extracts the relevant field from `value_json`, and compares against the target.

**What's needed:**
The existing `Goal` model targets `metric_code` + single `target_value`. The nutrition JSON has 4 sub-fields (calories, protein, carbs, fat). The goal evaluator needs to know WHICH sub-field to compare. This could be done by:
- Extending `Goal` with a `nutrition_field` enum (calories/protein/carbs/fat)
- Or having 4 separate metric_definitions (`nutrition_calories`, `nutrition_protein`, etc.) — but this was explicitly rejected in the architecture decision to avoid metric proliferation

**Status:** Goal integration is architecturally sound but needs the evaluator to handle JSON sub-fields. This is a small extension to the existing `evaluate_goal()` logic.

#### E. Insights / AI Coach Integration

**How it works:**
The `InsightService` can generate nutrition-related insights by:
1. Calling `NutritionAnalysisService.daily_totals()` → 7-day macro trends
2. Comparing to goals (e.g., "You've hit your protein target 5/7 days this week")
3. Cross-referencing with other metrics (e.g., "On days with >100g protein, your workout volume is 15% higher")
4. Detecting patterns (e.g., "Your fat intake increases on weekends by 30%")

**No changes needed** — the insight service already reads measurements, and our bridge creates measurements. The insight logic just needs prompts/rules for nutrition analysis.

#### F. Workout Autoregulation Integration

**How it works:**
The workout autoregulation system in `AnalyticsOrchestrator._compute_tdee()` already calculates Total Daily Energy Expenditure using:
- BMR (from weight, height, age, sex)
- PAL (Physical Activity Level — from heart rate data)
- TEF (Thermic Effect of Food — **from nutrition measurements**)

Our bridge creates the nutrition measurements that `_compute_tdee()` reads. This means:
- Recovery score automatically considers whether the user is in a caloric surplus or deficit
- Workout volume recommendations can factor in energy availability
- "You're undereating for your training load" type of insights become possible

**Code reference:** `src/salus/services/analytics/orchestrator.py:488-494`

#### G. Live Sync (SSE) Integration

**How it works:**
When a meal is created/updated/deleted:
1. `MealService` commits via UoW
2. The `Measurement` create/update/delete triggers the WritePipeline
3. WritePipeline calls `event_bus.publish(user_id)` 
4. SSE pushes to connected clients
5. Frontend `live-events.ts` debounces → `pullDelta()` → Dexie updates reactively

This means: if User A logs a meal on their phone, User A's laptop dashboard updates within 2 seconds.

#### H. Correlation Analysis Integration

**Cross-domain correlations that work automatically:**
Since all data flows into the Measurement table, the correlation engine can find relationships between:
- `nutrition.calories` ↔ `weight` (caloric surplus/deficit vs weight change)
- `nutrition.protein_g` ↔ `workout.volume_kg` (protein intake vs strength progression)
- `nutrition.carbs_g` ↔ `sleep.duration` (carb timing vs sleep quality)
- `nutrition.fat_g` ↔ `mood.score` (fat intake vs mood)

**No code needed** — the correlation analysis reads Measurement rows by `metric_code` and `data_type`. Our bridge creates `data_type="nutrition"` measurements. The correlator just needs to include `"nutrition"` in its data_type filter.

---

### 2.3 Yazio / FDDB Feature Parity Assessment

| Feature | Yazio | FDDB | Salus (now) | Salus (after Gaps 1-8) | Salus (after ALL) |
|---|---|---|---|---|---|
| Mahlzeiten loggen | ✅ | ✅ | ✅ (happy path) | ✅ | ✅ |
| Food-DB-Suche | ✅ | ✅ | ✅ (text only) | ✅ | ✅ |
| Barcode-Scanner | ✅ | ✅ (main feature) | ❌ | ❌ | ✅ (Gap 9) |
| Produkt-Datenbank | ✅ (paid DB) | ✅ (1.4M items) | ❌ (empty) | ❌ | ✅ (Gap 10 + 12) |
| Makro-Tracking | ✅ | ✅ | ✅ | ✅ | ✅ |
| Kalorienziele | ✅ | ✅ | ❌ | ✅ (via Goals) | ✅ |
| Rezepte | ✅ | ❌ | ✅ | ✅ | ✅ |
| "Cook"-Workflow | ❌ | ❌ | ✅ (broken) | ✅ | ✅ |
| Progress-Fotos | ✅ | ❌ | ❌ | ❌ | ✅ (Gap 11) |
| Wochen-Trend | ✅ | ✅ | ❌ | ❌ | ✅ (Gap 8) |
| Offline-fähig | ❌ | ❌ | ✅ | ✅ | ✅ |
| Self-hosted | ❌ | ❌ | ✅ | ✅ | ✅ |
| KI-Coaching | ❌ | ❌ | ✅ (via Insights) | ✅ | ✅ |
| E2EE-Sharing | ❌ | ❌ | ✅ | ✅ | ✅ |
| Korrelationen | ❌ | ❌ | ✅ (via Analytics) | ✅ | ✅ |

**Salus-Alleinstellungsmerkmale, die Yazio/FDDB nicht haben:**
- **Offline-First** — Logging funktioniert ohne Internet, sync bei Konnektivität
- **Self-Hosted** — Daten verlassen nie den eigenen Server
- **Korrelationen** — Ernährung × Schlaf × Training × Stimmung in einem System
- **KI-Coaching** — Personalisiertes Ernährungs-Coaching auf Basis aller Gesundheitsdaten

---

## 3. What is COMPLETE (Backend)

### Models (`src/salus/models/food.py`)
- `FoodItem` — nutritional data + barcode index, nullable `user_id` (shared_nullable)
- `Meal` — user-scoped, date-scoped, `MealType` enum (breakfast/lunch/dinner/snack/other)
- `MealItem` — junction: meal × food_item with servings/amount_g
- `Recipe` — user-scoped with prep/cook time, servings, is_favorite
- `RecipeIngredient` — junction: recipe × food_item with amount_g, notes

### Schemas (`src/salus/schemas/food.py`)
- Full Create/Update/Response for all 5 entities
- `MealItemResponse` embeds computed macros (derived from food_item × servings)
- `MealResponse` embeds items + total macros
- `MealSummaryResponse` — per-date aggregation
- `RecipeResponse` embeds ingredients + total macros

### Repositories (`src/salus/repositories/food.py`)
- `FoodItemRepository` — search (ilike), barcode lookup, frequent items (join meal_item)
- `MealRepository` — by user + date range, by date, by user
- `MealItemRepository` — by meal
- `RecipeRepository` — by user
- `RecipeIngredientRepository` — by recipe

### Services (3 files)
- **`FoodItemService`** — search, create, barcode, frequent
- **`MealService`** — CRUD with measurement lifecycle:
  - `create`: validates non-empty items → creates meal + items + `Measurement(external_id=meal.id)`
  - `update`: replaces items → soft-deletes old measurement → creates new
  - `delete`: soft-deletes meal + items + measurement (one UoW transaction)
  - `get_today`, `get_summary` — list/dict responses with derived macros
- **`RecipeService`** — CRUD + `cook`: creates Meal + MealItems + Measurement from recipe ingredients, scaled by servings parameter

### Routers (3 files, 18 endpoints)
| Router | Endpoints |
|---|---|
| `api_food.py` (`/api/v1/food`) | `GET /items/search?q=`, `GET /items/barcode/{code}`, `POST /items`, `GET /items/{id}`, `GET /frequent` |
| `api_meal.py` (`/api/v1/meals`) | `GET /meals?since=&until=`, `POST /meals`, `GET /meals/today`, `GET /meals/summary`, `GET /meals/{id}`, `PUT /meals/{id}`, `DELETE /meals/{id}` |
| `api_recipe.py` (`/api/v1/recipes`) | `GET /recipes`, `POST /recipes`, `GET /recipes/{id}`, `PUT /recipes/{id}`, `DELETE /recipes/{id}`, `POST /recipes/{id}/cook?servings=` |

### Wire-up
- `dependencies.py` — `get_food_item_service`, `get_meal_service`, `get_recipe_service`
- `main.py` — all three routers included
- `entity_meta.py` — 5 entries (`food_item` shared_nullable, rest user_scoped)
- `protocols.py` — 5 protocol classes
- `unit_of_work.py` — 5 repo properties in both IUnitOfWork + SqlUnitOfWork
- `repositories/measurement.py` — added `find_by_external_id(external_id, source?)` method

### Tests (`tests/test_food.py` — 16 tests, all passing)
- FoodItem: create, search, get, barcode, empty search
- Meal: create with items + derived macros, today, summary, delete, empty-meal rejection, auth, cross-user ownership
- Recipe: create with ingredients, list, delete, cook → creates meal, auth

---

## 3. What is COMPLETE (Frontend)

### Types (`frontend/src/lib/db/types.ts`)
- `FoodItem`, `Meal`, `MealItem`, `Recipe`, `RecipeIngredient` interfaces

### Dexie Schema (`frontend/src/lib/db/database.ts`)
- Version 16: `food_item`, `meal`, `meal_item`, `recipe`, `recipe_ingredient` tables with indexes

### Mutations (3 files)
- `mutations/food-item.ts` — `createFoodItem`
- `mutations/meal.ts` — `createMeal` (with optimistic payload), `updateMeal`, `deleteMeal`
- `mutations/recipe.ts` — `createRecipe`, `updateRecipe`, `deleteRecipe`

### Components (6)
| Component | Location | Status |
|---|---|---|
| `NutritionSummary.svelte` | `components/food/` | Complete — calorie total + P/C/F progress bars |
| `MealItemRow.svelte` | `components/food/` | Complete — name, macros, servings stepper, remove button |
| `MealCard.svelte` | `components/food/` | Complete — expandable meal with items |
| `MealGrid.svelte` | `components/food/` | Complete — grid + EmptyState |
| `MealForm.svelte` | `components/food/` | Complete — modal: type picker, food search with auto-add, items list with steppers |
| `RecipeCard.svelte` | `components/food/` | Complete — card with Cook button |
| `RecipeGrid.svelte` | `components/food/` | Complete — grid + EmptyState |
| `RecipeForm.svelte` | `components/food/` | Complete — modal: name, servings, ingredients search, instructions |

### Pages (5)
| Page | Route | Status |
|---|---|---|
| Meal List | `/meals` | Complete — DayNavigator, NutritionSummary, MealGrid + MealForm modal |
| Meal Detail | `/meals/[id]` | Complete — items list, macros, delete |
| Food Database | `/food` | Complete — search, results list, "New Item" modal with nutrition form |
| Recipe List | `/recipes` | Complete — RecipeGrid + RecipeForm modal |
| Recipe Detail | `/recipes/[id]` | Complete — ingredients, instructions, nutrition sidebar, Cook button |

### Infrastructure
- `schema.d.ts` regenerated (includes all food/meal/recipe API types)
- `icons.json` regenerated (104 icons including `restaurant`, `menu-book`, `whatshot`, `add-circle`)
- `generate-icons.mjs` skip-list extended: `dosage`, `strength`, `time`, `brand`, `calories`, `carbs`, `fat`, `protein`, `servings`

---

## 4. GAPS — Critical (Blocks Production Use)

### Gap 0: Measurement JSON field names don't match Analytics/Dashboard
**Files:** `src/salus/services/meal.py`, `src/salus/services/recipe.py`

**The bug:** Three different field-name conventions exist in the codebase for the same nutrition data:

| Field | `display_value` reads | `NutritionAnalysisService` reads | Our bridge writes |
|---|---|---|---|
| Calories | `total_kcal` | `calories` | `calories` |
| Protein | `protein_g` | `protein_grams` | `protein_g` |
| Carbs | `carbs_g` | `carbs_grams` | `carbs_g` |
| Fat | `fat_g` | `fat_grams` | `fat_g` |

**Impact:** Neither the dashboard widget (`display_value` expects `total_kcal`) nor the analytics pipeline (`daily_totals` expects `*_grams`) can read our measurements. The entire Measurement bridge is writing data into a format that no consumer understands.

**Required fix:**
1. Standardize on ONE convention. The `NutritionAnalysisService` convention (`calories`, `protein_grams`, `carbs_grams`, `fat_grams`) is the most "consumer" of nutrition data — align to it.
2. Update `_calc_macros()` in both `meal.py` and `recipe.py` to use the standard keys
3. Update `Measurement.display_value` to also support `calories` key (add fallback)
4. Add a migration note: existing `total_kcal`-format measurements remain readable via fallback

### Gap 1: Meal Items cannot be edited or removed after meal creation
**Files:** `MealItemRow.svelte`, `routes/meals/+page.svelte`, `routes/meals/[id]/+page.svelte`

The `MealItemRow` component has `onIncrement`, `onDecrement`, `onRemove` callbacks, but they are wired to `() => {}` (no-op) in both `MealCard.svelte` and `routes/meals/[id]/+page.svelte`.

**Required fix:**
1. `MealCard.svelte` — wire `onIncrement`/`onDecrement`/`onRemove` through to parent `onEdit` callback (or handle locally with state mutation + debounced API call)
2. `routes/meals/[id]/+page.svelte` — wire the callbacks to call `updateMeal(id, { items: updatedItems })` with the modified item list
3. `MealItemRow.svelte` — already structurally correct, just needs live callbacks

### Gap 2: Cannot add new items to an existing meal
**Files:** `routes/meals/[id]/+page.svelte`

The detail page has no "Add Item" button and no food search for adding items to an existing meal. User must delete and re-create the entire meal.

**Required fix:**
1. Add a food search input above the items list in the detail page
2. On selecting a food item, call `updateMeal(id, { items: [...existingItems, newItem] })`
3. Optionally reuse the search-dropdown pattern from `MealForm.svelte`

### Gap 3: Recipe "Cook" bypasses backend cook endpoint
**Files:** `routes/recipes/+page.svelte`, `routes/recipes/[id]/+page.svelte`

Both pages call `createMeal()` directly with raw ingredient data instead of `POST /api/v1/recipes/{id}/cook?servings=...`. This means:
- No servings-scaling (ingredient amounts are not adjusted for portion count)
- No recipe → meal linkage
- The backend's `RecipeService.cook()` which properly scales ingredients and creates the measurement is unused

**Required fix:**
1. Add `cookRecipe` to `mutations/recipe.ts` — calls the `/api/v1/recipes/{id}/cook?servings=X` endpoint
2. Update both `+page.svelte` files to use `cookRecipe` instead of `createMeal`
3. Add a servings picker (e.g., "Cook X portions") before triggering cook

### Gap 4: Recipe Cook — no servings selector
**Files:** `routes/recipes/+page.svelte`, `routes/recipes/[id]/+page.svelte`

When clicking "Cook", no dialog asks how many portions the user wants. The recipe has a `servings` field (e.g., 4 portions), but the cook action should let the user choose 1, 2, or all 4.

**Required fix:**
1. Add a small modal or inline selector: "How many servings? [1] [2] [4]"
2. Pass `servings` parameter to the cook API call
3. Default to 1 portion

### Gap 5: No cross-navigation between food features
**Files:** All 5 page files

User has no way to navigate from `/meals` to `/food` (to create a new food item while logging a meal) or to `/recipes` (to cook a recipe). Each page is an island.

**Required fix:**
1. Add quick-link buttons or a sub-navigation to the PageHeader actions area
2. Suggested layout on `/meals`:
   ```
   [Log Meal]  [Browse Food DB →]  [Recipes →]
   ```
3. Or add a tab bar / sub-nav component for the food domain

### Gap 6: Food Items cannot be edited or deleted
**Files:** `routes/food/+page.svelte`, `mutations/food-item.ts`

The food database page shows food items as read-only list items. There is no edit button and no delete button. If a user creates a food item with wrong nutrition data, it's permanent.

**Required fix:**
1. Add `updateFoodItem` and `deleteFoodItem` to `mutations/food-item.ts`
2. Add edit/delete buttons to each food item row in `/food/+page.svelte`
3. Add a `FoodItemForm` modal variant for editing (reuse the existing create form with pre-filled values)
4. Backend: add `PUT /api/v1/food/items/{id}` and `DELETE /api/v1/food/items/{id}` endpoints (currently missing!)

### Gap 7: Recipe ingredient amounts are not editable
**Files:** `components/food/RecipeForm.svelte`

The recipe form displays ingredient amounts in `<Input>` fields, but they are not connected to any state update function. `updateAmount()` existed but was removed (dead code). Changing the amount input has no effect on the saved data.

**Required fix:**
1. Wire each ingredient amount `<Input>` to an `oninput`/`onchange` handler that updates the ingredient's `amountG` in the `ingredients` array
2. Or restructure ingredients as `$state` objects with individual reactive properties

### Gap 8: No weekly/monthly nutrition overview
**Files:** `routes/meals/+page.svelte`

Only daily view exists via DayNavigator. The backend has `GET /meals/summary?since=&until=` but the frontend never calls it. User cannot see trends.

**Required fix:**
1. Add a "Week"/"Month" toggle near the DayNavigator
2. When toggled, call `/api/v1/meals/summary?since=X&until=Y` and render a summary card per day
3. Or render a simple bar chart showing daily calorie totals

---

## 5. GAPS — Non-Critical (Quality of Life)

### Gap 9: No barcode scanner integration
**Spec:** `GET /api/v1/food/items/barcode/{code}` exists in backend. Frontend has no barcode input or scanner UI.
**Required:** Add barcode text input to `/food` page + optionally integrate `BarcodeDetector` API or ZXing library.

### Gap 10: No OpenFoodFacts proxy
**Spec:** Server-side proxy for `GET /food/items/barcode/{code}` → OFF API. Backend endpoint exists but returns `null` for unknown barcodes (no proxy call implemented).
**Required:** Implement proxy in `FoodItemService.find_by_barcode()` — call OFF API, cache result, return food item.

### Gap 11: Meal Photos — not implemented
**Spec:** `meal_photo` table + file upload API + IndexedDB blob storage. Completely absent.
**Decision:** Deferred to v2 due to file-storage complexity.

### Gap 12: No nutrition data seeding
**Files:** Backend — no seed script for `food_item`
The food database starts empty. Users must create every item from scratch. A seed set of 50-100 common foods (oats, chicken, rice, eggs, milk, etc.) would dramatically improve onboarding.

---

## 6. Backend Endpoints — Missing

These endpoints are needed for the frontend gaps above:

| Method | Path | Needed for | Gap |
|---|---|---|---|
| `PUT` | `/api/v1/food/items/{id}` | Edit food item | Gap 6 |
| `DELETE` | `/api/v1/food/items/{id}` | Delete food item | Gap 6 |

Everything else in the API schema is implemented and tested.

---

## 7. Implementation Priority

| Priority | Gaps | Effort | Impact |
|---|---|---|---|
| **P0 — Critical bugs** | Gap 0 (measurement field names), Gap 1 (item edit), Gap 2 (add items to meal) | 2h | Fixes the broken analytics bridge + makes logging usable |
| **P1 — Core UX** | Gap 3 (cook via backend), Gap 4 (servings picker), Gap 5 (navigation) | 2h | Completes the recipe flow, connects the islands |
| **P2 — Completeness** | Gap 6 (food-item edit/delete + backend), Gap 7 (recipe ingredient amounts) | 3h | Completes CRUD for all entities |
| **P3 — Polish** | Gap 8 (weekly overview), Gap 12 (food seeding), EC1 (food_item deletion blocking) | 3h | Makes the nutrition page feel complete, protects data integrity |

---

## 8. Files Checklist for Next Session

When resuming work, the following files need attention:

### Backend (2 new, 2 modified)
- `src/salus/routers/api_food.py` — add PUT + DELETE endpoints for food items
- `src/salus/services/food_item.py` — add update + delete methods
- `src/salus/schemas/food.py` — add `FoodItemUpdate` schema
- `src/salus/repositories/protocols.py` — add `find_by_external_id` to `IMeasurementRepository` protocol (already exists in impl but not in protocol)

### Frontend (8 files to modify)
- `src/lib/mutations/food-item.ts` — add updateFoodItem, deleteFoodItem
- `src/lib/mutations/recipe.ts` — add cookRecipe (calls backend cook endpoint)
- `src/lib/mutations/meal.ts` — no changes needed (already complete)
- `src/lib/components/food/MealItemRow.svelte` — no changes (correct, callbacks just need wiring)
- `src/lib/components/food/MealCard.svelte` — wire item callbacks to parent
- `src/lib/components/food/RecipeForm.svelte` — wire ingredient amount inputs to state
- `src/routes/meals/+page.svelte` — add food/recipes navigation links
- `src/routes/meals/[id]/+page.svelte` — wire item callbacks, add food search for adding items
- `src/routes/food/+page.svelte` — add edit/delete for food items
- `src/routes/recipes/+page.svelte` — use cookRecipe mutation, add servings picker
- `src/routes/recipes/[id]/+page.svelte` — use cookRecipe mutation, add servings picker

### New files needed
- `src/salus/schemas/food.py` — `FoodItemUpdate` class
- Frontend weekly summary component (optional, P3)

---

## 9. Known Technical Debt (Non-blocking)

1. **eslint warnings** on all new Svelte files — `state_referenced_locally` pattern (same as pre-existing in HabitForm, MoodForm, etc.). Acceptable per project convention.
2. **`any` types in callback signatures** — cosmetic, same pattern used in medication/habits pages.
3. **Prettier formatting** on `schema.d.ts` and `icons.json` — auto-generated files, formatting noise.
4. **`generate-icons.mjs` skip list** — growing list of false-positive `name="..."` attributes on `<Input>` components. Could be fixed by making the regex context-aware (only match inside `<Icon` tags), but low priority.

---

## 10. Edge Cases & Data Integrity

### EC1: Deleted food_item referenced by meal_items
**Scenario:** User creates food_item "Haferflocken", logs it in 3 meals, then deletes the food_item.
**Current behavior:** `FoodItem` is soft-deleted. `MealItem` rows still reference the old `food_item_id`. `_calc_macros()` checks `food_map.get(item.food_item_id)` — returns `None` → macro contribution = 0.
**Impact:** Meal totals silently drop. User sees "0 kcal" for the item but the meal still exists.
**Mitigation needed:** When a food_item is about to be deleted, check if any meal_items reference it. If yes, either:
- Block deletion with a message: "This item is used in 3 meals. Delete those first?"
- Or soft-delete the item but preserve its name/macros in the meal_item as a snapshot (denormalize)

### EC2: Recipe ingredient references deleted food_item
**Same as EC1 but for recipes.** Mitigation identical — block or snapshot.

### EC3: Meal with 0 items after all items removed
**Scenario:** User removes all items from a meal.
**Current behavior:** `MealService.create()` rejects empty meals via `ApiError(code="empty_meal")`. But `update()` with empty items array is NOT checked.
**Impact:** Meal exists with no items and 0-value measurement.
**Fix:** Add validation in `update()` — if `data.items` is provided and empty, reject.

### EC4: Multi-device sync race condition
**Scenario:** User logs meal on phone (offline), then edits it on laptop (online). Phone comes online later.
**Resolution:** Last-write-wins via `updated_at` timestamps. Conflict dialog offers field-level merge if needed. This is handled by the existing sync/conflict system — no food-specific code needed.

### EC5: DayNavigator crosses into future dates
**Scenario:** User clicks "Next" repeatedly into next week.
**Current behavior:** Shows empty state — no meals. OK.
**Potential improvement:** Disable "Next" button when viewing today/tomorrow. The DayNavigator currently allows unlimited forward navigation.

---

## 11. Frontend Data Flow — Dexie-First Pattern

The frontend NEVER calls the REST API directly for reading data. All data flows through Dexie IndexedDB:

```
Dexie (IndexedDB) ← liveQuery subscribe ← $effect setup/teardown ← $state
     │                                                              │
     │ sync pulls (pullFull / pullDelta)                           │ $derived
     │                                                              │ computed views
     │  syncEngine.flushSingle()                                    ▼
     │  outbox flush                                         Components + Pages
     │
     │  mutate() ← user actions (create/update/delete)
     │  kind:'crud', optimistic payload
```

**Key implications for food/meal data:**
- `/meals` page loads meals + meal_items + food_items via 3 `liveQuery()` subscriptions
- `NutritionSummary` is `$derived.by()` — pure computation, no extra DB queries
- All writes go through `mutate()` (outbox → sync push)
- Optimistic payload in `createMeal` sets `user_id=''` — server fills it in
- No direct `fetch()` or `api.GET()` calls in any page or component
- This is exactly the same pattern used by habits, medications, mood, and journal

---

## 12. Missing from the Original Spec (not yet implemented)

These features were mentioned in the original `docs/food-meal-logging.md` spec but are NOT yet scoped or planned:

| Feature | Spec reference | Reason deferred |
|---|---|---|
| OpenFoodFacts API Key per user | Section "Ergänzungen" | Requires user settings UI for API key storage |
| Server-side OFF proxy | Section "Open Questions" | Backend implementation + rate limiting |
| BarcodeDetector vs ZXing debate | Section "Open Questions" | Need cross-browser solution decision |
| Meal Photos (local + server) | Section "Ergänzungen" | File upload + IndexedDB blob = v2 complexity |
| Calorie Target (TDEE) config | Section "Frontend" | TDEE calculator exists in analytics, needs UI |
| "Häufig zusammen gegessen" | Not in spec | Co-occurrence analysis for food pairing suggestions
