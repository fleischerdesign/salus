# Salus Codebase Audit — SOLID, DRY, Clean Code & Academic Professionalism

> Generated 2026-07-03. Exhaustive audit of `src/salus/` (55 service files, 19 routers, 12 models, 18 repos, 75+ templates, 5 cross-cutting concerns).
> 
> **Companion specification:** [`DESIGN.md`](./DESIGN.md) — Part I: Brand & Principles, Part II: Complete token architecture, color scales, component specs.

---

## Executive Summary

| Metric | Count |
|---|---|
| **Total issues found** | **~290** |
| HIGH severity | 94 |
| MEDIUM severity | 104 |
| LOW severity | 90+ |
| Files with issues | 50+ |
| Quick wins (<1h to fix) | 50+ |

**Top structural problems:**
1. `SharingService` is a 1042-line God class mixing 6+ concerns (SRP)
2. 36+ raw `session.exec()` calls across services and routers bypassing repository abstraction (DIP)
3. 5x copy-paste of aggregation logic (DRY)
4. 45+ hardcoded English strings in templates missing `_()` i18n wrapper
5. `routers/sharing.py` has 17 direct `sharing_svc.uow` accesses (thin-router violation)
6. CORS `allow_origins=["*"]` + `allow_credentials=True` — broken cross-origin cookie auth (Security)
7. `PermissionError` (built-in) instead of `ForbiddenError` in 6 places — auth failures → 500 errors
8. Repository base class uses `get_*` prefix for nullable returns — violates documented `get` vs `find` convention
9. No CSRF protection, no security headers (CSP/HSTS/X-Frame-Options), `Secure` flag missing on auth cookie
10. 668 inline `style="..."` occurrences across templates; 34 hardcoded colors break dark mode; 12 undefined CSS variables
11. Zero HTMX error handling or loading indicators; modals break on failure; 14 forms non-functional without JavaScript

---

## Criteria Summary

| Principle | Grade | Verdict |
|---|---|---|
| **SRP** | D | God class (`sharing.py`), mixed domains (`models/sharing.py`, `routers/sharing.py`) |
| **OCP** | B- | Parser + Auth provider pattern is extensible; metric type icons hardcoded in templates |
| **LSP/ISP** | C+ | `IUnitOfWork` exposes raw `session` leaking all repos; 15/18 repos skip interface declaration |
| **DIP** | C- | 36+ raw session accesses, webhook route instantiates its own graph, onboarding uses raw Session |
| **DRY** | C+ | Aggregation logic 5x copied, retry-with-backoff 2x, parser guard clauses 4x, template macros missing |
| **Clean Code** | B- | Good naming overall; some `print()` in prod, magic strings, `assert` for control flow |
| **Modularity** | C+ | Models/Services mix domains; templates have 56 i18n violations; leaderboard/federation lumped together |
| **Extensibility** | B | Plugin system (parsers, hooks, widgets) is well-designed; fixed defaults block dynamic extension |
| **Naming** | C+ | `get_*`/`find_*` inconsistency across all repos; German hardcoded labels; mixed British/American spelling |
| **CSS/Design System** | C+ | DESIGN.md spec 85% implemented; 34 hardcoded colors break dark mode; 12 undefined CSS variables; 668 inline styles |
| **HTMX / UX** | D+ | No error handlers, no loading indicators, no `<noscript>`, modals break on error, 14 forms broken without JS |
| **Security** | D | No CSP, no CSRF, no HSTS, no X-Frame-Options; `Secure` flag missing on auth cookie; CORS misconfigured |
| **Accessibility** | D- | No aria-live, no modal accessibility, WCAG contrast failures, no keyboard support for custom elements |
| **API Design** | B- | Good OpenAPI base, but inconsistent error format, missing response_model on 6 endpoints, unversioned routes |
| **Academic Quality** | B- | Good core architecture (DIP via `dependencies.py`); undermined by violations documented below |

---

## Issue Categories

### 1. GOD CLASS & SRP VIOLATIONS

#### 1.1 [HIGH] `SharingService` (1042 lines, 6+ concerns)
`src/salus/services/sharing.py:1-1042`

| Concern | Lines | Should be |
|---|---|---|
| Handle utilities | 29–54 | `HandleUtil` static class |
| Relationship CRUD | 60–179 | `SharingRelationshipService` |
| Peer connection views | 185–281 | same, or `PeerConnectionService` |
| Federation key management + signing/verify | 429–671 | `FederationKeyService` + `HttpSignatureService` |
| WebFinger + remote endpoint resolution | 673–720 | `FederationDiscoveryService` |
| Remote data fetch + caching + feed assembly | 722–986 | `FederationDataResolver` + `FederationFeedService` |
| Push notification broadcasting | 988–1042 | `PeerNotificationService` |

**Impact:** Cannot test federation key management independently. Adding a new remote protocol requires modifying 6 concerns. Backpressure from one concern blocks the entire service.

#### 1.2 [HIGH] `DashboardWidgetService` (581 lines, 3 concerns)
`src/salus/services/dashboard_widget.py:1-581`

| Concern | Lines |
|---|---|
| Widget CRUD | 7 methods |
| Visualization building | 7 methods |
| Chart computation | 4 helper functions (candlestick 52 lines, pill chart 65 lines) |

Chart computation should be in `services/analytics/visualization.py`.

#### 1.3 [MED] `CircadianService` mixes solar calculator with profile management
`src/salus/services/circadian.py:44-126`

`calculate_solar_times()` (82 lines of pure-math NOAA solar calculation) is a distinct domain from profile CRUD. Extract to `SolarCalculator` utility.

#### 1.4 [HIGH] `models/sharing.py` mixes 3 unrelated domains
`src/salus/models/sharing.py:1-93`

`SharingRelationship` + `LeaderboardGroup`/`LeaderboardMember` + `FederatedMeasurementCache`/`FederatedAccessLog`. Split into `models/leaderboard.py` and `models/federation.py`.

#### 1.5 [HIGH] `routers/sharing.py` mixes 5 separate route groups
`src/salus/routers/sharing.py:1-706`

Feed (33–47) + Leaderboard CRUD (54–216) + Connection management (248–422) + Federation API (429–618) + WebFinger/Actor (621–706). Split into `routers/leaderboard.py` and `routers/federation.py`.

---

### 2. DIP VIOLATIONS — Raw Session Access

#### 2.1 [HIGH] 15 raw `session.exec()` in `SharingService`
`src/salus/services/sharing.py`

Lines: 97, 317, 335, 339, 348, 432, 435, 467, 472, 480, 483, 745, 848, 871, 877, 902, 1005

All bypass `ISharingRelationshipRepository` interface. Should add methods like `find_active_for_metric()`, `find_by_token_hash()`, `find_remote_grantees()` to the repository.

#### 2.2 [HIGH] 3 raw `session.exec()` in `LeaderboardService`
`src/salus/services/leaderboard.py:93-98,101-106,188-194`

Raw queries for `SharingRelationship` and `WorkoutSession`. Should use repo methods.

#### 2.3 [HIGH] 4 raw `session.exec()` in WorkoutPlanner
`src/salus/services/workout/planner.py:82-83,103,161-170,186-189`

`cast(SqlUnitOfWork, self.uow)` + raw `session.exec()` — direct DIP violation with type cast.

#### 2.4 [HIGH] 17 `sharing_svc.uow.*` accesses in router
`src/salus/routers/sharing.py`

Lines: 254, 258, 441-502, 632-633, 658-659, 688-692

Includes 5 raw `session.exec()` in route handlers, 1 raw `session.add()`, and 2 model imports (`FederatedAccessLog`, `hashlib`).

#### 2.5 [HIGH] `webhook.py` instantiates entire service graph inline
`src/salus/routers/webhook.py:15-56`

`run_background_ingest()` constructs `MeasurementRepository`, `MetricTypeRepository`, `FlexiblePayloadParser`, `WebhookIngestionService`, `SqlUnitOfWork`, and `SharingService` directly. Completely bypasses the DI system.

#### 2.6 [HIGH] Onboarding route uses raw `Session`
`src/salus/routers/onboarding.py:29-33`

`session.add(current_user)` + `session.commit()` directly in route. Should delegate to `UserService`.

#### 2.7 [MED] `api.py` accesses `measurement_svc.repo` directly
`src/salus/routers/api.py:136`

`measurement_svc.repo.find_all(...)` — pierces service abstraction to call repo method.

#### 2.8 [MED] `insight.py` accesses `service._uow` directly
`src/salus/routers/insight.py:34`

`service._uow.insights.list_by_user(...)` — double pierce (service._uow → repo).

#### 2.9 [MED] Admin routes access `backup_svc.provider` directly
`src/salus/routers/admin.py:44-47`

`backup_svc.provider.list_backups()` — should be wrapped by service method.

#### 2.10 [MED] `dependencies.py:93` accesses `api_token_svc._user_repo`
`src/salus/dependencies.py:93`

Private attribute access in dependency factory. `ApiTokenService` should expose `get_user_repo()`.

