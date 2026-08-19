# AGENTS.md — salus

Health data tracker. FastAPI (backend) + SvelteKit SPA (frontend) + SQLite / PostgreSQL.
This file is written for LLM agents. Follow these rules exactly.

## Core Principles (ALWAYS apply)

- **DRY** — Zero duplication. Every piece of knowledge has a single, authoritative representation.
- **SOLID** — Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.
- **Akademisch professionell** — Code reads like a textbook: clear naming, minimal comments (code explains itself), rigorous correctness.
- **Clean** — No dead code, no magic numbers, no commented-out blocks, no TODO comments without a ticket reference.
- **Konsistent** — Follow the existing patterns in the codebase exactly. New code should be indistinguishable from existing code in style, structure, and conventions.
- **Agnostisch wo möglich** — Don't couple to implementation details. Use protocols/interfaces. Avoid vendor-lock. Prefer standards-based solutions.
- **System-Integration** — Every new domain MUST be evaluated against the existing ecosystem. Ask: (a) does it produce data that belongs in the Measurement/metric system? (b) should the dashboard surface it via a widget? (c) can analytics derive trends from it? (d) can goals reference it? (e) can insights generate coaching from it? (f) does it need to sync offline across devices? Not every domain needs every integration — Medication doesn't write Measurements, Journal doesn't need Goals — but every omission must be a conscious decision with a documented rationale, not an oversight.

## Stack

| Concern | Choice |
|---|---|
| Web framework | FastAPI (backend JSON API) |
| Frontend | SvelteKit (SPA mode, `adapter-static`) + TypeScript + Tailwind CSS |
| PWA / Offline | SvelteKit-native service worker (`src/service-worker.js`), Dexie.js (IndexedDB) |
| ORM layer | SQLModel for all tables (`metric_definition`, `metric_group`, `user_metric_preference`, `measurement`, `user`, `user_identity`, `goal`) |
| Database | `salus.db` (SQLite default) or PostgreSQL via `SALUS_DATABASE_URL` |
| Package manager (Python) | uv via `pyproject.toml` |
| Package manager (JS) | npm via `frontend/package.json` |
| Dev environment | Nix flake (`nix develop`) providing python313, uv, ruff, pyright, nodejs_22 |
| Password hashing | `bcrypt` directly (NOT passlib — incompatible with bcrypt 5.x on Python 3.13) |
| JWT | `python-jose[cryptography]` via `JwtService` in `services/jwt.py` |
| OAuth/OIDC | `authlib` via `OidcAuthProvider` in `services/auth/providers.py` |
| LDAP | `ldap3` via `LdapAuthProvider` in `services/auth/providers.py` |
| Live Sync | SSE (Server-Sent Events) via `EventBus` + `EventSource` |
| Lint / Format (Python) | ruff (`uv run ruff check src/`) |
| Type check (Python) | pyright (`uv run pyright src/`) |
| Lint / Format (Frontend) | prettier + eslint (`cd frontend && npm run lint`) |
| Type check (Frontend) | svelte-check (`cd frontend && npm run check`) |

## Project structure

