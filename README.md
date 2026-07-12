# salus

**Personal Health Data Tracker: self-hosted, privacy-first, offline-capable.**

[![CI](https://github.com/fleischerdesign/salus/actions/workflows/ci.yml/badge.svg)](https://github.com/fleischerdesign/salus/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/ghcr.io-fleischerdesign%2Fsalus-086dd7)](https://github.com/fleischerdesign/salus/pkgs/container/salus)
[![Nix Flake](https://img.shields.io/badge/nix-flake-blue.svg)](https://nixos.wiki/wiki/Flakes)

---

salus gives you a private, self-hosted dashboard for your health data. It ingests metrics from wearables and health platforms via a simple webhook API, displays them on a clean SvelteKit SPA dashboard, and tracks your goals over time.

It runs anywhere: a Docker container, or a native NixOS module. Your data stays on your machine.

## Features

- **Dashboard:** Configurable widget grid with day navigation. Steps, heart rate, sleep, weight, exercise, nutrition, and more.
- **Webhook Ingestion:** `POST /webhook` with Bearer token or API key. Auto-detects Health Connect, flat arrays, and source-specific formats (Apple Health, Google Fit, Fitbit, Oura). Deduplicates by external ID.
- **Manual Entry:** Log weight, blood pressure, or any custom metric manually through the UI.
- **Goal Tracking:** Set daily, weekly, or one-time targets with directional goals (increase/decrease). Visual progress bars and streak indicators.
- **Analytics:** Per-metric detail pages with trend charts and statistics.
- **Workouts:** Exercise catalog, training plans, session logging with RPE and 1RM estimation. Autoregulation based on recovery metrics.
- **Coach:** Circadian rhythm advisor using NOAA solar calculations, AI-powered health chat with local LLM support.
- **Community:** Leaderboards, activity feed, federated instance sharing.
- **Authentication:** Local bcrypt accounts, OAuth2/OIDC (Google, GitHub, generic), and LDAP. JWT with Bearer tokens or HTTP-only cookies.
- **Multi-Tenant:** Full user isolation. Every record, metric, widget, and goal is user-scoped.
- **Offline-First:** SvelteKit SPA with service worker precaching. IndexedDB (Dexie.js) for local-first data. Full offline dashboard, entry logging, and workout tracking.
- **Live Sync:** SSE-based real-time cross-device sync. Delta-first pull with cursor-paginated full sync fallback. Conflict resolution with field-level merge.
- **Dark Mode:** System, light, and dark themes via CSS custom properties. Persisted per user.
- **Admin Panel:** User management, system configuration, API token administration, storage statistics.
- **Onboarding Wizard:** Guided setup for new users: first metric, first entry, first goal, webhook token generation.

## Tech Stack

| Concern | Choice |
|---|---|
| Backend Framework | FastAPI |
| Frontend Framework | SvelteKit (SPA mode, `adapter-static`) |
| UI Styling | Tailwind CSS v4 |
| Frontend Language | TypeScript |
| PWA / Offline | Custom service worker, Dexie.js (IndexedDB) |
| ORM | SQLModel |
| Database | SQLite (default) or PostgreSQL |
| Package Manager (Python) | uv via `pyproject.toml` |
| Package Manager (JS) | npm via `frontend/package.json` |
| Dev Environment | Nix flake (`nix develop`) |
| Lint / Format (Python) | ruff |
| Type Check (Python) | pyright |
| Lint / Format (Frontend) | prettier + eslint |
| Type Check (Frontend) | svelte-check |
| Test (Python) | pytest |
| Test (Frontend) | vitest |
| Auth | bcrypt + python-jose (JWT) + authlib (OIDC) + ldap3 |
| CI/CD | GitHub Actions |
| Container | Docker (Nix-built via `dockerTools`) |

## Quick Start

### Nix (recommended for development)

```bash
git clone https://github.com/fleischerdesign/salus.git
cd salus

nix develop          # enter dev shell (python, uv, ruff, pyright, node)
uv sync              # install Python dependencies
cd frontend && npm install   # install JS dependencies
```

Start the backend (terminal 1):

```bash
uv run uvicorn src.salus.main:app --reload
```

Start the frontend dev server (terminal 2):

```bash
cd frontend && npm run dev
```

Open `http://localhost:5173`. Register an account and you'll be guided through onboarding.

The frontend dev server proxies `/api` requests to `localhost:8000`.

### Docker

```bash
docker run -p 8000:8000 -v ./data:/data ghcr.io/fleischerdesign/salus:latest
```

The `/data` volume stores your SQLite database. Set `SALUS_DATABASE_URL` to use PostgreSQL instead.

## Configuration

All settings are environment variables prefixed with `SALUS_`.

| Variable | Default | Purpose |
|---|---|---|
| `SALUS_DATABASE_URL` | `sqlite:///salus.db` | Database connection. Use `postgresql://...` for PostgreSQL. |
| `SALUS_JWT_SECRET_KEY` | `change-me-in-production-salus-2026` | JWT signing secret. **Change this in production.** |
| `SALUS_API_TOKEN` | `s3ns0r-h34lth-t0k3n-2026` | Global webhook API token. Use scoped `sls_*` tokens per device for better security. |
| `SALUS_JWT_ALGORITHM` | `HS256` | JWT signing algorithm. |
| `SALUS_JWT_EXPIRE_MINUTES` | `1440` | Session duration (24 hours). |
| `SALUS_OAUTH_REDIRECT_BASE` | `http://localhost:8000` | Base URL for OAuth redirects. |
| `SALUS_GOOGLE_CLIENT_ID` | - | Google OAuth client ID (optional). |
| `SALUS_GOOGLE_CLIENT_SECRET` | - | Google OAuth client secret (optional). |
| `SALUS_GITHUB_CLIENT_ID` | - | GitHub OAuth client ID (optional). |
| `SALUS_GITHUB_CLIENT_SECRET` | - | GitHub OAuth client secret (optional). |
| `SALUS_OIDC_ISSUER_URL` | - | Generic OIDC provider URL (optional). |
| `SALUS_LDAP_SERVER_URI` | - | LDAP server URI (optional). |
| `SALUS_LDAP_BASE_DN` | - | LDAP base DN (optional). |
| `LOG_LEVEL` | `INFO` | Python logging level. Set to `DEBUG` for verbose webhook logging. |

See `src/salus/config.py` for the full list.

## Development

### Prerequisites

- [Nix](https://nixos.org) with flakes enabled
- Or: Python 3.13+, [uv](https://docs.astral.sh/uv/), and Node.js 22+

### Commands

```bash
# Backend
uv run uvicorn src.salus.main:app --reload   # dev server
uv run pytest -v                              # 260 tests
uv run ruff check src/                        # lint
uv run pyright src/                           # type check

# Frontend
cd frontend
npm run dev           # dev server with HMR + API proxy
npm run build         # production build
npm run check         # type-check Svelte components
npm run lint          # lint + format check
npm run format        # auto-format
npm run test          # vitest (20 tests)

# Full pre-commit check
uv run ruff check src/ && uv run pytest -v && uv run pyright src/
cd frontend && npm run lint && npm run check
```

### Git Workflow

```
main     ← production mirror (push here = release)
develop  ← integration branch (all PRs target this)
feat/*   ← feature branches
fix/*    ← bug fixes
chore/*  ← maintenance
```

Conventional Commits (`feat:`, `fix:`, `chore:`, `refactor:`, `test:`) drive automated SemVer via release-please. During active development, push only to `develop`. Merging to `main` triggers a release.

## Project Structure

```
src/salus/
├── models/          ← SQLModel tables
├── schemas/         ← Pydantic request/response DTOs
├── repositories/    ← Data access layer (Repository[T] base)
│   └── entity_meta.py   ← Entity registry (single source of truth)
├── services/        ← Business logic (constructor injection)
│   ├── analytics/   ← Steps, HR, sleep, nutrition, weight analysis
│   ├── auth/        ← Local, LDAP, OIDC providers
│   └── parsers/     ← Apple Health, Google Fit, Fitbit, Oura
├── routers/         ← FastAPI route handlers (thin, JSON-only)
├── config.py        ← pydantic-settings singleton
├── database.py      ← Engine builder (SQLite/PostgreSQL)
├── dependencies.py  ← All Depends() factories
└── main.py          ← App factory, lifespan, CORS, router mounting, SPA mount

frontend/
├── src/
│   ├── app.html     ← HTML shell
│   ├── app.css      ← Design tokens (colors, typography, shadows, animation) + Tailwind
│   ├── lib/
│   │   ├── api/     ← Typed openapi-fetch client
│   │   ├── components/ ← Svelte components (ui/, dashboard/, forms/, layout/)
│   │   ├── db/      ← Dexie database + sync engine + live events
│   │   ├── stores/  ← Svelte 5 runes ($state stores)
│   │   └── utils/   ← Utilities (diff, formatting)
│   └── routes/      ← File-based routing
├── static/          ← PWA icons, manifest, offline fallback
├── svelte.config.js
├── vite.config.ts
└── package.json

tests/               ← pytest (Backend)
frontend/tests/      ← vitest (Frontend)
```

### Architecture Principles

- **Dependency Inversion:** Services receive repositories via constructor injection. All wiring lives in `dependencies.py`.
- **Thin Routers:** Route handlers parse input, call a service, return JSON. No business logic in routers.
- **Two Write Paths (Frontend):** `mutate()` for entity CRUD via sync push, `mutateDomain()` for domain commands via dedicated HTTP endpoints.
- **Sync Architecture:** Delta-first pull (7-day window), cursor-paginated full sync fallback. SSE live sync with client-side debounce.
- **Offline-First:** Dexie.js IndexedDB as primary data store. Service worker caches all assets including SPA shell for full offline operation.
- **Auth Flow:** SPA → `POST /api/v1/auth/login` → `AuthService` → Provider → JWT token. Token stored in localStorage, sent as `Authorization: Bearer`.

See `AGENTS.md` for the complete architecture reference.

## Deployment

### Docker

Images are built with Nix (`dockerTools.buildLayeredImage`) and published to GitHub Container Registry on every push to `main`.

```bash
docker run -p 8000:8000 -v ./data:/data ghcr.io/fleischerdesign/salus:latest
```

Environment variables can be passed with `-e`:

```bash
docker run -p 8000:8000 \
  -v ./data:/data \
  -e SALUS_JWT_SECRET_KEY=my-secret-key \
  -e SALUS_DATABASE_URL=sqlite:///data/salus.db \
  ghcr.io/fleischerdesign/salus:latest
```

### NixOS

Add the flake input and enable the service:

```nix
{
  inputs.salus.url = "github:fleischerdesign/salus";

  outputs = { self, nixpkgs, salus, ... }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      modules = [
        { nixpkgs.overlays = [ salus.overlays.default ]; }
        salus.nixosModules.default
        {
          services.salus = {
            enable = true;
            port = 8200;
            databaseUrl = "sqlite:///var/lib/salus/salus.db";
            openFirewall = true;
          };
        }
      ];
    };
  };
}
```

A systemd-nspawn container module is also available:

```nix
{
  imports = [ salus.nixosModules.container ];
  containers.salus = {
    enable = true;
    port = 8200;
  };
}
```

## Webhook Integration

salus ingests health data via `POST /webhook`. Authenticate with an `X-API-Token` or `Authorization: Bearer` header.

### Health Connect Example

```bash
curl -X POST https://your-instance/webhook \
  -H "X-API-Token: s3ns0r-h34lth-t0k3n-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "steps": [{"count": 8432, "start_time": "2026-06-30T06:00:00", "end_time": "2026-06-30T21:00:00"}],
    "heart_rate": [{"bpm": 72, "start_time": "2026-06-30T08:00:00"}],
    "sleep": [{"start_time": "2026-06-29T23:15:00", "end_time": "2026-06-30T06:45:00", "stages": {"light": 240, "deep": 90, "rem": 105}}]
  }'
```

Response:

```json
{"status": "ok", "inserted": 3, "duplicates": 0}
```

### Supported Data Types

The parser auto-detects the payload format and maps known data types to metric widgets:

| Payload Key | Widget | Unit |
|---|---|---|
| `steps` | Steps | steps |
| `heart_rate` | Heart Rate | bpm |
| `sleep` | Sleep | hours |
| `weight` | Weight | kg |
| `exercise` | Exercise | minutes |
| `nutrition` | Nutrition | kcal |
| `blood_pressure` | Blood Pressure | mmHg |
| `blood_glucose` | Blood Glucose | mmol/L |
| `body_fat` | Body Fat | % |
| `water` | Water | L |
| `stress` | Stress | - |
| `readiness` | Readiness | - |

More data types are recognized and stored even if no default widget exists for them. Scoped `sls_*` API tokens with `ingest:write` scope can be generated per device in Settings → API Tokens.

## CI/CD

| Workflow | Trigger | Action |
|---|---|---|
| **CI** | PR → main, develop | Ruff → Pyright → Pytest |
| **Docker Publish** | push → main | Build + push to ghcr.io |
| **Release Please** | push → main | Automated SemVer + CHANGELOG |
| **Merge Back** | push → main | Auto-sync main → develop |
| **Flake Update** | weekly | Update `flake.lock` |
| **Dependabot** | weekly | Update GitHub Actions |

## License

MIT. See [LICENSE](LICENSE).

---

Built with [Nix](https://nixos.org), [FastAPI](https://fastapi.tiangolo.com), [SvelteKit](https://svelte.dev/docs/kit), [SQLModel](https://sqlmodel.tiangolo.com), and [Dexie.js](https://dexie.org). Health data belongs to you.