#### 2.11 [MED] `dependencies.py:388-396` runs raw SQL in `get_current_user_or_api`
`src/salus/dependencies.py:388-396`

`session.exec(select(UserModel).where(UserModel.is_admin)).first()` — should use `UserRepository`.

---

### 3. DRY VIOLATIONS

#### 3.1 [HIGH] Aggregation logic (`sum` vs `avg` for `steps`/`water`) duplicated 5x
| File | Lines |
|---|---|
| `services/sharing.py:_resolve_local()` | 397–406 |
| `routers/sharing.py:federated_shared_data()` | 518–527 |
| `services/leaderboard.py:get_group_rankings()` local | 206–208 |
| `services/leaderboard.py:get_group_rankings()` remote | 235–237 |
| `services/insight/service.py:_build_current_states()` | 85 |

Extract to `services/_aggregation.py` as `aggregate_values(values, data_type) -> float`.

#### 3.2 [HIGH] WebFinger + actor endpoint resolution duplicated within `SharingService`
`services/sharing.py`

`resolve_actor_public_key()` (492–519) and `_resolve_remote_endpoints()` (677–704) share 15 identical lines. Extract `_webfinger_resolve_actor(handle) -> dict`.

#### 3.3 [HIGH] Exponential backoff retry loop duplicated within `SharingService`
`services/sharing.py`

`_fetch_remote()` (771–797) and `_notify_federation_accept()` (811–839) have identical retry+backoff logic. Extract `_retry_http_request(method, url, ...)`.

#### 3.4 [HIGH] accept/decline relationship methods are duplicates
`services/sharing.py:124-145,147-165` and `routers/sharing.py:343-358,361-376`

Identical structure differing only in target status and notification flag. Extract `_change_relationship_status(rel, new_status, notify=False)`.

#### 3.5 [HIGH] Parser guard clause duplicated 4x
`services/parsers/apple_health.py:14-15`, `google_fit.py:14-15`, `fitbit.py:14-15`, `oura.py:14-15`

All have `if not isinstance(payload, dict): return []`. Should be in a base class `BaseParser` with `can_handle()` + `parse()`.

#### 3.6 [HIGH] LLM provider response parsing pattern duplicated 3x
`services/insight/providers/openai.py:24-33`, `anthropic.py:26-35`, `ollama.py:22-30`

All three: construct `messages` list, set `temperature: 0.2`, POST, parse JSON, extract content. Use a shared abstract base `LLMProvider` with `_make_request()` template method.

#### 3.7 [MED] Handle construction `f"@{user.username}"` 14+ occurrences
`services/sharing.py:74,129,198,278,301,356,755,866,993` and `services/leaderboard.py:55,74,91,129,156,183,265`

Extract `_helpers.make_handle(user: User) -> str`.

#### 3.8 [MED] Date range day iteration 4x
`services/sharing.py:921,959`, `leaderboard.py:217-232`, `goal.py:108-115`

`for offset in range(days): day = today - timedelta(days=offset)` repeated. Extract `date_range(days_back: int) -> Generator[date]`.

#### 3.9 [MED] METRIC-TYPE-CODE → ICON MAPPING IN TEMPLATES (2 IDENTICAL COPIES)
`templates/pages/sharing_leaderboard.html:39-43` and `templates/pages/sharing_leaderboard_detail.html:15-19`

```jinja2
{% if group.metric_type_code == 'steps' %}footprint
{% elif ... == 'workouts' %}fitness_center
{% elif ... == 'sleep' %}bedtime
{% elif ... == 'water' %}local_drink
{% else %}leaderboard{% endif %}
```

Extract to `components/macros/metric_type_icon.jinja2`.

#### 3.10 [MED] RANK BADGE (GOLD/SILVER/BRONZE) IN TEMPLATES (2 IDENTICAL COPIES)
`templates/pages/sharing_leaderboard.html:62-71` and `templates/pages/sharing_leaderboard_detail.html:55-63`

Extract to `components/macros/rank_badge.jinja2`.

#### 3.11 [MED] SCORE FORMATTING PER METRIC TYPE IN TEMPLATES (2 IDENTICAL COPIES)
`templates/pages/sharing_leaderboard.html:82-92` and `templates/pages/sharing_leaderboard_detail.html:82-98`

Extract to `components/macros/format_challenge_score.jinja2`.

#### 3.12 [MED] EXERCISE LIST ITEM IN TEMPLATES (2 IDENTICAL COPIES)
`templates/pages/workouts.html:107-129` and `templates/pages/exercises.html:25-48`

Extract to `components/exercise_list_item.html`.

#### 3.13 [MED] EMPTY STATE PATTERN (4 COPIES)
`sharing_connections.html`, `sharing_feed.html`, `sharing_leaderboard.html`, `sharing_access_log.html`

```html
<div class="card empty-state-card">
    <span class="material-symbols-outlined empty-state-icon">...</span>
    <h3 class="empty-state-title">{{ _("...") }}</h3>
    <p class="text-muted empty-state-text">{{ _("...") }}</p>
</div>
```

Create `components/macros/empty_state.jinja2`.

#### 3.14 [MED] FORM ACTION BUTTONS PATTERN (7 COPIES)
`goal_form.html`, `entry_form.html`, `metric_form.html`, `plan_form.html`, `exercise_form.html`, `add_widget_modal.html`, `edit_widget_modal.html`

```html
<div class="form-actions">
    <button type="submit" class="btn">{{ _("Save") }}</button>
    <button type="button" class="btn-ghost" ...>{{ _("Cancel") }}</button>
</div>
```

Create `components/macros/form_actions.jinja2`.

#### 3.15 [MED] Date validation pattern 3x
`routers/dashboard.py:49-51,87-90`, `routers/sharing.py:507-512`, `services/sharing.py:386-388`

`datetime.strptime(date_str, "%Y-%m-%d")` with `except ValueError` fallback. Extract to `_helpers.parse_date(date_str)`.

---

---

### 4. NAMING & DEVELOPER EXPERIENCE

#### 4.1 [HIGH] Repository base class `get_by_id()` returns None — violates `get` vs `find` convention
`repositories/base.py:14`

AGENTS.md states "get = raises on not found, find = returns None or list." The base repository method `get_by_id` returns `None` (does NOT raise), so it should be `find_by_id`. This propagates to all 18 subclasses.

#### 4.2 [HIGH] `UserRepository.get_by_username()` / `.get_by_email()` return None
`repositories/user.py:11,16`

Both return `User | None`. Should be `find_by_username()` / `find_by_email()`.

#### 4.3 [HIGH] `SystemConfigRepository.get_all()` / `.get_by_key()` — wrong prefix
`repositories/system_config.py:10,13`

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
`services/dashboard_widget.py:411-576`

| Current (German) | Should be |
|---|---|
| `"Schritte"` | `"Steps"` (via i18n) |
| `"Puls"` | `"Heart Rate"` |
| `"Schlaf"` | `"Sleep"` |
| `"Ernährung"` | `"Nutrition"` |
| `"Gewicht"` | `"Weight"` |
| `"Training"` | `"Exercise"` |

These bypass the i18n system entirely.

#### 4.6 [MED] `_bind()` returns bool without boolean prefix
`services/auth/providers.py:42`

`_bind(…) -> bool` — caller sees `if self._bind(...)` with no indication it returns a boolean. Rename to `_try_bind()` or `_can_bind()`.

#### 4.7 [MED] `_is_remote()` misleading name
`services/sharing.py:37-38`

Checks `":" in handle` but doesn't verify connectivity. Rename to `_has_domain()` or `_is_remote_handle_format()`.

#### 4.8 [MED] `get_instance_keys()` actually generates keys on first call
`services/sharing.py:429`

Misleading name — it creates keys, not just retrieves them. Rename to `ensure_instance_keys()`.

#### 4.9 [MED] `GoalService.progress()` — noun used as computation method
`services/goal.py:53`

Method named like a property but performs computation. Rename to `compute_progress()` or `get_progress()`.

#### 4.10 [MED] `find_all_goals()` — redundant entity suffix
`repositories/goal.py:17`

The `_goals` suffix is redundant since it's already `GoalRepository`. Rename to `find_all()`.

#### 4.11 [LOW] Mixed British/American spelling
`services/sharing.py:30` — `_normalise_handle()` (British "s"). Codebase otherwise uses American English ("color", "authorization"). Rename to `_normalize_handle()`.

#### 4.12 [LOW] Abbreviated function name `_to_dt()`
`services/parser.py:12` — `_to_dt(time_str)` obscure. Rename to `_parse_datetime()`.

#### 4.13 [LOW] Over-abbreviated parameter names
- `services/dashboard_widget.py:363` — `sd` → `source_data_type`
- `routers/entries.py:92` — `dt` → `entry_time`
- `services/dashboard_widget.py:474,508` — `sl`, `n`, `w` → `sleep_summary`, `nutrition`, `weight_point`

#### 4.14 [LOW] Awkward parameter name `by_user_id`
`services/admin.py:106` — `delete_user(user_id, by_user_id)` reads poorly. Use `deleted_by: int`.

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

