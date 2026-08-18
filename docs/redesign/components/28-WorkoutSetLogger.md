# Komponentenspezifikation: `WorkoutSetLogger.svelte`
**Pfad:** `frontend/src/lib/components/workouts/WorkoutSetLogger.svelte`  
**Kategorie:** Organismus / Live-Satz-Erfassung  
**Zweck:** Extrem ergonomische, touch-optimierte Satz-Erfassungszeile für den aktiven Trainingsmodus mit großen Ziffernfeldern, Vorwochen-Referenz, 1RM-Kalkulation und RPE/RIR-Selector.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🏋️ BANKDRÜCKEN (Kurzhanteln)                 [ 1RM: 94 kg ] │
├─────────────────────────────────────────────────────────────┤
│  SATZ   VORWOCHE        GEWICHT (kg)    WDH.      RPE   [ ✓ ]│
│  ────────────────────────────────────────────────────────── │
│  [ 1 ]  80 kg × 10    [  82.5  ]  [  10  ]  [ @8 ]  [ ✓ ] │
│  [ 2 ]  80 kg × 8     [  82.5  ]  [   8  ]  [ @9 ]  [ ✓ ] │
│  [ 3 ]  80 kg × 8     [  80.0  ]  [   -  ]  [ -- ]  [   ] │
│                                                             │
│  [ + Satz hinzufügen ]               [ ⏱️ Auto-Rest: 90s ]  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface WorkoutSet {
  setNumber: number;
  type: 'warmup' | 'normal' | 'drop' | 'failure';
  weightKg: number | null;
  reps: number | null;
  rpe?: number | null;
  completed: boolean;
  previousWeightKg?: number;
  previousReps?: number;
}

interface Props {
  exerciseId: string;
  exerciseName: string;
  sets: WorkoutSet[];
  targetReps?: string; // z.B. "8 - 12"
  restSeconds?: number;
  onUpdateSet: (index: number, updated: WorkoutSet) => void;
  onAddSet: () => void;
  onDeleteSet: (index: number) => void;
  onCompleteSet: (index: number) => void;
}
```
