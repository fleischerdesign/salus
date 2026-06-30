# AGENTS.md — salus

Health data tracker. FastAPI + Jinja2 + HTMX + SQLite + raw sqlite3 ingestion pipeline.
This file is written for LLM agents. Follow these rules exactly.

## Stack

| Concern | Choice |
|---|---|
| Web framework | FastAPI |
| Templates | Jinja2 via `starlette.templating.Jinja2Templates` (NOT `fastapi.templating`) |
| Interactivity | HTMX 2.x (loaded via CDN in `base.html`) |
| ORM layer | SQLModel for `metric_type`, `entry`, `user`, `user_identity`; raw sqlite3 for `health_records` ingestion |
| Database files | `salus.db` (SQLModel engine), `health.db` (separate raw sqlite3) |
| Package manager | uv via `pyproject.toml` |
| Dev environment | Nix flake (`nix develop`) providing python313, uv, ruff, pyright |
| Password hashing | `bcrypt` directly (NOT passlib — incompatible with bcrypt 5.x on Python 3.13) |
| JWT | `python-jose[cryptography]` via `JwtService` in `services/jwt.py` |
| OAuth/OIDC | `authlib` via `OidcAuthProvider` in `services/auth/providers.py` |
| LDAP | `ldap3` via `LdapAuthProvider` in `services/auth/providers.py` |
| Lint / Format | ruff (`uv run ruff check src/`) |
| Type check | pyright (`uv run pyright src/`) |

## Project structure

```
src/salus/
├── models/          ← Dataclasses + SQLModel tables (DB structure)
├── schemas/         ← Pydantic API request/response models (API contract)
├── repositories/    ← Data access — Repository[T] base for SQLModel, raw sqlite3 class for health
├── services/        ← Business logic — receives repos via constructor injection
├── routers/         ← FastAPI route handlers — THIN: parse input, call service, return template/redirect
├── templates/       ← Jinja2 (base.html, pages/, components/)
├── static/          ← CSS
├── config.py        ← pydantic-settings singleton
├── database.py      ← SQLModel engine + get_session generator
├── dependencies.py  ← ALL FastAPI Depends factory functions live here
├── exceptions.py    ← NotFoundError(message), ConflictError(message)
└── main.py          ← App factory, lifespan, CORS, router mounting, exception handlers
```

### Directory purposes (strict)

| Directory | Contains | Does NOT contain |
|---|---|---|
| `models/` | Dataclasses, SQLModel `table=True` classes | API schemas, request/response DTOs |
| `schemas/` | Pydantic `BaseModel` for request/response | DB models, dataclasses, internal DTOs |
| `repositories/` | Classes that wrap data access (SQLModel Session or raw sqlite3) | Business logic, validation |
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

    def get(self, id: int) -> MetricType:
        ...

# ❌ WRONG — violates DIP, untestable
class MetricTypeService:
    def __init__(self, session: Session):
        self.repo = MetricTypeRepository(session)
```

### 2. Wiring lives ONLY in dependencies.py
All `Depends` factory functions go in `dependencies.py`. Routers import them from there.
NEVER construct a repo or service in a router function body.

```python
# ✅ CORRECT — in dependencies.py
def get_metric_type_service(
    repo: MetricTypeRepository = Depends(get_metric_type_repo),
) -> MetricTypeService:
    return MetricTypeService(repo)

# ✅ CORRECT — in router
@router.get("")
async def list_metrics(
    request: Request,
    service: MetricTypeService = Depends(get_metric_type_service),
):
    ...

# ❌ WRONG — constructing in router
async def list_metrics(request: Request, session: Session = Depends(get_session)):
    repo = MetricTypeRepository(session)
    service = MetricTypeService(repo)
    ...