```
src/salus/
├── models/          ← Dataclasses + SQLModel tables (DB structure)
├── schemas/         ← Pydantic API request/response models (API contract)
├── repositories/    ← Data access — Repository[T] base for SQLModel
│   ├── entity_meta.py   ← Single source of truth: ENTITY_META → all registries + validators
│   ├── unit_of_work.py  ← IUnitOfWork / SqlUnitOfWork (auto-commit Generator)
│   └── ...              ← Entity-specific repositories
├── services/        ← Business logic — receives repos via constructor injection
│   ├── sync.py          ← Full sync (cursor paginated) + delta sync (per-strategy security)
│   ├── write_pipeline.py ← Sync push: create/update/delete, dedup, ownership, PK protection
│   ├── event_bus.py     ← EventBus ABC + InMemoryEventBus (asyncio.Queue) for SSE live sync
│   ├── scheduler.py     ← AppScheduler (dependency-free asyncio loop) + ScheduledJob protocol
│   ├── timezone.py      ← Single source for local-day computation (User.timezone, ADR-009)
│   ├── data_quality/    ← checks.py (write-time), service.py (sweep), jobs.py (scheduled)
│   └── ...              ← Domain services
├── routers/         ← FastAPI route handlers — THIN: parse input, call service, return JSON
│   ├── api_sync.py      ← Sync endpoints (/api/v1/sync, /sync/push, /sync/entities, /sync/events)
│   ├── api_auth.py      ← Auth endpoints (/api/v1/auth/*)
│   ├── api_dashboard.py ← Dashboard data (/api/v1/dashboard/*)
│   ├── api_misc.py      ← Goals, Analytics, Insights, Circadian, Notifications, Onboarding
│   ├── api_settings.py  ← Settings endpoints
│   ├── api_admin.py     ← Admin endpoints
│   ├── api_sharing.py   ← Sharing/Community endpoints
│   ├── auth.py          ← OIDC redirect routes (/auth/oidc/*)
│   ├── sharing.py       ← Federation API (/.well-known/webfinger, /api/v1/federation/*)
│   ├── workout.py       ← Workout JSON API (/api/v1/workouts/*)
│   ├── asymmetric_share.py ← E2EE share API (/api/v1/shares/*)
│   ├── open_science.py  ← Open science synthesis API
│   ├── api.py           ← Metrics + Entries REST API (thin routes, UoW-backed)
│   ├── webhook.py       ← Webhook ingestion
│   └── export.py        ← CSV/JSON export download
├── config.py        ← pydantic-settings singleton
├── database.py      ← SQLModel engine + get_session generator
├── dependencies.py  ← ALL FastAPI Depends factory functions live here
├── exceptions.py    ← ApiError + NotFoundError, ConflictError, AuthenticationError,
│                       ForbiddenError, InvalidCredentialsError, raise_from_command_result
└── main.py          ← App factory, lifespan, CORS, router mounting, SPA mount

frontend/
├── src/
│   ├── app.html        ← HTML shell
│   ├── app.css         ← Design tokens + Tailwind
│   ├── lib/
│   │   ├── api/        ← openapi-fetch typed client
│   │   ├── components/ ← Svelte components (ui/, dashboard/, forms/, layout/)
│   │   ├── db/         ← Dexie database + sync engine + live events
│   │   │   ├── database.ts            ← Dexie schema (incremental versions)
│   │   │   ├── sync-engine.svelte.ts  ← Reactive sync engine ($state)
│   │   │   ├── sync-pull.ts           ← Paginated pullFull + pullDelta
│   │   │   ├── offline-service.ts     ← Delta-first syncAll
│   │   │   ├── mutate.ts            ← Unified write gateway (crud + command)
│   │   │   ├── entity-info.ts         ← Dynamic entity discovery from /sync/entities
│   │   │   ├── live-events.ts         ← EventSource SSE manager (debounced)
│   │   │   └── types.ts               ← OutboxOp, OutboxCrudOp, OutboxCommandOp, entity types
│   │   ├── stores/     ← Svelte 5 runes ($state stores)
│   │   └── utils/      ← Utilities (diff, formatting)
│   └── routes/         ← File-based routing (31 pages)
├── static/             ← PWA icons, manifest
├── svelte.config.js
├── vite.config.ts
├── tsconfig.json
└── package.json

tests/                  ← pytest (Backend)
```

### Directory purposes (strict)

| Directory | Contains | Does NOT contain |
|---|---|---|
| `models/` | Dataclasses, SQLModel `table=True` classes | API schemas, request/response DTOs |
| `schemas/` | Pydantic `BaseModel` for request/response | DB models, dataclasses, internal DTOs |
| `repositories/` | Classes that wrap data access (SQLModel Session) | Business logic, validation |
| `services/` | Business logic classes (injected repos via `__init__`) | HTTP concerns, route handlers |
| `routers/` | FastAPI `APIRouter` instances, route handler functions | Business logic, DB access |

## Architecture rules (DO NOT VIOLATE)


### 0. Metric system (global definitions, per-user preferences)

Metrics are a **finite, code-defined set** — users do NOT create custom metrics.

| Model | PK | Purpose |
|---|---|---|
| `MetricDefinition` | `code` (str) | Global truth: "steps", "systolic_bp", etc. Immutable; seeded at migration. |
| `MetricGroup` | `key` (str) | Groups related metrics. `input_mode`: `"combined"` (single form → multiple measurements, e.g. BP) or `"individual"` (separate entries, e.g. body measurements). |
| `UserMetricPreference` | `id` (UUID) | Per-user display: color, icon, enabled, widget visibility. FK → `MetricDefinition.code`. |

No custom `metric_type` table. No UUID per-unit metric types.

`MetricDefinition.replace()` returns the global definition. Use `mergeMetricPrefs()` on the frontend to combine definition + preference data.

Sync: `metric_group` and `metric_definition` use `strategy="global"`. `user_metric_preference` uses `strategy="user_scoped"`.

API: `GET /api/v1/metrics/groups` returns groups with sub-definitions pre-merged with user preferences.

**Three distinct terms (see `docs/adr/001-metric-terminology.md`) — never conflate them:**
- `metric_code` — canonical metric identity (`MetricDefinition.code`, `Measurement.metric_code`). Use for metric-based filtering and display.
- `source_data_type` — the raw source channel (`MetricDefinition.source_data_type`, `Measurement.source_data_type`, `LeaderboardGroup.source_data_type`). Use for federation/sharing.
- `data_type` — the value storage type (`MetricDefinition.data_type`, a `DataType` enum: `"number"`/`"text"`). Retained only on `MetricDefinition`.