#### 5.1 [HIGH] `PermissionError` (built-in) instead of `ForbiddenError` in 6 places
`services/sharing.py:376`, `services/leaderboard.py:110,159,277`, `services/plugin/context.py:21`, `services/workout/planner.py:61`

`PermissionError` in Python is for OS file permissions. Authorization failures should use `ForbiddenError` (already defined in `exceptions.py:19`). Because `main.py` catches `ForbiddenError` → 403 but NOT `PermissionError`, these all become 500 errors.

#### 4.2 [HIGH] Bare `except Exception: pass` — 13 locations
| File | Line | Impact |
|---|---|---|
| `routers/entries.py` | 95–96 | Swallows federation sync failures |
| `routers/workout.py` | 169–170 | Swallows exercise creation errors |
| `routers/sharing.py` | 77–79 | Blank ranking data on any error |
| `routers/sharing.py` | 119,161,175,200,214 | 5x leaderboard exception → redirect |
| `routers/admin.py` | 46–47,325–326,361–362,384–385 | 4x backup/plugin operation → no feedback |
| `services/sharing.py` | 322–323 | Swallows JSON parse errors in cache |
| `services/sharing.py` | 713–720 | Swallows WebFinger resolution errors |
| `services/sharing.py` | 795–797,837–839 | Swallows remote fetch errors |
| `services/sharing.py` | 979–980 | Swallows feed assembly errors |
| `services/leaderboard.py` | 230–231,239–240 | Swallows remote fetch errors in rankings |
| `services/backup/service.py` | 93–94 | Swallows retention parse errors |
| `services/plugin/manager.py` | 38–39,50,102–103,130–131,137–139 | 3x bare except, 2x too broad |
| `services/auth/providers.py` | 52–53 | Swallows ALL ldap3 errors → False |

Every bare `except: pass` or `except Exception: pass` MUST either log the error or re-raise a domain exception.

#### 4.3 [HIGH] LLM providers have no error handling on response parsing
`services/insight/providers/openai.py:33`, `anthropic.py:35`, `ollama.py:30`

`data["choices"][0]["message"]["content"]` — any `KeyError`, `IndexError`, or `TypeError` from malformed responses propagates as a 500. Add try/except with a `ValueError(f"Malformed response from {provider_name}")`.

#### 4.4 [HIGH] `print()` statements in production service
`services/open_science.py:65,71,73`

`print("DEBUG: ...")` leaks user data to stdout. Replace with `logger.debug()`.

#### 4.5 [MED] `InvalidCredentialsError` has no exception handler in `main.py`
`exceptions.py:17`

`NotFoundError`, `ConflictError`, `AuthenticationError`, and `ForbiddenError` all have handlers. `InvalidCredentialsError` falls through to the generic handler (500).

#### 4.6 [MED] `AuthService.get_user_from_token` — unhandled `ValueError`
`services/auth/service.py:55-62`

`int(user_id)` on a malformed token with non-numeric `sub` crashes with `ValueError`. Add try/except returning `None` or a specific `AuthenticationError`.

#### 4.7 [MED] `GoalService._extract_current_value` returns `None` on both "no entries" and "parse error"
`services/goal.py:127-128`

`except (ValueError, TypeError): return None` — caller cannot distinguish between the two cases.

---

### 5. SECURITY & CONFIG

#### 5.1 [HIGH] CORS `allow_origins=["*"]` + `allow_credentials=True`
`src/salus/main.py:235-239`

This combination is explicitly forbidden by the CORS spec. Browsers will block cross-origin requests with credentials. If the app is deployed on a different domain, cookie-based auth breaks. Fix: use explicit origins.

#### 5.2 [MED] Default API token and JWT secret are published in AGENTS.md
`config.py:8,10`

`"s3ns0r-h34lth-t0k3n-2026"` and `"change-me-in-production-salus-2026"` are publicly documented. Add startup warnings for production deployments.

#### 5.3 [MED] `schemas/sharing.py:23` — raw `api_token` in response schema
`src/salus/schemas/sharing.py:23`

`PeerConnection.api_token: Optional[str]` — exposes the full API token in API responses. Never expose raw credentials in DTOs.

#### 5.4 [LOW] Admin storage stats uses brittle SQLite path extraction
`services/admin.py:37`

`db_path = settings.database_url.replace("sqlite:///", "")` — produces wrong paths for PostgreSQL URLs and absolute SQLite paths.

---

### 6. MODELS & RELATIONSHIPS

#### 6.1 [HIGH] `DashboardWidget` — FK to user.id + metric_type.id but NO Relationships
`src/salus/models/dashboard.py:13-23`

Missing `TYPE_CHECKING` guard, no `Relationship` definitions. ORM cannot eagerly load owner or metric_type.

#### 6.2 [HIGH] `FederatedAccessLog` — FK to user.id but NO Relationship
`src/salus/models/sharing.py:85-93`

No `Relationship` to `User`, no `TYPE_CHECKING` guard.

#### 6.3 [MED] `ApiToken` — FK to user.id but NO Relationship
`src/salus/models/api_token.py:18-31`

No `Relationship` to `User`.

#### 6.4 [MED] `Goal` — FK to metric_type.id but NO Relationship
`src/salus/models/goal.py:22-35`

Only `User` is in `TYPE_CHECKING` block. `MetricType` relationship missing.

#### 6.5 [MED] `LeaderboardGroup.creator` Relationship has no `back_populates` on `User`
`src/salus/models/sharing.py:56`

All other cross-model relationships use `back_populates`. This one is orphaned.

#### 6.6 [LOW] `models/asymmetric_share.py` — missing `# noqa: F401` on TYPE_CHECKING import
Line 6.

#### 6.7 [MED] `models/__init__.py` — `MetricType` defined inline
Lines 19–36. All other domain models have dedicated files. Move to `models/metric_type.py`.

---

### 7. REPOSITORIES

#### 7.1 [HIGH] `DashboardRepository.reorder()` — N+1 commit problem
`repositories/dashboard.py:19-24`

Each widget position update calls `self.update(widget)` which calls `self.session.commit()`. For 10 widgets, that's 10 separate commits. Should be a single transaction.

#### 7.2 [MED] `Repository.update()` commits immediately — breaks UoW transactions
`repositories/base.py:23-27`

The base class calls `self.session.commit()` inside `update()`. This means the `SqlUnitOfWork.__exit__` rollback on exception cannot undo already-committed operations within the same `with` block.

#### 7.3 [MED] 15 of 18 repos don't explicitly implement their protocol interfaces
Classes like `UserRepository`, `MetricTypeRepository`, etc. do not declare `class UserRepository(Repository[User], IUserRepository)`, even though the protocols exist in `repositories/protocols.py`. Pyright cannot verify interface conformance at class definition time.

#### 7.4 [MED] `SqlUnitOfWork` ignores `HookRegistry` for `MeasurementRepository`
`repositories/unit_of_work.py:107`

`MeasurementRepository.__init__` accepts optional `registry` parameter. The `SqlUnitOfWork` constructor doesn't pass it, so any service using the UoW gets a measurement repo without plugin hook support — while direct DI gets plugin support. Inconsistency.

#### 7.5 [HIGH] Missing repositories for `FederatedAccessLog` + `FederatedMeasurementCache`
These tables are queried via raw `session.exec()` in both services and routers. They need dedicated repositories to eliminate 8+ raw session accesses.

---

### 8. TEMPLATES — i18n

#### 8.1 [HIGH] 45+ hardcoded English strings missing `_()`
**Worst files:**
| File | Count |
|---|---|
| `pages/circadian.html` | ~18 |
| `pages/doctor_view.html` | ~15 |
| `components/admin/backup_table.html` | 6 |
| `pages/sharing_leaderboard.html` | 5 |
| `components/admin/plugin_table.html` | 5 |
| `pages/analytics.html` | ~8 |
| `components/sharing/relationship_list.html` | 4 |
| `base.html:104` | 1 ("Sign In") |

Complete list in appendix.

#### 8.2 [MED] Unused macros — `checkbox.html` and `textarea.html`
`components/ui/checkbox.html` and `components/ui/textarea.html` define macros that no template imports.

---

### 9. TESTS

#### 9.1 [HIGH] Massive engine creation duplication
At least 9 test functions duplicate `create_engine("sqlite://", ...)` + `SQLModel.metadata.create_all()` + `TestClient(app)` + `app.dependency_overrides` instead of using the `conftest.py:client` fixture. `test_admin.py:TestFirstUserAdmin` does this twice.

#### 9.2 [MED] Hardcoded magic credentials — 49 occurrences
`"admin"/"admin"`, `"secret123"`, `"alice@example.com"` repeated throughout 20+ test locations. Use fixtures.

#### 9.3 [MED] Fragile hardcoded database IDs
`test_onboarding.py:59,68` uses `data={"metric_type_id": 1, ...}` — breaks if seed order changes.

---

### 10. LOGGING

#### 10.1 [HIGH] `print()` in production (already listed in 4.4)
`services/open_science.py:65,71,73`

