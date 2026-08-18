# Komponentenspezifikation: `ClinicalGaugeMeter.svelte`
**Pfad:** `frontend/src/lib/components/labs/ClinicalGaugeMeter.svelte`  
**Kategorie:** Molekül / Klinische Präzisions-Diagnostik  
**Zweck:** Visualisierung klinischer Laborwerte und Biomarker im Verhältnis zu evidenzbasierten Referenzbereichen (ESC/EAS, ADA, WHO) mit 4-Zonen-Farbleiste und Messwert-Nadel.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ LDL-CHOLESTERIN                                   68 mg/dL  │
│ [ ℹ️ ESC/EAS Leitlinie: Ziel < 70 mg/dL ]         Status: 🟢 Optimal│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   KRITISCH NIEDRIG   │     OPTIMAL / ZIEL     │    GRENZWERTIG   │    KRITISCH HOCH     │
│     < 40 mg/dL       │      40 - 70 mg/dL     │   70 - 115 mg/dL │      > 116 mg/dL     │
│   ░░░░░░░░░░░░░░░░░░ │ ██████████████████████ │ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│                      │           ▲ (68 mg/dL) │                  │                      │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│ Historischer Verlauf: [ 82 → 74 → 68 mg/dL ] (Letzte 90 Tage ↘) │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Die 4 Klinischen Zonen

1. **Zone 1: Kritisch Niedrig (Blau/Rot):** Wert unterhalb des physiologischen Minimums (`< low_critical`).
2. **Zone 2: Optimal / Leitlinien-Ziel (Smaragdgrün):** Medizinisch wünschenswerter Normalbereich (`low_normal` bis `high_normal`).
3. **Zone 3: Grenzwertig / Erhöht (Amber/Gelb):** Leicht erhöhte Werte ohne akute Gefahr (`high_normal` bis `high_critical`).
4. **Zone 4: Kritisch Hoch (Karminrot):** Pathologisch erhöhte Werte, die ärztlicher Abklärung bedürfen (`> high_critical`).

---

## 3. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  markerName: string; // z.B. "LDL-Cholesterin"
  markerCode: string; // z.B. "ldl_c"
  value: number; // z.B. 68
  unit: string; // z.B. "mg/dL"
  ranges: {
    lowCritical?: number;
    lowNormal: number;
    highNormal: number;
    highCritical?: number;
  };
  guidelineLabel?: string; // z.B. "ESC/EAS Leitlinie 2023"
  history?: Array<{ date: string; value: number }>;
  size?: 'compact' | 'standard' | 'large';
  onclick?: () => void;
}
```

---

## 4. Zeiger-Mathematik & Nadel-Positionierung

Die Position der Nadel ($\text{Position in } \%$) wird nicht-linear berechnet, sodass der optimale Bereich optisch immer ca. 40–50% der Leistenbreite einnimmt (optimale visuelle Spreizung um den Normalwert).

```typescript
function calculateNeedlePercent(value: number, ranges: Props['ranges']): number {
  const { lowNormal, highNormal } = ranges;
  if (value < lowNormal) {
    return Math.max(5, (value / lowNormal) * 30);
  }
  if (value <= highNormal) {
    const fraction = (value - lowNormal) / (highNormal - lowNormal);
    return 30 + fraction * 40; // 30% bis 70% der Balkenbreite
  }
  const maxScale = (ranges.highCritical ?? highNormal * 1.5);
  const fraction = (value - highNormal) / (maxScale - highNormal);
  return Math.min(95, 70 + fraction * 25);
}
```