The historical collision of `data_type` (enum) vs `data_type` (source channel) caused the empty entries trend chart. Do not pass `MetricDefinition.data_type` where a `metric_code` is required.


### 1. Service constructor injection (DIP)
Services MUST receive their dependencies via constructor. NEVER instantiate a repo inside a service.

```python
# ✅ CORRECT
class MetricTypeService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

# ❌ WRONG — violates DIP, untestable
class MetricTypeService:
    def __init__(self, session: Session):
        self.repo = MetricTypeRepository(session)
```

### 2. Wiring lives ONLY in dependencies.py
All `Depends` factory functions go in `dependencies.py`. Routers import them from there.
NEVER construct a repo or service in a router function body.

### 3. Routers are THIN
Router functions do: parse input → call service → return JSON/204.
No business logic. No raw SQL. No data transformation.

### 4. JSON-only responses
All routes return JSONResponse, Pydantic models (auto-serialized), or Response(status_code=204).
Exception handlers return only JSONResponse.

### 5. Cross-module relationship annotations
Models that reference types from other model files must use **string forward references** on
the *outer* annotation with `TYPE_CHECKING` guard. NEVER use `from __future__ import annotations`.

### 6. Narrowing `int | None` from SQLModel pk fields
Use `uid(user)` from `services/_helpers.py` to narrow the type.

### 7. Authentication architecture (Strategy Pattern)
- `LocalAuthProvider` — bcrypt password verification
- `LdapAuthProvider` — LDAP bind via `ldap3`
- `OidcAuthProvider` — OAuth2/OIDC via `authlib`

`AuthService` orchestrates. `JwtService` handles token creation/verification.

Auth flow:
```
SPA → POST /api/v1/auth/login → AuthService → Provider → JWT token
SPA stores token in localStorage, sends as Authorization: Bearer
Backend → get_current_user (dependencies.py) → verify Bearer or cookie → User
```

### 8. JWT cookie name
`salus_session` (defined as `TOKEN_COOKIE_NAME` in `dependencies.py`). Always use the constant.

### 9. Database engine configuration
SQLite: `check_same_thread=False`. PostgreSQL: no special connect_args.
Test: `sqlite://` + `StaticPool`.

### 10. Absolute imports only
Always use absolute imports starting from `salus.`. Never use relative imports.

### 11. Frontend component rules
- All components use Svelte 5 runes: `$props()`, `$state()`, `$derived()`, `$effect()`
- Prefer `$effect` for side effects; `onMount` is allowed only for one-time bootstrap logic
  (e.g. the auth bootstrap in `+layout.svelte` that must run exactly once and reacts on auth state otherwise)
- Props with default values use `let { prop = default } = $props()`
- Children slots use `Snippet` type from `import('svelte')`
- Use Tailwind utility classes, not BEM
- Material Symbols icon font for icons. Icons use the `<Icon name="icon-name" />` component
  which wraps `@iconify/svelte` OfflineIcon with the `material-symbols:` prefix.
  Icons MUST be bundled in `src/lib/icons.json` (generated by `npm run icons`).
  The `scripts/generate-icons.mjs` scanner extracts icon names from `icon="..."` and `name="..."` patterns in frontend code.
  Add new icons to the codebase first, then run `npm run icons`.
- Design tokens (colors, radii, shadows) are Tailwind theme variables matching the existing design system

### 12. Metrics / Entries frontend routing
```
/entries                                  ← Overview: group cards + standalone metric cards
/entries/[id]                             ← Dual-purpose: group view (if id=group_key) OR metric detail
/entries/[id]/[metric_code]               ← Metric detail within a group (back-nav to /entries/[id])
```
- `[id]/+page.svelte` determines group vs metric via `db.metric_group.get(id)` then renders accordingly.
- Group cards replace individual metric cards for grouped metrics on the overview.
- Groups with `input_mode="combined"` (Blood Pressure) get a combined entry form (systolic + diastolic → 2 measurements via `mutate()`).
- "New Metric" / edit / delete buttons on metrics are removed — metrics are finite/global.

### 13. Frontend API calls
All API calls go through `$lib/api/client.ts` which provides a typed `openapi-fetch` client.
Auth token is automatically added via interceptor.

### 14. SvelteKit SPA mode
- `adapter-static` with `fallback: 'index.html'`
- `ssr = false` in `+layout.ts`
- Routes are purely client-side (no server-side rendering)
- Service worker via SvelteKit's native `$service-worker` module (`src/service-worker.js`, auto-registered by SvelteKit)

### 14. Sync architecture (Local-First)

**Single write path (Unified Outbox):**
- `mutate()` — Unified write gateway via sync push (`POST /api/v1/sync/push`)
  - `kind: 'crud'` — Entity CRUD (create/update/delete), batchable
  - `kind: 'command'` — Domain Commands (start workout, log set, etc.)
  - All operations enqueued to a single FIFO `outbox` table in Dexie
  - Flushed in FIFO order preserving temporal dependencies

