# Komponentenspezifikation: `BiomarkerHistoryTable.svelte`
**Pfad:** `frontend/src/lib/components/labs/BiomarkerHistoryTable.svelte`  
**Kategorie:** Organismus / Tabellarische Zeitreihen-Matrix  
**Zweck:** Akademisch exakte, tabellarische Matrix für Ärzte zur Gegenüberstellung aller Biomarker über mehrere Blutentnahmen hinweg mit Trendpfeilen, Grenzwert-Highlights und Min/Max-Ausweisung.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📊 TABELLARISCHER LABOR-VERGLEICH                          [ mg/dL ↔ mmol/L ]│
├─────────────────────────────────────────────────────────────────────────────┤
│ Biomarker      Referenz      14.08.2026    12.02.2026    10.08.2025   Trend │
│ ─────────────────────────────────────────────────────────────────────────── │
│ Nüchterngluk.  70 - 99       84 mg/dL      88 mg/dL      92 mg/dL     ↘ -8  │
│ HbA1c          < 5.7 %       5.1 %         5.2 %         5.4 %        ↘ -0.3│
│ LDL-C (ESC)    < 70 mg/dL    68 mg/dL      76 mg/dL ⚠️   84 mg/dL ⚠️  ↘ -16 │
│ HDL-C          > 40 mg/dL    62 mg/dL      58 mg/dL      54 mg/dL     ↗ +8  │
│ Triglyzeride   < 150 mg/dL   74 mg/dL      88 mg/dL      104 mg/dL    ↘ -30 │
│ hs-CRP (Entz.) < 1.0 mg/L    0.4 mg/L      0.6 mg/L      0.9 mg/L     ↘ -0.5│
│ 25-OH Vit. D3  40 - 70 ng/mL 54 ng/mL      42 ng/mL      28 ng/mL ⚠️  ↗ +26 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface LabDrawColumn {
  id: string;
  date: string;
  doctorOrLab: string;
}

interface BiomarkerRow {
  code: string;
  name: string;
  unit: string;
  referenceRange: string;
  values: Record<string, number | null>; // labDrawId -> value
  trend: 'improving' | 'stable' | 'worsening' | 'neutral';
}

interface Props {
  columns: LabDrawColumn[];
  rows: BiomarkerRow[];
  unitMode?: 'conventional' | 'si'; // mg/dL vs. mmol/L
  onToggleUnitMode?: () => void;
}
```