#### 10.2 [MED] `logging.basicConfig` at module level
`main.py:25-26`

If any other module or test runner configures logging first, `basicConfig` does nothing (Python logging gotcha).

#### 10.3 [LOW] No JSON-structured logging
Plain text format. Production improvement.

---

### 11. CONFIG & DEFAULT VALUES

#### 11.1 [MED] Magic string `"#4f46e5"` in 7 places
`models/__init__.py:27`, `schemas/__init__.py:10`, `schemas/sharing.py:9`, `routers/metrics.py:48,81`, `services/sharing.py:220,253`

Define once as `DEFAULT_METRIC_COLOR` in a shared constant.

#### 11.2 [MED] Schema defaults inconsistent with model defaults
3 cases where `MetricTypeCreate.color`, `MetricTypeCreate.icon`, and `ExerciseBase.equipment` duplicate model defaults. Change in model must be mirrored in schema.

#### 11.3 [MED] `WorkoutSessionCreate.started_at` uses naive `datetime.utcnow`
`schemas/workout.py:92`

Model uses timezone-aware `datetime.now(timezone.utc)`. Inconsistency.

#### 11.4 [LOW] `_is_remote()` misleading name
`services/sharing.py:37-38`

Checks `":" in handle` — does not verify remote reachability. Rename to `_has_domain()` or `_is_remote_handle_format()`.

---

### 12. SCHEMAS

#### 12.1 [MED] `EntryResponse` field names don't match `Measurement` model
`schemas/api.py:16-21`

Has `value: str` and `timestamp: datetime` but model has `value_numeric`, `value_text`, `value_json`, `start_time`/`end_time`. Cannot directly map.

#### 12.2 [MED] Untyped `dict` in `CircadianAdviceResponse`
`schemas/circadian.py:34-36`

`sleep_window: dict`, `light_advice: list[dict]` — should be typed Pydantic models.

#### 12.3 [MED] 9 SQLModel tables have no corresponding schemas
`ApiToken`, `SystemConfig`, `DashboardWidget`, `Insight`, `SharingRelationship`, `LeaderboardGroup`, `LeaderboardMember`, `FederatedMeasurementCache`, `FederatedAccessLog`.

---

### 13. MISC

#### 13.1 [LOW] `analytics/dashboard.py:21-36` — `summary()` missing `user_id` parameter
All child services require `user_id` but `DashboardService.summary()` doesn't pass one.

#### 13.2 [MED] `insight/factory.py:24,29` — empty API key defaults
`api_key or ""` — leads to cryptic 401 errors at request time instead of clear startup validation.

#### 13.3 [LOW] `backup/service.py:99` — uses `os.path.join(os.getcwd(), ...)`
Could fail if CWD is not writable. Use `tempfile`.

#### 13.4 [MED] `services/dashboard_widget.py:412` — hardcoded German labels
`"Schritte"`, `"Ziel: ..."`, `"Puls"`, `"Schlaf"`, `"Ernährung"`, `"Gewicht"`, `"Training"` should use i18n.

#### 13.5 [MED] `services/dashboard_widget.py:59-89` — `_delta_str()` returns HTML
Service method returns raw HTML strings (`<span class="widget-delta...">`). View concern leaking into service.

#### 13.6 [LOW] HTMX kudos system uses `onclick` bypassing HTMX
`templates/pages/sharing_feed.html:54` — kudos toggle with direct DOM manipulation. Should use `hx-post` or hx-trigger.

---

## Quick Wins (Small Effort, High Impact)

These 28 issues can each be fixed in <30 minutes:

| # | Category | Issue | Effort |
|---|---|---|---|
| Q1 | Error | Replace all bare `except Exception: pass` with logged warnings (13 locations) | 30 min |
| Q2 | Error | Replace `PermissionError` → `ForbiddenError` in 6 locations | 15 min |
| Q3 | Error | Add `print()` → `logger.debug()` in `open_science.py` | 5 min |
| Q4 | DRY | Extract `aggregate_values()` function (5 → 1 call sites) | 20 min |
| Q5 | DRY | Extract `make_handle(user)` helper (14 → 1 call sites) | 10 min |
| Q6 | DRY | Extract `parse_date()` helper (3 call sites) | 10 min |
| Q7 | Config | Add `DEFAULT_METRIC_COLOR` constant (7 → 1 call site) | 5 min |
| Q8 | Models | Add missing `Relationship` to `DashboardWidget`, `ApiToken`, `Goal`, `FederatedAccessLog` | 15 min |
| Q9 | Templates | Add `_()` wrapper to 45 untranslated strings | 30 min |
| Q10 | Templates | Extract `metric_type_icon` macro (2 templates → 1 macro) | 10 min |
| Q11 | Templates | Extract `rank_badge` macro (2 templates → 1 macro) | 10 min |
| Q12 | Templates | Extract `format_challenge_score` macro (2 → 1) | 10 min |
| Q13 | Templates | Extract `empty_state` macro (4 templates → 1 macro) | 10 min |
| Q14 | Templates | Extract `form_actions` macro (7 → 1) | 10 min |
| Q15 | Templates | Extract `exercise_list_item` template (2 → 1) | 10 min |
| Q16 | DRY | Extract `_webfinger_resolve()` (2 → 1 in sharing.py) | 15 min |
| Q17 | DRY | Extract `_retry_http_request()` (2 → 1 in sharing.py) | 15 min |
| Q18 | DRY | Extract `_change_relationship_status()` (accept/decline dedup) | 10 min |
| Q19 | DRY | Extract Parser base class with guard clause (4 → 1) | 15 min |
| Q20 | DRY | Extract LLM provider base class (3 → 1) | 20 min |
| Q21 | Security | Fix CORS `allow_origins=["*"]` + `allow_credentials=True` | 5 min |
| Q22 | Error | Add `InvalidCredentialsError` handler in `main.py` | 5 min |
| Q23 | Error | Add try/except for `int(user_id)` in `AuthService.get_user_from_token` | 5 min |
| Q24 | Error | Add error handling in LLM providers (3 files) | 15 min |
| Q25 | Models | Add `# noqa: F401` to `asymmetric_share.py` TYPE_CHECKING import | 1 min |
| Q26 | Schemas | Fix `datetime.utcnow` → `datetime.now(timezone.utc)` in workout schema | 2 min |
| Q27 | Schemas | Add typed models for `CircadianAdviceResponse` dict fields | 15 min |
| Q28 | Repos | Add `FederatedAccessLogRepository` + update 2 raw queries | 20 min |
| Q29 | Naming | Rename `get_all()` → `find_all()` on SystemConfigRepository | 5 min |
| Q30 | Naming | Rename `get_by_username()` / `get_by_email()` → `find_by_*()` in UserRepository | 5 min |
| Q31 | Naming | Replace German hardcoded labels in dashboard_widget.py with English + i18n key | 15 min |
| Q32 | Naming | Rename `_bind()` → `_try_bind()` in auth providers | 2 min |
| Q33 | Naming | Rename `_is_remote()` → `_has_domain()` in sharing service | 2 min |
| Q34 | Naming | Rename `get_instance_keys()` → `ensure_instance_keys()` | 2 min |
| Q35 | Naming | Rename `GoalService.progress()` → `compute_progress()` | 2 min |
| Q36 | Naming | Rename `_normalise_handle()` → `_normalize_handle()` (British→American) | 1 min |
| Q37 | Naming | Rename `_to_dt()` → `_parse_datetime()` in parser | 2 min |
| Q38 | Naming | Add `find_all()` abstract method to `Repository` base class | 10 min |

**Total quick-win time: ~6 hours**

---

## Architectural Refactoring Roadmap

### Phase 1: Harden (Quick Wins above)
Fix errors, add missing i18n, extract duplicated logic, fix security issues.

### Phase 2: Split God Classes
1. Split `SharingService` → `RelationshipService` + `FederationKeyService` + `FederationDataResolver` + `FederationFeedService` + `PeerNotificationService`
2. Split `DashboardWidgetService` → extract chart computation to `services/analytics/visualization.py`
3. Split `routers/sharing.py` → `routers/leaderboard.py` + `routers/federation.py`

### Phase 3: Eliminate DIP Violations
1. Add missing repository methods for all 15 raw `session.exec()` call sites
2. Move `run_background_ingest()` to a service, inject dependencies
3. Add `UserService.dismiss_onboarding()` method
4. Encapsulate `api_token_svc._user_repo` behind a public method

### Phase 4: Repository Layer Cleanup
1. Remove `commit()` from `Repository.update()` / `create()` / `delete()` — defer to UoW
2. Fix `DashboardRepository.reorder()` N+1 commit
3. Add explicit protocol implementations to all repos

### Phase 5: Template Modernization
1. Extract all identified macros
2. Reduce inline styles (create CSS utility classes)
3. Full i18n pass

---

## Appendix: Full Issue Catalog

### HIGH (73 issues)

