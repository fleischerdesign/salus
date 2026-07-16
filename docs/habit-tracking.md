# Habit Tracking

## Overview
Erfasse tägliche Gewohnheiten (nicht Metriken — siehe Abgrenzung zu Goals).
Fokus auf binäre Prüfung (done/not done) und Konsistenz-Streaks.

**Abgrenzung zu Goals:** Goals = Zielwert erreichen (z.B. "10k Schritte/Tag"). Habits = Ja/Nein-Check (z.B. "Meditiert?").

## Data Model

### habit
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| name | str | "Morgens dehnen" |
| description | str? | |
| color | str | Hex |
| icon | str | Material Symbols name |
| frequency | enum | daily / weekly(n_times) / custom_days([mon,tue,...]) |
| target_count | int | Anzahl pro Frequenz-Zeitraum |
| stack_hint | str? | "Nach dem Zähneputzen" (Habit-Stacking) |
| is_archived | bool | soft-delete |
| created_at | datetime | |

### habit_log
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| habit_id | UUID | FK → habit |
| date | date | Welcher Tag |
| completed | bool | |
| completed_at | datetime? | Zeitstempel |
| notes | str? | |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /api/v1/habits | List habits |
| POST | /api/v1/habits | Create habit |
| PUT | /api/v1/habits/{id} | Update habit |
| DELETE | /api/v1/habits/{id} | Archive habit |
| POST | /api/v1/habits/{id}/check | Toggle today's check |
| GET | /api/v1/habits/{id}/logs | Log history (paginated) |
| GET | /api/v1/habits/stats | Streaks, completion rates |

## Frontend

- **HabitCard** — Checkbox mit Streak-Counter, Fortschrittsring für Woche
- **HabitGrid** — Grid-Layout (Widget-ähnlich) auf Dashboard oder eigener Seite
- **HabitDetail** — Monats-Heatmap, Jahresübersicht, längster Streak, Completion-Rate
- **HabitForm** — Name, Icon-Picker, Farbe, Frequenz-Konfigurator

## Integration Points
- **Streaks & Achievements** → Habit-Streaks speisen das Achievement-System
- **Dashboard Widgets** → Habit-Widget für den Dashboard-Grid
- **Mood/Journal** → Korrelation: "Tage mit Meditation → bessere Stimmung?"
- **Reminders** → Push-Reminder "Hast du heute schon X gemacht?"

## Open Questions
- Soll es ein "nicht 2 Tage in Folge verpassen"-Feature geben (never-miss-twice)?
- Check nur für heute oder auch rückwirkend eintragbar?
- Widget: Kompaktes Grid (alle Habits auf einen Blick) vs. einzelne Widgets pro Habit?

## Ergänzungen von Philipp
An sich hab ich hier erstmal nichts auszusetzen.. 

Zu deinen Fragen:
Was soll uns ein never miss twice feature bringen? Also ich verstehe nicht was passieren soll, wenn der User es doch 2 Tage vergisst?
Auch rückwirgend eintragbar
Wieso denn nicht Beides zwecks Widget?

Zudem müssen wir dann auch überlegen, ob wir dann auch eine Habit Overview Seite erstellen und eine Habit Detail Seite, dabei kannst du dich gerne auch an den anderen Seiten orientieren
