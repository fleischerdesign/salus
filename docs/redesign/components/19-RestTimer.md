# Komponentenspezifikation: `RestTimer.svelte`
**Pfad:** `frontend/src/lib/components/workouts/RestTimer.svelte`  
**Kategorie:** Molekül / Schwebender Workout-Pausentimer  
**Zweck:** Schwebender Countdown-Balken während des Live-Trainings mit automatischer Aktivierung nach Satz-Abschluss, Pausieren, +30s Schnell-Verlängerung und akustischem/haptischem Signal bei 0s.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ ⏱️ PAUSE: 01:14 (von 01:30)       [ +30s ]  [ ⏸️ ]  [ ⏩ Skip]│
│ ██████████████████████████████░░░░░░░░░░                    │
└─────────────────────────────────────────────────────────────┘
```

- **Position:** Schwebendes Panel am unteren Bildschirmrand (`fixed bottom-20 left-4 right-4 max-w-lg mx-auto z-40`).
- **Design:** `bg-surface-900 text-white rounded-2xl p-4 shadow-2xl backdrop-blur-md border border-surface-700`.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  initialSeconds: number; // z.B. 90
  running: boolean;
  onFinish?: () => void;
  onSkip?: () => void;
}
```