| ID | Category | File | Line | Issue |
|---|---|---|---|---|
| H1 | SRP | `services/sharing.py` | 1-1042 | God class mixing 6+ concerns |
| H2 | SRP | `services/dashboard_widget.py` | 1-581 | Widget CRUD + visualization + charts |
| H3 | SRP | `models/sharing.py` | 18-93 | 3 unrelated domains in one file |
| H4 | SRP | `routers/sharing.py` | 1-706 | 5 route groups mixed |
| H5 | DIP | `services/sharing.py` | 97 | raw session.exec() |
| H6 | DIP | `services/sharing.py` | 317 | raw session.exec() |
| H7 | DIP | `services/sharing.py` | 335 | raw session.exec() |
| H8 | DIP | `services/sharing.py` | 339 | raw session.add() |
| H9 | DIP | `services/sharing.py` | 348 | raw session.add() |
| H10 | DIP | `services/sharing.py` | 432-436 | raw session for SystemConfig |
| H11 | DIP | `services/sharing.py` | 467,472,480,483 | raw session.add() for config |
| H12 | DIP | `services/sharing.py` | 745 | raw session.exec() |
| H13 | DIP | `services/sharing.py` | 848 | raw session.exec() |
| H14 | DIP | `services/sharing.py` | 871 | raw session.exec() |
| H15 | DIP | `services/sharing.py` | 877 | raw session.exec() |
| H16 | DIP | `services/sharing.py` | 902 | raw session.exec() |
| H17 | DIP | `services/sharing.py` | 1005 | raw session.exec() |
| H18 | DIP | `services/leaderboard.py` | 93-98 | raw session.exec() |
| H19 | DIP | `services/leaderboard.py` | 101-106 | raw session.exec() |
| H20 | DIP | `services/leaderboard.py` | 188-194 | raw session.exec() |
| H21 | DIP | `services/workout/planner.py` | 82-83,170 | cast(SqlUoW) + raw session |
| H22 | DIP | `routers/sharing.py` | 255-258 | raw select in access-log route |
| H23 | DIP | `routers/sharing.py` | 441-502 | massive raw DB in federated endpoint |
| H24 | DIP | `routers/sharing.py` | 493-500 | model import + session.add in router |
| H25 | DIP | `routers/sharing.py` | 602-606 | raw select in notify-update |
| H26 | DIP | `routers/sharing.py` | 689-692 | raw select in access-log API |
| H27 | DIP | `routers/webhook.py` | 15-56 | inline service construction (entire graph) |
| H28 | DIP | `routers/onboarding.py` | 29-33 | raw Session in route |
| H29 | DRY | 5 files | — | Aggregation logic 5x duplicated |
| H30 | DRY | `services/sharing.py` | 492-519,677-704 | WebFinger 2x within same file |
| H31 | DRY | `services/sharing.py` | 771-797,811-839 | Retry backoff 2x within same file |
| H32 | DRY | `services/sharing.py` | 124-145,147-165 | accept/decline duplicate logic |
| H33 | DRY | 4 parser files | 14-15 | Guard clause 4x duplicated |
| H34 | DRY | 3 LLM provider files | — | Response parsing 3x duplicated |
| H35 | DRY | `sharing_leaderboard.html` | 39-43,82-92 | Icon + score mapping 2x in templates |
| H36 | DRY | `sharing_leaderboard_detail.html` | 15-19,82-98 | Same icon + score (cross-template) |
| H37 | DRY | `exercises.html`, `workouts.html` | — | Exercise list item 2x |
| H38 | Error | 13 locations | — | Bare `except Exception: pass` |
| H39 | Error | 6 locations | — | `PermissionError` instead of `ForbiddenError` |
| H40 | Error | 3 LLM files | — | No error handling on response parse |
| H41 | Error | `services/open_science.py` | 65,71,73 | `print()` in production |
| H42 | Error | `services/backup/providers.py` | 84-85 | Returns [] on 401/403 |
| H43 | Error | `services/backup/providers.py` | 98-99 | Swallows all WebDAV errors |
| H44 | Error | `services/insight/service.py` | 144-156 | Broad except in LLM fallback |
| H45 | Security | `main.py` | 235-239 | CORS * + credentials |
| H46 | Models | `models/dashboard.py` | 13-23 | FK but no Relationship |
| H47 | Models | `models/sharing.py` | 85-93 | FederatedAccessLog FK, no Relationship |
| H48 | Models | `repositories/dashboard.py` | 19-24 | N+1 commit in reorder() |
| H49 | Repos | multiple | — | Missing repos for FederatedAccessLog, FederatedMeasurementCache |
| H50 | Tests | 9 test functions | — | Engine creation duplicated instead of conftest.py fixture |
| H51 | i18n | `pages/circadian.html` | 21-138 | ~18 untranslated strings |
| H52 | i18n | `pages/doctor_view.html` | 134-195 | ~15 untranslated strings |
| H53 | i18n | `components/admin/backup_table.html` | 8-52 | 6 untranslated strings |
| H54 | i18n | `components/admin/plugin_table.html` | 41-62 | 5 untranslated strings |
| H55 | i18n | `components/sharing/relationship_list.html` | 29-44 | 4 untranslated strings |
| H56 | i18n | `pages/sharing_leaderboard.html` | 64-70 | 3 rank labels + undefined |
| H57 | i18n | `pages/analytics.html` | 3-127 | ~8 untranslated strings |
| H58 | i18n | `pages/workout_active.html` | 97 | Hardcoded placeholder |
| H59 | i18n | `components/plan_form.html` | 13-15 | Untranslated option values |
| H60 | i18n | `components/onboarding/step_modal.html` | 19 | "Done" not wrapped |
| H61 | i18n | `components/admin/upload_modal.html` | 18-35 | 4 untranslated strings |
| H62 | i18n | `base.html` | 104 | "Sign In" not wrapped |
| H63 | Deps | `dependencies.py` | 388-396 | Raw SQL in factory function |
| H64 | Config | `config.py` | 8,10 | Published default secrets |
| H65 | Logging | `services/open_science.py` | 65,71,73 | print() in production |
| H66 | Schemas | `schemas/sharing.py` | 23 | Raw api_token in response DTO |
| H67 | Bug | `analytics/dashboard.py` | 21-36 | summary() missing user_id parameter |
| H68 | Config | `services/admin.py` | 37 | Brittle SQLite path extraction |
| H69 | Naming | `repositories/base.py` | 14 | `get_by_id()` returns None, should be `find_by_id()` |
| H70 | Naming | `repositories/user.py` | 11,16 | `get_by_username()`/`get_by_email()` return None |
| H71 | Naming | `repositories/system_config.py` | 10,13 | `get_all()`/`get_by_key()` wrong prefix for nullable/collection |
| H72 | Naming | 5 repos | — | Three competing prefixes (`list_`, `find_`, `get_`) for same operation |
| H73 | Naming | `services/dashboard_widget.py` | 411-576 | German hardcoded labels bypassing i18n |

### MEDIUM (78 issues)

