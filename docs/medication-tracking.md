# Medication Tracking

## Overview
Verwalte Medikamente, Dosierungen und Einnahmepläne.
Kritisch: Reminder und Vorrat-Warnungen (nicht leer laufen lassen).

## Data Model

### medication
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| name | str | "Ibuprofen 400mg" |
| active_ingredient | str? | "Ibuprofen" |
| strength | str? | "400mg" |
| form | enum? | tablet/capsule/liquid/injection/patch/cream/drops |
| instructions | str? | "Mit Mahlzeit einnehmen" |
| color_hex | str? | Für UI |
| icon | str? | Material Symbols |
| is_active | bool | soft-delete |
| created_at | datetime | |

### medication_schedule
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| medication_id | UUID | FK → medication |
| dosage | str | "1 Tablette" / "5ml" |
| times | json | ["08:00", "20:00"] — Uhrzeiten |
| days_of_week | json? | [1,2,3,4,5] — optional (nur Mo-Fr) |
| start_date | date | |
| end_date | date? | Bei zeitlich begrenzter Einnahme |

### medication_log
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| medication_id | UUID | FK |
| schedule_id | UUID? | FK |
| taken_at | datetime | Wann eingenommen |
| dosage_taken | str? | Abweichung dokumentieren |
| skipped | bool | |
| notes | str? | |

### medication_inventory
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| medication_id | UUID | FK → medication |
| initial_count | int | Packungsgröße |
| remaining_count | int | Aktueller Stand |
| refill_at_count | int | Warn-Schwelle |
| prescription_refills | int? | Noch verfügbare Rezepte |
| next_refill_date | date? | Nächster Arzttermin für neues Rezept |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /api/v1/medications | List medications |
| POST | /api/v1/medications | Create medication |
| PUT | /api/v1/medications/{id} | Update medication |
| DELETE | /api/v1/medications/{id} | Deactivate |
| GET | /api/v1/medications/{id}/schedule | Get schedules |
| POST | /api/v1/medications/{id}/schedule | Add schedule |
| DELETE | /api/v1/medications/schedule/{id} | Remove schedule |
| POST | /api/v1/medications/{id}/log | Log intake |
| GET | /api/v1/medications/{id}/log | Intake history |
| GET | /api/v1/medications/{id}/inventory | Get inventory |
| PUT | /api/v1/medications/{id}/inventory | Update inventory |
| GET | /api/v1/medications/today | Today's schedule |

## Frontend

- **MedicationList** — Karten mit nächster Dosis, Status-Farben (fällig/erledigt/überfällig)
- **MedicationForm** — Name, Wirkstoff, Stärke, Form, Anweisungen
- **ScheduleEditor** — Uhrzeiten-Picker, Wochentage-Toggle
- **InventoryTracker** — Zähler mit Warn-Fortschrittsbalken
- **MedicationTimeline** — Tages-Ansicht: Timeline mit allen Medikamenten
- **Dashboard-Widget** — Heutige Einnahmen als Checkliste

## Integration Points
- **Reminders** → Push-Benachrichtigung zu Einnahmezeiten
- **Metrics** → Optional: Einnahme als MetricType loggen für Korrelation mit anderen Daten
- **Goal** → Adhärenz-Ziel ("90% Einnahme-Treue diese Woche")
- **Insights/AI Coach** → Wechselwirkungs-Check (Datenbank-gestützt), Erinnerung an Refill

## Open Questions
- Wechselwirkungs-Check: Lokale DB? Externe API (OpenFDA)? Nur Warnhinweis ohne medizinische Beratung?
- Push-Reminder: Soll es "Snooze" und "Quittierung" als separate Aktionen geben?
- Soll es eine "As-needed" (Bedarfsmedikation) Option ohne festen Schedule geben?

## Ergänzungen von Philipp

Zu deinen Fragen:
Wechselwirkungs-Check: Das was am akademisch professionellsten ist und für den User am besten.
Push-Reminder: Überlasse ich dir
As Needed klingt gut! 