**Sync pull:**
- Full sync: `GET /api/v1/sync` → paginated via `?cursor=<base64(json)>`, `WHERE id > cursor ORDER BY id LIMIT batch_size`
- Delta sync: `GET /api/v1/sync?since=<ISO>` → per-entity strategy filtering (`user_scoped`, `shared_nullable`, `relational`, `global`, `append_only`, `special`)
- Delta-first: `syncAll()` tries delta first (if last sync < 7 days old), falls back to full

**Sync push:**
- `POST /api/v1/sync/push { operations: [{ type, entity, client_id, data, id?, expected_updated_at? }] }`
- WritePipeline: dedup via `sync_push_log` (24h TTL), ownership check (`user_id`/`owner_id`/`User`), PK protection, `updated_at` auto-set
- UoW auto-commit: `get_unit_of_work` → Generator `try/yield/except/rollback/else/commit`

**Entity registry:**
- `entity_meta.py` — single source of truth: `ENTITY_META` list derives `ENTITY_REGISTRY`, `SYNC_ENTITY_SPECS`, `DELTA_ENTITY_SPECS`, `APPEND_ONLY_DELTA_SPECS` + validators
- `GET /api/v1/sync/entities` — dynamic entity discovery for frontend
- `entity-info.ts` — fetches from endpoint, caches result in memory + Dexie (no hardcoded fallback)

**Conflict resolution:**
- Background sync: auto-resolve with server version (last-write-wins)
- Interactive `mutate()`: enqueue to `conflictStore` → `ConflictDialog` with field-level merge (per-field Server/Mine radio buttons)
- `expected_updated_at` auto-extract from `opts.optimistic.updated_at`

### 15. Live Sync (SSE)

```
WritePipeline commit → event_bus.publish(user_id)
  → GET /api/v1/sync/events (SSE)
    → EventSource (Browser) → debounce 2s → pullDelta()
```

- `EventBus` ABC + `InMemoryEventBus` (asyncio.Queue, maxsize 32) — `app.state.event_bus` singleton
- Auth via `salus_session` cookie (EventSource sends cookies same-origin automatically)
- `connectLiveSync(onSync)` / `disconnectLiveSync()` in `live-events.ts`
- Started after successful `syncAll()`, stopped on session expiry
- Debounce: multiple rapid events → single delta sync after 2s quiet period

### 16. Sync protocol versioning
`X-Salus-Sync-Version: 1` header sent by frontend via `getAuthHeaders()`, validated by backend `_check_sync_version` dependency. Backend rejects unsupported versions with 400.

### 17. REST API surface (one concept)

> **auto-CRUD = the only way to CRUD. Action routers = only domain verbs. Sync = sync.**

- **auto-CRUD** (`routers/api_rest.py`) is the single generic CRUD surface for sync entities
  (list/get/create/update/delete). It is strategy-driven: `user_scoped`/`shared_nullable`/
  `relational` get full CRUD; `global` and `append_only` are read-only. Write routes are derived
  from `EntityMeta.strategy` — never special-case an entity by hand.
- **Typed responses**: SQLModel classes are used as `response_model`; entities with computed
  reads register an **enricher** + response model in `services/entity_enrichment.py` (e.g. habit
  stats). No hand-rolled `_*_to_response` dict builders in routers.
- **Action routers** exist only for domain verbs and aggregations (habit `check`/`stats`,
  medication `today`/`schedule`/`log`/`inventory`, journal `date`/`search`, workout session
  lifecycle, insight `generate`, notification `read-all`). Composed-aggregate domains (meal,
  recipe, achievement progress) keep dedicated routers because their responses carry child
  items/progress that flat auto-CRUD rows cannot express.
- **Ownership**: auto-CRUD scopes reads by owner and returns 404 (not 403) on cross-user access,
  matching the service convention of not revealing resource existence.
- **Write channels** (documented): CRUD → WritePipeline (sync push + auto-CRUD); domain verbs →
  services; commands → command handlers. All channels must publish SSE events after commit.

### 18. Timezone & local-day boundaries (ADR-009)

`User.timezone` (IANA name, default `UTC`) is the **single source** for "which calendar day an
instant belongs to". Measurements are stored as naive UTC; day strings (`log_date`, `entry_date`)
are opaque local dates created by the tz-aware frontend `todayString()`.

- Backend: route all day logic through `services/timezone.py` (`local_date`, `today_in_tz`,
  `local_day_range`, `start_of_local_day`, `tz_for`, `user_today`). Never `datetime.now(utc).date()`
  or `date.today()` for a *user's* day; use half-open `[local_midnight, next_local_midnight)`.
- Frontend: `$lib/utils/timezone.ts` (cached profile zone + `dateStringInTz`/`startOfTodayMs`);
  `$lib/utils/datetime.ts`'s `todayString()` is tz-aware. Display formatting stays browser-local.
