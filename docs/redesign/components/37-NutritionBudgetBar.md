# Komponentenspezifikation: `NutritionBudgetBar.svelte`
**Pfad:** `frontend/src/lib/components/food/NutritionBudgetBar.svelte`  
**Kategorie:** Molekül / Kompakter Makro-Balken  
**Zweck:** Kompakte lineare Fortschrittsleiste für Dashboard-Kacheln und Mahlzeiten-Header mit verbleibendem Kalorien- und Makronährstoff-Budget.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🥩 Protein: 140g / 180g (78%)            [ Noch 40g übrig ] │
│ ██████████████████████████████████░░░░░░░░░                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  label: string;
  current: number;
  target: number;
  unit: string; // "g", "kcal"
  color?: string; // z.B. var(--color-nutrition)
  showRemaining?: boolean;
}
```