```

### 3. Routers are THIN
Router functions do: parse input → call service → return template/redirect.
No business logic. No raw SQL. No data transformation beyond simple dict unpacking.

### 4. health_records table is RAW SQLITE3 ONLY
The `health_records` table lives in a SEPARATE database (`health.db`) managed by `HealthRecordRepository` using raw `sqlite3`. It is NOT part of `SQLModel.metadata`. It does NOT use the SQLModel engine.

NEVER use SQLModel or `Session` to access `health_records`.
NEVER register `health_records` with `SQLModel.metadata`.
The `HealthRecord` and `ParsedRecord` classes in `models/health_record.py` are plain `@dataclass`, NOT SQLModel tables.

### 5. TemplateResponse signature
The Starlette `Jinja2Templates.TemplateResponse` requires `request` as the FIRST positional argument:

```python
# ✅ CORRECT
return request.app.state.templates.TemplateResponse(
    request,               # ← required first arg
    "pages/dashboard.html",
    {"metrics": metrics},
)

# ❌ WRONG — skips request, context dict becomes template name
return request.app.state.templates.TemplateResponse(
    "pages/dashboard.html",
    {"request": request, "metrics": metrics},  # breaks Jinja2 cache
)
```

Jinja2 context automatically includes `{{ request }}` — do NOT pass it manually in the context dict.

### 6. Cross-module relationship annotations

Models that reference types from other model files must use **string forward references** on
the *outer* annotation so that Python's runtime type evaluation does not resolve the name
before SQLAlchemy has configured the registry.  Combine this with a `TYPE_CHECKING` guard
so that pyright sees the real types during static analysis — **no `# type: ignore` needed**.

```python
from __future__ import annotations  # ← PROHIBITED in model files — breaks mapper
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class MetricType(SQLModel, table=True):
    user: "User" = Relationship(back_populates="metric_types")
    entries: list["Entry"] = Relationship(back_populates="metric_type")
```

