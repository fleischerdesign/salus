# Blood Work / Lab Results

## Overview
Laborwerte (Blutbild, Hormone, Vitamine, etc.) mit Referenzbereichen tracken.
Biomarker-Verlauf über Jahre — für chronische Erkrankungen oder Gesundheitsoptimierung.

## Data Model

### lab_panel
(Eine Blutabnahme = ein Panel mit mehreren Markern)

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| date | date | Abnahmedatum |
| lab_name | str? | "Hausarzt Dr. Müller" / "Selbstzahler" |
| fasting | bool | Nüchtern? |
| notes | str? | |
| attachment_path | str? | PDF des Laborbefunds |
| created_at | datetime | |

### lab_result
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| panel_id | UUID | FK → lab_panel |
| marker_code | str | FK → lab_marker |
| value | float | |
| unit | str | "mg/dL", "ng/mL" (override der Marker-Default) |
| is_abnormal | bool? | Flag vom Labor |
| reference_range_low | float? | (override) |
| reference_range_high | float? | (override) |

### lab_marker
(Referenztabelle, seeded)

| Column | Type | Notes |
|---|---|---|
| code | str | PK — "hdl_cholesterol" |
| name | str | "HDL-Cholesterin" |
| default_unit | str | "mg/dL" |
| category | enum | lipid / cbc / metabolic / thyroid / hormone / vitamin / inflammation / liver / kidney / iron / other |
| reference_low | float? | Generischer Referenzbereich |
| reference_high | float? | |
| optimal_low | float? | Optimalbereich (enger als Referenz) |
| optimal_high | float? | |
| description | str? | Was bedeutet dieser Wert? |
| sort_order | int | |

## Vordefinierte Marker (Seed — Auswahl)

```
Lipid: total_cholesterol, hdl_cholesterol, ldl_cholesterol, triglycerides, non_hdl_cholesterol
CBC: wbc, rbc, hemoglobin, hematocrit, mcv, mch, mchc, platelets, neutrophils, lymphocytes, monocytes, eosinophils, basophils
Metabolic: glucose_fasting, hba1c, insulin_fasting, homa_ir
Thyroid: tsh, ft3, ft4, tpo_antibodies
Hormone: testosterone_total, testosterone_free, estradiol, progesterone, cortisol, dhea_s
Vitamin: vitamin_d_25oh, vitamin_b12, folate, ferritin, iron, transferrin, transferrin_saturation
Inflammation: crp_hs, esr
Liver: alt, ast, ggt, alp, bilirubin_total
Kidney: creatinine, egfr, urea, uric_acid
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /api/v1/lab/markers | List all markers (categories) |
| GET | /api/v1/lab/panels | List panels (date range) |
| POST | /api/v1/lab/panels | Create panel with results |
| GET | /api/v1/lab/panels/{id} | Get panel details |
| PUT | /api/v1/lab/panels/{id} | Update panel |
| DELETE | /api/v1/lab/panels/{id} | Delete panel |
| GET | /api/v1/lab/results/{marker_code} | History of one marker |
| GET | /api/v1/lab/trends | Multi-marker trend overview |
| POST | /api/v1/lab/import | Import PDF/CSV lab report |

## Frontend

- **LabPanelForm** — Datum, Labor, Marker-Werte-Tabelle (alle Marker einer Kategorie)
- **MarkerChart** — Liniendiagramm mit Referenzbereich-Band (grün/gelb/rot Zonen)
- **LabOverview** — Kategorisierte Karten mit aktuellstem Wert + Trend-Indikator
- **LabTimeline** — Chronologische Panels
- **OptimalRangeIndicator** — Zeigt an ob Wert im optimalen, Referenz- oder kritischen Bereich
- **LabImport** — PDF-Upload oder manuelle Eingabe via Tabellenform

## Integration Points
- **Analytics** → Marker-Trends, Korrelation zwischen Markern (z.B. Vitamin D ↔ Testosteron)
- **Insights/AI Coach** → "Dein HDL ist in 6 Monaten um 15% gestiegen"
- **PDF Report Generation** → Laborwerte in Arzt-Bericht integrieren
- **Goals** → "Vitamin D auf 50 ng/ml bringen"

## Open Questions
- PDF-Import: OCR/Parsing oder nur als Attachment speichern? Komplexität von Labor-PDFs ist hoch.
- Soll es "benutzerdefinierte Marker" geben oder nur aus der Referenztabelle?
- Referenzbereiche: Generisch oder personalisiert (M/W/Alter)?
- Integration mit externen Laboren? (z.B. Thriva, InsideTracker, etc. — APIs?)

## Ergänzungen von Philipp
Hier müssten wir dann auch wieder überlegen, ob wir das ganze nicht auch lieber über unser Metrik system handhaben, oder was am sinnvollsten ist.

Zu deinen Fragen:
OCR bzw. Parsing wäre schon ein must have, aber alternativ kann der User diese Werte selbstverständlich auch manuell eingeben, wie bei metriken üblich.
Keine Ahnung was du mit benutzerdefinierte Marker meinst
Referenzbereiche: Hier gilt wieder die akademische professionalität und präzision!
Wir könnten gerne Integrationen mit externen Laboren bereitstellen.