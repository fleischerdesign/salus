# Salus Codebase Audit — SOLID, DRY, Clean Code & Academic Professionalism

> Refreshed 2026-07-12. Post-SPA migration: Jinja2/HTMX templates, inline CSS, and macros removed. Frontend is now SvelteKit SPA with Tailwind CSS. Audit covers `src/salus/` (backend only — ~55 service files, 19 routers, 12 models, 18 repos).
>
> Original audit: 2026-07-03 (~290 issues). SPA migration obsoleted ~140 template/HTMX/CSS issues. This refresh verifies remaining backend issues against current code, adds new ones discovered since.

---

## Executive Summary

| Metric | Count |
|---|---|
| **Total issues found** | **~150** |
| HIGH severity | ~55 |
| MEDIUM severity | ~50 |
| LOW severity | ~45 |
| Files with issues | 40+ |
| Quick wins (<1h to fix) | 25+ |

**Top structural problems:**
1. `SharingService` is a 1192-line God class mixing 6+ concerns (SRP)
2. 51 raw `session.exec()` calls across services and routers bypassing repository abstraction (DIP)
3. CORS `allow_origins=["*"]` + `allow_credentials=True` — broken cross-origin cookie auth (Security)
4. `PermissionError` (built-in) instead of `ForbiddenError` in 11 places — auth failures → 500 errors
5. 5x copy-paste of aggregation logic (DRY)
6. Repository base class uses `get_*` prefix for nullable returns — violates documented `get` vs `find` convention
7. No CSRF protection, no security headers (CSP/HSTS/X-Frame-Options), `Secure` flag missing on auth cookie
8. `routers/sharing.py` has 4 `sharing_svc.uow.*` accesses (thin-router violation)
9. `DashboardRepository.reorder()` N+1 commit problem
10. 3x `print()` statements in production code (`services/open_science.py`)

---

## Criteria Summary

| Principle | Grade | Verdict |
|---|---|---|
| **SRP** | D | God class (`sharing.py` 1192 lines), mixed domains (`models/sharing.py`, `routers/sharing.py`) |
| **OCP** | B- | Parser + Auth provider pattern is extensible; plugin system well-designed |
| **LSP/ISP** | C+ | `IUnitOfWork` exposes raw `session` leaking all repos; 15/18 repos skip interface declaration |
| **DIP** | C- | 51 raw session accesses, webhook route instantiates its own graph, onboarding uses raw Session |
| **DRY** | C+ | Aggregation logic 5x copied, retry-with-backoff 2x, parser guard clauses 4x, LLM provider construction 5x |
| **Clean Code** | B- | Good naming overall; some `print()` in prod, magic strings, `assert` for control flow |
| **Modularity** | C+ | Models/Services mix domains; leaderboard/federation lumped together in `routers/sharing.py` |
| **Extensibility** | B | Plugin system (parsers, hooks, widgets) is well-designed; fixed defaults block dynamic extension |
| **Naming** | C+ | `get_*`/`find_*` inconsistency across all repos; German hardcoded labels; mixed British/American spelling |
| **Security** | D | No CSP, no CSRF, no HSTS, no X-Frame-Options; `Secure` flag missing on auth cookie; CORS misconfigured |
| **API Design** | B- | Good OpenAPI base, but inconsistent error format, missing response_model on endpoints, unversioned routes |
| **Academic Quality** | B- | Good core architecture (DIP via `dependencies.py`); undermined by violations documented below |

---

## Issue Categories

### 1. GOD CLASS & SRP VIOLATIONS

#### 1.1 [HIGH] `SharingService` (1192 lines, 6+ concerns)
`src/salus/services/sharing.py`

| Concern | Lines (approx) | Should be |
|---|---|---|
| Handle utilities | ~29-54 | `HandleUtil` static class |
| Relationship CRUD | ~60-179 | `SharingRelationshipService` |
| Peer connection views | ~185-281 | same, or `PeerConnectionService` |
| Federation key management + signing/verify | ~429-671 | `FederationKeyService` + `HttpSignatureService` |
| WebFinger + remote endpoint resolution | ~673-720 | `FederationDiscoveryService` |
| Remote data fetch + caching + feed assembly | ~722-986 | `FederationDataResolver` + `FederationFeedService` |
| Push notification broadcasting | ~988-1192 | `PeerNotificationService` |

**Impact:** Cannot test federation key management independently. Adding a new remote protocol requires modifying 6 concerns. Grew by 150 lines since July audit.

#### 1.2 [HIGH] `DashboardWidgetService` (697 lines, 3 concerns)
`src/salus/services/dashboard_widget.py`

| Concern | Lines |
|---|---|
| Widget CRUD | 7 methods |
| Visualization building | 7 methods |
| Chart computation | 4 helper functions (candlestick 52 lines, pill chart 65 lines) |

Chart computation should be in `services/analytics/visualization.py`.

#### 1.3 [MED] `CircadianService` mixes solar calculator with profile management
`src/salus/services/circadian.py`

`calculate_solar_times()` (82 lines of pure-math NOAA solar calculation) is a distinct domain from profile CRUD. Extract to `SolarCalculator` utility.

#### 1.4 [HIGH] `models/sharing.py` mixes 3 unrelated domains
`src/salus/models/sharing.py`

`SharingRelationship` + `LeaderboardGroup`/`LeaderboardMember` + `FederatedMeasurementCache`/`FederatedAccessLog`. Split into `models/leaderboard.py` and `models/federation.py`.

#### 1.5 [HIGH] `routers/sharing.py` mixes 5 separate route groups
`src/salus/routers/sharing.py`

Feed + Leaderboard CRUD + Connection management + Federation API + WebFinger/Actor. Split into `routers/leaderboard.py` and `routers/federation.py`.

