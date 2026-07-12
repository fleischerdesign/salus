# Changelog

## Unreleased

### Features

* **sync refactor** — comprehensive sync system overhaul for security, completeness, idempotency, pagination, and reactivity
  * Delta sync with per-entity security filtering (`user_scoped`, `shared_nullable`, `relational`, `global`, `append_only`, `special`)
  * Cursor-based paginated full sync (`GET /api/v1/sync?cursor=<base64>`)
  * WritePipeline deduplication via `sync_push_log` table (24h TTL)
  * UoW auto-commit (Generator `try/yield/except/rollback/else/commit`)
  * Entity meta single source of truth (`entity_meta.py` derives all registries + validators)
  * Dynamic entity discovery (`GET /api/v1/sync/entities` + frontend `entity-info.ts`)
  * Sync protocol versioning (`X-Salus-Sync-Version: 1`)
  * Conflict resolution with field-level merge (`ConflictDialog` with per-field radio buttons)
* **live sync via SSE** — real-time cross-device sync without polling
  * `EventBus` ABC + `InMemoryEventBus` (asyncio `Queue`, maxsize 32)
  * SSE endpoint (`GET /api/v1/sync/events`) with per-user subscription
  * Frontend `EventSource` manager with 2s debounce (`live-events.ts`)
  * Auto-connects after initial `syncAll()`, disconnects on session expiry

## 0.1.0 (2026-06-30)


### Features

* admin panel with user management, config, drill-down, storage stats ([f61b962](https://github.com/fleischerdesign/salus/commit/f61b962dd1ab8a9013ce07b89a89a28505cdc7d7))
* dashboard day navigator, dark mode, delta indicators, passlib removed ([5445f1c](https://github.com/fleischerdesign/salus/commit/5445f1c11f0433b79ab444419406ae64fc4f957c))
* devops, git flow, ci/cd, nix packaging ([7a38697](https://github.com/fleischerdesign/salus/commit/7a386979c93a02aa175c23418a4f94640a0c8fe3))
* devops, git flow, ci/cd, nix packaging, PostgreSQL support ([4fa4a29](https://github.com/fleischerdesign/salus/commit/4fa4a29fd71d10096f39cc4409397a1d93258483))
* webhook user-scoping, dynamic dashboard, onboarding wizard, design audit ([1dbff2b](https://github.com/fleischerdesign/salus/commit/1dbff2b0c75c7b61b7fc993cbedef897a71f63a5))


### Bug Fixes

* add bcrypt dependency and fix CI tool invocation ([569bc4d](https://github.com/fleischerdesign/salus/commit/569bc4d2d32dbc8528656f5add5d52bcb5220710))
* use PAT for release-please, inline merge-back, fix docker var ([b5ba997](https://github.com/fleischerdesign/salus/commit/b5ba997f91cd7ab8e257f99707ea1d79a6257cc2))