| ID | Category | File | Line | Issue |
|---|---|---|---|---|
| M1 | DIP | `routers/api.py` | 136 | `measurement_svc.repo` access |
| M2 | DIP | `routers/insight.py` | 34 | `service._uow` access |
| M3 | DIP | `routers/admin.py` | 44-47 | `backup_svc.provider` access |
| M4 | DIP | `dependencies.py` | 93 | `api_token_svc._user_repo` private attr |
| M5 | DIP | `routers/dashboard.py` | 97-98 | Plugin manager via app.state not Depends |
| M6 | Error | `main.py` | — | Missing InvalidCredentialsError handler |
| M7 | Error | `services/auth/service.py` | 55-62 | Unhandled ValueError in int(user_id) |
| M8 | Error | `services/auth/providers.py` | 43 | Lazy import inside method |
| M9 | Error | `services/goal.py` | 127-128 | None on both "no entries" and "parse error" |
| M10 | Error | `services/backup/service.py` | 93-94 | Swallows retention parse errors |
| M11 | Error | `services/plugin/manager.py` | 38-39,50,102,130,137 | 5x too-broad except |
| M12 | Error | `services/parser.py` | 249-251 | ValueError instead of custom UnsupportedPayloadError |
| M13 | Error | `services/insight/factory.py` | 24,29 | Empty API key → cryptic 401 |
| M14 | DRY | `services/sharing.py` + `leaderboard.py` | — | `_is_remote()` vs inline `":" not in handle` |
| M15 | DRY | `services/sharing.py` + `leaderboard.py` | — | Handle construction 14x |
| M16 | DRY | 3 services | — | Date range day iteration 4x |
| M17 | DRY | `sharing_connections.html` + 3 others | — | Empty state pattern 4x |
| M18 | DRY | 7 form templates | — | form_actions pattern 7x |
| M19 | DRY | `sharing_leaderboard.html` + detail | — | Rank badge 2x |
| M20 | DRY | `dashboard.py` + `sharing.py` | — | Date validation 3x |
| M21 | DRY | `onboarding.py`: step_body templates | 8-13 | Metric select dropdown 2x |
| M22 | Models | `models/__init__.py` | 19-36 | MetricType inline instead of own file |
| M23 | Models | `models/api_token.py` | 26 | FK no Relationship |
| M24 | Models | `models/goal.py` | 27 | FK to metric_type, no Relationship |
| M25 | Models | `models/sharing.py` | 56 | LeaderboardGroup.creator no back_populates |
| M26 | Models | `models/sharing.py` | 73-82 | FederatedMeasurementCache no TYPE_CHECKING |
| M27 | Models | `models/__init__.py` | 7-10 | Fragile circular import topology |
| M28 | Schemas | `schemas/__init__.py` | 6-11 | MetricTypeCreate inline instead of own file |
| M29 | Schemas | 3 locations | — | Duplicated default values model↔schema |
| M30 | Schemas | `schemas/workout.py` | 92 | naive datetime.utcnow |
| M31 | Schemas | `schemas/api.py` | 16-21 | EntryResponse ↔ Measurement mismatch |
| M32 | Schemas | `schemas/api.py` | 25 | HealthRecordResponse.id: str vs int |
| M33 | Schemas | `schemas/api.py` | 8-13 | MetricTypeResponse missing fields |
| M34 | Schemas | `schemas/circadian.py` | 34-36 | Untyped dict in response |
| M35 | Schemas | 9 tables | — | No corresponding schemas |
| M36 | Repos | `repositories/base.py` | 23-27 | update() commits immediately |
| M37 | Repos | `repositories/unit_of_work.py` | 107 | Ignores HookRegistry |
| M38 | Repos | `repositories/unit_of_work.py` | 126-133 | UoW rollback can't undo committed ops |
| M39 | Repos | 15 repos | — | Don't explicitly implement protocol interfaces |
| M40 | Repos | — | — | No repos for WorkoutPlanExercise, WorkoutLogEntry |
| M41 | Templates | `circadian.html` | 25+ | Inline styles |
| M42 | Templates | `sharing_leaderboard.html` | 20+ | Inline styles |
| M43 | Templates | `workouts.html` | 20+ | Inline styles |
| M44 | Templates | `settings_tabs/shares.html` | 30+ | Inline styles |
| M45 | Templates | `doctor_view.html` | 15+ | Inline styles |
| M46 | Templates | `components/admin/user_detail.html` | 8+ | Inline styles |
| M47 | Templates | `checkbox.html`, `textarea.html` | — | Unused macros |
| M48 | Templates | `sharing_feed.html` | 54 | Kudos onclick bypasses HTMX |
| M49 | Templates | `workout_active.html` | 109-165 | fetch() bypasses HTMX |
| M50 | Config | `main.py` | 29-61 | NAV_ITEMS hardcoded |
| M51 | Config | `main.py` | 67-68 | Locale only de/en |
| M52 | i18n | `services/i18n.py` | 1-301 | Single 300-line dict, won't scale |
| M53 | i18n | Python source | — | _() only in templates, not in services/routers |
| M54 | i18n | `services/dashboard_widget.py` | 412 | Hardcoded German labels |
| M55 | Logging | `main.py` | 25-26 | basicConfig at module level |
| M56 | DB | `database.py` | 9-17 | SQLite check applies to all non-PG engines |
| M57 | Deps | `dependencies.py` | 464-466 | backup service hard-couples to module engine |
| M58 | Tests | 20+ locations | — | Magic credentials repeated 49x |
| M59 | Tests | `test_onboarding.py` | 59,68 | Fragile hardcoded DB IDs |
| M60 | Tests | `test_dashboard.py` | — | Inconsistent fixture usage (no admin_client) |
| M61 | Config | `main.py` | 211-217 | Plugin router only /api/plugins prefix |
| M62 | Config | `onboarding.py` | 99-118 | _STEP_DEFS in router, not service |
| M63 | Schemas | `schemas/sharing.py` | — | PeerConnection/PeerMetricInfo no Create counterpart |
| M64 | Services | `circadian.py` | 44-126 | Solar calculator mixed with profile mgmt |
| M65 | Services | `dashboard_widget.py` | 59-89 | _delta_str() returns HTML |
| M66 | Services | `dashboard_widget.py` | 283 | type: ignore instead of uid() helper |
| M67 | Error | `services/parser.py` | 222-226 | except ImportError: silently degrades (no warning) |
| M68 | Services | `analytics/orchestrator.py` | 65 | Missing type annotation on weight_trend |
| M69 | Services | `analytics/sleep.py` | 41 | Missing type annotation on record param |
| M70 | Security | `config.py` | 8,10 | No startup warning for default secrets |
| M71 | Access | `doctor_view.html` | 1-353 | No semantic HTML (no main/header/nav) |
| M72 | Tests | — | — | No test for CORS configuration |
| M73 | Schemas | `schemas/__init__.py` | 3 | Schema imports DataType from models layer |
| M74 | Naming | `services/auth/providers.py` | 42 | `_bind()` returns bool without `is_`/`can_` prefix |
| M75 | Naming | `services/sharing.py` | 429 | `get_instance_keys()` actually generates keys on first call |
| M76 | Naming | `services/goal.py` | 53 | `progress()` noun used as computation method name |
| M77 | Naming | `repositories/goal.py` | 17 | `find_all_goals()` redundant entity suffix |
| M78 | Naming | `repositories/base.py` | — | Missing abstract `find_all()` method causes inconsistency |

### LOW (65 issues)

| ID | Category | File | Line | Issue |
|---|---|---|---|---|
| L1 | Naming | `services/sharing.py` | 37 | `_is_remote()` misleading |
| L2 | Naming | `services/sharing.py` | 429 | `get_instance_keys()` actually generates |
| L3 | Naming | `services/parser.py` | 12 | `_to_dt()` abbreviated |
| L4 | Naming | `services/leaderboard.py` | 62 | Parameter ordering unusual |
| L5 | Models | `models/asymmetric_share.py` | 6 | Missing # noqa: F401 |
| L6 | Models | `models/analytics.py` | 118-134 | DTOs in models/ (allowed but unusual) |
| L7 | Schemas | `schemas/__init__.py` | 3 | Schema → model import |
| L8 | Repos | `repositories/__init__.py` | — | Empty file |
| L9 | Repos | `services/workout/planner.py` | — | ValueError instead of ConflictError |
| L10 | Error | `services/backup/service.py` | 99 | os.getcwd() tempfile |
| L11 | Error | `routers/open_science.py` | 27-30 | Broad except returning 400 |
| L12 | Error | `routers/asymmetric_share.py` | 35-36 | Broad except returning 404 |
| L13 | Services | `analytics/calculations.py` | 91 | Hardcoded height/age defaults |
| L14 | Services | `services/insight/providers/` | — | 2x api_key or "" |
| L15 | Config | `config.py` | 33-39 | Missing LLM/Backup docs in AGENTS.md |
| L16 | Config | `database.py` | 12,14 | No echo config flag |
| L17 | Config | `main.py` | 211-217 | Dynamic plugin router prefix |
| L18 | Config | `repositories/unit_of_work.py` | 126-133 | UoW commits on exit |
| L19 | Logging | `main.py` | 25-26 | No JSON-structured logging |
| L20 | i18n | `main.py` | 68 | Default locale is German, not English |
| L21 | Templates | `settings_tabs/shares.html` | 283-561 | alert()/confirm() calls bypass i18n |
| L22 | Templates | `sharing_leaderboard.html` | 63-69 | Hardcoded rank colors (gold/silver/bronze) |
| L23 | Templates | `workout_active.html` | 154 | Hardcoded color #10b981 |
| L24 | Templates | `doctor_view.html` | — | Duplicate font CDN from base.html |
| L25 | Templates | `base.html` | — | var(--color-*) no fallback values |
| L26 | Templates | 3 places | — | Missing aria-label on buttons |
| L27 | Templates | `sharing_leaderboard.html` | 9 | Empty table header |
| L28 | Templates | Meta | — | No favicon or manifest.json |
| L29 | Deps | `dependencies.py` | 449 | Lazy import in function |
| L30 | Deps | `dependencies.py` | — | 496 lines, could split into sub-modules |
| L31 | Tests | — | — | AAA pattern not consistently followed |
| L32 | Deps | `routers/sharing.py` | 24-26 | 303 redirect no request param (cosmetic) |
| L33 | Models | `models/sharing.py` | 80 | FederatedMeasurementCache.value_numeric dead column |
| L34 | Naming | `services/sharing.py` | 30 | `_normalise_handle()` British spelling vs American |
| L35 | Naming | `services/parser.py` | 12 | `_to_dt()` obscure abbreviation |
| L36 | Naming | `services/dashboard_widget.py` | 363 | `sd` parameter too abbreviated |
| L37 | Naming | `services/dashboard_widget.py` | 474,508,547 | `sl`, `n`, `w` single-letter variables |
| L38 | Naming | `routers/entries.py` | 92 | `dt` abbreviation for entry_time |
| L39 | Naming | `services/insight/factory.py` | 9 | `LlmProviderFactory` → `LLMProviderFactory` |
| L40 | Naming | `services/admin.py` | 106 | `by_user_id` awkward parameter name |
| L41 | Naming | `services/dashboard_widget.py` | 21,36 | `_EMPTY_TEXTS`, `_VIZ_TYPE_DEFAULTS` redundant `_` on UPPER_CASE |
| L42 | Naming | `services/analytics/orchestrator.py` | 10,12 | `_RANGE_DAYS`, `_RANGE_BUTTONS` redundant `_` |
| L43 | Naming | `services/analytics/activity.py` | 91 | `_OHLC_DAY_LABELS` redundant `_` on constant |
| L44 | Naming | `repositories/api_token.py` | 31 | `list_all_active()` → `find_all_active()` |
| L45 | Naming | `repositories/workout.py` | 9,48 | `find_all_catalog()` / `get_last_session_for_plan()` inconsistent |
| L46 | Naming | `services/goal.py` | 53 | `progress()` noun instead of action verb |
| L47 | Naming | `repositories/user_identity.py` | 18 | `list_by_user()` → `find_by_user()` for consistency |
| L48 | Naming | `repositories/workout.py` | 48 | `get_last_session_for_plan()` returns None, should be `find_` |
| L49 | Naming | `services/auth/service.py` | 65 | Duplicate `uid` import inside method |
| L50 | Naming | `repositories/leaderboard.py` | 44 | `get_member()` returns None, should be `find_member()` |

