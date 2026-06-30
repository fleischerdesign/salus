"""
Pure calculation functions for health analytics.
No dependencies on repositories or external services.
All functions are stateless and independently testable.
"""

from salus.models.goal import GoalDirection, GoalFrequency

SLEEP_STAGE_MAP: dict[str, str] = {"1": "Awake", "4": "Light", "5": "Deep", "6": "REM"}

EXERCISE_TYPE_MAP: dict[int, str] = {
    0: "Other Workout",
    2: "Badminton",
    4: "Baseball",
    5: "Basketball",
    8: "Cycling",
    9: "Cycling (Stationary)",
    10: "Boot Camp",
    11: "Boxing",
    13: "Calisthenics",
    14: "Cricket",
    16: "Dancing",
    25: "Elliptical",
    26: "Fitness Class",
    27: "Fencing",
    28: "Football (American)",
    29: "Football (Australian)",
    31: "Frisbee",
    32: "Golf",
    33: "Guided Breathing",
    34: "Gymnastics",
    35: "Handball",
    36: "HIIT",
    37: "Hiking",
    38: "Ice Hockey",
    39: "Ice Skating",
    44: "Martial Arts",
    46: "Paddling",
    47: "Paragliding",
    48: "Pilates",
    50: "Racquetball",
    51: "Rock Climbing",
    52: "Roller Hockey",
    53: "Rowing",
    54: "Rowing Machine",
    55: "Rugby",
    56: "Running",
    57: "Running (Treadmill)",
    58: "Sailing",
    59: "Scuba Diving",
    60: "Skating",
    61: "Skiing",
    62: "Snowboarding",
    63: "Snowshoeing",
    64: "Soccer",
    65: "Softball",
    66: "Squash",
    68: "Stair Climbing",
    69: "Stair Climbing (Machine)",
    70: "Strength Training",
    71: "Stretching",
    72: "Surfing",
    73: "Swimming (Open Water)",
    74: "Swimming (Pool)",
    75: "Table Tennis",
    76: "Tennis",
    78: "Volleyball",
    79: "Walking",
    80: "Water Polo",
    81: "Weightlifting",
    82: "Wheelchair",
    83: "Yoga",
}


def map_sleep_stage(code: str) -> str:
    """Map Samsung Health sleep stage code to human-readable label."""
    return SLEEP_STAGE_MAP.get(code, f"Stage {code}")


def map_exercise_type(code: int) -> str:
    """Map Samsung Health exercise type code to human-readable name."""
    return EXERCISE_TYPE_MAP.get(code, f"Activity {code}")


def calc_bmr_cunningham(weight_kg: float, body_fat_pct: float | None = None) -> float:
    """BMR via Cunningham formula: 500 + 22 * LBM. Falls back to Mifflin-St Jeor."""
    if body_fat_pct is not None and 0 <= body_fat_pct < 1:
        lbm = weight_kg * (1.0 - body_fat_pct)
        return round(500 + 22.0 * lbm, 1)
    return round(10 * weight_kg + 6.25 * 181 - 5 * 30 + 5, 1)


def calc_tef(protein_g: float, carbs_g: float, fat_g: float) -> float:
    """Thermic effect of food from macro intake.
    Protein: 25%, Carbs: 6%, Fat: 2%.
    Returns kcal."""
    return round(
        (protein_g * 4 * 0.25) + (carbs_g * 4 * 0.06) + (fat_g * 9 * 0.02), 1
    )


def calc_tdee(
    bmr: float,
    hr_avg_awake: float,
    hr_resting: float,
    age: int = 30,
    tef: float = 0,
    calibration_factor: float = 1.5,
) -> tuple[float, float, float] | None:
    """TDEE = BMR * PAL(HRR) + TEF.

    Returns (tdee_kcal, pal_factor, hrr_pct) or None if inputs invalid.
    """
    if not all([bmr, hr_avg_awake, hr_resting]):
        return None
    hr_max = 208 - 0.7 * age
    if hr_max <= hr_resting:
        return None
    hrr_pct = (hr_avg_awake - hr_resting) / (hr_max - hr_resting)
    hrr_pct = max(0.05, min(0.85, hrr_pct))
    pal = max(1.0, min(2.5, 1.0 + hrr_pct * calibration_factor))
    tdee = round(bmr * pal + tef, 0)
    return tdee, round(pal, 3), round(hrr_pct, 3)


def compute_goal_progress(
    current_value: float | None,
    target_value: float,
    direction: GoalDirection,
    frequency: GoalFrequency,
    deadline_passed: bool = False,
) -> tuple[int, str, bool]:
    """Compute goal progress as (percent, status, is_fulfilled).

    Status is one of: "fulfilled", "pending", "missed".
    """
    if current_value is None:
        return 0, "pending", False

    if direction == direction.INCREASE:
        fulfilled = current_value >= target_value
    else:
        fulfilled = current_value <= target_value

    if fulfilled:
        return 100, "fulfilled", True

    if direction == direction.INCREASE:
        percent = min(int(current_value / target_value * 100), 100)
    else:
        if current_value <= target_value:
            percent = 100
        else:
            percent = max(0, int(target_value / current_value * 100))

    if frequency == frequency.ONCE and deadline_passed:
        return percent, "missed", False

    return percent, "pending", False