---

### 2. DIP VIOLATIONS — Raw Session Access (51 total)

#### 2.1 [HIGH] 12 raw `session.exec()` in `SharingService`
`src/salus/services/sharing.py`

Bypass `ISharingRelationshipRepository` interface. Should add methods like `find_active_for_metric()`, `find_by_token_hash()`, `find_remote_grantees()` to the repository.

#### 2.2 [HIGH] 3 raw `session.exec()` in `LeaderboardService`
`src/salus/services/leaderboard.py`

Raw queries for `SharingRelationship` and entities. Should use repo methods.

#### 2.3 [HIGH] 14 raw `session.exec()` in `services/workout/planner.py`
`src/salus/services/workout/planner.py`

`cast(SqlUnitOfWork, self.uow)` + raw `session.exec()` — direct DIP violation with type cast.

#### 2.4 [HIGH] 4 raw `session.exec()` in routers
`src/salus/routers/sharing.py`

In route handlers with raw `session.add()` and direct model imports.

#### 2.5 [HIGH] `webhook.py` instantiates entire service graph inline
`src/salus/routers/webhook.py`

`run_background_ingest()` constructs repos, parsers, services, and UoW directly. Completely bypasses DI.

#### 2.6 [HIGH] Onboarding route uses raw `Session`
`src/salus/routers/onboarding.py`

`session.add(current_user)` + `session.commit()` directly in route. Should delegate to `UserService`.

#### 2.7 [HIGH] 12 raw `session.exec()` in `services/portability.py`
`src/salus/services/portability.py`

GDPR portability service directly accesses session for data export queries.

#### 2.8 [MED] `api.py` accesses `measurement_svc.repo` directly
`src/salus/routers/api.py`

`measurement_svc.repo.find_all(...)` — pierces service abstraction to call repo method.

#### 2.9 [MED] `insight.py` accesses `service._uow` directly
`src/salus/routers/insight.py`

`service._uow.insights.list_by_user(...)` — double pierce.

#### 2.10 [MED] Admin routes access `backup_svc.provider` directly
`src/salus/routers/admin.py`

`backup_svc.provider.list_backups()` — should be wrapped by service method.

#### 2.11 [MED] `dependencies.py` accesses `api_token_svc._user_repo`
`src/salus/dependencies.py`

Private attribute access in dependency factory.

#### 2.12 [MED] `dependencies.py` runs raw SQL in `get_current_user_or_api`
`src/salus/dependencies.py`

`session.exec(select(UserModel).where(...))` — should use `UserRepository`.

#### 2.13 [MED] 2 raw `session.exec()` in `services/write_pipeline.py`
`src/salus/services/write_pipeline.py`

Sync push pipeline directly queries client_id dedup log.

---

### 3. DRY VIOLATIONS

#### 3.1 [HIGH] Aggregation logic (`sum` vs `avg` for `steps`/`water`) duplicated 5x
| File | Lines |
|---|---|
| `services/sharing.py:_resolve_local()` | ~397-406 |
| `routers/sharing.py:federated_shared_data()` | ~518-527 |
| `services/leaderboard.py:get_group_rankings()` local | ~206-208 |
| `services/leaderboard.py:get_group_rankings()` remote | ~235-237 |
| `services/insight/service.py:_build_current_states()` | ~85 |

Extract to `services/_aggregation.py` as `aggregate_values(values, data_type) -> float`.

#### 3.2 [HIGH] WebFinger + actor endpoint resolution duplicated within `SharingService`
`services/sharing.py`

`resolve_actor_public_key()` and `_resolve_remote_endpoints()` share 15 identical lines. Extract `_webfinger_resolve_actor(handle) -> dict`.

#### 3.3 [HIGH] Exponential backoff retry loop duplicated within `SharingService`
`services/sharing.py`

`_fetch_remote()` and `_notify_federation_accept()` have identical retry+backoff logic. Extract `_retry_http_request(method, url, ...)`.

#### 3.4 [HIGH] accept/decline relationship methods are duplicates
`services/sharing.py` and `routers/sharing.py`

Identical structure differing only in target status and notification flag. Extract `_change_relationship_status(rel, new_status, notify=False)`.

#### 3.5 [HIGH] Parser guard clause duplicated 4x
`services/parsers/apple_health.py`, `google_fit.py`, `fitbit.py`, `oura.py`

All have `if not isinstance(payload, dict): return []`. Should be in a base class with `can_handle()` + `parse()`.

#### 3.6 [HIGH] LLM provider construction duplicated 5x
`services/insight/providers/openai.py`, `anthropic.py`, `ollama.py` + factory deepseek/openrouter reuse

All providers construct: `messages` list, `temperature: 0.2`, POST, parse JSON, extract content. A `base.py` Protocol exists but doesn't extract the template method. Additionally, response JSON parsing (`data["choices"][0]["message"]["content"]`) still lacks error handling in all providers.

#### 3.7 [MED] Handle construction `f"@{user.username}"` 14+ occurrences
`services/sharing.py` and `services/leaderboard.py`

Extract `_helpers.make_handle(user: User) -> str`.

#### 3.8 [MED] Date range day iteration 4x
`services/sharing.py`, `leaderboard.py`, `goal.py`

`for offset in range(days): day = today - timedelta(days=offset)` repeated. Extract `date_range(days_back: int) -> Generator[date]`.

#### 3.9 [MED] Date validation pattern 3x
`routers/dashboard.py`, `routers/sharing.py`, `services/sharing.py`

`datetime.strptime(date_str, "%Y-%m-%d")` with `except ValueError` fallback. Extract to `_helpers.parse_date(date_str)`.

