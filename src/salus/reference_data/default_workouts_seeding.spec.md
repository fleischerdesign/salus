# Specification: Default Workouts and Programs Seeding

## 1. Problem Statement
Salus seeds standard exercises (`COMMON_EXERCISES`) as shared reference data (`shared_nullable`), but currently does not provide evidence-based default workout routines (training days) or structured multi-day periodization programs (splits). New and existing users start with an empty workout planner, requiring manual assembly of exercises into workouts and programs before training can begin. Default evidence-based workouts and programs must be provided out-of-the-box as immutable system templates, synchronized via local-first sync (`shared_nullable` + `relational`), and ready for direct execution or user customization.

## 2. User Story
As an athlete or health-conscious user using Salus  
I want pre-configured, sports-scientifically sound workout routines and multi-day training programs available immediately upon installation/registration  
So that I can immediately start an evidence-based training session (e.g. Full Body, Upper/Lower, or Push/Pull/Legs) without having to manually configure exercises, sets, reps, and RPE from scratch.

---

## 3. Acceptance Criteria (Gherkin Scenarios)

```gherkin
Feature: Seeded Default Workouts and Programs

  Background:
    Given the reference data engine runs against an empty or existing database
    And the standard exercises catalog is registered

  Scenario: Startup seeding of default workouts and programs
    When the reference data engine executes seed_all()
    Then exactly 9 default workouts (templates) are created with user_id = null
    And exactly 3 default programs are created with user_id = null
    And all workout_exercise bridges reference valid seeded exercise IDs
    And all program_workout bridges reference valid seeded program and workout IDs
    And subsequent seed_all() runs are skipped via SHA-256 hash comparison with 0 created and 0 updated

  Scenario: Starting a training session directly from a system-default workout
    Given an authenticated user "athlete"
    And a system workout "wo-fb-a" ("Ganzkörper A") exists with user_id = null
    When the user dispatches the command "start_workout" with workout_id = "wo-fb-a"
    Then a new WorkoutSession is created with user_id = "athlete" and workout_id = "wo-fb-a"
    And the session targets match the exercise configuration defined in "wo-fb-a"

  Scenario: Activating a system-default program for weekly scheduling
    Given an authenticated user "athlete"
    And a system program "prog-upper-lower-4d" exists with user_id = null
    When the user starts a session referencing "prog-upper-lower-4d"
    Then the session adopts the program's progression_scheme ("autoregulated")
    And recovery score calculations are applied to the session targets

  Scenario: Immutability of system-default templates
    Given an authenticated user "athlete"
    And a system workout "wo-fb-a" with user_id = null
    When the user attempts a sync push or REST update/delete targeting "wo-fb-a"
    Then the operation is rejected with status "forbidden"
    And the system workout remains unchanged in the database

  Scenario: Full sync synchronization of shared workouts and relational exercises
    Given an authenticated user "athlete"
    And system workouts and programs exist in the database
    When the user performs a full sync (GET /api/v1/sync)
    Then the "workout" entity payload includes all system workouts
    And the "program" entity payload includes all system programs
    And the "workout_exercise" entity payload includes all exercises for system workouts
    And the "program_workout" entity payload includes all schedule slots for system programs

  Scenario: Delta sync synchronization of shared workouts
    Given an authenticated user "athlete"
    And system workouts and programs were modified or seeded at timestamp T
    When the user performs a delta sync (GET /api/v1/sync?since=T_minus_1)
    Then the delta response includes all updated system workouts, programs, and child relations
```

---

## 4. Edge Case Enumeration

### Covered:
- **Foreign Key Integrity**: All `WorkoutExercise.exercise_id` references map to verified IDs in `COMMON_EXERCISES`.
- **Relational Ownership in Sync**: `_parent_ids` in `sync.py` resolves parent IDs where `user_id == user_id OR user_id IS NULL`, ensuring child `WorkoutExercise` and `ProgramWorkout` records of system parents sync to all users.
- **Duplicate Prevention & Idempotency**: All items use deterministic primary keys (`wo-*`, `woex-*`, `prog-*`, `prgw-*`) and SHA-256 hash fast-skip.
- **Soft Deletion Isolation**: Soft-deleted user workouts or system updates never resurrect deleted templates.
- **Empty Custom Slots**: Programs without explicit weekday slots function as rotation-based queues.

### Out of Scope:
- Automatic migration or forced replacement of user-modified custom workouts bearing the same name.
- UI drag-and-drop reordering of system templates (users clone first before customizing).

---

## 5. Sizing Assessment
- **Estimated Scope**: Contained cross-cutting extension of reference data definitions, registry, entity meta strategies, sync parent resolution, and automated test coverage.
- **Complexity**: Low risk, high value, clean architecture compliance.