- `services/scheduler.py` (`AppScheduler`/`ScheduledJob`) runs periodic jobs; write-time side
  effects hook via `ENTITY_AFTER_WRITE` (registered explicitly in `main.create_app`, not by import).

## Adding a new entity (checklist)

1. `models/<name>.py` — SQLModel table
2. `schemas/<name>.py` — Pydantic Create/Response models
3. `repositories/<name>.py` — Repository class
4. `repositories/protocols.py` — `@runtime_checkable` Protocol class, import model types
5. `repositories/unit_of_work.py` — Add protocol import, concrete repo import, property to `IUnitOfWork` AND `SqlUnitOfWork` (both protocol type annotation AND `__init__` assignment)
6. `repositories/entity_meta.py` — `EntityMeta` entry with correct `strategy` and `batch_size`
7. `services/<name>.py` — Business logic service
8. `dependencies.py` — Repository + Service factories
9. `routers/api_<name>.py` — JSON API routes under `/api/v1/`
10. `main.py` — `app.include_router()`
11. `tests/test_<name>.py` — pytest tests
12. Frontend: `types.ts` — TypeScript interfaces matching SQLModel fields
13. Frontend: `database.ts` — new `this.version(N).stores({...})` block (only new tables, never repeat existing ones)
14. Frontend: `mutations/<name>.ts` — async functions wrapping `mutate()` for each CRUD operation
15. `cd frontend && npm run gen-schema` — regenerate typed API client after new endpoints
16. `cd frontend && npm run icons` — regenerate icon bundle after new icon references

### Sync strategy decision

Every new entity needs a sync strategy. Available values:

| Strategy | When to use | Example |
|---|---|---|
| `user_scoped` (default) | Data belongs to one user, synced only to their devices | `habit`, `meal`, `medication`, `lab_panel`, `lab_result`, `fasting_session` |
| `shared_nullable` | System-seeded items (user_id=null) + user-created items (user_id set). All users see system items, only creator sees theirs. | `exercise`, `food_item` |
| `global` | Immutable reference data, same for all users, no user_id column | `metric_definition`, `achievement_definition`, `lab_marker` |
| `relational` | Child entity whose owner is determined via parent FK chain | `workout_plan_exercise`, `workout_log_entry` |
| `append_only` | Write-once, never updated or deleted | `api_token`, `federated_access_log`, `data_quality_flag` |

`batch_size`: parent entities → 500, high-volume log children → 2000.

Composed domains that also write a Measurement bridge (lab panels/results, fasting sessions)
use command handlers as their single write path (`_SKIP_AUTO_CRUD`), not generic CRUD.

### Metric system vs Domain Model decision

Not every domain belongs in the metric system. Use this framework:

| Question | Yes → | No → |
|---|---|---|
| Is the entity primarily a numeric measurement over time? | Metric system | Domain model |
| Is the set of entities finite and code-defined? | Metric system | Domain model |
| Does the entity have complex internal structure (sub-items, schedules)? | Domain model | Metric system |
| Does the domain produce data that should appear on the dashboard/analytics? | Add Measurement bridge | Keep standalone |

**Hybrid pattern (Food):** Own domain model for rich structure (food_item, meal, meal_item, recipe), PLUS a Measurement bridge that writes `metric_code="nutrition"` rows so dashboard/analytics/goals consume the data unchanged. Link via `Measurement.external_id` and `source` field for lifecycle management (delete meal → delete measurement).

**Standalone pattern (Medication):** Own domain model only. No measurement bridge because schedules + inventory don't map to numeric time-series metrics. Can still integrate via Goals (adherence %) and Insights (refill reminders).

### Frontend data loading (Dexie-first)

**NEVER call the REST API directly for reading data.** All data lives in Dexie IndexedDB. The single reactive-read idiom is the **`useQuery`** hook from `$lib/db/use-query.svelte`. Dexie's `liveQuery` runs the querier asynchronously, so reads *inside* the querier are invisible to Svelte reactivity — pass a **`deps` getter** for any external reactive input (dates, params, view modes) so the subscription re-runs when it changes:

```typescript
const dayQuery = useQuery(
  async () => {
    const meals = await db.meal.where('log_date').equals(selectedDate).toArray();
    // ... also query meal_item, both tables in one liveQuery (no cross-query dependency)
    return { meals, items };
  },
  () => selectedDate   // ← re-subscribes when selectedDate changes
);
```

Do **not** hand-write `$effect(() => { liveQuery(...).subscribe(...) })` blocks and do **not** assign a `liveQuery` store (`let x = liveQuery(...)` + `$x`). Avoid one `useQuery` reading another query's *result* as its input — the child query never re-runs when the parent updates (and early-returning `[]` before touching a table leaves it with **no observer at all**). Query each table independently and join in `$derived`, or read both tables in one composite query.

