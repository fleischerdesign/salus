# Komponentenspezifikation: `MetricTile.svelte`
**Pfad:** `frontend/src/lib/components/ui/MetricTile.svelte`  
**Kategorie:** Molekül / Universelle Messwert-Kachel  
**Zweck:** Hochpräzise, ästhetische Darstellung eines Messwerts mit 7-Tage-Sparkline, Trend-Delta, Zielbalken und optionaler Interaktivität.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ [Icon] SCHRITTE                                  84% ZIEL   │
│ 8.420 / 10.000                                              │
│ ████████████████████░░░░░░░░░░░░░  6.1 km                   │
│ ─────────────────────────────────────────────────────────── │
│ ↗ +1.200 vs. gestern     [ ▂▃▅▇█▇▅ ] (7T-Sparkline)         │
└─────────────────────────────────────────────────────────────┘
```

### 1.1 Größen-Varianten (`size`)
- **`small` (1/3 Zeile auf Desktop / 1 Spalte auf Mobile):**
  - Kompaktes Layout: Icon + Titel oben, Display-Zahl zentriert, kleine Sparkline unten.
- **`medium` (1/2 Zeile auf Desktop):**
  - Standard-Layout: Titel, große Display-Zahl mit Einheit, Fortschrittsbalken zum Ziel, Trend-Delta und Sparkline nebeneinander.
- **`large` (Volle Zeile auf Desktop):**
  - Detailliertes Layout: Umfassendes Spline-Chart mit Tooltips, Min/Max/Avg-Werten und Inline-Aktionen.

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  title: string;
  value: string | number;
  unit?: string;
  color?: string; // z.B. var(--color-vital) oder Hex
  icon?: string; // Material Symbols Name
  sparklineData?: number[];
  delta?: {
    value: string;
    direction: 'up' | 'down' | 'neutral';
    isPositive: boolean; // z.B. Puls runter = positiv, Schritte hoch = positiv
    comparisonText: string; // z.B. "vs. 7T-Schnitt"
  };
  goal?: {
    target: number;
    current: number;
    percent: number;
  };
  size?: 'small' | 'medium' | 'large';
  interactive?: boolean; // Ermöglicht Klick zur Detailansicht
  editMode?: boolean; // Blendet Drag-Handle und Größen-Schalter ein
  onclick?: () => void;
  onSizeChange?: (newSize: 'small' | 'medium' | 'large') => void;
  onDelete?: () => void;
}
```

---

## 3. Typografie & Styling-Regeln

1. **Display-Zahl:**
   - Große Schriftart: `font-size: 2rem` (`32px`), `font-weight: 800`, `letter-spacing: -0.03em`.
   - Tabellenziffern: `font-variant-numeric: tabular-nums lining-nums`.
2. **Einheit (`unit`):**
   - Direkt neben der Zahl in `text-xs font-semibold text-surface-400`.
3. **Delta-Badge:**
   - Pill-Badge mit dezentem Hintergrund: Grün (`bg-success-50 text-success-700`) oder Rot (`bg-error-50 text-error-700`), wenn eine Abweichung positiv oder negativ für die Gesundheit ist.
4. **Sparkline:**
   - Glatter SVG-Pfad (`<path stroke="var(--accent-color)" fill="none" stroke-width="2" stroke-linecap="round" />`) mit flüssigem Verlauf.

---

## 4. Edit-Modus Interaktion

Befindet sich das Dashboard im Edit-Modus (`editMode={true}`):
- Die Kachel zeigt oben links den Drag-Griff (`drag-indicator`).
- Oben rechts erscheint der Größen-Wahlschalter: `[ S ] [ M ] [ L ]`.
- Ein Klick auf `[ M ]` löst sofort `onSizeChange('medium')` aus, was das Raster reaktiv anpasst.
