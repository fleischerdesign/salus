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

### ✅ P0 — Migrations-Drift (committed: a5e182f)
- Migration `002_complete_schema` (10 Tabellen, 3 Composite-Indizes), `env.py` auf
  `import salus.models` vereinheitlicht, Plugin-Discovery aus Migrations-Runtime entfernt.
- `alembic check`: keine Drift, 43 Tabellen == 43 Modelle.

### ✅ P1 — auto-CRUD strategy-bewusst (committed: 0a14b36)
- Write-Routen abgeleitet aus `EntityMeta.strategy`: `user_scoped`/`shared_nullable`/`relational`
  → volles CRUD; `global`/`append_only` → read-only (list/get).
- Ausgeschlossen aus generischem CRUD: `user`/`api_token` (Credential-Hashes),
  dedicated Domains, relational children, interne Tabellen.
- Getippte Responses (`response_model=SQLModel`), `_PLURAL_MAP` sauber, Startup-Assert
  `_validate_entity_map()`.

### ✅ P2 — Enricher-Registry + Habit-Pilot (committed: bea35b9)
- `services/entity_enrichment.py`: Enricher- + Response-Model-Registry für berechnete Reads.
- Habit CRUD → auto-CRUD (mit Stats-Enricher); Router auf `check`/`stats`-Actions reduziert.
- Update-Route registriert PUT + PATCH; Ownership-Verstoß → 404 (Konvention).

### ✅ P3 — Doppel-Routing + Legacy entfernt (committed: 9dbdda4)
- Goals → auto-CRUD (dedizierte Routen entfernt).
- `/entries`-Legacy entfernt → `/measurements` (mit generischem `?field=value`-Filter).
- `POST/PUT/DELETE /metrics` + `MetricPreferenceCreate` entfernt →
  `/user-metric-preferences` (mit Entity-Validator: metric_code muss existieren, keine Duplikate).
- auto-CRUD akzeptiert JWT + API-Token (`get_current_user_or_api`).
- Tote Measurement-Query-Methoden entfernt.

### ✅ P4 — Action-Router verschlanken (committed: b6c9833)
- journal, medication, food_item, mood_entry, mood_tag → auto-CRUD (journal/medication/food
  mit registrierten Response-Models, mood_tag read-only).
- Router auf Actions reduziert: journal (date/search), medication (today/schedule/log/inventory),
  food (search/barcode/frequent).
- meal/recipe/achievement bleiben dediziert: komponierte Aggregate (items/ingredients/progress)
  sind nicht als flache auto-CRUD-Zeilen darstellbar.
- `JournalEntry.entry_date` mit `default_factory=date.today`; Pipeline serialisiert `date`-Felder.

### ✅ P5 — Streaks aus Router (committed: a42c961)
- `AchievementService.get_streaks`; Set-basierte Repo-Queries, N+1 und Inline-SQL aus dem Router entfernt.

### ✅ P6 — DIP reparieren (committed: a82b985)
- `BackgroundIngestionService` via Factory-Injection; gemeinsamer `serialize_record()` (WritePipeline + Commands);
  `build_autoregulation_service(uow)`.

### ✅ P7 — uuid7_str in utils-Modul (committed: 9c68c01)
- 24 Modelle/Dateien importieren aus `salus.utils` statt `services._helpers`; Layer-Inversion aufgelöst.

### ✅ P8 — Soft-Delete-Bugfix (committed: 1fd18da)
- `find_all`/`find_recent_entries` filtern `deleted_at`.

### ✅ P9 — Frontend (committed: e75fbba)
- ESLint 69→0 (inkl. `_-`-Präfix-Konvention), `SalusDB.notDeleted()`-Helper (7× `null as any` eliminiert),
  Dead Code entfernt, `handleSave` typisiert, a11y-Fixes. svelte-check 0/0, vitest 119, Build OK.
- **Offen:** `useQuery()`-Ausrollen über ~29 Seiten (bewusst delegiert — mechanischer, großer Einzelrefactor).

### ✅ P10 — Streak zentralisiert (committed: df688c4)
- 3× Streak → `services/achievement/streak.py:compute_streak`.
- **Ehrlicher Befund:** `find_by_user`-Methoden sind signatur-varianter (limit/is_active/Optional/
  andere Namen) — kein generischer Basis-Helper, ohne echte Duplikations-Eliminierung wäre reine Abstraktion.

### ✅ P11 — Konstanten zentral (committed: a58c339)
- `services/constants.py`; Dedup-TTL (3 Quellen), Batch-Sizes, Workout-Defaults verdrahtet.
- **Ehrlicher Befund:** Exercise-Validierung war bereits DRY (eine `find_by_name`-Repo-Methode,
  drei kontextbedingte Fehlerformen).

### ✅ P12 — Fehler-Taxonomie (committed: f92868c)
- planner `ValueError`→`ConflictError`/`RuntimeError`, dashboard_widget `ValueError`→`NotFoundError`,
  circadian loggt statt still zu schlucken.

### P13 — God-Objects splitten (offen)
- sync.py Admin/Community/Config, dashboard_widget VizBuilder, orchestrator 7 Domänen.
  Risikoreichster Refactor — characterization-getrieben, eigenes Arbeitspaket.

### P14 — Write-Kanäle + Events + AGENTS.md (offen)
- AGENTS.md: Konzept-Regel dokumentieren. Event-Publishing in Services als dokumentierter Folge-Punkt.