---

### 4. NAMING & DEVELOPER EXPERIENCE

#### 4.1 [HIGH] Repository base class `get_by_id()` returns None — violates `get` vs `find` convention
`repositories/base.py:14`

AGENTS.md states "get = raises on not found, find = returns None or list." The base repository method `get_by_id` returns `None` (does NOT raise), so it should be `find_by_id`. This propagates to all 18 subclasses.

#### 4.2 [HIGH] `UserRepository.get_by_username()` / `.get_by_email()` return None
`repositories/user.py`

Both return `User | None`. Should be `find_by_username()` / `find_by_email()`.

#### 4.3 [HIGH] `SystemConfigRepository.get_all()` / `.get_by_key()` — wrong prefix
`repositories/system_config.py`

`get_all()` returns `list[SystemConfig]`, `get_by_key()` returns `SystemConfig | None`. Neither raises. Should be `find_all()` / `find_by_key()`.

#### 4.4 [HIGH] Three competing prefixes for "return all records"
| File | Method | Prefix |
|---|---|---|
| `repositories/user.py` | `list_all()` | `list_` |
| `repositories/metric_type.py` | `find_all()` | `find_` |
| `repositories/system_config.py` | `get_all()` | `get_` |
| `repositories/goal.py` | `find_all_goals()` | `find_` + redundant suffix |
| `repositories/user_identity.py` | `list_by_user()` | `list_` |

**Standardize all to `find_all()` / `find_by_user()`.**

#### 4.5 [HIGH] German hardcoded labels in source code
`services/dashboard_widget.py`

| Current (German) | Should be |
|---|---|
| `"Schritte"` | i18n key |
| `"Puls"` | i18n key |
| `"Schlaf"` | i18n key |
| `"Ernährung"` | i18n key |
| `"Gewicht"` | i18n key |
| `"Training"` | i18n key |

These bypass the i18n system entirely.

#### 4.6 [MED] `_bind()` returns bool without boolean prefix
`services/auth/providers.py:42`

Rename to `_try_bind()` or `_can_bind()`.

#### 4.7 [MED] `_is_remote()` misleading name
`services/sharing.py:37-38`

Checks `":" in handle` but doesn't verify connectivity. Rename to `_has_domain()`.

#### 4.8 [MED] `get_instance_keys()` actually generates keys on first call
`services/sharing.py:429`

Rename to `ensure_instance_keys()`.

#### 4.9 [MED] `GoalService.progress()` — noun used as computation method
`services/goal.py:53`

Rename to `compute_progress()` or `get_progress()`.

#### 4.10 [MED] `find_all_goals()` — redundant entity suffix
`repositories/goal.py:17`

Rename to `find_all()`.

#### 4.11 [LOW] Mixed British/American spelling
`services/sharing.py:30` — `_normalise_handle()` (British "s"). Rename to `_normalize_handle()`.

#### 4.12 [LOW] Abbreviated function name `_to_dt()`
`services/parser.py:12` — Rename to `_parse_datetime()`.

#### 4.13 [LOW] Over-abbreviated parameter names
- `services/dashboard_widget.py:363` — `sd` → `source_data_type`
- `routers/entries.py:92` — `dt` → `entry_time`
- `services/dashboard_widget.py:474,508` — `sl`, `n`, `w` → `sleep_summary`, `nutrition`, `weight_point`

#### 4.14 [LOW] Awkward parameter name `by_user_id`
`services/admin.py:106` — Use `deleted_by: int`.

#### 4.15 [LOW] `LlmProviderFactory` — acronym casing
`services/insight/factory.py:9` — should be `LLMProviderFactory` (PEP 8: all-caps acronyms in class names).

#### 4.16 [LOW] Module-level constants with redundant `_` prefix
- `services/dashboard_widget.py:21` — `_EMPTY_TEXTS` → `EMPTY_TEXTS`
- `services/dashboard_widget.py:36` — `_VIZ_TYPE_DEFAULTS` → `VIZ_TYPE_DEFAULTS`
- `services/analytics/orchestrator.py:10,12` — `_RANGE_DAYS` → `RANGE_DAYS`, `_RANGE_BUTTONS` → `RANGE_BUTTONS`
- `services/analytics/activity.py:91` — `_OHLC_DAY_LABELS` → `OHLC_DAY_LABELS`

UPPER_CASE already signals "constant"; `_` prefixed upper_case is ambiguous.

---

### 5. ERROR HANDLING ISSUES

#### 5.1 [HIGH] `PermissionError` (built-in) instead of `ForbiddenError` in 11 places
`services/sharing.py:403`, `services/leaderboard.py:118,171,304`, `services/plugin/context.py:21`, `services/workout/planner.py:57,91` (raises); `routers/api_sharing.py:108,143,176`, `routers/workout.py:49` (catches)

`PermissionError` in Python is for OS file permissions. Authorization failures should use `ForbiddenError` (already defined in `exceptions.py:19`). Because `main.py` catches `ForbiddenError` → 403 but NOT `PermissionError`, these all become 500 errors.

#### 5.2 [HIGH] Bare `except Exception: pass` — 6 locations
| File | Line | Impact |
|---|---|---|
| `routers/api_admin.py` | ~81-82 | Backup listing parse failure → `pass` (returns stale list) |
| `models/measurement.py` | ~62-63 | JSON display format fallback → `pass` (returns raw JSON) |
| `services/sharing.py` | ~346-347 | Federated cache JSON parse → `pass` (refetches remote) |
| `services/backup/service.py` | ~97-98 | Retention cleanup filename parse → `pass` (skips file) |
| `routers/api_admin.py` | ~38-39 | `os.path.getsize()` failure → returns `"--"` |
| `services/backup/providers.py` | ~99-100 | Provider file listing parse → returns `[]` |

