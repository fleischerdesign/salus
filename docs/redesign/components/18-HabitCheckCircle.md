# Komponentenspezifikation: `HabitCheckCircle.svelte`
**Pfad:** `frontend/src/lib/components/ui/HabitCheckCircle.svelte`  
**Kategorie:** Molekül / Taktiler Gewohnheiten-Toggle  
**Zweck:** Extrem befriedigender Check-Button zum Abhaken täglicher Gewohnheiten mit SVG-Lichtburst, animiertem Häkchen und haptischem Feedback.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│  [ ✓ ] 3L Wasser getrunken              🔥 14-Tage Streak   │
└─────────────────────────────────────────────────────────────┘
```

- **Unchecked:** `h-8 w-8 rounded-full border-2 border-surface-300 bg-transparent hover:border-primary-400`.
- **Checked:** `h-8 w-8 rounded-full bg-success-500 text-white shadow-sm shadow-success-500/30`.

---

## 2. Mikro-Animation (Der Completion-Burst)
Beim Klick auf den Kreis:
1. Der Kreis schrumpft kurz auf `scale(0.85)` (Druck-Gefühl).
2. Das weiße SVG-Häkchen zeichnet sich flüssig von links nach rechts (`stroke-dashoffset: 0`).
3. Kleine goldene/grüne Partikel-Punkte strahlen radial nach außen ab (`opacity: 1 -> 0, translate`).
4. Auf Mobilgeräten wird ein kurzer 25ms Vibrationsimpuls ausgelöst (`navigator.vibrate(25)`).

---

## 3. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  checked: boolean;
  disabled?: boolean;
  color?: string; // z.B. Habit-Farbe
  onchange: (checked: boolean) => Promise<void> | void;
}
```
