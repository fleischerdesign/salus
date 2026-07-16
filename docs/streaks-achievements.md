# Streaks & Achievements

## Overview
Gamification-Layer: Belohnt Konsistenz und Meilensteine mit Badges, Streaks und Leveln.
Quer über alle Features (Habits, Mood, Workouts, Goals, Tracking).

## Data Model

### achievement_definition
(Game-Design: Welche Achievements gibt es? Seeded vom Backend)

| Column | Type | Notes |
|---|---|---|
| code | str | PK — "first_entry" |
| title | str | "Der erste Schritt" |
| description | str | "Deinen ersten Eintrag geloggt" |
| category | enum | tracking / streak / milestone / goal / workout / social / special |
| icon | str | Material Symbols |
| tier | enum | bronze / silver / gold / platinum |
| condition_type | enum | count / streak / value / compound |
| condition_config | json | `{"entity": "measurement", "operator": "gte", "value": 1}` |
| is_hidden | bool | Secret achievements |
| sort_order | int | |

### user_achievement
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| achievement_code | str | FK → achievement_definition |
| unlocked_at | datetime | |
| progress_current | float? | 45.0 (Zwischenstand bei mehrstufigen) |
| progress_target | float? | 100.0 |
| notified | bool | Wurde die Notification bereits gesendet? |

### streak
(Virtuell — wird on-the-fly berechnet, nicht persistiert)

Berechnung: Pro Entity-Type (habit_log, mood_entry, measurement, workout_session, etc.)
→ Längste Serie aufeinanderfolgender Tage mit mind. 1 Eintrag.

## Vordefinierte Achievements (Ideen)

### Tracking (Tier 1 — Bronze)
- `first_entry` — Erster Eintrag geloggt
- `first_metric` — Erste benutzerdefinierte Metrik erstellt
- `first_goal` — Erstes Ziel gesetzt
- `first_workout` — Erstes Workout abgeschlossen
- `first_habit` — Erster Habit erstellt

### Streaks (Tier 2 — Silver)
- `tracking_7_day` — 7 Tage in Folge getrackt
- `tracking_30_day` — 30 Tage in Folge
- `tracking_90_day` — 90 Tage in Folge
- `tracking_365_day` — 365 Tage in Folge (Platinum!)
- `mood_7_day` — 7 Tage Stimmung geloggt
- `habit_30_day` — 30-Tage Habit-Streak

### Milestones (Tier 2-3)
- `entries_100` — 100 Einträge insgesamt
- `entries_1000` — 1000 Einträge
- `workouts_50` — 50 Workouts
- `workouts_100` — 100 Workouts
- `total_weight_1t` — 1 Tonne Gesamtgewicht bewegt (Summe aller Sets)

### Goals
- `goal_achieved_1` — Erstes Ziel erreicht
- `goal_achieved_5` — 5 Ziele erreicht
- `goal_all_active` — Alle aktiven Ziele gleichzeitig erfüllt

### Social
- `first_share` — Erste Daten geteilt
- `leaderboard_top3` — Top-3 in einer Leaderboard-Gruppe
- `leaderboard_win` — #1 in einer Woche

### Special (Hidden)
- `night_owl_tracker` — Nach Mitternacht noch Einträge geloggt
- `early_bird` — Vor 6 Uhr morgens getrackt
- `perfect_week` — Jeden Tag mindestens 1 Eintrag + 1 Workout + 1 Habit
- `data_donor` — Daten an Open Science gespendet

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /api/v1/achievements | List all definitions + user progress |
| GET | /api/v1/achievements/unlocked | My unlocked achievements |
| GET | /api/v1/achievements/{code} | Detail + progress |
| GET | /api/v1/streaks | All current streaks (habit, mood, tracking, workout) |
| GET | /api/v1/streaks/{entity} | Streak for specific entity type |

## Frontend

- **AchievementGrid** — Badge-Wall mit unlocked/locked-Status
- **AchievementToast** — Unlock-Notification (pop-in mit Sound/Animation)
- **StreakBar** — Aktuelle Streaks als Fortschrittsbalken
- **ProfileBadges** — User-Profil mit sichtbaren Badges
- **AchievementNotification** — "Achievement freigeschaltet!" in Notification Center

## Integration Points
- **Notification System** → Achievement-Unlock generiert Notification
- **Habits** → Habit-Streaks
- **Mood** → Mood-Streaks
- **Workouts** → Workout-Zähler, Gewicht-Summe
- **Goals** → Goal-Completion
- **Sharing/Community** → Leaderboard-Rankings
- **Sync** → Achievements sind Read-only, berechnet server-seitig

## Open Questions
- Soll man Badges im Profil "showcasen" können (Top-3 auswählbar)?
- Achievement-Berechnung: Eager (bei jeder relevanten Aktion checken) oder Lazy (nur bei API-Call)?
- Level-System zusätzlich zu Badges? (XP für Aktionen → Level-Up)
- Weekly Challenges zusätzlich zu permanenten Achievements? (z.B. "Diese Woche: 5 Workouts")
- Secret Achievements: Nur Name/Icon versteckt oder komplett unsichtbar bis Unlock?

## Ergänzungen von Philipp
Wäre natürlich super, wenn das ganze möglichst agnostisch und dynamisch funktionieren würde, also möglichst nicht hardcoded, da ja unser Metrik System und alles andere auch sehr dynamisch ist..

Zu deinen Fragen:
Ja, Badges sollte man showcasen können
Gute Frage, was wäre denn die beste UX bzw. akademisch professionell also bzgl eager oder lazy
Ein level System wäre auch recht cool!
Weekly Challenges: Weiß nicht, wir haben ja auch schon Leaderboards, nicht wahr? Da müssten wir überlegen, ob sich das überschneidet oder ob das coexistieren kann bzw. sollte.
Secret Achievements: Wozu? Also ich weiß nicht was für den User am besten wäre, würde ich dich entscheiden lassen.