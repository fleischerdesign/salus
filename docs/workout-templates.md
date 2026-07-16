# Workout Templates

## Overview
Importierbare Workout-Plan-Vorlagen für gängige Trainingsprogramme.
Nutzer können mit einem Klick ein komplettes Programm starten statt alles manuell zu konfigurieren.

**Abgrenzung zu WorkoutPlans:** WorkoutPlans sind user-erstellte Pläne mit manuell konfigurierten Übungen. Templates sind vordefinierte, importierbare "Blaupausen" die einen WorkoutPlan erzeugen.

## Data Model

### workout_template
(Seeded vom System — nicht user-editable direkt)

| Column | Type | Notes |
|---|---|---|
| code | str | PK — "starting_strength" |
| name | str | "Starting Strength" |
| description | str | Markdown — Programmbeschreibung |
| author | str | "Mark Rippetoe" |
| category | enum | strength / hypertrophy / powerlifting / bodyweight / cardio / mobility / beginner / sport_specific |
| difficulty | enum | beginner / intermediate / advanced |
| weeks | int | Programmdauer (0 = unbegrenzt) |
| sessions_per_week | int | 3 |
| estimated_duration_min | int | 60 |
| equipment_needed | json | ["barbell", "squat_rack", "bench"] |
| tags | json | ["full_body", "linear_progression"] |
| image_url | str? | Vorschaubild |
| source_url | str? | Link zur Original-Quelle |
| is_featured | bool | Auf Startseite hervorheben |
| sort_order | int | |

### workout_template_week
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| template_code | str | FK → workout_template |
| week_number | int | 1, 2, 3... |
| name | str? | "Week 1 — Introduction" |

### workout_template_session
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| template_week_id | UUID | FK → workout_template_week |
| day_of_week | int | 1-7 (Mo-So) oder session order |
| name | str? | "Workout A" |
| notes | str? | |

### workout_template_exercise
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| template_session_id | UUID | FK → workout_template_session |
| exercise_name | str | Name der Übung (muss in Exercise-Tabelle existieren oder neu erstellt werden) |
| sequence | int | Reihenfolge |
| target_sets | int | 3 |
| target_reps | str? | "5" oder "8-12" (String für Ranges) |
| target_rpe | float? | |
| rest_seconds | int? | |
| notes | str? | "Add 2.5kg each session" |
| progression_type | enum? | linear / double_progression / autoregulated / fixed |
| progression_config | json? | `{"weekly_increment_kg": 2.5}` |

### workout_template_import
(Trackt, welche Templates ein User importiert hat)

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| template_code | str | FK |
| imported_at | datetime | |
| resulting_plan_id | UUID | FK → workout_plan |
| current_week | int | Fortschritt |
| completed | bool | |

## Vordefinierte Templates (Seed-Ideen)

```
Kategorie "beginner":
  - starting_strength    (Starting Strength — 3x5, A/B rotation)
  - stronglifts_5x5      (StrongLifts 5x5)
  - greyskull_lp         (Greyskull LP)
  - basic_push_pull_legs (Einfacher PPL)
  - couch_to_5k          (Couch to 5K — Laufprogramm)

Kategorie "intermediate":
  - 531_boring_but_big   (5/3/1 BBB)
  - n_suns_531           (nSuns 5/3/1)
  - candito_6_week       (Candito 6-Week)
  - phul                 (PHUL — Power Hypertrophy Upper Lower)
  - phat                 (PHAT)

Kategorie "bodyweight":
  - recommended_routine   (r/bodyweightfitness Recommended Routine)
  - move_routine          (r/bodyweightfitness Move Routine)
  - convict_conditioning

Kategorie "mobility":
  - starting_stretching
  - molding_mobility
  - simple_yoga_flow

Kategorie "cardio":
  - couch_to_5k
  - bridge_to_10k
  - hiit_beginner
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /api/v1/workouts/templates | List templates (filter: category, difficulty) |
| GET | /api/v1/workouts/templates/{code} | Get template detail + weeks/sessions |
| POST | /api/v1/workouts/templates/{code}/import | Import as WorkoutPlan |
| GET | /api/v1/workouts/templates/my | My imported templates |
| POST | /api/v1/workouts/templates/{code}/abandon | Stop template tracking |
| POST | /api/v1/workouts/templates/custom | Save current WorkoutPlan as custom template |

## Import-Flow

```
1. User browst Templates → wählt "Starting Strength"
2. Sieht Vorschau: Wochen, Sessions, Übungen, Progression
3. Klickt "Importieren"
4. Backend:
   a. Erzeugt WorkoutPlan (name = template.name)
   b. Erzeugt WorkoutPlanExercise für Woche 1
   c. (Woche 2+ lazily bei Wochen-Wechsel?)
   d. Setzt Autoregulation = template.progression
5. User hat jetzt einen WorkoutPlan unter "Meine Pläne"
```

## Frontend

- **TemplateBrowser** — Karten-Grid mit Filter nach Kategorie/Schwierigkeit
- **TemplateDetail** — Vorschau mit allen Sessions, Übungen, Progression
- **TemplateImportButton** — Mit Confirmation-Dialog
- **MyTemplates** — Liste aktiver Template-Imports mit Fortschritt
- **SaveAsTemplate** — "Plan als Template speichern" (custom user-templates)

## Integration Points
- **Workout System** → Templates erzeugen WorkoutPlans mit WorkoutPlanExercises
- **Exercise Catalog** → Template-Übungen müssen in der Exercise-Tabelle existieren oder beim Import erstellt werden
- **Streaks & Achievements** → "Ein Template-Programm abgeschlossen"

## Open Questions
- Sollen alle Wochen auf einmal erstellt werden oder lazy (Week-by-Week)? Bei 5/3/1 wären das 52+ Wochen für ein Jahr — ineffizient.
- Eigene Templates: Soll User eigene Templates erstellen und teilen können? Community-Template-Sharing?
- Exercise-Matching: Template enthält "Barbell Squat" → wie matchen wir das mit der Exercise-Tabelle (Name-Ähnlichkeit, Manuelles Mapping)?
- Template-Updates: Wenn ein System-Template aktualisiert wird, wie beeinflusst das bereits importierte Pläne?

## Ergänzungen von Philipp
Hier würde ich dich auch gerne darauf aufmerksam machen, dass das wirklich gut mit unserem Workout Plan / Exercises System integriert werden muss und ob man die Templates nicht auch einfach auf der workout plan overview seite irgendwie implementiert.. Müsste man überlegen ob wir dann da eine extra overview seite und detail seite für die templates realisiert oder eben nicht. Wenn wir konsistent bleiben wollen, sollten wir das aber denke ich.

Zu deinen Fragen:
Gute Frage.. Sollten alle Wochen auf einmal erstellt werden? Wie will man das denn sonst lösen? 
Ja! Der User soll auch eigene Templates erstellen können und auch teilen können, dafür haben wir ja das federation / share feature!
Gute Frage.. Was würdest du denn Sagen? Gerade zwecks Federation / Sharing wirds da knifflig, denn der User muss ja dann auch die exercises in seine Bibliothek bekommen (Wenn noch nicht vorhanden), die der andere User in seinem Template nutzt? DA muss man wirklich tief analysieren und überlegen
Template-Updates: Auch eine sehr gute Frage, was würdest du denn sagen?