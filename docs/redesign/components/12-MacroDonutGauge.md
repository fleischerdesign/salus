# Komponentenspezifikation: `MacroDonutGauge.svelte`
**Pfad:** `frontend/src/lib/components/food/MacroDonutGauge.svelte`  
**Kategorie:** Organismus / Nährwert- & Kalorien-Visualisierung  
**Zweck:** Ästhetischer Kalorien-Kreisbogen mit 3 farbigen Makronährstoff-Balken (Protein, Kohlenhydrate, Fett) und dynamischem Restkalorien-Budget.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🥗 NÄHRWERTE & KALORIEN                          76% TAGES-BUDGET│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                      (   1.840 kcal  )                      │
│                   /   /   gegessen    \   \                 │
│                  |   |  Noch 560 kcal  |   |                │
│                  |   |   übrig (TDEE)  |   |                │
│                   \   \               /   /                 │
│                      (   P: 140g/180g )                     │
│                                                             │
│   Makronährstoff-Verteilung:                                │
│   🥩 Protein: 140g / 180g (78%)   [ ██████████████░░░░ ]    │
│   🍞 Carbs:   180g / 220g (82%)   [ ███████████████░░░ ]    │
│   🥑 Fett:    52g / 70g (74%)     [ █████████████░░░░░ ]    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  calories: { current: number; target: number };
  protein: { current: number; target: number };
  carbs: { current: number; target: number };
  fat: { current: number; target: number };
  size?: 'compact' | 'standard' | 'large';
}
```

---

## 3. Dynamische Farbkodierung
- **Kalorien:** Neutraler Primär-Gradient (`primary-500`). Bei Überschreitung des Ziels ($>105\%$) sanfter Übergang zu Amber (`warning-500`).
- **Protein (Muskelaufbau / Sättigung):** Signal-Rubin / Koralle (`oklch(0.62 0.20 25)`).
- **Kohlenhydrate (Energie):** Warmes Bernstein / Gold (`oklch(0.70 0.18 70)`).
- **Fett (Hormonsynthese):** Frisches Smaragdgrün (`oklch(0.64 0.16 150)`).
