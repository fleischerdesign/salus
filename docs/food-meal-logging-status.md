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

## 2. What is COMPLETE (Backend)

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
| **P0 — Blockers** | Gap 1 (item edit), Gap 2 (add items to meal) | 1-2h | Makes the app usable — user can correct mistakes |
| **P1 — Core UX** | Gap 3 (cook via backend), Gap 4 (servings picker), Gap 5 (navigation) | 2h | Completes the recipe flow, connects the islands |
| **P2 — Completeness** | Gap 6 (food-item edit/delete + backend), Gap 7 (recipe ingredient amounts) | 3h | Completes CRUD for all entities |
| **P3 — Polish** | Gap 8 (weekly overview), Gap 12 (food seeding) | 3h | Makes the nutrition page feel complete |

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