Rules:
- Each model file that references a type from *another* model file gets its own `if TYPE_CHECKING:` block.
- The annotation itself remains a string literal or a `list["Type"]` generic — Python never resolves it at class-body time.
- NEVER use `from __future__ import annotations` in ``models/*.py`` — it turns `list[MetricType]` into a string that SQLAlchemy's mapper cannot decode.

### 7. Narrowing ``int | None`` from SQLModel pk fields

SQLModel declares primary-key fields as ``int | None`` because they are absent before
the first INSERT.  After a successful `Repository.create()` (which calls `session.commit()` /
`session.refresh()`), the id is **always** populated.  Use ``uid(user)`` from
``services/_helpers.py`` to narrow the type instead of sprinkling ``# type: ignore[arg-type]``:

```python
from salus.services._helpers import uid

# ✅  pyright-satisfied, self-documenting
service.create(data, user_id=uid(current_user))
```

The helper raises ``ValueError`` if the id is ``None``, which serves as an explicit
debugging aid if a pre-persist object leaks through.

### 8. Authentication architecture (Strategy Pattern)
- `LocalAuthProvider` — bcrypt password verification
- `LdapAuthProvider` — LDAP bind via `ldap3`
- `OidcAuthProvider` — OAuth2/OIDC via `authlib` (Google, GitHub, generic OIDC)

`AuthService` (in `services/auth/service.py`) is the orchestrator — receives providers via constructor. `JwtService` (in `services/jwt.py`) handles token creation/verification. Password hashing is `bcrypt` directly (NOT passlib).

Auth flow:
```
router → AuthService → Provider → UserService → UserRepository
                  ↓
            JwtService → JWT token → HttpOnly cookie (salus_session)
                  ↓
       get_current_user (dependencies.py) → verify cookie → User
```

### 9. JWT cookie name

The auth cookie is `salus_session` (defined as `TOKEN_COOKIE_NAME` in `dependencies.py`). Always use the constant, never hardcode the string.

### 10. SQLite engine configuration
The SQLAlchemy engine for SQLite MUST include `connect_args={"check_same_thread": False}`.
If you create a new engine (e.g. for tests), use `poolclass=StaticPool` for in-memory databases.

```python
# Production
engine = create_engine("sqlite:///salus.db", connect_args={"check_same_thread": False})

# Test
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
```

### 11. Absolute imports only
Always use absolute imports starting from `salus.`. Never use relative imports (`from .models import ...`).

## Adding a new entity (checklist)

When adding a new domain entity (e.g. `Goal`, `Tag`), create all of these:

1. `models/<name>.py` — `@dataclass` or `SQLModel(table=True)` class
2. `schemas/<name>.py` or add to `schemas/__init__.py` — Pydantic `BaseModel` for Create/Response
3. `repositories/<name>.py` — class extending `Repository[T]` (SQLModel) or standalone (raw sqlite3)
4. `services/<name>.py` — business logic class, receives repo via `__init__`
5. `routers/<name>.py` — `APIRouter` with route functions
6. `tests/test_<name>.py` — pytest tests
7. `dependencies.py` — add `get_<name>_repo()` and `get_<name>_service()` factories
8. `main.py` — `app.include_router(<name>.router)`

## Database separation

| Database | Engine | Tables | Access pattern |
|---|---|---|---|
| `salus.db` | SQLModel in `database.py` | `metric_type`, `entry`, future CRUD tables | SQLModel Session via `get_session()` → Repository |
| `health.db` | raw sqlite3 in `HealthRecordRepository` | `health_records` | `sqlite3.connect()` direct, upsert + nutrition cleanup |

## Webhook ingestion flow

```
POST /webhook (Bearer token)
  → verify_webhook_token (dependencies.py)
  → HealthIngestionService.parse(payload) 
    → FlexiblePayloadParser.parse(payload)
      → HealthConnectWebhookParser  (format: top-level keys with arrays)
      → FlatArrayParser             (format: array of record objects)
      → recurses into records/data wrappers
  → HealthRecordRepository.upsert_many(parsed_records)
    → Nutrition cleanup (delete same day + meal_name)
    → INSERT ON CONFLICT(id) DO UPDATE
  → return {"status": "ok", "inserted": N, "duplicates": N}
```

## Parser architecture

`RecordParser` is a Protocol in `services/parser.py`. Two implementations exist:

| Parser | Input format |
|---|---|
| `HealthConnectWebhookParser` | Dict with data-type keys → arrays of records |
| `FlatArrayParser` | List of record dicts with id/type/startTime/value fields |

`FlexiblePayloadParser` is the orchestrator — it auto-detects the format and delegates.
To add a new format: implement `RecordParser`, add detection logic in `FlexiblePayloadParser.parse()`.

Payload auto-detection order:
1. List → `FlatArrayParser`
2. Dict with data-type arrays → `HealthConnectWebhookParser`
3. Dict with `"records"` key → recurse
4. Dict with `"data"` key → recurse
5. Dict with `"type"`/`"dataType"`/`"id"` → wrap in list → `FlatArrayParser`
6. Otherwise → `ValueError`

## Config

All config lives in `config.py` via `pydantic-settings.BaseSettings` with `SALUS_` env prefix.

| Setting | Default | Env var |
|---|---|---|
| `app_name` | `"salus"` | `SALUS_APP_NAME` |
| `database_url` | `"sqlite:///salus.db"` | `SALUS_DATABASE_URL` |
| `hermes_home` | `"data"` (or `$HERMES_HOME`) | `SALUS_HERMES_HOME` |
| `api_token` | `"s3ns0r-h34lth-t0k3n-2026"` | `SALUS_API_TOKEN` |
| `health_db_path` | `hermes_home/health-bridge/health.db` (computed property) | — |

## Commands

```bash
# Enter dev shell
nix develop

# Run server
uv run uvicorn src.salus.main:app --reload

# Run tests
uv run pytest -v

# Lint
uv run ruff check src/

# Type check
uv run pyright src/

# Install after adding dependencies
uv sync
```

## Pre-commit checklist

Before considering work done, run:

```bash
uv run ruff check src/ && uv run pytest -v && uv run pyright src/
```

All three must pass with zero errors.
