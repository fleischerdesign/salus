# Komponentenspezifikation: `Slider.svelte`
**Pfad:** `frontend/src/lib/components/ui/Slider.svelte`  
**Kategorie:** Atom / Bereichs-Schieberegler  
**Zweck:** Feinfühliger Bereichs-Schieberegler (z. B. für RPE 1–10, Kaloriendefizit -1000 bis +1000 kcal oder Fastenstunden 12–24h) mit gefüllter Spur, Einrast-Stufen und schwebender Werte-Blase.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ Tägliches Defizit: [ -500 kcal ]                            │
│                                                             │
│       -1000 kcal          -500 kcal           +1000 kcal    │
│  ───────│────────────────────(•)──────────────────│──────── │
│         [████████████████████]░░░░░░░░░░░░░░░░░░░░░         │
└─────────────────────────────────────────────────────────────┘
```

- **Spur:** `h-2 bg-surface-200 rounded-full overflow-hidden`.
- **Gefüllte Spur:** `bg-primary-500 rounded-full`.
- **Daumen:** `h-6 w-6 bg-white border-2 border-primary-500 rounded-full shadow-md active:scale-110 transition-transform`.
- **Werte-Blase:** Schwebendes Tooltip-Badge über dem Daumen beim Ziehen.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  label?: string;
  ticks?: Array<{ value: number; label: string }>;
  disabled?: boolean;
  onchange: (val: number) => void;
}
```
