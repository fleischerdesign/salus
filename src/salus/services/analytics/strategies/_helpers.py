"""Pure computation helpers shared by analytics strategies."""
from salus.models.analytics import TDEEResult
from salus.services.analytics.stats import (
    bmr_cunningham,
    bmr_mifflin_st_jeor,
    hrr_pct,
    hr_max_tanaka,
    pal_from_hrr,
    tdee as kernel_tdee,
    tef_from_macros,
)


def metrics_require_sum(name: str) -> bool:
    return name in {"steps"}


def interpret_cohens(d_val: float) -> str:
    abs_d = abs(d_val)
    if abs_d >= 0.8:
        return "large"
    if abs_d >= 0.5:
        return "medium"
    if abs_d >= 0.2:
        return "small"
    return "negligible"


def safe_std(values: list[float]) -> float:
    if len(values) < 2:
        return 1.0
    m = sum(values) / len(values)
    var = sum((v - m) ** 2 for v in values) / (len(values) - 1)
    return var ** 0.5


def compute_tdee(ctx, user_id: str, weight_trend) -> TDEEResult | None:
    weight_kg = weight_trend.current if weight_trend else None
    if not weight_kg:
        return None
    bmr = bmr_cunningham(weight_kg)
    if bmr is None:
        bmr = bmr_mifflin_st_jeor(weight_kg, 170.0, 30.0, None)
    hr_summary = ctx.activity.heart_rate_summary(user_id=user_id)
    hr_rest = hr_summary.resting_bpm if hr_summary else 60.0
    hr_awake = hr_summary.avg_bpm if hr_summary else 75.0
    hr_max = hr_max_tanaka(30.0)
    hrr_pct_val = hrr_pct(hr_awake, hr_rest, hr_max)
    pal = pal_from_hrr(hrr_pct_val)
    nutrition_today = ctx.nutrition.today(user_id=user_id)
    tef = 0.0
    if nutrition_today:
        tef = tef_from_macros(
            nutrition_today.protein_g,
            nutrition_today.carbs_g,
            nutrition_today.fat_g,
        )
    tdee_val = kernel_tdee(bmr, pal, tef)
    return TDEEResult(
        bmr_kcal=bmr,
        tdee_kcal=tdee_val,
        pal_factor=pal,
        hrr_pct=hrr_pct_val,
        hr_resting=hr_rest,
        hr_awake_avg=hr_awake,
        lean_mass_kg=None,
        body_fat_pct=None,
    )
