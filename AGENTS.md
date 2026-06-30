# AGENTS.md — salus

Health data tracker. FastAPI + Jinja2 + HTMX + SQLite / PostgreSQL.
This file is written for LLM agents. Follow these rules exactly.

## Stack

| Concern | Choice |
|---|---|
| Web framework | FastAPI |
| Templates | Jinja2 via `starlette.templating.Jinja2Templates` (NOT `fastapi.templating`) |
| Interactivity | HTMX 2.x (loaded via CDN in `base.html`) |
| ORM layer | SQLModel for all tables (`metric_type`, `measurement`, `user`, `user_identity`, `goal`) |
| Database | `salus.db` (SQLite default) or PostgreSQL via `SALUS_DATABASE_URL` |
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
├── repositories/    ← Data access — Repository[T] base for SQLModel
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

### 4. TemplateResponse signature
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

### 5. Cross-module relationship annotations

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

### 6. Narrowing ``int | None`` from SQLModel pk fields

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

### 7. Authentication architecture (Strategy Pattern)
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

### 8. JWT cookie name

The auth cookie is `salus_session` (defined as `TOKEN_COOKIE_NAME` in `dependencies.py`). Always use the constant, never hardcode the string.

### 9. Database engine configuration

The engine is built in `database.py` via `_build_engine()` which detects the URL scheme:

```python
# SQLite — requires check_same_thread=False
engine = create_engine("sqlite:///salus.db", connect_args={"check_same_thread": False})

# PostgreSQL — no special connect_args needed
engine = create_engine("postgresql://user:pass@host/salus")

# Test
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
```

`SALUS_DATABASE_URL` accepts any scheme SQLAlchemy supports. `psycopg2-binary` is included for PostgreSQL.

### 10. Absolute imports only
Always use absolute imports starting from `salus.`. Never use relative imports (`from .models import ...`).

## Adding a new entity (checklist)

When adding a new domain entity (e.g. `Goal`, `Tag`), create all of these:

1. `models/<name>.py` — `@dataclass` or `SQLModel(table=True)` class
2. `schemas/<name>.py` or add to `schemas/__init__.py` — Pydantic `BaseModel` for Create/Response
3. `repositories/<name>.py` — class extending `Repository[T]` (SQLModel)
4. `services/<name>.py` — business logic class, receives repo via `__init__`
5. `routers/<name>.py` — `APIRouter` with route functions
6. `tests/test_<name>.py` — pytest tests
7. `dependencies.py` — add `get_<name>_repo()` and `get_<name>_service()` factories
8. `main.py` — `app.include_router(<name>.router)`

## Webhook ingestion flow

```
POST /webhook (Bearer token or X-API-Token header)
  → verify_webhook_token (dependencies.py)
  → WebhookIngestionService.ingest(payload)
    → FlexiblePayloadParser.parse(payload)
    → MetricTypeMappingService.resolve(data_type) → metric_type_id
    → MeasurementRepository.upsert_all(records)
      → dedup by external_id + source
  → return {"status": "ok", "inserted": N, "duplicates": N}
```

## Parser architecture

`RecordParser` is a Protocol in `services/parser.py`. Built-in implementations:

| Parser | Input format |
|---|---|
| `HealthConnectWebhookParser` | Dict with data-type keys → arrays of records |
| `FlatArrayParser` | List of record dicts with id/type/startTime/value fields |

Additional source-specific parsers live in `services/parsers/`:

| Parser | Source | File |
|---|---|---|
| `AppleHealthExportParser` | `apple_health` | `services/parsers/apple_health.py` |
| `GoogleFitParser` | `google_fit` | `services/parsers/google_fit.py` |
| `FitbitParser` | `fitbit` | `services/parsers/fitbit.py` |
| `OuraParser` | `oura` | `services/parsers/oura.py` |

