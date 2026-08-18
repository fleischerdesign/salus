# Komponentenspezifikation: `LabPanelCard.svelte`
**Pfad:** `frontend/src/lib/components/labs/LabPanelCard.svelte`  
**Kategorie:** Molekül / Klinische Labor-Panel-Kachel  
**Zweck:** Übersichtskarte für ein komplettes Blutbild-Panel (z. B. *„Lipidstoffwechsel“*, *„Großes Blutbild“*, *„Schilddrüse & Hormone“*) mit Gesamtstatus-Pille, Testdatum, Arzt-Notiz und aufklappbaren Einzel-Biomarkern.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🧬 LIPIDPROFIL & KARDIOMARKER                     14.08.2026│
│ Labor Dr. Kramer & Kollegen • 6 Biomarker       [ 🟢 Optimal ]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ • LDL-Cholesterin:  68 mg/dL    [ ██████████░░░░ ] 🟢 Optimal│
│ • HDL-Cholesterin:  62 mg/dL    [ ████████████░░ ] 🟢 Optimal│
│ • Triglyzeride:     74 mg/dL    [ ████████░░░░░░ ] 🟢 Optimal│
│ • ApoB:             64 mg/dL    [ █████████░░░░░ ] 🟢 Optimal│
│ • TG / HDL Ratio:   1.19        [ Ideal < 2.0 ]    🟢 Optimal│
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│ [ 📄 PDF-Laborbericht ]          [ ▾ Alle 6 Marker anzeigen]│
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface LabMarkerSummary {
  code: string;
  name: string;
  value: number;
  unit: string;
  status: 'optimal' | 'low' | 'elevated' | 'critical';
}

interface Props {
  panelName: string;
  panelCategory: string; // z.B. "Lipide", "Hämatologie", "Vitamine"
  labDate: string; // YYYY-MM-DD
  doctorNote?: string;
  markers: LabMarkerSummary[];
  overallStatus: 'optimal' | 'attention_needed' | 'critical';
  onOpenDetail?: () => void;
  onExportPdf?: () => void;
}
```