Every bare `except: pass` or `except Exception: pass` MUST either log the error or re-raise a domain exception.

#### 5.3 [HIGH] `print()` statements in production service
`services/open_science.py:69,75,77`

`print("DEBUG: ...")` leaks user data to stdout. Replace with `logger.debug()`.

#### 5.4 [HIGH] LLM providers have no error handling on response parsing
`services/insight/providers/openai.py:35`, `anthropic.py`, `ollama.py`

`data["choices"][0]["message"]["content"]` — any `KeyError`, `IndexError`, or `TypeError` from malformed responses propagates. The `InsightService` has a top-level try/except wrapper (line 180), but individual providers should still validate their responses. Add try/except with a `ValueError(f"Malformed response from {provider_name}")`.

#### 5.5 [MED] `InvalidCredentialsError` has no exception handler in `main.py`
`exceptions.py:17`

`NotFoundError`, `ConflictError`, `AuthenticationError`, and `ForbiddenError` all have handlers. `InvalidCredentialsError` falls through to the generic handler (500).

#### 5.6 [MED] `AuthService.get_user_from_token` — unhandled `ValueError`
`services/auth/service.py:55-62`

`int(user_id)` on a malformed token with non-numeric `sub` crashes with `ValueError`. Add try/except returning `None` or a specific `AuthenticationError`.

#### 5.7 [MED] `GoalService._extract_current_value` returns `None` on both "no entries" and "parse error"
`services/goal.py:127-128`

`except (ValueError, TypeError): return None` — caller cannot distinguish between the two cases.

#### 5.8 [MED] LLM plugin hooks catch broad `Exception`
`services/insight/service.py:155-160`

`except Exception as e: logger.error(...)` — swallows unexpected errors from plugin AI coach contexts without propagating.

---

### 6. SECURITY & CONFIG

#### 6.1 [HIGH] CORS `allow_origins=["*"]` + `allow_credentials=True`
`src/salus/main.py:155-156`

This combination is explicitly forbidden by the CORS spec. Browsers will block cross-origin requests with credentials. Fix: use explicit origins or remove the middleware if SPA is served same-origin.

#### 6.2 [MED] Default API token and JWT secret are published in AGENTS.md
`config.py`

`"s3ns0r-h34lth-t0k3n-2026"` and `"change-me-in-production-salus-2026"` are publicly documented. Add startup warnings for production deployments.

#### 6.3 [MED] `schemas/sharing.py` — raw `api_token` in response schema
`schemas/sharing.py:23`

`PeerConnection.api_token: Optional[str]` — exposes the full API token in API responses. Never expose raw credentials in DTOs.

#### 6.4 [LOW] Admin storage stats uses brittle SQLite path extraction
`services/admin.py:37`

`db_path = settings.database_url.replace("sqlite:///", "")` — produces wrong paths for PostgreSQL URLs and absolute SQLite paths.

---

### 7. MODELS & RELATIONSHIPS

#### 7.1 [HIGH] `DashboardWidget` — FK to user.id + metric_type.id but NO Relationships
`models/dashboard.py`

Missing `TYPE_CHECKING` guard, no `Relationship` definitions. ORM cannot eagerly load.

#### 7.2 [HIGH] `FederatedAccessLog` — FK to user.id but NO Relationship
`models/sharing.py`

No `Relationship` to `User`, no `TYPE_CHECKING` guard.

#### 7.3 [MED] `ApiToken` — FK to user.id but NO Relationship
`models/api_token.py`

No `Relationship` to `User`.

#### 7.4 [MED] `Goal` — FK to metric_type.id but NO Relationship
`models/goal.py`

Only `User` is in `TYPE_CHECKING` block. `MetricType` relationship missing.

#### 7.5 [MED] `LeaderboardGroup.creator` Relationship has no `back_populates` on `User`
`models/sharing.py`

All other cross-model relationships use `back_populates`. This one is orphaned.

#### 7.6 [LOW] `models/asymmetric_share.py` — missing `# noqa: F401` on TYPE_CHECKING import

#### 7.7 [MED] `models/__init__.py` — `MetricType` defined inline
All other domain models have dedicated files. Move to `models/metric_type.py`.

---

### 8. REPOSITORIES

#### 8.1 [HIGH] `DashboardRepository.reorder()` — N+1 commit problem
`repositories/dashboard.py:19-24`

Each widget position update calls `self.update(widget)` which calls `self.session.commit()`. For 10 widgets, that's 10 separate commits. Should be a single transaction.

#### 8.2 [MED] `Repository.update()` commits immediately — breaks UoW transactions
`repositories/base.py:23-39`

The base class calls `self.session.commit()` inside `update()`, `create()`, and `delete()`. This means the `SqlUnitOfWork.__exit__` rollback on exception cannot undo already-committed operations within the same `with` block.

#### 8.3 [MED] 15 of 18 repos don't explicitly implement their protocol interfaces
Classes like `UserRepository`, `MetricTypeRepository` do not declare `class UserRepository(Repository[User], IUserRepository)`, even though the protocols exist in `repositories/protocols.py`. Pyright cannot verify interface conformance at class definition time.

#### 8.4 [MED] `SqlUnitOfWork` ignores `HookRegistry` for `MeasurementRepository`
`repositories/unit_of_work.py`

`MeasurementRepository.__init__` accepts optional `registry` parameter. The `SqlUnitOfWork` constructor doesn't pass it. Services using the UoW get a measurement repo without plugin hook support.

#### 8.5 [HIGH] Missing repositories for `FederatedAccessLog` + `FederatedMeasurementCache`
These tables are queried via raw `session.exec()` in both services and routers. They need dedicated repositories.

