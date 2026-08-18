# Komponentenspezifikation: `CorrelationMatrix.svelte`
**Pfad:** `frontend/src/lib/components/analytics/CorrelationMatrix.svelte`  
**Kategorie:** Organismus / Statistische Korrelations-Heatmap  
**Zweck:** Akademisch exakte, interaktive Heatmap-Matrix zwischen zwei beliebigen Gesundheitsfaktoren mit Pearson ($r$), Spearman ($\rho$), Signifikanz-Sternchen ($p < 0.05$) und natürlicher Sprachsynthese.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🧠 BIOMETRISCHE KORRELATIONS-MATRIX              [ 90 Tage ]│
├─────────────────────────────────────────────────────────────┤
│                 Schritte   Schlafdauer  HRV (rMSSD) Koffein │
│  Schritte         1.00       +0.64**      +0.42*     -0.12  │
│  Schlafdauer     +0.64**      1.00        +0.78***   -0.58**│
│  HRV (rMSSD)     +0.42*      +0.78***      1.00      -0.45* │
│  Koffein         -0.12       -0.58**      -0.45*      1.00  │
│                                                             │
│   Erkenntnis des Tages:                                     │
│   💡 Starker Zusammenhang (r = +0.78, p < 0.001):          │
│   Jede zusätzliche Stunde Schlaf erhöht deine nächtliche    │
│   HRV am Folgetag im Schnitt um 6.2 ms.                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface CorrelationPair {
  factorA: string;
  factorB: string;
  r: number; // Pearson Koeffizient (-1 bis +1)
  p: number; // p-Wert
  n: number; // Stichprobengröße (Tage)
  significance: 'none' | '*' | '**' | '***';
}

interface Props {
  matrix: CorrelationPair[];
  selectedPair?: CorrelationPair | null;
  onSelectPair?: (pair: CorrelationPair) => void;
}
```