**Never destructure `useQuery`'s result.** Svelte 5 `$state` reactivity is resolved at compile time (`$.get`/`$.set`); it does **not** survive returning a value out of a function and destructuring it. `const { value: medications } = useQuery(...)` captures a one-time snapshot — `loading` stays `true` and `value` stays `undefined` forever. Keep the query object and bind `value`/`loading` via `$derived` aliases, which are reactive reads.

```typescript
// ✅ CORRECT — the only reactive-read idiom
const medicationsQuery = useQuery(
  () => db.medication.notDeleted(db.medication).toArray()
);
const medications = $derived(medicationsQuery.value);
const loading = $derived(medicationsQuery.loading);
// template: {#each medications ?? [] as med} · {#if loading}skeleton{/if}

// ❌ WRONG — destructuring captures a one-time snapshot; loading stays true, value stays undefined
const { value: medications, loading } = useQuery(
  () => db.medication.notDeleted(db.medication).toArray()
);

// ❌ WRONG — direct API call
onMount(async () => {
  const res = await api.GET('/api/v1/medications');
  items = res.data;
});

// ❌ WRONG — liveQuery store (not reactive to state params, stale on navigation)
let medications = liveQuery(() => db.medication.toArray());

// ❌ WRONG — unindexed full-table scan on high-volume time-series (deserializes 50k items to RAM)
const measurementsQuery = useQuery(() => db.measurement.filter((m) => !m.deleted_at).toArray());

// ✅ CORRECT — indexed query bounded by compound key or limit
const latestQuery = useQuery(async () => {
  return await db.measurement.where('metric_code').equals(code).and((m) => !m.deleted_at).reverse().sortBy('start_time').then(r => r[0]);
});
```

**High-Volume Time-Series Performance Rule:**
Entities with large append-only/log volumes (`measurement`, `workout_log_entry`, `data_quality_flag`, `federated_access_log`) must NEVER be scanned with unindexed `.toArray()`. Always use B-Tree indexes (`.where('metric_code').equals(...)`), compound index ranges (`.where('[metric_code+start_time]').between(...)`), or bounded slices (`.then(items => items.slice(0, 100))`) to keep query latency below 5ms.

**All writes go through `mutate()`**, never `api.POST()` or `fetch()`:
```typescript
// ✅ CORRECT
await mutate({ kind: 'crud', op: 'create', entity: 'medication', id: crypto.randomUUID(), data });

// ❌ WRONG
await api.POST('/api/v1/medications', { body: data });
```

### Food / Nutrition frontend (Log Food builder + flat rendering)

- **One universal add flow**: `MealForm` is the **Log Food builder** — the only entry to log food. It has a slot selector (meal type), a search that surfaces **foods and recipes**, a scan button, frequent-food chips, a live item list with ±/×, a collapsible "Details" section (optional **name + notes**), and a sticky "Add to [Slot]" footer with live macros. Reachable from the PageHeader "Log Food" button (slot inferred by time) and per-group "+ Add" (slot preselected).
- **`name` is the composition trigger**: a meal with a name (or a cooked recipe, named `Recipe: …`) renders as a **`MealBlock`** (header + expandable items, edit/delete). An unnamed meal renders its items as **flat `MealItemRow`s** directly under the meal-type group — single foods and several separate foods stand alone. Rendering rule lives in `MealGroups`.
- **Recipes flow into the builder**: `composeRecipe(recipeId, servings)` (`mutations/recipe.ts`) returns scaled `{ name, items }` without committing; `CookModal` hands the servings back to the builder, which lands the composition in the item list.
- **Barcode scanning uses `@zxing/browser`** (`BarcodeScanner.svelte`, `BrowserMultiFormatOneDReader` + `decodeFromConstraints`, FullHD ideal, `facingMode: environment`). Cross-browser; a `BarcodeNotFound` notice (not a forced modal) offers inline food creation with the scanned barcode.
- **PortionPickerModal** (`servings` stepper + grams input for g/ml units, live macros) is used for every food selection. `MealItemRow` shows the real quantity (`servings × serving_size + unit`), not the vestigial `amount_g`.
- **Shared helpers** in `$lib/food/`: `frequent.ts` (`loadFrequentFoods`, `newestFood`), `nutrition-goals.ts` (`fetchNutritionTargets`), `barcode.ts` (`lookupBarcode`).
- **Nutrition goals (P6)**: `Goal.nutrition_field` (`calories|protein|carbs|fat`, nullable) targets a `value_json` sub-field; the evaluator **sums** it over the period. The `/goals` form shows a sub-field picker when `metric_code="nutrition"`.

### High-Performance Time-Series & Frontend Data Architecture (Strict Rules)

Continuous health tracking (e.g. Android Health Connect, Apple Health, wearable smartwatches) ingests **tens of thousands of data points per week** into `db.measurement`. To guarantee deterministic **sub-10ms UI rendering (60–120 FPS)** without frame drops:

