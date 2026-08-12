# Codebase-Hygiene: Plan (P0–P14)

Branch: `feat/codebase-hygiene` (von `develop`). Jede Phase = 1 Commit (Conventional
Commits), `just check` davor, `gen-schema` bei API-Vertragswechsel (sonst schlägt
`test_openapi_contract.py::TestSchemaDrift` fehl). Sicherheitsnetz: 430 Backend- +
119 Frontend-Tests.

## Zielarchitektur (eine Regel)

> **auto-CRUD = der einzige Weg für CRUD. Action-Router = nur Domain-Verben. Sync = Sync.**
> Einen Datensatz lesen/erstellen/ändern/löschen → auto-CRUD. Eine *Handlung*
> (abhaken, starten, generieren) oder *Aggregation* (today-View, progress, stats)
> → Action-Endpoint. Alles andere → Sync.

- **auto-CRUD ist strategy-bewusst:** Die REST-Oberfläche spiegelt `EntityMeta.strategy`.
  `user_scoped`/`shared_nullable`/`relational` → volles CRUD; `global`/`append_only`
  → read-only (list/get), Schreiben nur über dedizierte Endpoints.
- **Getippt statt dict:** SQLModel-Klassen als `response_model` (kein `_serialize_row`).
- **Enricher-Registry:** pro Entity optionaler `enricher(uow, user_id, rows)`-Hook für
  berechnete Reads (z. B. Habit-Statistiken) — in der Service-Ebene, nicht in `entity_meta.py`.
- **Startup-Assert:** keine Write-Routen für `global`/`append_only`; kein Entity doppelt
  (auto-CRUD + dediziert). Abgeleitete Invariante, keine Liste.
- **Write-Kanäle dokumentiert + Events überall:** WritePipeline (Sync + auto-CRUD),
  Services (Actions), Command-Handler — alle publizieren nach Commit SSE-Events.
- **Kein deprecated Code:** `/entries`, `POST/PUT/DELETE /metrics`,
  `MetricPreferenceCreate`, toter `metric_type`-Eintrag werden entfernt.
- **Naming:** `_PLURAL_MAP` mit sauberen Hyphen-Plurals für alle Entities
  (z. B. `metric_group → metric-groups`, `metric_definition → metric-definitions`).

## Akzeptierte Trade-offs (dokumentiert, nicht versteckt)

1. **Zwei Write-Engines:** WritePipeline (Sync-Konzepte: client_id, dedup) für
   Sync+auto-CRUD; Services für Actions. Vereinheitlicht über Events, bewusst nicht
   „alles durch eine Maschine" (würde Sync-Konzepte in REST injizieren).
2. **Read-Duplikation Metriken:** `/metric-definitions` (generisch, roh) +
   `/metrics/groups` (getypt, gemerged Produktansicht) koexistieren getrennt per Name.

## Phasen

### P0 — Migrations-Drift
- Neue Migration `002_complete_schema` (`down_revision=5fba86e6f14d`, append-only).
- 10 fehlende Tabellen: `food_item`, `meal`, `meal_item`, `recipe`, `recipe_ingredient`,
  `medication`, `medication_schedule`, `medication_log`, `medication_inventory`,
  `user_source_preference` — exakt aus den SQLModel-Modellen.
- 3 Composite-Indizes `measurement`: `ix_measurement_user_metric_time`,
  `ix_measurement_user_updated_at`, `ix_measurement_user_created_at`.
- `migrations/env.py`: fehlende Modell-Imports (`food`, `medication`,
  `user_source_preference`); Plugin-Discovery aus der Migrations-Runtime entkoppeln.
- Verify: `alembic upgrade head` auf frische SQLite-DB → 43 Tabellen; `alembic check`.

### P1 — auto-CRUD strategy-bewusst
- `register_auto_crud` leitet Routen aus `EntityMeta.strategy` ab
  (`global`/`append_only` → read-only).
- Startup-Assert: keine Write-Routen für global/append_only.
- `_PLURAL_MAP`: saubere Hyphen-Plurals; toter `metric_type`-Eintrag raus.
- Verify: `test_rest_api`, `gen-schema`, `test_openapi_contract`.

### P2 — Enricher-Registry + Coverage-Erweiterung
- Enricher-Registry in Service-Ebene; Enricher für habit (stats), ggf. weitere.
- `habit`, `mood_entry`, `journal_entry`, `medication`, `food_item`, `meal`, `recipe`,
  `user_metric_preference` in auto-CRUD aufnehmen (getypt).
- Verify: neue auto-CRUD-Tests; bestehende Domain-Tests grün.

