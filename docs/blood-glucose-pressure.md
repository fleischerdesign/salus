# Blood Glucose & Blood Pressure

> Status: Blood Pressure implemented via `MetricGroup` (key=`blood_pressure`, input_mode=`combined`).
> Metrics: `systolic_bp`, `diastolic_bp` as NUMBER. Combined input form on group page.
> Blood glucose, pulse, arm/position, dedicated BP model are NOT yet implemented.
> Old `blood_pressure` TEXT metric removed.

## Overview
Dedizierte Widgets und Tracking für Blutzucker und Blutdruck.
Weniger generisch als normale MetricTypes — mit spezifischen Referenzbereichen, Zielzonen und Korrelationen.

**Abgrenzung zu normalen Metrics:** Blutdruck hat zwei Werte (systolisch/diastolisch) plus Puls. Blutzucker hat kontextabhängige Referenzbereiche (nüchtern, vor/nach Mahlzeit). Beide profitieren von spezialisierten Visualisierungen.

## Data Model

### blood_pressure
(Eigenes Model statt generisches Measurement wegen strukturierter Werte)

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| measured_at | datetime | |
| systolic | int | mmHg (z.B. 120) |
| diastolic | int | mmHg (z.B. 80) |
| pulse | int? | bpm |
| arm | enum? | left / right |
| position | enum? | sitting / standing / lying |
| context | enum? | resting / after_exercise / after_meal / medication |
| notes | str? | |
| source | str | manual / device / omron / withings / apple_health |
| device_id | str? | Geräte-ID für Zuordnung |

### blood_glucose
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| measured_at | datetime | |
| value_mgdl | float | mg/dL |
| value_mmol | float | mmol/L (berechnet aus mg/dL / 18.018) |
| measurement_type | enum | fasting / before_meal / after_meal (1h/2h) / bedtime / random / cgm |
| meal_description | str? | Was wurde gegessen (bei after_meal) |
| insulin_units | float? | Insulineinheiten (falls zutreffend) |
| notes | str? | |
| source | str | manual / cgm / freestyle_libre / dexcom / apple_health |
| device_id | str? | |

### glucose_range_config
(Pro User — personalisierte Zielbereiche)

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| measurement_type | str | fasting / before_meal / after_meal / general |
| target_low | float | 70 mg/dL |
| target_high | float | 100 mg/dL (nüchtern) |
| alert_low | float? | 55 (Hypoglykämie-Warnung) |
| alert_high | float? | 180 (Hyperglykämie) |

## Referenzbereiche (Defaults)

### Blutdruck (AHA/ESC 2024 Guidelines)
| Kategorie | Systolisch | Diastolisch |
|---|---|---|
| Optimal | < 120 | < 80 |
| Normal | 120-129 | 80-84 |
| High Normal | 130-139 | 85-89 |
| Hypertonie Grad 1 | 140-159 | 90-99 |
| Hypertonie Grad 2 | 160-179 | 100-109 |
| Hypertonie Grad 3 | ≥ 180 | ≥ 110 |

### Blutzucker (ADA Guidelines)
| Messung | Normal | Prädiabetes | Diabetes |
|---|---|---|---|
| Nüchtern | < 100 | 100-125 | ≥ 126 |
| 2h nach Mahlzeit | < 140 | 140-199 | ≥ 200 |
| HbA1c (aus Lab) | < 5.7% | 5.7-6.4% | ≥ 6.5% |

## API Endpoints

### Blood Pressure
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/health/blood-pressure | List (date range, paginated) |
| POST | /api/v1/health/blood-pressure | Create reading |
| GET | /api/v1/health/blood-pressure/{id} | Get reading |
| PUT | /api/v1/health/blood-pressure/{id} | Update |
| DELETE | /api/v1/health/blood-pressure/{id} | Delete |
| GET | /api/v1/health/blood-pressure/stats | Avg, min, max, morning/evening split |
| GET | /api/v1/health/blood-pressure/classification | Distribution across categories |

### Blood Glucose
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/health/blood-glucose | List (filter: measurement_type, date range) |
| POST | /api/v1/health/blood-glucose | Create reading |
| GET | /api/v1/health/blood-glucose/{id} | Get reading |
| PUT | /api/v1/health/blood-glucose/{id} | Update |
| DELETE | /api/v1/health/blood-glucose/{id} | Delete |
| GET | /api/v1/health/blood-glucose/stats | Avg, time-in-range, variability |
| GET | /api/v1/health/blood-glucose/daily-profile | Average daily curve (CGMs) |
| PUT | /api/v1/health/blood-glucose/ranges | Update personal target ranges |