---

### 9. TESTS

#### 9.1 [HIGH] Massive engine creation duplication
At least 9 test functions duplicate `create_engine("sqlite://", ...)` + `SQLModel.metadata.create_all()` + `TestClient(app)` + `app.dependency_overrides` instead of using the `conftest.py:client` fixture.

#### 9.2 [MED] Hardcoded magic credentials — 49 occurrences
`"admin"/"admin"`, `"secret123"`, `"alice@example.com"` repeated throughout 20+ test locations. Use fixtures.

#### 9.3 [MED] Fragile hardcoded database IDs
Tests use `data={"metric_type_id": 1, ...}` — breaks if seed order changes.

---

### 10. LOGGING

#### 10.1 [HIGH] `print()` in production (see 5.3)
`services/open_science.py:69,75,77`

#### 10.2 [MED] `logging.basicConfig` at module level
`main.py:25-26`

If any other module or test runner configures logging first, `basicConfig` does nothing.

#### 10.3 [LOW] No JSON-structured logging
Plain text format. Production improvement.

---

### 11. CONFIG & DEFAULT VALUES

#### 11.1 [MED] Magic string `"#4f46e5"` in 7 places
`models/__init__.py`, `schemas/__init__.py`, `schemas/sharing.py`, `routers/metrics.py`, `services/sharing.py`

Define once as `DEFAULT_METRIC_COLOR` in a shared constant.

#### 11.2 [MED] Schema defaults inconsistent with model defaults
3 cases where `MetricTypeCreate.color`, `MetricTypeCreate.icon`, and `ExerciseBase.equipment` duplicate model defaults. Change in model must be mirrored in schema.

#### 11.3 [MED] `WorkoutSessionCreate.started_at` uses naive `datetime.utcnow`
`schemas/workout.py:92`

Model uses timezone-aware `datetime.now(timezone.utc)`. Inconsistency.

---

### 12. SCHEMAS

#### 12.1 [MED] `EntryResponse` field names don't match `Measurement` model
`schemas/api.py`

Has `value: str` and `timestamp: datetime` but model has `value_numeric`, `value_text`, `value_json`, `start_time`/`end_time`. Cannot directly map.

#### 12.2 [MED] Untyped `dict` in `CircadianAdviceResponse`
`schemas/circadian.py`

`sleep_window: dict`, `light_advice: list[dict]` — should be typed Pydantic models.

#### 12.3 [MED] 9 SQLModel tables have no corresponding schemas
`ApiToken`, `SystemConfig`, `DashboardWidget`, `Insight`, `SharingRelationship`, `LeaderboardGroup`, `LeaderboardMember`, `FederatedMeasurementCache`, `FederatedAccessLog`.

---

### 13. MISC

#### 13.1 [LOW] `analytics/dashboard.py` — `summary()` missing `user_id` parameter
All child services require `user_id` but `DashboardService.summary()` doesn't pass one.

#### 13.2 [MED] `insight/factory.py` — empty API key defaults
`api_key or ""` — leads to cryptic HTTP errors at request time instead of clear startup validation. Now 5 providers (was 3, +deepseek +openrouter).

#### 13.3 [LOW] `backup/service.py` — uses `os.path.join(os.getcwd(), ...)`
Could fail if CWD is not writable. Use `tempfile`.

#### 13.4 [MED] `services/dashboard_widget.py` — hardcoded German labels
`"Schritte"`, `"Ziel: ..."`, `"Puls"`, `"Schlaf"`, `"Ernährung"`, `"Gewicht"`, `"Training"` should use i18n keys.

#### 13.5 [MED] `services/dashboard_widget.py` — `_delta_str()` returns HTML
Service method returns raw HTML strings. View concern leaking into service.

#### 13.6 [MED] `api_dynamic.py` `register_crud_routes()` never called
`routers/api_dynamic.py:20` — defined but never invoked from `main.py`. Dynamic CRUD endpoints for `ENTITY_REGISTRY` entities don't exist at runtime. Dead code.

---

## Quick Wins (Small Effort, High Impact)

These issues can each be fixed in <30 minutes:

| # | Category | Issue | Effort |
|---|---|---|---|
| Q1 | Error | Replace all bare `except Exception: pass` with logged warnings (6 locations) | 15 min |
| Q2 | Error | Replace `PermissionError` → `ForbiddenError` in 11 locations | 15 min |
| Q3 | Error | Add `print()` → `logger.debug()` in `open_science.py` | 5 min |
| Q4 | DRY | Extract `aggregate_values()` function (5 → 1 call sites) | 20 min |
| Q5 | DRY | Extract `make_handle(user)` helper (14 → 1 call sites) | 10 min |
| Q6 | DRY | Extract `parse_date()` helper (3 call sites) | 10 min |
| Q7 | Config | Add `DEFAULT_METRIC_COLOR` constant (7 → 1 call site) | 5 min |
| Q8 | Models | Add missing `Relationship` to `DashboardWidget`, `ApiToken`, `Goal`, `FederatedAccessLog` | 15 min |
| Q9 | DRY | Extract `_webfinger_resolve()` (2 → 1 in sharing.py) | 15 min |
| Q10 | DRY | Extract `_retry_http_request()` (2 → 1 in sharing.py) | 15 min |
| Q11 | DRY | Extract `_change_relationship_status()` (accept/decline dedup) | 10 min |
| Q12 | DRY | Extract Parser base class with guard clause (4 → 1) | 15 min |
| Q13 | DRY | Extract LLM provider template method + add response error handling | 20 min |
| Q14 | Security | Fix CORS `allow_origins=["*"]` + `allow_credentials=True` | 5 min |
| Q15 | Error | Add `InvalidCredentialsError` handler in `main.py` | 5 min |
| Q16 | Error | Add try/except for `int(user_id)` in `AuthService.get_user_from_token` | 5 min |
| Q17 | Schemas | Fix `datetime.utcnow` → `datetime.now(timezone.utc)` in workout schema | 2 min |
| Q18 | Schemas | Add typed models for `CircadianAdviceResponse` dict fields | 15 min |
| Q19 | Repos | Add `FederatedAccessLogRepository` + update raw queries | 20 min |
| Q20 | Naming | Rename `get_all()` → `find_all()` on SystemConfigRepository | 5 min |
| Q21 | Naming | Rename `get_by_username()` / `get_by_email()` → `find_by_*()` | 5 min |
| Q22 | Naming | Replace German hardcoded labels with i18n keys | 15 min |
| Q23 | Naming | Rename `_bind()` → `_try_bind()`, `_is_remote()` → `_has_domain()`, `get_instance_keys()` → `ensure_instance_keys()` | 5 min |
| Q24 | Naming | Rename `GoalService.progress()` → `compute_progress()` | 2 min |
| Q25 | Naming | Rename `_normalise_handle()` → `_normalize_handle()`, `_to_dt()` → `_parse_datetime()` | 3 min |

