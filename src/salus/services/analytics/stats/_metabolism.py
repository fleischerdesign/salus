def bmr_cunningham(weight_kg: float, body_fat_pct: float | None = None) -> float | None:
    if body_fat_pct is None or body_fat_pct < 0.0 or body_fat_pct >= 1.0:
        return None
    lbm = weight_kg * (1.0 - body_fat_pct)
    return 500.0 + 22.0 * lbm


def bmr_mifflin_st_jeor(
    weight_kg: float, height_cm: float, age_y: float, sex: str | None = None
) -> float:
    base = 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age_y
    if sex == "male":
        return base + 5.0
    return base - 161.0


def hr_max_tanaka(age_y: float) -> float:
    return 208.0 - 0.7 * age_y


def hrr_pct(hr_avg_awake: float, hr_resting: float, hr_max: float) -> float:
    if hr_max == hr_resting:
        return 0.05
    raw = (hr_avg_awake - hr_resting) / (hr_max - hr_resting)
    return max(0.05, min(0.85, raw))


def pal_from_hrr(hrr_percent: float, calibration_factor: float = 1.5) -> float:
    return max(1.0, min(2.5, 1.0 + hrr_percent * calibration_factor))


def tef_from_macros(protein_g: float, carbs_g: float, fat_g: float) -> float:
    return protein_g * 4.0 * 0.25 + carbs_g * 4.0 * 0.06 + fat_g * 9.0 * 0.02


def tdee(bmr: float, pal: float, tef: float) -> float:
    return round(bmr * pal + tef)
