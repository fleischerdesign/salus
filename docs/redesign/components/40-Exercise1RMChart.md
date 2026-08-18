# Komponentenspezifikation: `Exercise1RMChart.svelte`
**Pfad:** `frontend/src/lib/components/workouts/Exercise1RMChart.svelte`  
**Kategorie:** Organismus / Kraftkurven- & 1RM-Diagramm  
**Zweck:** Dediziertes Kraftentwicklungs-Diagramm für eine spezifische Übung mit berechnetem 1RM-Verlauf (Epley/Brzycki), getätigten Arbeitssätzen und goldenen Sternchen bei neuen persönlichen Rekorden (PR).

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 📈 KRAFTENTWICKLUNG: BANKDRÜCKEN               [ Aktuell: 94 kg 1RM ]│
├─────────────────────────────────────────────────────────────┤
│ 100 kg ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
│                                             ★ (94 kg PR!)   │
│  90 kg ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ╭─╯ ─ ─ ─ ─ ─ ─ ─ ─ │
│                     ★ (88 kg)       ╭───╯                   │
│  80 kg ─ ─ ─ ─ ─ ╭──╯ ─ ─ ─ ─ ─ ╭───╯ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
│         ─────────┴──────────────┴────────────────────────── │
│         Mai 2026                Juni 2026           Aug 2026│
│                                                             │
│   Gesamtfortschritt: ↗ +14 kg (+17.5%) in 12 Wochen         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface StrengthDataPoint {
  date: string;
  weightKg: number;
  reps: number;
  estimated1RM: number;
  isPR: boolean;
}

interface Props {
  exerciseName: string;
  history: StrengthDataPoint[];
  current1RM: number;
  formula?: 'epley' | 'brzycki';
}
```
