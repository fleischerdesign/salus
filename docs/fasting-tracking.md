# Fasting Tracking

## Overview
Tracke Intervallfasten (Intermittent Fasting) und längere Fastenperioden.
Visualisiere Fasten-Fenster, Essens-Fenster und Fortschritt.

## Data Model

### fasting_session
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| started_at | datetime | Fasten-Beginn |
| ended_at | datetime? | Fasten-Ende (null = läuft noch) |
| target_hours | float | Ziel-Fastenzeit (z.B. 16.0) |
| fasting_type | enum | intermittent / 24h / 36h / 48h / extended / custom |
| water_only | bool | Nur Wasser? |
| notes | str? | |
| mood_during | int? | 1-10 (retrospektiv) |
| difficulty | int? | 1-10 |
| created_at | datetime | |

### fasting_protocol
(Gespeicherte Fasten-Protokolle als Vorlage)

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| name | str | "16:8" |
| fasting_hours | float | 16.0 |
| eating_window_hours | float | 8.0 |
| schedule_type | enum | daily / weekdays_only / custom_days |
| target_days_per_week | int? | 5 (wenn weekdays_only) |
| is_default | bool | Aktives Protokoll |
| created_at | datetime | |

### fasting_check_in
(Optional: Während des Fastens Status tracken)

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| session_id | UUID | FK → fasting_session |
| checked_at | datetime | |
| hunger_level | int? | 1-10 |
| energy_level | int? | 1-10 |
| ketones_mmol? | float? | Optional: Ketone-Messung |
| glucose_mgdl? | float? | Optional: Blutzucker |
| notes | str? | |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /api/v1/fasting/protocols | List protocols |
| POST | /api/v1/fasting/protocols | Create protocol |
| PUT | /api/v1/fasting/protocols/{id} | Update |
| DELETE | /api/v1/fasting/protocols/{id} | Delete |
| GET | /api/v1/fasting/active | Get active session (if any) |
| POST | /api/v1/fasting/start | Start fasting |
| POST | /api/v1/fasting/{id}/end | End fasting |
| GET | /api/v1/fasting/history | Past fasts (paginated) |
| GET | /api/v1/fasting/{id} | Get session detail |
| PUT | /api/v1/fasting/{id} | Update (notes, etc.) |
| DELETE | /api/v1/fasting/{id} | Delete |
| POST | /api/v1/fasting/{id}/check-in | Log check-in |
| GET | /api/v1/fasting/stats | Stats: avg duration, streak, compliance |
| POST | /api/v1/fasting/quick-start | Quick start with protocol |

## Frontend

- **FastingTimer** — Live-Countdown: "15:32 von 16:00 Stunden" mit Fortschrittsring
- **FastingProtocolCard** — Protokoll-Auswahl (16:8, 18:6, 20:4, OMAD, 5:2, etc.)
- **FastingHistory** — Kalender-Heatmap, Liste vergangener Fasten
- **FastingDashboardWidget** — Aktueller Status: Fastend / Essensfenster / Pause
- **FastingChart** — Stunden pro Tag, Rolling Average
- **CheckInPrompt** — Während des Fastens: "Wie hungrig bist du? (1-10)"
- **EatingWindowWidget** — Countdown bis Essensfenster öffnet/schließt

## Integration Points
- **Metrics** → Fasten-Stunden als MetricType für Analytics
- **Blood Glucose** → Korrelation: Blutzucker während Fasten vs. nach Mahlzeiten
- **Mood** → Stimmung während Fasten-Perioden
- **Weight** → Gewichtsverlauf mit Fasten-Compliance-Overlay
- **Goals** → "16h Fasten an 5 Tagen pro Woche"
- **Streaks & Achievements** → "30 Tage Intermittent Fasting Streak"
- **Reminders** → "Dein Essensfenster öffnet in 30 Minuten"

## Open Questions
- Soll es Ketose-Tracking geben? (Ketone-Messgerät-Integration)
- Quick-Start: Ein-Knopf "16:8 heute starten" basierend auf Default-Protokoll?
- Automatische Erkennung: Fasten läuft noch vom Vortag? (über Mitternacht)
- Soll die App Fasten-Brechen zu ungeplanten Zeiten tracken (Compliance)?
- Integration mit existierendem Circadian-Profil (Chronotyp ↔ optimales Essensfenster)?

## Ergänzungen von Philipp
Wie gehabt, verweise ich hier auch nochmal darauf, dass wir möglichst das Metrik System nutzen wollen und es gerne anpassen / erweitern können, damit alle Pläne möglichst perfekt umgesetzt werden können.

Zu deinen Fragen:
Ketose Tracking wäre super, ich glaube mittlerweile wäre es dann auch schlau darüber nachzudenken, ein System zu entwerfen, welches externe Geräte managed, oder?
Quick-Start könnte man machen, ist jetzt aber nicht zwingend notwendig
Automatische Erkennung klingt auch gut, je nach dem wie gut das umsetzbar / erkennbar ist.
Fasten Brechen klingt auch nicht verkehrt zu tracken
Das kann man gerne integrieren bzw. kombinieren. Es ist immer gut, wenn Daten zusammenarbeiten und dem Nutzer daraus ein Mehrwert entsteht
