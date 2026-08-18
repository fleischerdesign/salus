# Komponentenspezifikation: `MealItemRow.svelte`
**Pfad:** `frontend/src/lib/components/food/MealItemRow.svelte`  
**Kategorie:** Molekül / Mahlzeiten-Eintragszeile  
**Zweck:** Interaktive Zeile für einzelne Lebensmittel innerhalb einer Mahlzeit mit Portionsanpassung, Live-Makro-Werten und Wisch-zum-Löschen-Geste.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🍗 Hähnchenbrustfilet (Bio)                    [ 250 g ] ▾  │
│ 412 kcal • 77.5g P • 0g C • 9.0g F             [ 🗑️ Löschen]│
└─────────────────────────────────────────────────────────────┘
```

- **Hintergrund:** `bg-surface-50 hover:bg-surface-100 rounded-xl p-3 flex items-center justify-between transition-colors`.
- **Direktes Editieren:** Klick auf `[ 250 g ]` öffnet ein Inline-Ziffernfeld oder eine Portions-Auswahl (Gramm, Portion, Esslöffel).

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  foodName: string;
  amountGrams: number;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  onUpdateAmount?: (newGrams: number) => void;
  onDelete?: () => void;
}
```