> **Scope:** these rules target *rendering* of continuous, high-frequency metrics on the dashboard and
> entry/trend views. One-off batch analyses (insight generation, leaderboard scoring, export) may
> legitimately read broader windows (e.g. 7 days of context for an LLM coaching prompt) — they are not
> per-frame and their cost is amortized over a single request.

1. **Cursor Streaming over Array Allocation (`.each()` vs `.toArray()`)**:
   - **NEVER** call `.toArray()` on unbounded time-series tables (`db.measurement`).
   - Use IndexedDB Cursor Streaming (`.each((m) => { ... })`) directly over composite indexes (e.g. `[metric_code+start_time]`).
   - Aggregations (hourly buckets, sums, averages, min/max, percentiles, heatmaps) MUST be computed in-flight within the stream to prevent allocating thousands of heavy JavaScript objects on the V8 heap.

2. **Contract-Driven Lookback Windowing**:
   - High-Frequency Metrics (`heart_rate`, `steps`): Query **only Today + Yesterday (1-day lookback)**. Never fetch arbitrary 7-day or 30-day windows for continuous high-frequency streams.
   - Low-Frequency Metrics (`weight`, `body_fat`, `blood_pressure`): 7-day lookback for sparklines/trends.
   - Always specify explicit lower AND upper bounds: `.between([code, windowStart], [code, windowEnd])`.

3. **Separation of Static Dimensions from Time-Series Facts**:
   - Static metadata (`MetricDefinition`, `UserMetricPreference`, `Goal`, `DashboardWidget`) must be cached in-memory (`getDashboardMeta()`).
   - Date switches must NEVER re-query static tables from IndexedDB; only time-series facts for active metric codes are fetched.

4. **In-Card Skeleton Loading (`Card` and `ChromeCard`)**:
   - Use `loading?: boolean` and optional `skeleton?: Snippet` on cards.
   - Do NOT unmount cards or show full-screen layout thrashing on date switches. Card headers, titles, and grid slots remain locked in place while only the inner body transitions smoothly.

### Context-Sensitive Platform Model (APK vs. Web/PWA) & Settings Decoupling

Salus operates across two runtime environments with strict context-awareness:

| Runtime | Environment | Server Host Resolution | Hardware Capabilities |
|---|---|---|---|
| **Native Android APK** | Local Capacitor WebView (`https://localhost`) | Configured via `salus_server_url` / dynamic `getApiBaseUrl()` | Android Health Connect, WorkManager background sync, Biometric lock, Native haptics |
| **Web Browser / PWA** | Hosted instance origin (`window.location.origin`) | Fixed to current origin session (`window.location.origin`) | Service Worker offline cache, IndexedDB storage meter, WebAuthn |

**Device-Local vs. Cloud-Synced Preferences Rule:**
- **Cloud-Synced (`User` fields)**: Cross-device user settings live on the `User` model — `theme`, `locale`, `display_name`, `onboarding_dismissed`, `colorblind`, `accent_hue`. Updated via the `update_profile` command / sync-push `user` update, synced down through the sync `user_profile`. There is **no** `user_preference` entity.
- **Device-Local (`localStorage` / Dexie device config)**: Hardware-specific options (Biometric app lock, Haptic vibration, Local cache quota, Server Host URL). **NEVER synced across devices.** Theme/colorblind/accent also fall back to `localStorage` in Local Mode.

**UI Context-Sensitivity (`/settings/app` & `/auth/login`):**
- Features requiring native hardware (Server Host URL inputs, biometric sensors, haptic toggles) MUST be guarded with `{#if Capacitor.isNativePlatform()}`.
- Web/PWA sessions display read-only origin info (`Active Origin: window.location.origin`) and browser storage gauges instead of redundant server host inputs.

**Android Health Connect gotchas:**
- Every Health Connect permission the plugin requests (`HealthConnectPlugin.PERMISSIONS`, `HealthConnectHarvester.recordTypes`) MUST be declared as `<uses-permission>` in `AndroidManifest.xml`. Android's PermissionController silently drops any runtime-requested permission that is not manifest-declared — it is never offered in the permission prompt and never appears in `dumpsys`.
- `getChangesToken(ChangesTokenRequest(recordTypes))` throws a SecurityException if the app lacks a read permission for ANY requested record type — always filter `recordTypes` against `getGrantedPermissions()` before requesting a token.
- Without `PERMISSION_READ_HEALTH_DATA_HISTORY`, reads silently return no data older than 30 days (no error). Granting it requires re-launching the Health Connect permission prompt after the app started requesting it.

**Measurement write facade + daily-aggregate cache:**
- ALL measurement row writes MUST route through `$lib/db/measurement-writes.ts`
  (`create/upsert/update/delete/restoreMeasurements`) — never `db.measurement.put/delete`
  directly. The four write sites are: `mutate.ts` (crud + command optimistic rows),
  `sync-pull.ts`, `health-sync.svelte.ts` ingest, `export-import.ts` import.
