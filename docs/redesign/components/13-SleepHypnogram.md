# Komponentenspezifikation: `SleepHypnogram.svelte`
**Pfad:** `frontend/src/lib/components/dashboard/SleepHypnogram.svelte`  
**Kategorie:** Organismus / Schlafarchitektur-Analyse  
**Zweck:** Glatte, interpolierte Spline-Flächenkurve der nächtlichen Schlafphasen (Tiefschlaf, REM-Schlaf, Leichtschlaf, Wachphasen) mit Zyklus-Markern und Schlafschuld-Indikator.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🌙 SCHLAFARCHITEKTUR & ERHOLUNG               7h 45m (92% Score)│
│ [ Schlafschuld: 0 Min (Ausgeglichen) ]        HRV: 64 ms    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Wach   ──┐           ┌──┐                                  │
│  REM      │     ┌─────┘  │        ┌──┐                      │
│  Leicht   └─────┘        └────────┘  └────────┐             │
│  Tief   █████████                      ██████ └──────────── │
│         ─────────────────────────────────────────────────── │
│         23:00   01:00   03:00   05:00   07:00   07:45       │
│                                                             │
│   Phasen-Zusammenfassung:                                   │
│   🔵 Tiefschlaf:  1h 35m (20%)   🟣 REM-Schlaf: 2h 05m (27%)│
│   🔷 Leichtschlaf:3h 40m (48%)   ⚪ Wach:       0h 25m (5%) │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface SleepStageInterval {
  stage: 'deep' | 'rem' | 'light' | 'awake';
  start: string; // ISO
  end: string; // ISO
  durationSeconds: number;
}

interface Props {
  totalSeconds: number;
  stages: SleepStageInterval[];
  sleepDebtMinutes?: number;
  avgHrv?: number;
  score?: number;
  size?: 'compact' | 'standard' | 'large';
}
```