`FlexiblePayloadParser` is the orchestrator — it auto-detects the format and delegates.
To add a new source: implement `RecordParser`, register in `FlexiblePayloadParser`.

Payload auto-detection order:
1. List → `FlatArrayParser`
2. Dict with data-type arrays → source-specific parsers, then `HealthConnectWebhookParser`
3. Dict with `"records"` key → recurse
4. Dict with `"data"` key → recurse
5. Dict with `"type"`/`"dataType"`/`"id"` → wrap in list → `FlatArrayParser`
6. Otherwise → `ValueError`

## Config

All config lives in `config.py` via `pydantic-settings.BaseSettings` with `SALUS_` env prefix.

| Setting | Default | Env var |
|---|---|---|---|
| `app_name` | `"salus"` | `SALUS_APP_NAME` |
| `database_url` | `"sqlite:///salus.db"` | `SALUS_DATABASE_URL` |
| `hermes_home` | `"data"` (or `$HERMES_HOME`) | `SALUS_HERMES_HOME` |
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
| `ldap_server_uri` | `None` | `SALUS_LDAP_SERVER_URI` |
| `ldap_base_dn` | `None` | `SALUS_LDAP_BASE_DN` |
| `ldap_user_dn_template` | `"uid={username},{base_dn}"` | `SALUS_LDAP_USER_DN_TEMPLATE` |
| `ldap_use_tls` | `False` | `SALUS_LDAP_USE_TLS` |

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

# Nix checks
nix flake check               # verify devShell + packages + modules
nix build .#default           # build the Python package
nix build .#dockerImage       # build the Docker image
docker load < result          # load into local Docker
```

## Git workflow

```
main     ← default branch, production mirror (always deployable)
develop  ← integration branch, all PRs target this
feat/*   ← feature branches off develop
fix/*    ← bug fix branches
chore/*  ← maintenance (deps, ci, etc.)
```

**Conventional Commits**: `feat:`, `fix:`, `chore:`, `refactor:`, `test:` — used by release-please for automatic SemVer.

**Merge flow**: PR → develop → CI (ruff + pyright + pytest) → merge → **auto merge-back** syncs main → develop.

**IMPORTANT**: Pushing to `main` triggers a release (release-please + Docker publish + Nix build). During active development, push **only to `develop`**. Only merge develop → main when you explicitly want a release.

## CI/CD

| Workflow | Trigger | File |
|---|---|---|
| CI | PR → main, develop | `.github/workflows/ci.yml` |
| Merge-Back | push → main | `.github/workflows/merge-back.yml` |
| Docker Publish | push → main | `.github/workflows/docker-publish.yml` |
| Release Please | push → main | `.github/workflows/release-please.yml` |
| Flake Update | weekly cron | `.github/workflows/update-flake.yml` |
| Dependabot | weekly | `.github/dependabot.yml` |

## Release process

Push to `main` with conventional commit → release-please creates/updates a release PR.
Merge it → Git tag + GitHub Release + CHANGELOG.md update.

Release-please uses the PAT stored in `RELEASE_PLEASE_TOKEN` repo secret.

## Deployment

### Docker

```bash
docker run -p 8000:8000 -v ./data:/data ghcr.io/fleischerdesign/salus:latest
```

Image is built via `dockerTools.buildLayeredImage` in `flake.nix`. Published to `ghcr.io/fleischerdesign/salus` on every push to main.

### NixOS module

```nix
{
  nixpkgs.overlays = [ inputs.salus.overlays.default ];
  imports = [ inputs.salus.nixosModules.default ];
  services.salus = {
    enable = true;
    port = 8200;
    databaseUrl = "sqlite:///var/lib/salus/salus.db";
    openFirewall = true;
  };
}
```

Also available: `nixosModules.container` for systemd-nspawn isolation.

## Pre-commit checklist

Before considering work done, run:

```bash
uv run ruff check src/ && uv run pytest -v && uv run pyright src/
```

All three must pass with zero errors.
