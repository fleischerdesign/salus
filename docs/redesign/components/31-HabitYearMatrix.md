# Komponentenspezifikation: `HabitYearMatrix.svelte`
**Pfad:** `frontend/src/lib/components/habits/HabitYearMatrix.svelte`  
**Kategorie:** Organismus / 365-Tage-Konsistenz-Matrix  
**Zweck:** GitHub-Style 52-Wochen-Jahresmatrix zur Visualisierung von Langzeit-Konsistenz und Streaks für eine Gewohnheit.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 📅 JAHRES-KONSISTENZ (Letzte 52 Wochen)        🔥 284/365 TAGE│
├─────────────────────────────────────────────────────────────┤
│ Jan      Mär       Mai       Jul       Sep       Nov        │
│ ░░███░░████████████████████████████████████████████████████ │
│ ░░█████████████████████████████████████████████████████████ │
│                                                             │
│ Weniger [ ░ ] [ ▒ ] [ ▓ ] [ █ ] Mehr                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  habitId: string;
  yearHistory: Record<string, number>; // "YYYY-MM-DD" -> count (0, 1, 2...)
  color?: string; // z.B. Habit-Farbe
  onSelectDay?: (date: string) => void;
}
```
