# Komponentenspezifikation: `ForecastSimulator.svelte`
**Pfad:** `frontend/src/lib/components/analytics/ForecastSimulator.svelte`  
**Kategorie:** Organismus / Interaktiver Prognose-Simulator  
**Zweck:** Interaktiver Defizit- & Trainingsschieberegler zur Simulation von Körperfett-, Gewichts- und Kraftverläufen über 30 bis 180 Tage mit 80%-Konfidenztrichter.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🔮 PROGNOSE-SIMULATOR (Forecast Lab)                        │
├─────────────────────────────────────────────────────────────┤
│  Tägliches Kaloriendefizit: [ -500 kcal / Tag ]             │
│  ├───●──────────────────────┤ (-1000 kcal bis +1000 kcal)   │
│                                                             │
│  Prognose in 90 Tagen (am 15. November 2026):               │
│  ⚖️ Zielgewicht: 76.5 kg  (↘ -5.9 kg)                       │
│  📉 Fettmasse:   -5.2 kg  |  💪 Muskelmasse: Erhalten       │
│                                                             │
│  [ Visualisierter 80%-Konfidenztrichter im Verlaufschart ]  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  currentWeightKg: number;
  currentBodyFatPercent?: number;
  tdeeKcal: number;
  deficitKcal?: number;
  horizonDays?: number; // 30, 60, 90, 180
  onDeficitChange?: (newDeficit: number) => void;
}
```
