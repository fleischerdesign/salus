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
- **System-Integration** — Every new feature MUST be designed with full integration into the existing ecosystem (sync, offline, dashboard, analytics, goals, insights, live-sync). Features are not islands — they interact. When designing a new domain, think about: (a) how it feeds the Measurement/metric system, (b) how the dashboard and analytics consume it, (c) how goals can reference it, (d) how insights can derive coaching from it, (e) how it syncs offline across devices.

## Stack

| Concern | Choice |
|---|---|
| Web framework | FastAPI (backend JSON API) |
| Frontend | SvelteKit (SPA mode, `adapter-static`) + TypeScript + Tailwind CSS |
| PWA / Offline | `@vite-pwa/sveltekit` (Workbox), Dexie.js (IndexedDB) |
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
- Service worker via `@vite-pwa/sveltekit`

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

## Adding a new entity (checklist)

1. `models/<name>.py` — SQLModel table
2. `schemas/<name>.py` — Pydantic Create/Response models
3. `repositories/<name>.py` — Repository class
4. `services/<name>.py` — Business logic service
5. `routers/api_<name>.py` — JSON API routes under `/api/v1/`
6. `dependencies.py` — Repository + Service factories
7. `main.py` — `app.include_router()`
8. Frontend: Svelte page component using the API
9. `tests/test_<name>.py` — pytest tests

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
| `just check` | Full pre-commit: lint + typecheck + test (backend + frontend) |

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
