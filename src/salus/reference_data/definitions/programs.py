"""Default standard periodization programs (splits) seeded on system startup.

Shared across all users (user_id=None, shared_nullable strategy). Each program
holds a progression scheme and schedules workouts across the week via
``ProgramWorkout`` slots (day_of_week: 0=Mo .. 6=So).
"""

DEFAULT_PROGRAMS: list[dict] = [
    {
        "id": "prog-full-body-3d",
        "name": "Ganzkörper 3er-Split (Alternierend A/B)",
        "description": "Alternierend effizientes Ganzkörpertraining an 3 Tagen (Mo/Mi/Fr). Wechselt zwischen Ganzkörper A (Kniebeuge & Druck) und Ganzkörper B (Kreuzheben & Zug) für ausgewogene Entwicklung.",
        "progression_scheme": "autoregulated",
        "position": 0,
        "is_active": False,
    },
    {
        "id": "prog-upper-lower-4d",
        "name": "Oberkörper / Unterkörper 4-Tage-Split (OK/UK)",
        "description": "Klassischer 4-Tage-Oberkörper/Unterkörper-Split mit abwechselnden schweren und volumenbasierten Tagen für Masse und Kraft.",
        "progression_scheme": "autoregulated",
        "position": 1,
        "is_active": False,
    },
    {
        "id": "prog-ppl-hypertrophy",
        "name": "Push / Pull / Legs (PPL Hypertrophie)",
        "description": "Push-Pull-Legs Hypertrophie-Split: drückende, ziehende und Unterkörper-Workouts im wöchentlichen Zyklus für maximale Muskelmassensteigerung.",
        "progression_scheme": "autoregulated",
        "position": 2,
        "is_active": False,
    },
]

DEFAULT_PROGRAM_WORKOUTS: list[dict] = [
    # ── prog-full-body-3d: Ganzkörper 3er-Split (Alternierend A/B) ──
    {"id": "prgw-fb-mon", "program_id": "prog-full-body-3d", "workout_id": "wo-fb-a", "sequence": 0, "day_of_week": 0},
    {"id": "prgw-fb-wed", "program_id": "prog-full-body-3d", "workout_id": "wo-fb-b", "sequence": 1, "day_of_week": 2},
    {"id": "prgw-fb-fri", "program_id": "prog-full-body-3d", "workout_id": "wo-fb-a", "sequence": 2, "day_of_week": 4},

    # ── prog-upper-lower-4d: Oberkörper / Unterkörper 4-Tage-Split ──
    {"id": "prgw-ul-mon", "program_id": "prog-upper-lower-4d", "workout_id": "wo-upper-a", "sequence": 0, "day_of_week": 0},
    {"id": "prgw-ul-tue", "program_id": "prog-upper-lower-4d", "workout_id": "wo-lower-a", "sequence": 1, "day_of_week": 1},
    {"id": "prgw-ul-thu", "program_id": "prog-upper-lower-4d", "workout_id": "wo-upper-b", "sequence": 2, "day_of_week": 3},
    {"id": "prgw-ul-fri", "program_id": "prog-upper-lower-4d", "workout_id": "wo-lower-b", "sequence": 3, "day_of_week": 4},

    # ── prog-ppl-hypertrophy: Push / Pull / Legs (PPL Hypertrophie) ──
    {"id": "prgw-ppl-mon", "program_id": "prog-ppl-hypertrophy", "workout_id": "wo-push-a", "sequence": 0, "day_of_week": 0},
    {"id": "prgw-ppl-tue", "program_id": "prog-ppl-hypertrophy", "workout_id": "wo-pull-a", "sequence": 1, "day_of_week": 1},
    {"id": "prgw-ppl-wed", "program_id": "prog-ppl-hypertrophy", "workout_id": "wo-legs-a", "sequence": 2, "day_of_week": 2},
    {"id": "prgw-ppl-thu", "program_id": "prog-ppl-hypertrophy", "workout_id": "wo-push-a", "sequence": 3, "day_of_week": 3},
    {"id": "prgw-ppl-fri", "program_id": "prog-ppl-hypertrophy", "workout_id": "wo-pull-a", "sequence": 4, "day_of_week": 4},
    {"id": "prgw-ppl-sat", "program_id": "prog-ppl-hypertrophy", "workout_id": "wo-legs-a", "sequence": 5, "day_of_week": 5},
]