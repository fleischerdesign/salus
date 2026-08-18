# Komponentenspezifikation: `InteractiveChart.svelte`
**Pfad:** `frontend/src/lib/components/charts/InteractiveChart.svelte`  
**Kategorie:** Organismus / Universelles Analyse-Diagramm  
**Zweck:** Hochpräzises, reaktives SVG-Diagramm mit wählbaren Zeitintervallen (7T, 30T, 90T, 1J, Max), 7-Tage-EMA-Glättung, Zielbändern, Konfidenztrichter und magnetischem Crosshair-Scrubbing.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ KÖRPERGEWICHT & 7-TAGE-EMA                      [ 7D | 30D | 90D | 1Y ]│
├─────────────────────────────────────────────────────────────┤
│  84 kg ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│
│          ╭──╮                                               │
│  82 kg ──╯  ╰╮     [ Ziel-Band 78-80 kg ░░░░░░░░░░░ ]       │
│              ╰───╮    ╭──── 7-Tage-EMA                      │
│  80 kg ─ ─ ─ ─ ─ ╰────╯ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│
│         ─────────────────────────────────────────────────── │
│         1. Aug       10. Aug       20. Aug       30. Aug    │
│                                                             │
│  Tooltip bei Hover: [ 14. Aug: 81.8 kg • EMA: 82.1 kg • ↘ -0.3kg ]│
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface DataPoint {
  date: string; // ISO oder YYYY-MM-DD
  value: number;
  secondaryValue?: number; // z.B. Diastolisch bei Blutdruck
  context?: string; // z.B. "Push Day absolviert"
}

interface Props {
  data: DataPoint[];
  metricCode: string;
  unit: string;
  color?: string;
  showEma?: boolean;
  targetRange?: { min: number; max: number; label?: string };
  confidenceInterval?: Array<{ date: string; lower: number; upper: number }>;
  height?: number; // Standard: 280px
  timeRange?: '7D' | '30D' | '90D' | '1Y' | 'ALL';
  onTimeRangeChange?: (range: '7D' | '30D' | '90D' | '1Y' | 'ALL') => void;
}
```