**Total quick-win time: ~4.5 hours**

---

## Architectural Refactoring Roadmap

### Phase 1: Harden (Quick Wins above)
Fix errors, add missing i18n, extract duplicated logic, fix security issues.

### Phase 2: Split God Classes
1. Split `SharingService` → `RelationshipService` + `FederationKeyService` + `FederationDataResolver` + `FederationFeedService` + `PeerNotificationService`
2. Split `DashboardWidgetService` → extract chart computation to `services/analytics/visualization.py`
3. Split `routers/sharing.py` → `routers/leaderboard.py` + `routers/federation.py`

### Phase 3: Eliminate DIP Violations
1. Add missing repository methods for all 51 raw `session.exec()` call sites
2. Move `run_background_ingest()` to a service, inject dependencies
3. Add `UserService.dismiss_onboarding()` method
4. Encapsulate `api_token_svc._user_repo` behind a public method

### Phase 4: Repository Layer Cleanup
1. Remove `commit()` from `Repository.update()` / `create()` / `delete()` — defer to UoW
2. Fix `DashboardRepository.reorder()` N+1 commit
3. Add explicit protocol implementations to all 15 repos
4. Add repos for `FederatedAccessLog`, `FederatedMeasurementCache`

### Phase 5: Test Quality
1. Consolidate engine creation to `conftest.py` fixtures
2. Replace magic credentials with fixtures
3. Remove fragile hardcoded DB IDs

---

## Appendix: Full Issue Catalog

### HIGH (~55 issues)

| ID | Category | File | Issue |
|---|---|---|---|
| H1 | SRP | `services/sharing.py` | God class (1192 lines, 6+ concerns, grew 150 lines) |
| H2 | SRP | `services/dashboard_widget.py` | Widget CRUD + visualization + charts (697 lines, grew 116 lines) |
| H3 | SRP | `models/sharing.py` | 3 unrelated domains in one file |
| H4 | SRP | `routers/sharing.py` | 5 route groups mixed |
| H5 | DIP | `services/sharing.py` | 12 raw session.exec() |
| H6 | DIP | `services/leaderboard.py` | 3 raw session.exec() |
| H7 | DIP | `services/workout/planner.py` | 14 raw session.exec() + cast(SqlUoW) |
| H8 | DIP | `routers/sharing.py` | 4 raw session.exec() in handlers |
| H9 | DIP | `routers/webhook.py` | Inline service construction (entire graph) |
| H10 | DIP | `routers/onboarding.py` | Raw Session in route |
| H11 | DIP | `services/portability.py` | 12 raw session.exec() |
| H12 | DIP | `services/write_pipeline.py` | 2 raw session.exec() |
| H13 | DRY | 5 files | Aggregation logic 5x duplicated |
| H14 | DRY | `services/sharing.py` | WebFinger 2x within same file |
| H15 | DRY | `services/sharing.py` | Retry backoff 2x within same file |
| H16 | DRY | `services/sharing.py` | accept/decline duplicate logic |
| H17 | DRY | 4 parser files | Guard clause 4x duplicated |
| H18 | DRY | 5 LLM provider files | Response parsing duplicated, no error handling |
| H19 | Error | 6 locations | Bare `except Exception: pass` |
| H20 | Error | 11 locations | `PermissionError` instead of `ForbiddenError` |
| H21 | Error | 5 LLM provider files | No error handling on response JSON parse |
| H22 | Error | `services/open_science.py` | `print()` in production (3 occurrences) |
| H23 | Error | `services/backup/providers.py` | Returns `[]` on 401/403 |
| H24 | Error | `services/backup/providers.py` | Swallows all WebDAV errors |
| H25 | Error | `services/insight/service.py` | Broad except in LLM fallback + plugin hooks |
| H26 | Security | `main.py` | CORS `*` + credentials |
| H27 | Models | `models/dashboard.py` | FK but no Relationship |
| H28 | Models | `models/sharing.py` | FederatedAccessLog FK, no Relationship |
| H29 | Repos | `repositories/dashboard.py` | N+1 commit in reorder() |
| H30 | Repos | multiple | Missing repos for FederatedAccessLog, FederatedMeasurementCache |
| H31 | Tests | 9 test functions | Engine creation duplicated instead of conftest fixture |
| H32 | Deps | `dependencies.py` | Raw SQL in factory function |
| H33 | Config | `config.py` | Published default secrets |
| H34 | Logging | `services/open_science.py` | print() in production |
| H35 | Schemas | `schemas/sharing.py` | Raw api_token in response DTO |
| H36 | Config | `services/admin.py` | Brittle SQLite path extraction |
| H37 | Naming | `repositories/base.py` | `get_by_id()` returns None, should be `find_by_id()` |
| H38 | Naming | `repositories/user.py` | `get_by_username()`/`get_by_email()` return None |
| H39 | Naming | `repositories/system_config.py` | `get_all()`/`get_by_key()` wrong prefix |
| H40 | Naming | 5 repos | Three competing prefixes (`list_`, `find_`, `get_`) |
| H41 | Naming | `services/dashboard_widget.py` | German hardcoded labels bypassing i18n |
| H42 | SRP | `services/circadian.py` | Solar calculator mixed with profile CRUD |
| H43 | SRP | `models/__init__.py` | MetricType defined inline instead of own file |
| H44 | Bug | `routers/api_dynamic.py` | `register_crud_routes()` never called — dead code |
| H45 | Schemas | `schemas/sharing.py` | api_token leaked in PeerConnection response |

