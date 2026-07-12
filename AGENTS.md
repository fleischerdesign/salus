# AGENTS.md — salus

Health data tracker. FastAPI (backend) + SvelteKit SPA (frontend) + SQLite / PostgreSQL.
This file is written for LLM agents. Follow these rules exactly.

## Stack

| Concern | Choice |
|---|---|
| Web framework | FastAPI (backend JSON API) |
| Frontend | SvelteKit (SPA mode, `adapter-static`) + TypeScript + Tailwind CSS |
| PWA / Offline | `@vite-pwa/sveltekit` (Workbox), Dexie.js (IndexedDB) |
| ORM layer | SQLModel for all tables (`metric_type`, `measurement`, `user`, `user_identity`, `goal`) |
| Database | `salus.db` (SQLite default) or PostgreSQL via `SALUS_DATABASE_URL` |
| Package manager (Python) | uv via `pyproject.toml` |
| Package manager (JS) | npm via `frontend/package.json` |
| Dev environment | Nix flake (`nix develop`) providing python313, uv, ruff, pyright, nodejs_22 |
| Password hashing | `bcrypt` directly (NOT passlib — incompatible with bcrypt 5.x on Python 3.13) |
| JWT | `python-jose[cryptography]` via `JwtService` in `services/jwt.py` |
| OAuth/OIDC | `authlib` via `OidcAuthProvider` in `services/auth/providers.py` |
| LDAP | `ldap3` via `LdapAuthProvider` in `services/auth/providers.py` |
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
├── services/        ← Business logic — receives repos via constructor injection
├── routers/         ← FastAPI route handlers — THIN: parse input, call service, return JSON
│   ├── api.py           ← Core REST API (/api/v1/metrics, /api/v1/entries)
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
│   ├── api.py           ← Legacy API endpoints (metrics, entries, health)
│   ├── webhook.py       ← Webhook ingestion
│   └── export.py        ← CSV/JSON export download
├── config.py        ← pydantic-settings singleton
├── database.py      ← SQLModel engine + get_session generator
├── dependencies.py  ← ALL FastAPI Depends factory functions live here
├── exceptions.py    ← NotFoundError(message), ConflictError(message)
└── main.py          ← App factory, lifespan, CORS, router mounting, SPA mount

frontend/
├── src/
│   ├── app.html        ← HTML shell
│   ├── app.css         ← Design tokens + Tailwind
│   ├── lib/
│   │   ├── api/        ← openapi-fetch typed client
│   │   ├── components/ ← Svelte components (ui/, dashboard/, forms/, layout/)
│   │   ├── stores/     ← Svelte 5 runes ($state stores)
│   │   └── utils/      ← Utilities
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

### 1. Service constructor injection (DIP)
Services MUST receive their dependencies via constructor. NEVER instantiate a repo inside a service.

```python
# ✅ CORRECT
class MetricTypeService:
    def __init__(self, repo: MetricTypeRepository) -> None:
        self.repo = repo

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
- Material Symbols icon font for icons: `<span class="material-symbols-outlined">icon_name</span>`
- Design tokens (colors, radii, shadows) are Tailwind theme variables matching the existing design system

### 12. Frontend API calls
All API calls go through `$lib/api/client.ts` which provides a typed `openapi-fetch` client.
Auth token is automatically added via interceptor.

### 13. SvelteKit SPA mode
- `adapter-static` with `fallback: 'index.html'`
- `ssr = false` in `+layout.ts`
- Routes are purely client-side (no server-side rendering)
- Service worker via `@vite-pwa/sveltekit`

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

# Backend
uv run uvicorn src.salus.main:app --reload
uv run pytest -v
uv run ruff check src/
uv run pyright src/

# Frontend
cd frontend
npm install
npm run dev          # Dev server with HMR + API proxy
npm run build        # Production build
npm run check        # Type-check Svelte components
npm run lint         # Lint + format check
npm run format       # Auto-format
npm run test         # Vitest

# Full pre-commit check
uv run ruff check src/ && uv run pytest -v && uv run pyright src/
cd frontend && npm run lint && npm run check
```

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
