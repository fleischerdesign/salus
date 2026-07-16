# Mood & Journal Tracking

## Overview
Tägliche Stimmungserfassung (Skala 1-10) plus optionales Freitext-Journal.
Haupt-Mehrwert: Korrelation mit anderen Metriken ("An Tagen mit >7h Schlaf ist meine Stimmung 1.5 Punkte besser").

## Data Model

### mood_entry
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| date | date | |
| mood_score | int | 1-10 (1=schlecht, 10=exzellent) |
| energy_level | int? | 1-10 |
| stress_level | int? | 1-10 |
| tags | json? | ["produktiv", "müde", "motiviert"] — predefined + custom |
| created_at | datetime | |

### journal_entry
(Getrennt von mood_entry: Es kann einen Mood-Eintrag ohne Journal geben und umgekehrt)

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| date | date | |
| title | str? | |
| content | str | Markdown |
| mood_score | int? | 1-10 (optional, falls direkt im Journal erfasst) |
| is_private | bool | Default true |
| created_at | datetime | |
| updated_at | datetime | |

### mood_tag
| Column | Type | Notes |
|---|---|---|
| code | str | PK — "productive", "tired", "anxious" |
| label | str | Anzeigename |
| emoji | str? | "⚡" |
| category | enum | positive / neutral / negative |
| is_system | bool | User-defined tags möglich |

## API Endpoints

### Mood
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/mood/tags | List available tags |
| GET | /api/v1/mood | Mood history (date range) |
| POST | /api/v1/mood | Create/log mood |
| GET | /api/v1/mood/{date} | Get specific day |
| PUT | /api/v1/mood/{date} | Update |
| GET | /api/v1/mood/stats | Distribution, streak, average |

### Journal
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/journal | List entries (paginated) |
| POST | /api/v1/journal | Create entry |
| GET | /api/v1/journal/{id} | Get entry |
| PUT | /api/v1/journal/{id} | Update |
| DELETE | /api/v1/journal/{id} | Delete |
| GET | /api/v1/journal/{date} | Get by date |
| GET | /api/v1/journal/search | Fulltext search |

## Frontend

- **MoodPicker** — Emoji-basierte 1-10 Skala (Tap/Toggle), Tags als Chips
- **MoodCalendar** — Monatskalender mit Farb-Heatmap der Stimmung
- **MoodTrend** — Liniendiagramm Stimmung über Zeit, gleitender Durchschnitt
- **JournalEditor** — Markdown-Editor mit Datumswahl
- **JournalList** — Karten mit Preview, suchbar
- **Dashboard-Widget** — Heutige Stimmung + "Wie fühlst du dich?" Prompt
- **MoodCorrelations** — Analytics-Integration: Korrelation Stimmung ↔ Schlaf/Sport/etc.

## Integration Points
- **Analytics** → Mood vs. Schlaf, Mood vs. Sport, Mood vs. Schritte (Korrelationen)
- **Insights/AI Coach** → "Deine Stimmung ist diese Woche im Schnitt 7.2 — dein bester Wert seit 3 Monaten!"
- **Streaks & Achievements** → "30-Tage Mood-Streak"
- **Circadian** → Stimmung nach Chronotyp analysieren
- **Habits** → "Meditation korreliert mit +0.8 Stimmungspunkten"

## Open Questions
- Tags: Komplett user-defined oder vordefinierte Liste? Mischung?
- Journal: Reines Markdown oder Rich-Text (tiptap/ProseMirror)?
- Privacy: Soll Journal optional E2EE-verschlüsselt sein?
- Soll es "Gratitude Journaling"-Prompts geben (optional)?

## Ergänzungen von Philipp
Tags: Würde ich dir überlassen, da wäre es einfach wichtig zu beachten, was akademisch professionell und für den User am besten wäre
Journal: Kein Markdown an sich, wir wollen dem User das ganze doch so einfach wie möglich machen.
Privacy: Erstmal egal, später im laufe der Entwicklung müssen wir eh schauen, wie wir die Daten der User insgesamt schützen bzw. verschlüsseln
Keine Ahnung was Gratitude Journaling Prompts sein sollen.