### MEDIUM (~50 issues)

| ID | Category | File | Issue |
|---|---|---|---|
| M1 | DIP | `routers/api.py` | `measurement_svc.repo` access |
| M2 | DIP | `routers/insight.py` | `service._uow` access |
| M3 | DIP | `routers/admin.py` | `backup_svc.provider` access |
| M4 | DIP | `dependencies.py` | `api_token_svc._user_repo` private attr |
| M5 | DIP | `routers/dashboard.py` | Plugin manager via app.state not Depends |
| M6 | Error | `main.py` | Missing InvalidCredentialsError handler |
| M7 | Error | `services/auth/service.py` | Unhandled ValueError in int(user_id) |
| M8 | Error | `services/auth/providers.py` | Lazy import inside method |
| M9 | Error | `services/goal.py` | None on both "no entries" and "parse error" |
| M10 | Error | `services/backup/service.py` | Swallows retention parse errors |
| M11 | Error | `services/plugin/manager.py` | 5x too-broad except |
| M12 | Error | `services/parser.py` | ValueError instead of custom exception |
| M13 | DRY | `services/sharing.py` + `leaderboard.py` | `_is_remote()` vs inline check |
| M14 | DRY | `services/sharing.py` + `leaderboard.py` | Handle construction 14x |
| M15 | DRY | 3 services | Date range day iteration 4x |
| M16 | DRY | `dashboard.py` + `sharing.py` | Date validation 3x |
| M17 | Models | `models/api_token.py` | FK no Relationship |
| M18 | Models | `models/goal.py` | FK to metric_type, no Relationship |
| M19 | Models | `models/sharing.py` | LeaderboardGroup.creator no back_populates |
| M20 | Models | `models/sharing.py` | FederatedMeasurementCache no TYPE_CHECKING |
| M21 | Models | `models/__init__.py` | Fragile circular import topology |
| M22 | Schemas | `schemas/__init__.py` | MetricTypeCreate inline instead of own file |
| M23 | Schemas | 3 locations | Duplicated default values model↔schema |
| M24 | Schemas | `schemas/workout.py:92` | naive datetime.utcnow |
| M25 | Schemas | `schemas/api.py` | EntryResponse ↔ Measurement mismatch |
| M26 | Schemas | `schemas/api.py` | HealthRecordResponse.id: str vs int |
| M27 | Schemas | `schemas/api.py` | MetricTypeResponse missing fields |
| M28 | Schemas | `schemas/circadian.py` | Untyped dict in response |
| M29 | Schemas | 9 tables | No corresponding schemas |
| M30 | Repos | `repositories/base.py` | update() commits immediately |
| M31 | Repos | `repositories/unit_of_work.py` | Ignores HookRegistry |
| M32 | Repos | `repositories/unit_of_work.py` | UoW rollback can't undo committed ops |
| M33 | Repos | 15 repos | Don't explicitly implement protocol interfaces |
| M34 | Repos | — | No repos for WorkoutPlanExercise, WorkoutLogEntry |
| M35 | Config | `main.py` | NAV_ITEMS hardcoded |
| M36 | Config | `main.py` | Locale only de/en |
| M37 | i18n | `services/i18n.py` | Single 300-line dict, won't scale |
| M38 | i18n | Python source | `_()` not used in services/routers |
| M39 | i18n | `services/dashboard_widget.py` | Hardcoded German labels |
| M40 | Logging | `main.py` | basicConfig at module level |
| M41 | DB | `database.py` | SQLite check applies to all non-PG engines |
| M42 | Deps | `dependencies.py` | backup service hard-couples to module engine |
| M43 | Tests | 20+ locations | Magic credentials repeated 49x |
| M44 | Tests | `test_onboarding.py` | Fragile hardcoded DB IDs |
| M45 | Config | `main.py` | Plugin router only /api/plugins prefix |
| M46 | Config | `onboarding.py` | _STEP_DEFS in router, not service |
| M47 | Schemas | `schemas/sharing.py` | PeerConnection/PeerMetricInfo no Create counterpart |
| M48 | Services | `circadian.py` | Solar calculator mixed with profile mgmt |
| M49 | Services | `dashboard_widget.py` | _delta_str() returns HTML |
| M50 | Services | `dashboard_widget.py` | `type: ignore` instead of uid() helper |
| M51 | Error | `services/parser.py` | except ImportError silently degrades |
| M52 | Services | `analytics/orchestrator.py` | Missing type annotation on weight_trend |
| M53 | Services | `analytics/sleep.py` | Missing type annotation on record param |
| M54 | Naming | `services/auth/providers.py` | `_bind()` returns bool without `is_`/`can_` prefix |
| M55 | Naming | `services/sharing.py` | `get_instance_keys()` actually generates |
| M56 | Naming | `services/goal.py` | `progress()` noun used as computation method |
| M57 | Naming | `repositories/goal.py` | `find_all_goals()` redundant suffix |
| M58 | Naming | `repositories/base.py` | Missing abstract `find_all()` method |
| M59 | Config | `services/insight/factory.py` | `api_key or ""` → cryptic errors (5 providers now) |
| M60 | Bug | `analytics/dashboard.py` | summary() missing user_id parameter |

