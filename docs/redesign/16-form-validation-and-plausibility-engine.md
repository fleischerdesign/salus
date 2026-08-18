# Salus 2.0 — Formular-Validierung & Plausibilitäts-Engine
**Dokument:** `16-form-validation-and-plausibility-engine.md`  
**Status:** Verbindlich  
**Zweck:** Mathematische und klinische Plausibilitätsgrenzen für alle ~40 physiologischen Metriken, automatische Ausreißer-Erkennung und länderspezifisches Parsen von Zahlen.

---

## 1. Lokalisierungs- & Zahlen-Parsing-Regeln

Benutzer in Deutschland geben Zahlen oft mit Komma ein (`82,5 kg`), während die englischsprachige Welt Punkte nutzt (`82.5 kg`).

```typescript
export function parseUserNumber(input: string): number | null {
  if (!input || input.trim() === '') return null;
  // Ersetzt Komma durch Punkt und entfernt Leerzeichen
  const sanitized = input.trim().replace(/\s/g, '').replace(',', '.');
  const val = Number(sanitized);
  return isNaN(val) ? null : val;
}
```

---

## 2. Klinische Plausibilitätsgrenzen & Validierungs-Matrix

Wenn ein eingegebener Wert außerhalb der physiologischen Grenzen liegt, blockiert Salus nicht stur die Eingabe, sondern blendet ein auffälliges Warn-Badge (`DataQualityFlagBadge.svelte`) ein: *"Wert liegt außerhalb des physiologischen Bereichs. Tippfehler?"*

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              PHYSIOLOGISCHE GRENZWERTE DER METRIKEN                                   │
├──────────────────────┬─────────────┬──────────────┬───────────────┬────────────────────────────────────┤
│ Metrik-Code          │ Einheit     │ Minimal-Wert │ Maximal-Wert  │ Plausibilitäts-Kriterium           │
├──────────────────────┼─────────────┼──────────────┼───────────────┼────────────────────────────────────┤
│ `systolic_bp`        │ mmHg        │ 60           │ 260           │ Typischerweise > diastolic_bp + 20 │
│ `diastolic_bp`       │ mmHg        │ 40           │ 150           │ Typischerweise < systolic_bp - 20 │
│ `resting_heart_rate` │ bpm         │ 30           │ 220           │ Ruhepuls unter 30 bpm = extrem     │
│ `blood_glucose`      │ mg/dL       │ 30           │ 600           │ < 54 = Schwere Hypoglykämie        │
│ `blood_glucose`      │ mmol/L      │ 1.7          │ 33.3          │ SI-Einheiten Konvertierung         │
│ `body_weight`        │ kg          │ 25           │ 350           │ Tägliche Änderung > 3kg = Flag     │
│ `body_fat`           │ %           │ 3.0          │ 65.0          │ Physiologisches Minimum Männer ~3% │
│ `ldl_cholesterol`    │ mg/dL       │ 10           │ 400           │ Ziel < 70 mg/dL (ESC)              │
│ `hdl_cholesterol`    │ mg/dL       │ 10           │ 150           │                                    │
│ `triglycerides`      │ mg/dL       │ 20           │ 1500          │ > 500 = Pankreatitis-Risiko        │
│ `creatinine`         │ mg/dL       │ 0.2          │ 15.0          │ Nierenmarker                       │
│ `hba1c`              │ %           │ 3.5          │ 18.0          │ Diabetes-Referenz                  │
│ `daily_steps`        │ Schritte    │ 0            │ 100.000       │                                    │
│ `water_ml`           │ ml          │ 0            │ 15.000        │                                    │
│ `workout_reps`       │ Wdh.        │ 1            │ 100           │                                    │
│ `workout_rpe`        │ Skala       │ 1.0          │ 10.0          │ RPE nach Borg/RIR (0.5 Schritte)   │
└──────────────────────┴─────────────┴──────────────┴───────────────┴────────────────────────────────────┘
```

---

## 3. Automatische Einheiten-Konvertierung (Dual-Layer)

Die Datenbank speichert intern immer die kanonische Basiseinheit (z.B. `kg`, `mg/dL`, `ml`). Die Anzeige konvertiert nahtlos in die per-User Präferenz:

```typescript
export const CONVERSIONS = {
  // Blutzucker & Cholesterin (mg/dL <-> mmol/L)
  glucose_mg_to_mmol: (mg: number) => mg / 18.0182,
  glucose_mmol_to_mg: (mmol: number) => mmol * 18.0182,
  cholesterol_mg_to_mmol: (mg: number) => mg / 38.67,
  cholesterol_mmol_to_mg: (mmol: number) => mmol * 38.67,

  // Gewicht & Distanz
  kg_to_lbs: (kg: number) => kg * 2.20462,
  lbs_to_kg: (lbs: number) => lbs / 2.20462,
  km_to_miles: (km: number) => km * 0.621371,
  miles_to_km: (miles: number) => miles / 0.621371
};
```
