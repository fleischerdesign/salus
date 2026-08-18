# Salus 2.0 — Offline-Sync & Concurrency Matrix
**Dokument:** `18-offline-sync-and-concurrency-matrix.md`  
**Status:** Verbindlich  
**Zweck:** Deterministische Behandlung von Offline-Modus, Browser-Crashes während aktiver Trainingssessions, SSE-Wiederverbindung mit Exponential Backoff und Datenintegrität.

---

## 1. Crash-Resistenz für aktive Workouts (State Recovery)

Wenn der Browser während eines aktiven Trainings geschlossen wird oder abstürzt:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 CRASH-RECOVERY WORKFLOW                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Bei jedem Satz-Eintrag (`mutate()`):                                                 │
│    • Satz wird lokal in `workout_log_entry` + `outbox` persistiert.                     │
│    • `active_session_state` wird in IndexedDB mit Zeitstempel & Satzliste aktualisiert.│
│                                                                                         │
│ 2. Beim Neustart der App / Neuladen der Seite:                                          │
│    • Layout-Check: Existiert ein unvollendeter `active_session_state` (< 12h alt)?      │
│    • Wenn JA: Banner oben auf dem Dashboard:                                            │
│      "Laufendes Workout 'Push Day A' (vor 18 Min) wiederherstellen? [ Fortsetzen ]"     │
│    • 1 Klick bringt den Nutzer mit exaktem Timer und allen Sätzen zurück.              │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. SSE-Live-Sync Reconnect-Strategie (Exponential Backoff)

```typescript
export class LiveEventsManager {
  private retryCount = 0;
  private maxDelayMs = 30000; // Max 30s

  private scheduleReconnect(onSync: () => void) {
    const delay = Math.min(1000 * Math.pow(1.5, this.retryCount), this.maxDelayMs);
    const jitter = Math.random() * 500;
    
    setTimeout(() => {
      this.retryCount++;
      this.connect(onSync);
    }, delay + jitter);
  }
}
```