- The facade maintains `metric_daily_stats` (`[metric_code+day]`, `{count,sum}` over
  non-deleted numeric rows) atomically with each write. Trend charts
  (`fetchTrend`) read per-day means from it — never scan raw windows of
  high-volume metrics. See `docs/adr/013-metric-daily-aggregate-cache.md`.
- Dexie's `between()` upper bound is unreliable for composite keys (drops the upper
  day): day-range reads use `aboveOrEqual(...)` + a JS `day <= toDay` filter.
- Every `useQuery` that reads external Svelte state (range/date/page/route params/
  another query's result) MUST pass a deps getter as the second argument, or the
  live query never re-runs when that input changes.

### Local Mode (server-optional)

Salus supports an additive **Local Mode** (`localMode` flag, `SELF_USER_ID='self'`):
a device profile (display name, no password) bypasses the auth gate and works
fully offline; the outbox is retained and flushed once a server is connected
("Connect server" promotes local data, and the server re-derives achievements).
Server-only features (sharing/federation, community, coach-LLM, admin) are
hidden via `SERVER_ONLY_PATH_PREFIXES`. See `docs/adr/004-local-mode.md`.

### Color & theme system

Colors fall into three kinds: semantic tokens (CSS `--color-*`), categorical
entity colors (resolved via `resolveColor`), and data-viz scales
(`$lib/theme/scales.ts`). A single theme controller (`$stores/theme.svelte`)
orchestrates mode (light/dark/system), colorblind, and accent (hue-driven
`--accent-hue`). Custom themes are scoped to accent + presets; arbitrary token
editing is excluded to protect the colorblind/contrast guarantees. See
`docs/adr/005-color-system.md`.

## Commands

```bash
# Enter dev shell
nix develop
```

Run `just --list` to see all available commands. Key recipes:

| Command | What it does |
|---|---|
| `just dev-backend` | Backend dev server (port 8000) |
| `just dev-frontend` | Frontend dev server (port 5173 → proxy to 8000) |
| `just test-backend` | Run backend tests (pytest) |
| `just test-frontend` | Run frontend tests (vitest) |
| `just lint-backend` | Lint Python (ruff) |
| `just lint-frontend` | Lint frontend (prettier + eslint) |
| `just typecheck-backend` | Type-check Python (pyright) |
| `just typecheck-frontend` | Type-check frontend (svelte-check) |
| `just format-frontend` | Auto-format frontend (prettier) |
| `just build-frontend` | Production build frontend |
| `just install-frontend` | Install frontend dependencies |
| `just sync-backend` | Sync Python dependencies (uv sync) |
| `just build-apk` | Build APK: build frontend → `cap sync android` (copies bundle into Android assets) → `assembleDebug` |
| `just install-apk` | `build-apk` + `adb install -r` on the connected device |
| `just check` | Full pre-commit: lint + typecheck + test (backend + frontend) |

**APK builds MUST go through `just build-apk` / `just install-apk`.** Never run
`npm run build` + `./gradlew assembleDebug` manually — that skips the Capacitor
asset copy (`cap sync`), so the APK silently ships the stale frontend bundle.

## Git workflow

```
main     ← Production mirror (deployable)
develop  ← Integration branch
feat/*   ← Feature branches
fix/*    ← Bug fix branches
```

**Conventional Commits**: `feat:`, `fix:`, `chore:`, `refactor:`, `test:`

## Config

| Setting | Default | Env var |
|---|---|---|
| `app_name` | `"salus"` | `SALUS_APP_NAME` |
| `database_url` | `"sqlite:///salus.db"` | `SALUS_DATABASE_URL` |
| `api_token` | `"s3ns0r-h34lth-t0k3n-2026"` | `SALUS_API_TOKEN` |
| `jwt_secret_key` | `"change-me-in-production-salus-2026"` | `SALUS_JWT_SECRET_KEY` |
| `jwt_algorithm` | `"HS256"` | `SALUS_JWT_ALGORITHM` |
| `jwt_expire_minutes` | `1440` (24h) | `SALUS_JWT_EXPIRE_MINUTES` |
| `google_client_id` | `None` | `SALUS_GOOGLE_CLIENT_ID` |
| `google_client_secret` | `None` | `SALUS_GOOGLE_CLIENT_SECRET` |
| `github_client_id` | `None` | `SALUS_GITHUB_CLIENT_ID` |
| `github_client_secret` | `None` | `SALUS_GITHUB_CLIENT_SECRET` |
| `oidc_issuer_url` | `None` | `SALUS_OIDC_ISSUER_URL` |
| `oidc_client_id` | `None` | `SALUS_OIDC_CLIENT_ID` |
| `oidc_client_secret` | `None` | `SALUS_OIDC_CLIENT_SECRET` |
| `oauth_redirect_base` | `"http://localhost:8000"` | `SALUS_OAUTH_REDIRECT_BASE` |
