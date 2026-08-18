# Komponentenspezifikation: `WorkoutSplitCard.svelte`
**Pfad:** `frontend/src/lib/components/workouts/WorkoutSplitCard.svelte`  
**Kategorie:** Molekül / Trainingsplan-Kachel  
**Zweck:** Ästhetische Plan-Kachel für Trainings-Splits (z. B. *„Push Day A“*, *„Pull Day B“*, *„Leg Day Heavy“*) mit Zielmuskel-Chips, Übungsanzahl, geschätzter Dauer und 1-Klick Start-Button.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🏋️ PUSH DAY A (Brust, Schulter, Trizeps)       [ 45-60 Min ] │
│ 6 Übungen • 18 Sätze • Letztes Mal: vor 3 Tagen (Dienstag)   │
├─────────────────────────────────────────────────────────────┤
│  Zielmuskeln:                                               │
│  [ Brust ]  [ Vordere Schulter ]  [ Trizeps ]  [ Bauch ]    │
│                                                             │
│  Übungs-Auszug:                                             │
│  1. Bankdrücken (4× 8-10)     2. Schrägbank KH (3× 10-12)   │
│  3. Seitheben (4× 12-15)      4. Trizepsdrücken (3× 12-15)  │
│                                                             │
│  [ ✏️ Plan bearbeiten ]           [ ▶️ Jetzt Workout starten ]│
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  planId: string;
  planName: string;
  muscleGroups: string[];
  exerciseCount: number;
  setCount: number;
  estimatedMinutes: number;
  lastPerformedDate?: string | null;
  onStartWorkout: () => void;
  onEditPlan?: () => void;
}
```
