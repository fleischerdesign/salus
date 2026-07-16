# Body Measurements

> Status: Implemented via `MetricGroup` (key=`body_measurements`, input_mode=`individual`).
> Metrics: `waist`, `hip`, `chest` as NUMBER. Individual entry forms per metric.
> Dedicated body_measurement_type table, DEXA integration, bilateral measurements NOT yet implemented.

## Overview
Erfasse Körpermaße jenseits vom Gewicht: Umfänge, Hautfalten, Körperfett%, etc.
Fortschritts-Tracking mit Vorher-/Nachher-Visualisierung.

## Data Model

### body_measurement_type
(Statische Referenztabelle, seeded)

| Column | Type | Notes |
|---|---|---|
| code | str | PK — "waist", "hip", "chest" |
| label | str | "Taillenumfang" |
| unit | str | "cm" / "mm" / "%" |
| category | enum | circumference / skinfold / composition / other |
| sort_order | int | |

### body_measurement
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| date | date | Messdatum |
| type_code | str | FK → body_measurement_type |
| value | float | |
| side | enum? | left/right/both — für bilaterale Messungen |
| notes | str? | |
| source | str | manual / dexa / impedance / caliper |
| created_at | datetime | |

### body_measurement_session
(Optional: Gruppierung mehrerer Messungen zu einem "Wiegetag")

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK |
| date | date | |
| weight_kg | float? | Gewicht an diesem Tag |
| notes | str? | |
| created_at | datetime | |

## Vordefinierte Typen (Seed)

```
Kategorie "circumference":
  neck, shoulders, chest, biceps_left, biceps_right,
  forearm_left, forearm_right, wrist_left, wrist_right,
  waist, hip, thigh_left, thigh_right, calf_left, calf_right, ankle_left, ankle_right

Kategorie "skinfold":
  chest_skinfold, abdominal_skinfold, thigh_skinfold,
  tricep_skinfold, subscapular_skinfold, suprailiac_skinfold,
  midaxillary_skinfold

Kategorie "composition":
  body_fat_pct, muscle_mass_kg, bone_mass_kg, water_pct,
  visceral_fat, metabolic_age, bmi  (BMI = berechnet aus weight/height²)

Kategorie "other":
  waist_to_hip_ratio, waist_to_height_ratio  (berechnet)
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /api/v1/body-measurements/types | Listet alle Typen |
| GET | /api/v1/body-measurements | List measurements (filter: type, from, to) |
| POST | /api/v1/body-measurements | Create single |
| POST | /api/v1/body-measurements/batch | Create multiple (e.g. whole session) |
| GET | /api/v1/body-measurements/{id} | Get single |
| PUT | /api/v1/body-measurements/{id} | Update |
| DELETE | /api/v1/body-measurements/{id} | Delete |
| GET | /api/v1/body-measurements/trend | Trend over time (per type) |

## Frontend

- **BodyMeasurementForm** — Grid mit allen Typen als Eingabefelder, kategorisiert
- **MeasurementHistory** — Tabelle mit Delta zum vorherigen Wert
- **MeasurementChart** — Liniendiagramm pro Typ über Zeit
- **BodyCompositionOverview** — Radardiagramm/Spider-Chart zur Visualisierung
- **ProgressPhotos** — Optional: Bilder-Upload mit Datum (Side-by-Side-Vergleich)

## Integration Points
- **Analytics** → Körperfett-Trend, Muskelmasse-Trend als MetricTypes
- **Dashboard Widgets** → Body-Measurement-Übersichts-Widget
- **Goals** → "Taillenumfang auf 85cm reduzieren"

## Open Questions
- Progress-Fotos: Sinnvoll? Datenschutz-Bedenken (nur lokal oder verschlüsselt auf Server)?
- Soll BMI automatisch aus weight (Measurements) + height (User-Profil) berechnet werden?
- Wie granular: Jeder Messpunkt einzeln oder immer als Session (mehrere auf einmal)?

## Ergänzungen von Philipp

Hier würde ich auch nochmal darauf Hinweisen, dass wir solche sachen, also alle Messungen am liebsten über das Metrik System lösen wollen..

Zu deinen Fragen:
Ja, Progress Fotos wären großartig! Allerdings wäre es auch super, wenn wir diese verschlüsselt auf dem Server speichern könnten.
Der BMI soll automatisch berechnet werden.
Granularität: Da müssten wir dann erstmal überlegen, wie wir das Metrik System anpassen bzw. wie das am besten umsetzbar wäre..