---

## Action Priority (Recommended Order)

1. **Fix critical errors:** Q1-Q3, Q21-Q24, H38-H44, H64-H66 (~2h)
2. **Fix security:** H45, H67, H68 (~30 min)
3. **Fix naming inconsistencies:** Q29-Q38, H69-H73, M74-M78 (~45 min)
4. **Add missing model relationships:** H46, H47, M22-M27 (~30 min)
5. **Extract duplicated logic:** Q4-Q7, Q16-Q20, H29-H37 (~2h)
6. **Extract template macros + i18n:** Q9-Q15, H51-H62 (~2h)
7. **Eliminate router DIP violations:** H22-H28, M1-M3, M5 (~2h)
8. **Split God classes:** H1-H4 (~4h)
9. **Repository layer cleanup:** H5-H21, H48-H49, M36-M40 (~3h)
10. **Test cleanup:** H50, M58-M60 (~1h)
11. **CSS Token Foundation (DS Phase 1):** See [`DESIGN.md`](./DESIGN.md) Section 12. Add complete 10-step color scales, dark mode overrides for all 6 families, fix `:root`/`[data-theme="light"]` divergence, add `--color-warning-*` family (~3h)
12. **Component Token Mapping (DS Phase 2):** Replace all 34 hardcoded hex colors with component tokens, consolidate shadow duplicates, add z-index/duration/easing tokens (~2h)
13. **Utility classes + template cleanup (DS Phases 3-4):** Add `.p-*`, `.text-*`, `.d-*`, `.gap-xs` utilities. Replace ~400 inline styles in templates (~3h)
14. **HTMX error handling:** Section 17 — add global `htmx:responseError` listener, `hx-indicator` on all forms, fix `admin.html` modal container, remove `setTimeout+location.reload` anti-pattern, add `<noscript>` fallback (~1h)
15. **Accessibility (WCAG AA):** Section 19 — add `aria-live` regions, modal focus trapping + Escape key, fix color contrast (`#94a3b8→#64748b`), add `role="button"` to dropzone, add `aria-label` to icon buttons, form error `aria-describedby` (~2h)

---

### 15. TEST COVERAGE ANALYSIS

**Overall: 77% (6287 statements, 1474 missed)**

#### Critical Gaps (<50% coverage — business-critical code untested)

| File | Coverage | Missed | Risk |
|---|---|---|---|
| `services/auth/providers.py` | **36%** | 36/56 | LDAP bind + OIDC token exchange entirely untested |
| `services/dashboard_widget.py` | **20%** | 246/308 | All viz builders (`_build_viz`, `_delta_str`, chart computations) untested |
| `routers/workout.py` | **45%** | 66/121 | Session management, log entry creation, exercise catalog untested |
| `services/backup/providers.py` | **51%** | 35/71 | WebDAV upload/download/delete untested |
| `services/analytics/activity.py` | **65%** | 33/94 | `_compute_ohlc_chart()`, `_compute_candlestick_chart()` untested |
| `services/sharing.py` | **58%** | 259/622 | Ed25519 signing/verify, WebFinger resolution, remote data fetch, feed assembly, push notifications — all untested |

#### High Gaps (60-70% — partial coverage, missing key paths)

| File | Coverage | What's Missing |
|---|---|---|
| `services/goal.py` | 62% | Plugin hooks (`validate_goal`, `on_goal_achieved`), `_extract_current_value` |
| `services/leaderboard.py` | 69% | Remote peer ranking computation, bare `except Exception: pass` paths |
| `routers/sharing.py` | **65%** | Federation API error paths (401/404/500), leaderboard edge cases, QR endpoint |
| `services/api_token.py` | 67% | `list_tokens()`, `revoke_token()`, `create_token()` success paths |
| `services/insight/service.py` | 69% | LLM provider fallback, cached vs uncached paths |
| `services/workout/planner.py` | 73% | Exercise update/delete, plan autoregulated targets |
| `services/user.py` | 74% | Password change, username change, `OidcAuthProvider` login flow |
| `routers/admin.py` | 70% | Backup triggers, plugin install/uninstall, user deletion, config editing |
| `services/insight/providers/` | 50% each | All 3 LLM providers (OpenAI, Anthropic, Ollama) — response parsing untested |
| `routers/dashboard.py` | 71% | Date parsing edge cases, plugin widget loading |

#### Moderate Gaps (71-90% — mostly covered)

| File | Coverage |
|---|---|
| `services/auth/service.py` | 72% |
| `services/workout/autoregulation.py` | 75% |
| `services/analytics/nutrition.py` | 78% |
| `services/parser.py` | 87% |
| `services/metric_type.py` | 80% |
| `services/user.py` | 74% |
| `services/backup/service.py` | 83% |
| `services/circadian.py` | 91% |
| `routers/auth.py` | 71% (OAuth redirects) |
| `routers/settings.py` | 87% |

#### Fully Covered (100%)

All models (`models/*.py`), all schemas (`schemas/*.py`), repos (`system_config`, `leaderboard`, `insight`, `asymmetric_share`, `circadian`, `goals`), services (`jwt.py`, `export.py`, `password.py`, `analytics/dashboard.py`), routers (`analytics`, `circadian`, `export`, `onboarding`).

#### Key Observations

1. **Federation/auth provider code is almost entirely untested** — LDAP, OIDC, Ed25519 signing/verification, WebFinger, remote data fetching. This is the most security-critical code in the app and has the lowest coverage.

2. **`DashboardWidgetService` is 20% covered** — all visualization/chart methods untested. Any refactoring of this service (H1 in this audit) is risky without tests.

3. **Federation error paths untested** — 401/404/500 responses in `federated_shared_data()`, invalid signatures, expired tokens, malformed dates — all uncovered.

4. **Bare `except Exception: pass` paths are collectively uncovered** — 13 instances across the codebase have no test exercising the exception path.

5. **37 files below 80% coverage** — representing the majority of business logic complexity.

6. **Test resource warnings** — `test_webhook.py` and `test_workout.py` generate `ResourceWarning: unclosed database` in multiple test functions, indicating `Session` objects not properly closed after tests.

#### Recommended Coverage Prioritization

| Priority | What | Est. Tests |
|---|---|---|
| 1 | `auth/providers.py` — LDAP bind + OIDC token exchange | 6-8 |
| 2 | `sharing.py` — Ed25519 signing, WebFinger, remote fetch | 12-15 |
| 3 | `dashboard_widget.py` — viz builders, chart computation | 8-10 |
| 4 | `routers/sharing.py` — federation API error paths | 6-8 |
| 5 | LLM providers — response parsing success/failure | 4-6 |
| 6 | `routers/workout.py` — session management | 5-7 |
| 7 | `leaderboard.py` — remote ranking edge cases | 3-5 |
| 8 | `backup/providers.py` — WebDAV upload/download | 3-4 |

**Estimated additional tests needed for 90%+ coverage: ~50-65 tests.**

---

### 16. CSS & DESIGN SYSTEM COMPLIANCE

**Style file:** `static/style.css` (3200 lines). Design spec: `DESIGN.md` (186 lines).

#### 16.1 Token Mismatches & Gaps

| Severity | Issue | Detail |
|---|---|---|
| **CRIT** | `--color-danger` undefined | Used at CSS:2438,2453; templates reference `--color-danger-{50,200,600,800}` — none defined |
| **CRIT** | 12+ undefined CSS variables | `--color-primary-{50-800}`, `--color-success-{50-800}`, `--font-title-sm` — all resolve to nothing |
| HIGH | Primary color 3-way mismatch | DESIGN.md: `#3525cd`, CSS `:root`: `#4f46e5`, CSS `[data-theme="light"]`: `#4d44e3` |
| HIGH | `.alert` redefined | Line 2781 overrides line 732 — merge conflict artifact |
| MED | `surface-variant` from DESIGN.md missing | DESIGN.md specifies `#d3e4fe` — no CSS variable exists |

