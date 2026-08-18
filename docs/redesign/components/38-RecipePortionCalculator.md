# Komponentenspezifikation: `RecipePortionCalculator.svelte`
**Pfad:** `frontend/src/lib/components/food/RecipePortionCalculator.svelte`  
**Kategorie:** Organismus / Dynamischer Rezept- & Portions-Skalierer  
**Zweck:** Interaktive Rezept-Anpassung mit Live-Neuberechnung aller Zutatenmengen, Gesamtkalorien und Makros beim Ändern der Portionsanzahl (z.B. von 1 auf 4 Portionen).

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🍲 HÄHNCHEN-REIS-CURRY                           [ Favorit ⭐]│
│ Portionsanzahl:  [ ➖ ]  [ 2 Portionen ]  [ ➕ ]             │
├─────────────────────────────────────────────────────────────┤
│  NÄHRWERTE PRO PORTION:                                     │
│  540 kcal • 42g Protein • 64g Carbs • 12g Fett              │
├─────────────────────────────────────────────────────────────┤
│  ZUTATENLISTE (Skaliert auf 2 Portionen):                   │
│  • Hähnchenbrustfilet:  400 g (vorher 200g)                 │
│  • Basmatireis:         160 g (vorher 80g)                  │
│  • Kokosmilch (light):  150 ml (vorher 75ml)                │
│  • Brokkoli & Paprika:  300 g (vorher 150g)                 │
│                                                             │
│  [ + In heutige Mahlzeit loggen ]   [ 🛒 Auf Einkaufsliste ]│
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface RecipeIngredient {
  name: string;
  baseAmount: number;
  unit: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
}

interface Props {
  recipeName: string;
  baseServings: number;
  currentServings: number;
  ingredients: RecipeIngredient[];
  onServingsChange: (newServings: number) => void;
  onLogMeal: (servings: number) => Promise<void> | void;
}
```
