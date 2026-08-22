"""Default evidence-based workouts (training days) seeded on system startup.

Shared across all users (user_id=None, shared_nullable strategy).
Each workout references valid exercise IDs from ``COMMON_EXERCISES`` and
carries evidence-based set/rep/RPE/rest targets per exercise.
"""

# NOTE: ``DEFAULT_WORKOUT_EXERCISES`` groups entries by workout for readability;
# the registry flattens them into the ``common_workout_exercises`` spec.

DEFAULT_WORKOUTS: list[dict] = [
    {
        "id": "wo-fb-a",
        "name": "Ganzkörper A (Kniebeuge & Druck)",
        "description": "Ganzkörper-Training mit hoher Intensität, aufgebaut um Kniebeuge und Drückbewegungen.",
        "position": 0,
    },
    {
        "id": "wo-fb-b",
        "name": "Ganzkörper B (Kreuzheben & Zug)",
        "description": "Ganzkörper-Training mit Fokus auf Kreuzheben und Zugbewegungen für die posteriore Kette.",
        "position": 1,
    },
    {
        "id": "wo-upper-a",
        "name": "Oberkörper A (Schwere Grundübungen)",
        "description": "Oberkörper-Schwerpunkt mit schweren Grundübungen für Masse und Kraft.",
        "position": 2,
    },
    {
        "id": "wo-lower-a",
        "name": "Unterkörper A (Kniebeugen & Quads)",
        "description": "Unterkörper-Schwerpunkt mit Fokus auf Kniebeugen und Quadrizeps.",
        "position": 3,
    },
    {
        "id": "wo-upper-b",
        "name": "Oberkörper B (Hypertrophie & Volumen)",
        "description": "Oberkörper-Tag mit höherem Volumen und Isolationsübungen für Hypertrophie.",
        "position": 4,
    },
    {
        "id": "wo-lower-b",
        "name": "Unterkörper B (Posteriore Kette)",
        "description": "Unterkörper-Tag mit Fokus auf der posterioren Kette (Hüfte & Beinbeuger).",
        "position": 5,
    },
    {
        "id": "wo-push-a",
        "name": "Push (Brust, Schulter, Trizeps)",
        "description": "Push-Tag: Brust, Schultern und Trizeps mit Drückbewegungen.",
        "position": 6,
    },
    {
        "id": "wo-pull-a",
        "name": "Pull (Rücken, hintere Schulter, Bizeps)",
        "description": "Pull-Tag: Rücken, hintere Schultern und Bizeps mit Zugbewegungen.",
        "position": 7,
    },
    {
        "id": "wo-legs-a",
        "name": "Legs & Core (Beine & Bauch)",
        "description": "Beine und Core mit Kniebeugen, Kreuzheben und Bauchübungen.",
        "position": 8,
    },
]

