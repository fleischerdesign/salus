# Salus 2.0 — System-Zustände, Offline-Handling & Edge Cases
**Dokument:** `09-system-states-and-edge-cases.md`  
**Status:** Verbindlich

---

## 1. Übersicht der System-Zustände

```
┌──────────────────────┬─────────────────────────────────────────────────────────────────────────────┐
│ Zustand / Szenario   │ System-Verhalten & UI-Darstellung                                           │
├──────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ **Initiales Laden**  │ Keine Spinner-Überlagerung. Shimmer-Skeletons in exakter Kachelgröße.       │
│ **Offline-Betrieb**  │ Vollständige Funktionalität. Änderungen landen in Dexie-Outbox.             │
│                      │ Dezente Status-Pille im Header zeigt „Offline (3 Änderungen wartend)“.      │
│ **Sync-Konflikt**    │ Nicht-blockierender automatischer Abgleich; bei echtem Datenkonflikt        │
│                      │ öffnet sich der `ConflictDialog` mit Feld-für-Feld Vergleich.               │
│ **Session-Ablauf**   │ Kein harter Absturz. Subtiler Warn-Banner im Header mit 1-Klick Re-Login.   │
│ **Leere Datenstände**│ Keine toten Bildschirme: Motivierende Empty States mit konkreten Vorschlägen│
│                      │ und 1-Klick Erfassungs-Start.                                               │
│ **Extremwerte / Bug**│ Plausibilitäts-Warnung bei Eingabe (z.B. "Puls > 220 bpm - Tippfehler?").   │
└──────────────────────┴─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Offline-First & Dexie Outbox Queue

1. **Lokale Verfügbarkeit:** Alle Daten liegen in der IndexedDB (`db`). Jedes Lesen geschieht lokal mit 0ms Latenz.
2. **Offline-Writing:** Wird ein neuer Datensatz erfasst (z. B. 500ml Wasser im Flugzeug), wird er sofort lokal persistiert und in die `outbox`-Tabelle eingereiht.
3. **Automatischer Reconnect:** Sobald der Browser wieder online ist, flusht `syncEngine.flush()` alle wartenden Operationen in strikter FIFO-Reihenfolge an `POST /api/v1/sync/push`.
4. **Status-Anzeige:**
   - Online & Live: Grüner Punkt `● Live Sync`.
   - Offline mit Warteschlange: Amber-Pille `● Offline (4 ungesynct)`.
   - Fehler: Roter Punkt mit 1-Klick-Re-Sync-Button.

---

## 3. Konflikt-Auflösung (Field-Level Merging)

Bei gleichzeitigen Änderungen auf zwei Geräten:
- Im Hintergrund synchronisiert Salus nach dem *Last-Write-Wins*-Prinzip.
- Bei interaktiven Bearbeitungskonflikten öffnet sich der `ConflictResolver`:
  - Feld-für-Feld Vergleich (Server-Version vs. Lokale Version).
  - Radio-Buttons für jedes Feld (`Meine Version behalten` vs. `Server-Version übernehmen`).
  - 1-Klick Auflösung.

---

## 4. Shimmer-Skeletons & Layout-Shift-Vermeidung

- Kein Screen darf beim Laden springen (CLS = 0).
- Alle Ladezustände nutzen `SkeletonCard.svelte`, die exakt dieselben Abmessungen, Ränder und Radien wie die Zielkomponenten besitzen.
