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

### P4 — Action-Router verschlanken (in Arbeit)
- Erkenntnis aus mood/food: diese Domains sind bereits Action-zentrisch (Upsert, Stats,
  Date-Lookup, Search) — kein flaches PUT/DELETE-Boilerplate. Für sie reicht: Entities in
  auto-CRUD aufnehmen (generische Fläche) + Domain-Actions behalten.
- Domains mit echtem CRUD-Boilerplate (journal, medication, food/meal/recipe): CRUD → auto-CRUD,
  Router auf Actions reduzieren.
- Response-Models mit String-Date-Feldern (z. B. `JournalEntryResponse`) erfordern
  Dict-Serialisierung in auto-CRUD (bereits über `_row_to_dict` umgesetzt).

### P5 — Streaks aus Router (offen)
### P6 — DIP reparieren (offen)
### P7 — uuid7_str in utils-Modul (offen)
### P8 — Soft-Delete-Bugfix (offen)
### P9 — Frontend (offen)
### P10 — Repo-Boilerplate + Streak zentral (offen)
### P11 — Magic Numbers + Validierung zentral (offen)
### P12 — Fehler-Taxonomie (offen)
### P13 — God-Objects splitten (offen)
### P14 — Write-Kanäle + Events + AGENTS.md (offen)
