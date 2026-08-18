# Salus 2.0 — Dexie-Schema & Indexierungs-Strategie
**Dokument:** `17-dexie-schema-and-indexing-strategy.md`  
**Status:** Verbindlich  
**Zweck:** Architektur des lokalen IndexedDB-Speichers (Dexie.js), Compound-Indexe für Zero-Latency Live-Queries und migrationssichere Versions-Verwaltung.

---

## 1. Dexie Versions-Prinzip (AGENTS.md Regel)

1. **Jede Schema-Änderung erhöht die Versionsnummer (`this.version(N)`) inkrementell.**
2. **Niemals bestehende Tabellen-Definitionen in früheren Versionen verändern!**
3. **Compound-Indexe für Multi-Parameter-Abfragen nutzen:**

```typescript
// frontend/src/lib/db/database.ts
export class SalusDatabase extends Dexie {
  // ... Tabellen-Typisierungen ...

  constructor() {
    super('salus_db');

    // Bestehende Basis-Versionen ...
    this.version(1).stores({
      user: 'id, email',
      outbox: 'id, created_at, kind',
      measurement: 'id, metric_code, recorded_at, [metric_code+recorded_at]'
    });

    // Version für Salus 2.0 (Redesign-Indexe für hochperformante Joins)
    this.version(15).stores({
      meal: 'id, log_date, user_id, [user_id+log_date]',
      meal_item: 'id, meal_id, food_item_id',
      workout_log_entry: 'id, workout_plan_id, session_id, exercise_id, [session_id+exercise_id]',
      lab_result: 'id, panel_id, marker_code, [panel_id+marker_code]',
      habit: 'id, user_id, archived_at, [user_id+archived_at]',
      habit_log: 'id, habit_id, log_date, [habit_id+log_date]'
    });
  }
}
```

---

## 2. Reaktivitäts-Sicherheit mit `useQuery`

Alle Bildschirm-Komponenten lesen Daten **ausschließlich** über den `useQuery`-Hook mit reaktiven Abhängigkeiten (`deps`):

```typescript
// Beispiel: Tagesspezifische Mahlzeiten abfragen
const dayMeals = useQuery(
  async () => {
    // Nutzt den Compound Index [user_id+log_date] für O(log n) Abfrage
    return await db.meal.where('[user_id+log_date]').equals([currentUserId, selectedDate]).toArray();
  },
  () => [currentUserId, selectedDate] // Re-Trigger bei Datumswechsel
);
```
