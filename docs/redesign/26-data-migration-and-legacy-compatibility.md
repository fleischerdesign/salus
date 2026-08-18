# Salus 2.0 — Datenmigration & Legacy-Kompatibilität
**Dokument:** `26-data-migration-and-legacy-compatibility.md`  
**Status:** Verbindlich  
**Zweck:** Unterbrechungsfreie und verlustfreie Migration von bestehenden Salus-Datenbanken (SQLite / PostgreSQL) und Browser-IndexedDB-Ständen auf Salus 2.0.

---

## 1. Zero-Data-Loss Migrations-Prinzipien

1. **Kein Tabellen-Drop:** Bestehende Messwerte (`measurement`), Benutzer (`user`), Mahlzeiten (`meal`) und Workouts (`workout_log_entry`) bleiben zu 100% erhalten.
2. **Kanonische Metrik-Zuordnung:** Alle historischen Messwerte werden auf die kanonischen globalen `metric_code`-Strings (ADR-001) gemappt.
3. **Automatische Schema-Aktualisierung beim Backend-Start:**

```python
# In database.py / Lifespan Handler:
def run_migrations(engine: Engine) -> None:
    SQLModel.metadata.create_all(engine)
    # Führt idempotente Daten-Seeding- & Transformations-Skripte aus
```

---

## 2. Dexie Client-Migration (v1 -> v15)

Der Service Worker und Dexie migrieren den lokalen Browser-Speicher beim ersten Start automatisch:

```typescript
// Bestehende Outbox-Einträge bleiben erhalten und werden vor dem Versionswechsel geflusht:
await offlineService.syncAll();
```