### Combined
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/health/overview | Current BP + latest glucose + trends |

## Frontend

### Blood Pressure
- **BPReadingForm** — Drei Felder (Systolisch, Diastolisch, Puls)
- **BPChart** — Dual-Line-Chart (Systolisch + Diastolisch) mit farbigen Zonen (grün/gelb/orange/rot)
- **BPStats** — Morgens/Abends Durchschnitt, Variabilität
- **BPClassificationGauge** — Speedometer-Visualisierung: "Optimal"
- **BPDashboardWidget** — Letzter Wert + Mini-Sparkline

### Blood Glucose
- **GlucoseReadingForm** — Wert + Messungstyp-Dropdown
- **GlucoseChart** — Scatter/Line mit farbigen Zielbereich-Bändern
- **GlucoseDailyProfile** — 24h-Durchschnittskurve (besonders sinnvoll für CGM)
- **GlucoseStats** — Time-in-Range %, Avg, Variabilität (CV%)
- **GlucoseDashboardWidget** — Letzter Wert + Typ + Zeit seit letzter Mahlzeit
- **MealImpactView** — Blutzucker vor/nach Mahlzeiten im Vergleich

### Health Overview
- **HealthOverview** — Kombiniertes Dashboard: BP + Glucose + Gewicht + Puls
- Kardiovaskuläres Risiko-Profil (vereinfacht, kein Medizinprodukt!)

## Integration Points
- **Metrics** → Optional: Werte auch als MetricTypes loggen für Analytics-Korrelation
- **Fasting Tracking** → Blutzucker während Fasten-Perioden
- **Food/Meal Logging** → Blutzucker vor/nach Mahlzeiten korrelieren
- **Lab Results** → HbA1c aus Labor importieren
- **Insights/AI Coach** → "Dein durchschnittlicher Nüchtern-Blutzucker ist diese Woche 92 — im optimalen Bereich"
- **Reminders** → "Zeit für die Blutdruck-Messung"
- **PDF Reports** → Blutdruck + Blutzucker als Sektionen im Arzt-Bericht
- **Goals** → "Nüchtern-Blutzucker unter 100 mg/dL halten"
- **Webhook/Device** → Eingehende Daten von Bluetooth-Geräten (Omron, Withings, Dexcom, Freestyle Libre)

## Open Questions
- CGM-Integration (Dexcom, Freestyle Libre): Gibt es APIs? Nightscout-Bridge?
- Blutdruck-Geräte-Integration (Omron, Withings): Bluetooth/BLE parsing?
- Time-in-Range (TIR): Standard 70-180 mg/dL oder personalisierte Bereiche?
- Soll die App Medizinprodukt-Charakter haben? (Nein — Disclaimer: "Kein Medizinprodukt, ersetzen Sie keine ärztliche Beratung")
- HbA1c: Als Blutdruck/Glucose-Feature oder als Lab-Result? (Eher Lab, geschätztes HbA1c aus CGM-Daten wäre ein Nice-to-have)
- Insulin-Tracking für Diabetiker: Wie detailliert? Basal/Bolus, I:E Ratio, Correction Factor?


## Ergänzungen von Philipp
Ich verstehe nicht, warum wir das Metrik system dabei umgehen wollen, das ist ein integraler bestandteil von Salus.. Wir müssen das schon als Metrik implementieren bzw. können wir, wenn das langfristig Sinn macht, gerne Metrikgruppierungen implementieren, wo verschiedene Metriken drunter gruppiert werden. Da kannst du mir gerne mal feedback zu geben. Zumal wir ja auch schon Pulse und sowas als Metrik drin haben.. Also da musst du nochmal nachdenken..

Zu deinen Fragen:
CGM Integrationen können wir gerne auch noch implementieren.
Genau so Blutdruckgerät integrationen
Ob Time in Range oder personalisierte Bereiche kann ich dir nicht beantworten, wir verfolgen aber den anspruch, akademisch professionell zu sein.
Ich denke nicht, dass wir das hier als Medizinprodukt verkaufen sollten.. zu mal das open source ist
HbA1C: Wie gesagt, das was akademisch professionell ist, da kenne ich mich zu wenig mit aus.
Insulin-Tracking: So detailliert wie möglich, oder?