DEFAULT_WORKOUT_EXERCISES: list[dict] = [
    # ── wo-fb-a: Ganzkörper A (Kniebeuge & Druck) ──
    {"id": "woex-fb-a-1", "workout_id": "wo-fb-a", "exercise_id": "ex-squats-high-bar", "sequence": 0, "target_sets": 4, "target_reps": 8, "target_rpe": 8.0, "rest_seconds": 180},
    {"id": "woex-fb-a-2", "workout_id": "wo-fb-a", "exercise_id": "ex-bench-press-barbell", "sequence": 1, "target_sets": 4, "target_reps": 8, "target_rpe": 8.0, "rest_seconds": 180},
    {"id": "woex-fb-a-3", "workout_id": "wo-fb-a", "exercise_id": "ex-bent-over-row-barbell", "sequence": 2, "target_sets": 3, "target_reps": 10, "target_rpe": 7.5, "rest_seconds": 120},
    {"id": "woex-fb-a-4", "workout_id": "wo-fb-a", "exercise_id": "ex-overhead-press-barbell", "sequence": 3, "target_sets": 3, "target_reps": 8, "target_rpe": 8.0, "rest_seconds": 150},
    {"id": "woex-fb-a-5", "workout_id": "wo-fb-a", "exercise_id": "ex-cable-woodchoppers", "sequence": 4, "target_sets": 3, "target_reps": 12, "target_rpe": 7.0, "rest_seconds": 60},

    # ── wo-fb-b: Ganzkörper B (Kreuzheben & Zug) ──
    {"id": "woex-fb-b-1", "workout_id": "wo-fb-b", "exercise_id": "ex-deadlift-conventional", "sequence": 0, "target_sets": 3, "target_reps": 6, "target_rpe": 8.0, "rest_seconds": 180},
    {"id": "woex-fb-b-2", "workout_id": "wo-fb-b", "exercise_id": "ex-pullups", "sequence": 1, "target_sets": 3, "target_reps": 8, "target_rpe": 8.0, "rest_seconds": 120},
    {"id": "woex-fb-b-3", "workout_id": "wo-fb-b", "exercise_id": "ex-incline-bench-press-dumbbell", "sequence": 2, "target_sets": 3, "target_reps": 10, "target_rpe": 7.5, "rest_seconds": 120},
    {"id": "woex-fb-b-4", "workout_id": "wo-fb-b", "exercise_id": "ex-lat-pulldown", "sequence": 3, "target_sets": 3, "target_reps": 10, "target_rpe": 7.5, "rest_seconds": 90},
    {"id": "woex-fb-b-5", "workout_id": "wo-fb-b", "exercise_id": "ex-biceps-curls-dumbbell", "sequence": 4, "target_sets": 3, "target_reps": 12, "target_rpe": 7.0, "rest_seconds": 75},

    # ── wo-upper-a: Oberkörper A (Schwere Grundübungen) ──
    {"id": "woex-upper-a-1", "workout_id": "wo-upper-a", "exercise_id": "ex-bench-press-barbell", "sequence": 0, "target_sets": 4, "target_reps": 6, "target_rpe": 8.5, "rest_seconds": 180},
    {"id": "woex-upper-a-2", "workout_id": "wo-upper-a", "exercise_id": "ex-bent-over-row-barbell", "sequence": 1, "target_sets": 3, "target_reps": 10, "target_rpe": 7.5, "rest_seconds": 150},
    {"id": "woex-upper-a-3", "workout_id": "wo-upper-a", "exercise_id": "ex-overhead-press-barbell", "sequence": 2, "target_sets": 4, "target_reps": 8, "target_rpe": 8.0, "rest_seconds": 150},
    {"id": "woex-upper-a-4", "workout_id": "wo-upper-a", "exercise_id": "ex-pullups", "sequence": 3, "target_sets": 3, "target_reps": 8, "target_rpe": 8.0, "rest_seconds": 120},
    {"id": "woex-upper-a-5", "workout_id": "wo-upper-a", "exercise_id": "ex-dips-chest", "sequence": 4, "target_sets": 3, "target_reps": 10, "target_rpe": 7.5, "rest_seconds": 120},

    # ── wo-lower-a: Unterkörper A (Kniebeuge & Quads) ──
    {"id": "woex-lower-a-1", "workout_id": "wo-lower-a", "exercise_id": "ex-squats-high-bar", "sequence": 0, "target_sets": 4, "target_reps": 8, "target_rpe": 8.0, "rest_seconds": 180},
    {"id": "woex-lower-a-2", "workout_id": "wo-lower-a", "exercise_id": "ex-leg-press-45", "sequence": 1, "target_sets": 4, "target_reps": 10, "target_rpe": 7.5, "rest_seconds": 120},
    {"id": "woex-lower-a-3", "workout_id": "wo-lower-a", "exercise_id": "ex-romanian-deadlift", "sequence": 2, "target_sets": 3, "target_reps": 10, "target_rpe": 7.5, "rest_seconds": 120},
    {"id": "woex-lower-a-4", "workout_id": "wo-lower-a", "exercise_id": "ex-leg-curls-seated", "sequence": 3, "target_sets": 3, "target_reps": 12, "target_rpe": 7.0, "rest_seconds": 90},
    {"id": "woex-lower-a-5", "workout_id": "wo-lower-a", "exercise_id": "ex-calf-raises-standing", "sequence": 4, "target_sets": 4, "target_reps": 15, "target_rpe": 6.5, "rest_seconds": 60},

    # ── wo-upper-b: Oberkörper B (Hypertrophie & Volumen) ──
    {"id": "woex-upper-b-1", "workout_id": "wo-upper-b", "exercise_id": "ex-incline-bench-press-dumbbell", "sequence": 0, "target_sets": 4, "target_reps": 10, "target_rpe": 8.0, "rest_seconds": 120},
    {"id": "woex-upper-b-2", "workout_id": "wo-upper-b", "exercise_id": "ex-lat-pulldown", "sequence": 1, "target_sets": 4, "target_reps": 12, "target_rpe": 7.5, "rest_seconds": 90},
    {"id": "woex-upper-b-3", "workout_id": "wo-upper-b", "exercise_id": "ex-cable-flys", "sequence": 2, "target_sets": 4, "target_reps": 10, "target_rpe": 7.0, "rest_seconds": 90},
    {"id": "woex-upper-b-4", "workout_id": "wo-upper-b", "exercise_id": "ex-lateral-raises-cable", "sequence": 3, "target_sets": 3, "target_reps": 12, "target_rpe": 7.0, "rest_seconds": 75},
    {"id": "woex-upper-b-5", "workout_id": "wo-upper-b", "exercise_id": "ex-face-pulls", "sequence": 4, "target_sets": 3, "target_reps": 15, "target_rpe": 7.0, "rest_seconds": 60},
    {"id": "woex-upper-b-6", "workout_id": "wo-upper-b", "exercise_id": "ex-triceps-pushdown-rope", "sequence": 5, "target_sets": 4, "target_reps": 12, "target_rpe": 7.5, "rest_seconds": 75},

    # ── wo-lower-b: Unterkörper B (Posteriore Kette) ──
    {"id": "woex-lower-b-1", "workout_id": "wo-lower-b", "exercise_id": "ex-deadlift-conventional", "sequence": 0, "target_sets": 3, "target_reps": 6, "target_rpe": 8.0, "rest_seconds": 180},
    {"id": "woex-lower-b-2", "workout_id": "wo-lower-b", "exercise_id": "ex-romanian-deadlift", "sequence": 1, "target_sets": 3, "target_reps": 8, "target_rpe": 8.0, "rest_seconds": 120},
    {"id": "woex-lower-b-3", "workout_id": "wo-lower-b", "exercise_id": "ex-leg-press-45", "sequence": 2, "target_sets": 3, "target_reps": 10, "target_rpe": 7.5, "rest_seconds": 120},
    {"id": "woex-lower-b-4", "workout_id": "wo-lower-b", "exercise_id": "ex-leg-curls-seated", "sequence": 3, "target_sets": 3, "target_reps": 12, "target_rpe": 7.0, "rest_seconds": 90},
    {"id": "woex-lower-b-5", "workout_id": "wo-lower-b", "exercise_id": "ex-calf-raises-standing", "sequence": 4, "target_sets": 4, "target_reps": 15, "target_rpe": 6.5, "rest_seconds": 60},

    # ── wo-push-a: Push (Brust, Schulter, Trizeps) ──
    {"id": "woex-push-a-1", "workout_id": "wo-push-a", "exercise_id": "ex-bench-press-barbell", "sequence": 0, "target_sets": 4, "target_reps": 8, "target_rpe": 8.0, "rest_seconds": 180},
    {"id": "woex-push-a-2", "workout_id": "wo-push-a", "exercise_id": "ex-overhead-press-barbell", "sequence": 1, "target_sets": 3, "target_reps": 8, "target_rpe": 8.0, "rest_seconds": 150},
    {"id": "woex-push-a-3", "workout_id": "wo-push-a", "exercise_id": "ex-incline-bench-press-dumbbell", "sequence": 2, "target_sets": 3, "target_reps": 10, "target_rpe": 7.5, "rest_seconds": 120},
    {"id": "woex-push-a-4", "workout_id": "wo-push-a", "exercise_id": "ex-dips-chest", "sequence": 3, "target_sets": 3, "target_reps": 10, "target_rpe": 7.5, "rest_seconds": 120},
    {"id": "woex-push-a-5", "workout_id": "wo-push-a", "exercise_id": "ex-triceps-pushdown-rope", "sequence": 4, "target_sets": 3, "target_reps": 12, "target_rpe": 7.5, "rest_seconds": 75},

    # ── wo-pull-a: Pull (Rücken, hintere Schulter, Bizeps) ──
    {"id": "woex-pull-a-1", "workout_id": "wo-pull-a", "exercise_id": "ex-pullups", "sequence": 0, "target_sets": 4, "target_reps": 8, "target_rpe": 8.0, "rest_seconds": 120},
    {"id": "woex-pull-a-2", "workout_id": "wo-pull-a", "exercise_id": "ex-bent-over-row-barbell", "sequence": 1, "target_sets": 3, "target_reps": 10, "target_rpe": 7.5, "rest_seconds": 120},
    {"id": "woex-pull-a-3", "workout_id": "wo-pull-a", "exercise_id": "ex-lat-pulldown", "sequence": 2, "target_sets": 3, "target_reps": 10, "target_rpe": 7.5, "rest_seconds": 90},
    {"id": "woex-pull-a-4", "workout_id": "wo-pull-a", "exercise_id": "ex-face-pulls", "sequence": 3, "target_sets": 3, "target_reps": 15, "target_rpe": 7.0, "rest_seconds": 60},
    {"id": "woex-pull-a-5", "workout_id": "wo-pull-a", "exercise_id": "ex-biceps-curls-dumbbell", "sequence": 4, "target_sets": 3, "target_reps": 12, "target_rpe": 7.0, "rest_seconds": 75},

    # ── wo-legs-a: Legs & Core (Beine & Bauch) ──
    {"id": "woex-legs-a-1", "workout_id": "wo-legs-a", "exercise_id": "ex-squats-high-bar", "sequence": 0, "target_sets": 4, "target_reps": 8, "target_rpe": 8.0, "rest_seconds": 180},
    {"id": "woex-legs-a-2", "workout_id": "wo-legs-a", "exercise_id": "ex-romanian-deadlift", "sequence": 1, "target_sets": 3, "target_reps": 10, "target_rpe": 7.5, "rest_seconds": 120},
    {"id": "woex-legs-a-3", "workout_id": "wo-legs-a", "exercise_id": "ex-hanging-leg-raises", "sequence": 2, "target_sets": 3, "target_reps": 12, "target_rpe": 7.0, "rest_seconds": 90},
    {"id": "woex-legs-a-4", "workout_id": "wo-legs-a", "exercise_id": "ex-calf-raises-standing", "sequence": 3, "target_sets": 4, "target_reps": 15, "target_rpe": 6.5, "rest_seconds": 60},
    {"id": "woex-legs-a-5", "workout_id": "wo-legs-a", "exercise_id": "ex-cable-woodchoppers", "sequence": 4, "target_sets": 3, "target_reps": 12, "target_rpe": 7.0, "rest_seconds": 60},
]