### P3 — Doppel-Routing auflösen + Legacy entfernen
- `goal` → auto-CRUD (dedizierte CRUD-Routen aus `api_misc` entfernen; Actions behalten).
- `/entries`-Router (`api.py`) entfernen (Legacy, `/measurements` übernimmt).
- `POST/PUT/DELETE /api/v1/metrics` + `MetricPreferenceCreate` + `metric_svc.create/update/delete` entfernen.
- Verify: `test_entries`, `test_api`, `test_metrics`, `gen-schema`.

### P4 — Action-Router verschlanken
- Dedizierte Router nur noch Domain-Verben: habit (`check`, `stats`), medication
  (`today`, `schedule/log/inventory`, refill), mood (upsert, stats), journal
  (`date`, search), workout (sessions start/complete/active/recent), insight
  (`generate`), notification (`read`, `read-all`), goal (`progress`).
- Boilerplate-CRUD entfernen (durch auto-CRUD abgedeckt).
- Verify: Domain-Tests grün, `gen-schema`.

### P5 — Streaks aus Router
- `AchievementService.get_streaks(user_id)`; SQL aus `api_achievement.py:86-152`
  in Repos (Set-Queries, kein N+1); Inline-Imports, `# noqa: E712`, `len(list(logs))` raus.
- Verify: `test_achievements`, `test_user_scoping`.

### P6 — DIP reparieren
- `background_ingestion.py`: `uow_factory` + gebaute Services statt inline
  `SqlUnitOfWork`/Repos/`SharingService.create`.
- `commands/workout.py`: `_calculate_recovery` über injizierte Factory; gemeinsamer
  Serializer statt `_serialize_session`/`_serialize_log_entry`.
- Verify: `test_workout`, `test_webhook`, `test_command_handlers`.

### P7 — uuid7_str in neutrales Modul
- Neu `src/salus/utils.py` mit `uuid7_str()`; 20 Modelle + `commands/workout.py` + `_helpers.py` umstellen.
- `uid()`, `make_handle`, `DEFAULT_METRIC_COLOR` bleiben in `_helpers.py`.
- Verify: pyright, ruff, Tests.

### P8 — Soft-Delete-Bugfix
- `MeasurementRepository.find_all` + `find_recent_entries` um `deleted_at.is_(None)` ergänzen.
- Verify: neue Tests in `test_entries`/`test_api`.

### P9 — Frontend
- Lint 0 (45 unused vars, 14 any, 4 stale svelte-ignore, 4 a11y, {@html}).
- Dead Code: `useGoalForecast`, Account-Theme-Block, tote Imports.
- `notDeleted()`-Helper in `database.ts` (ersetzt 7× `.equals(null as any)`).
- `handleSave` typisieren; `useQuery` reaktiv machen + ausrollen.
- Verify: `npm run lint` = 0, `npm run check` = 0 warnings, vitest grün.

### P10 — Repo-Boilerplate + Streak zentral
- `Repository[T]`: `find_by_user(user_id, *, order_by)`, `find_by_user_range`, `list_all`;
  zentrale Soft-Delete-Helper. ~17 dünne Repos umstellen (Protokoll-Signaturen unverändert).
- Streak: `habit.py:10` + `mood.py:139` → `achievement/streak.py:compute_streak`.
- Verify: pyright; `test_habits`, `test_mood`, `test_achievements`, `test_user_scoping`.

### P11 — Magic Numbers + Validierung zentral
- Neu `src/salus/services/constants.py`: `DEDUP_TTL_HOURS`, `DAY_WINDOWS`, `CHUNK_SIZES`, `WORKOUT_DEFAULTS`.
- Exercise-Name-Validierung (3×) → 1 gemeinsame Funktion.
- Verify: Tests.

### P12 — Fehler-Taxonomie
- `ValueError` → `NotFoundError`/`ConflictError` (planner, dashboard_widget).
- Kritische `except Exception` präzisieren (circadian:313, plugin/manager, portability).
- Verify: Tests.

### P13 — God-Objects splitten (characterization-getrieben)
- `sync.py`: Admin/Community/Config extrahieren, toter Branch `:319-320` raus.
- `dashboard_widget.py`: VizBuilder → eigenes Modul.
- `analytics/orchestrator.py`: 7 Domänen → Strategie-Klassen.
- Verify: kompletter Testlauf nach jedem Teil-Schritt.

### P14 — Write-Kanäle + Dokumentation
- Events in Domain-Services nachziehen (SSE nach Commit, konsistent zu WritePipeline).
- Legacy-Metrics-Reads bleiben; Konzept-Regel + Trade-offs + Write-Kanäle in AGENTS.md.
- Verify: `just check` komplett.