#### 16.2 Hardcoded Colors That Break Dark Mode

**34 hardcoded hex values** in component CSS (not in `:root`/dark blocks):

| Category | Count | Examples |
|---|---|---|
| Chips (success/warning/error) | 6 | `#ecfdf5`, `#065f46`, `#fffbeb`, `#92400e`, `#fef2f2`, `#991b1b` |
| Sleep segments | 8 | `#fbbf24`, `#60a5fa`, `#818cf8`, `#c084fc` (×2) |
| Segments/macros | 9 | `.segment-*`, `.macro-carbs`, `.macro-fat` |
| Goal statuses | 6 | `.goal-status-fulfilled`, `.goal-status-missed`, `.goal-card-*` |
| QR image | 1 | `.qr-image { background: #fff }` |
| Chart tooltip | 2 | `#chart-tooltip { background: #1e293b; color: #f8fafc }` |

**7 hardcoded `rgba()` shadows** outside token definitions (modal backdrop, mobile nav, user menu, chart tooltip, nav dropdown, peer card hover).

#### 16.3 Component Spec Compliance

| Component | Spec Match | Issue |
|---|---|---|
| `.btn` | 90% | `filter: brightness(0.9)` on hover instead of CSS variable |
| `.btn-secondary` | 95% | Hover uses `primary-fixed` instead of dedicated hover token |
| `.btn-ghost` | 100% | — |
| `.card` | 95% | Has hover shadow but spec says Level 1 = no shadow |
| `.data-grid` | 85% | Row height ~40px, spec says 48px |
| `.top-app-bar` | 100% | Perfect |
| Input fields | 95% | Focus glow uses container color instead of primary |

#### 16.4 CSS Architecture Issues

| Issue | Detail |
|---|---|
| **~18.5% unused classes** | 60 out of 325 CSS classes never referenced in templates |
| **12 `!important`** | 8 questionable — chip overrides, button overrides |
| **2 duplicate shadow tokens** | `--shadow-card-hover` = `--level-2-hover-shadow` (identical) |
| **Undocumented 900px breakpoint** | Lines 2672, 2705 — not in DESIGN.md |
| **Utilities underweight** | Only 2.4% of CSS is utility classes; component CSS is 85% |

#### 16.5 Inline Styles in Templates

**668 `style="..."` occurrences** across templates:

| Category | Count |
|---|---|
| Flexbox layout | ~220 (33%) |
| Font styling | ~180 (27%) |
| Spacing (padding/margin) | ~120 (18%) |
| Color (var/hex) | ~80 (12%) |
| Display/visibility | ~30 (4.5%) |
| Border/background | ~25 (3.7%) |

~40% could use existing utility classes (`.flex-1`, `.gap-sm`, `.text-muted`). Additional utility classes needed: `.text-xs`, `.font-body-sm`, `.font-label-sm`, `.bg-surface-low`, `.border-outline`, `.pill-input`, `.form-input-sm`.

---

### 17. HTMX ERROR HANDLING & PROGRESSIVE ENHANCEMENT

#### 17.1 CRITICAL

| # | File:Line | Issue |
|---|---|---|
| C1 | `admin_tabs/plugins.html:7` | `hx-target="#modal-container"` — **container missing in admin.html**
| C2 | All templates | **Zero `htmx:responseError` handlers** — errors silently swallowed |
| C3 | `add_widget_modal.html:6`, `edit_widget_modal.html:6` | `hx-on::afterRequest` fires on error too → modal closes, user never sees error |
| C4 | All templates | **No `<noscript>` fallback** — app silently broken without JS |

#### 17.2 HIGH

| # | File:Line | Issue |
|---|---|---|
| H1 | All templates | **3 `hx-indicator` uses across 80+ templates** — zero loading feedback for 97% of interactions |
| H2 | `workouts.html:82,124`, `exercises.html:42` | `hx-swap="none"` + `setTimeout(() => location.reload())` — race condition, defeats HTMX |
| H3 | `main.py:271-316` | Exception handlers don't check `HX-Request` header → redirects broken for HTMX |
| H4 | 5 forms | `hx-target="body"` + `RedirectResponse` — full body swap when partial update would work |
| H5 | 14+ forms | No `action`/`method` alongside `hx-post`/`hx-put` — broken without JavaScript |

#### 17.3 MEDIUM

| # | Issue |
|---|---|
| M1 | Dashboard widgets (`hx-trigger="load"`) — skeleton cards visible without JS |
| M2 | Analytics range/day nav requires JS — no `<a href>` fallback for date ranges |
| M3 | Theme/locale switches use `onchange="this.form.submit()"` — JS required |

---

### 18. HTTP SECURITY HEADERS & CSRF

#### 18.1 CRITICAL

| # | Issue | Location |
|---|---|---|
| C1 | **No security headers** — CSP, X-Content-Type-Options, X-Frame-Options, HSTS, Referrer-Policy, Permissions-Policy all missing | `main.py:232-240` |
| C2 | **No CSRF protection** — 39+ state-changing endpoints unprotected, no middleware, no tokens | Entire codebase |
| C3 | **`Secure` flag missing on `salus_session` cookie** — sent over HTTP, MITM-vulnerable | `routers/auth.py:20-26` |
| C4 | CORS `allow_origins=["*"]` + `allow_credentials=True` — invalid per spec, browsers ignore `*` | `main.py:235-236` |

#### 18.2 MEDIUM

| # | Issue |
|---|---|
| M1 | `salus_locale` cookie missing `secure` + `samesite` (`routers/settings.py:180`) |
| M2 | No rate limiting on any API endpoint |

---

### 19. ACCESSIBILITY (WCAG 2.1 AA)

#### 19.1 CRITICAL

| # | File:Line | WCAG | Issue |
|---|---|---|---|
| C1 | All templates | 4.1.2 | **No `aria-live` regions** — HTMX-swapped content invisible to screen readers |
| C2 | All modals | 4.1.2 | **No modal accessibility** — no `role="dialog"`, `aria-modal`, focus trap, Escape key |
| C3 | `doctor_view.html:145` | 2.1.1, 4.1.2 | `<div class="dropzone" onclick>` — no `role="button"`, `tabindex`, Enter/Space; keyboard users **cannot** upload files |
| C4 | `invite_modal.html:8` | 1.1.1 | QR `<img>` — **no `alt` attribute** |
| C5 | `style.css:1028,1084,1208,1452,1463,1469,1792,1810,1844` | 1.4.3 | `--color-slate-400 (#94a3b8)` on white = **2.99:1** — FAILS AA (needs 4.5:1). Used in 10+ text elements |
| C6 | `components/ui/input.html:9-11` | 3.3.1 | Error `<span>` — no `aria-describedby` linking to input |
| C7 | `components/ui/input.html:7` | 3.3.2 | Required fields — no visual indicator (asterisk/text) |

#### 19.2 HIGH

| # | Issue |
|---|---|
| H1 | **Focus styles missing** on `.btn-secondary`, `.btn-ghost`, `.btn-danger`, `.btn-sm`, `.top-app-bar-link`, `.day-navigator__date`, links |
| H2 | **Icon-only buttons without `aria-label`** — close buttons, widget actions, Material Symbols spans |
| H3 | `components/ui/alert.html` — missing `role="alert"` (manually added by some templates, not all) |
| H4 | Auth pages (`login.html`, `register.html`) — no `<h1>` heading, only `<h2>` |
| H5 | Dark mode `--color-slate-500: #94a3b8` on `#111827` = **3.25:1** — FAILS AA |

---

### 20. API DESIGN CONSISTENCY

#### 20.1 CRITICAL

| # | File:Line | Issue |
|---|---|---|
| C1 | `main.py:271-315` vs routers | **Inconsistent error format** — exception handlers use `{"error": "..."}` while `HTTPException` uses `{"detail": "..."}` |
| C2 | `sharing.py:429-706` | **6 federation endpoints missing `response_model`** — no OpenAPI schema |
| C3 | `api.py:37,51,67,115` | `assert result.id is not None` — crashes 500 instead of controlled error response |

#### 20.2 HIGH

| # | Issue |
|---|---|
| H1 | **Unversioned endpoints** — `/webhook`, `/api/plugins` (missing `/api/v1/`) |
| H2 | `main.py:232` | `FastAPI(title="salus")` — no `version`, `description`, `docs_url` |
| H3 | No pagination headers (`Link`, `X-Total-Count`) on list endpoints (except `api.py`) |
| H4 | No rate limiting headers on any endpoint |

#### 20.3 MEDIUM

| # | Issue |
|---|---|
| M1 | Inconsistent router prefix registration — mix of `include_router(prefix=...)` vs hardcoded paths |
| M2 | `asymmetric_share.py` router mixes HTML (`/share/doctor/*`) and API (`/api/v1/shares/*`) routes |
| M3 | `goals.py:85` — `response_class=HTMLResponse` but returns `RedirectResponse`