### LOW (~45 issues)

| ID | Category | File | Issue |
|---|---|---|---|
| L1 | Naming | `services/sharing.py` | `_is_remote()` misleading |
| L2 | Naming | `services/sharing.py` | `get_instance_keys()` actually generates |
| L3 | Naming | `services/parser.py` | `_to_dt()` abbreviated |
| L4 | Naming | `services/leaderboard.py` | Parameter ordering unusual |
| L5 | Models | `models/asymmetric_share.py` | Missing # noqa: F401 |
| L6 | Models | `models/analytics.py` | DTOs in models/ (allowed but unusual) |
| L7 | Schemas | `schemas/__init__.py` | Schema → model import |
| L8 | Repos | `repositories/__init__.py` | Empty file |
| L9 | Repos | `services/workout/planner.py` | ValueError instead of ConflictError |
| L10 | Error | `services/backup/service.py` | os.getcwd() tempfile |
| L11 | Error | `routers/open_science.py` | Broad except returning 400 |
| L12 | Error | `routers/asymmetric_share.py` | Broad except returning 404 |
| L13 | Services | `analytics/calculations.py` | Hardcoded height/age defaults |
| L14 | Services | `services/insight/providers/` | 2x api_key or "" |
| L15 | Config | `config.py` | Missing LLM/Backup docs in AGENTS.md |
| L16 | Config | `database.py` | No echo config flag |
| L17 | Config | `main.py` | Dynamic plugin router prefix |
| L18 | Config | `repositories/unit_of_work.py` | UoW commits on exit |
| L19 | Logging | `main.py` | No JSON-structured logging |
| L20 | i18n | `main.py` | Default locale is German, not English |
| L21 | Naming | `services/sharing.py` | `_normalise_handle()` British spelling vs American |
| L22 | Naming | `services/parser.py` | `_to_dt()` obscure abbreviation |
| L23 | Naming | `services/dashboard_widget.py` | `sd` parameter too abbreviated |
| L24 | Naming | `services/dashboard_widget.py` | `sl`, `n`, `w` single-letter variables |
| L25 | Naming | `routers/entries.py` | `dt` abbreviation for entry_time |
| L26 | Naming | `services/insight/factory.py` | `LlmProviderFactory` → `LLMProviderFactory` |
| L27 | Naming | `services/admin.py` | `by_user_id` awkward parameter name |
| L28 | Naming | `services/dashboard_widget.py` | `_EMPTY_TEXTS`, `_VIZ_TYPE_DEFAULTS` redundant `_` |
| L29 | Naming | `services/analytics/orchestrator.py` | `_RANGE_DAYS`, `_RANGE_BUTTONS` redundant `_` |
| L30 | Naming | `services/analytics/activity.py` | `_OHLC_DAY_LABELS` redundant `_` |
| L31 | Naming | `repositories/api_token.py` | `list_all_active()` → `find_all_active()` |
| L32 | Naming | `repositories/workout.py` | `find_all_catalog()` / `get_last_session_for_plan()` inconsistent |
| L33 | Naming | `services/goal.py` | `progress()` noun instead of action verb |
| L34 | Naming | `repositories/user_identity.py` | `list_by_user()` → `find_by_user()` |
| L35 | Naming | `repositories/workout.py` | `get_last_session_for_plan()` returns None, should be `find_` |
| L36 | Naming | `services/auth/service.py` | Duplicate `uid` import inside method |
| L37 | Naming | `repositories/leaderboard.py` | `get_member()` returns None, should be `find_member()` |
| L38 | Deps | `dependencies.py` | Lazy import in function |
| L39 | Deps | `dependencies.py` | 496 lines, could split into sub-modules |
| L40 | Tests | — | AAA pattern not consistently followed |
| L41 | Deps | `routers/sharing.py` | 303 redirect no request param (cosmetic) |
| L42 | Models | `models/sharing.py` | FederatedMeasurementCache.value_numeric dead column |
| L43 | Config | `services/insight/factory.py` | Empty API key defaults in addition to "or """ |
| L44 | Schemas | `schemas/backup.py` | Missing or incomplete BackupConfig schema |
| L45 | Config | — | No startup warning for production default secrets |

---

## Action Priority (Recommended Order)

1. **Fix critical errors:** Q1-Q3, Q14-Q16, H19-H25, H33-H34 (~1h)
2. **Fix security:** H26, H36, H35 (~15 min)
3. **Fix naming inconsistencies:** Q20-Q25, H37-H41, M54-M58 (~30 min)
4. **Add missing model relationships:** H27, H28, M17-M21 (~15 min)
5. **Extract duplicated logic:** Q4-Q7, Q9-Q13, H13-H18 (~1.5h)
6. **Eliminate router DIP violations:** H8-H10, M1-M3, M5 (~1h)
7. **Split God classes:** H1-H4 (~3h)
8. **Repository layer cleanup:** H5-H7, H11-H12, H29-H30, M30-M34 (~2h)
9. **Test cleanup:** H31, M43-M44 (~30 min)
10. **Wire up or remove api_dynamic.py:** H44 (~15 min)
