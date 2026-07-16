from datetime import datetime, timezone, timedelta
from typing import Optional
from salus.models.workout import Exercise, WorkoutPlanExercise
from salus.services.analytics.activity import ActivityAnalysisService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.stats import recovery_composite


class AutoregulationService:
    def __init__(
        self,
        sleep_svc: SleepAnalysisService,
        activity_svc: ActivityAnalysisService,
    ) -> None:
        self.sleep_svc = sleep_svc
        self.activity_svc = activity_svc

    def calculate_recovery_score(
        self, user_id: str, date_str: Optional[str] = None
    ) -> tuple[float, float, float, float]:
        if date_str is None:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        sleep_trend = self.sleep_svc.trend(days=7, user_id=user_id)
        if sleep_trend:
            durations = [s.duration_hours for s in sleep_trend]
            mu_sleep = sum(durations) / len(durations)
            sig_sleep = (
                (sum((d - mu_sleep) ** 2 for d in durations) / max(len(durations) - 1, 1))
                ** 0.5
            )
            last_sleep = durations[-1] if durations else 7.0
        else:
            mu_sleep = 7.0
            sig_sleep = 1.0
            last_sleep = 7.0

        anchor = datetime.strptime(date_str, "%Y-%m-%d")
        hr_values = []
        for i in range(1, 8):
            day_str = (anchor - timedelta(days=i)).strftime("%Y-%m-%d")
            summary = self.activity_svc.heart_rate_summary(
                user_id=user_id, date_str=day_str
            )
            if summary and summary.resting_bpm:
                hr_values.append(summary.resting_bpm)
        mu_hr = sum(hr_values) / len(hr_values) if hr_values else 60.0
        sig_hr = (
            (sum((v - mu_hr) ** 2 for v in hr_values) / max(len(hr_values) - 1, 1))
            ** 0.5
            if len(hr_values) >= 2
            else 5.0
        )
        today_hr_info = self.activity_svc.heart_rate_summary(
            user_id=user_id, date_str=date_str
        )
        today_rhr = today_hr_info.resting_bpm if (today_hr_info and today_hr_info.resting_bpm) else mu_hr

        steps_trend = self.activity_svc.steps_trend(
            days=8, user_id=user_id, date=date_str
        )
        if len(steps_trend) >= 2:
            step_vals = [float(s.count) for s in steps_trend[:-1]]
            mu_log = sum(max(v, 1) for v in step_vals) / len(step_vals)
            sig_log = (
                (sum((max(v, 1) - mu_log) ** 2 for v in step_vals) / max(len(step_vals) - 1, 1))
                ** 0.5
                if len(step_vals) >= 2
                else 1.0
            )
            yesterday_steps = int(steps_trend[-2].count)
        else:
            mu_log = 8.0
            sig_log = 1.0
            yesterday_steps = 5000

        has_data = (
            bool(sleep_trend)
            or bool(hr_values)
            or any(s.count > 0 for s in steps_trend)
        )
        if not has_data:
            return 100.0, 0.0, 0.0, 0.0

        has_steps = any(s.count > 0 for s in steps_trend)
        if not has_steps:
            mu_log = 8.0
            sig_log = 1.0
            yesterday_steps = 5000

        score = recovery_composite(
            sleep_score=last_sleep,
            hrv_rmssd=50.0,
            resting_hr=today_rhr,
            steps=yesterday_steps,
            baselines={
                "sleep": (mu_sleep, max(sig_sleep, 0.01)),
                "hrv": (50.0, 10.0),
                "resting_hr": (mu_hr, max(sig_hr, 0.01)),
                "log_steps": (mu_log, max(sig_log, 0.01)),
            },
            skip_steps=not has_steps,
        )
        return score.score, score.sleep_z, score.hr_z, score.steps_z

    def get_autoregulated_targets(
        self,
        user_id: str,
        exercises_with_targets: list[tuple[WorkoutPlanExercise, Exercise]],
        date_str: Optional[str] = None,
    ) -> list[dict]:
        """
        Resolves dynamic targets based on recovery and anatomical muscle mapping.
        """
        overall, sleep_score, rhr_score, steps_score = self.calculate_recovery_score(
            user_id, date_str
        )

        results = []
        lower_body_muscles = {
            "quadriceps",
            "hamstrings",
            "gluteus_maximus",
            "gastrocnemius",
            "soleus",
        }

        for plan_ex, ex in exercises_with_targets:
            # If manually locked or plan has disabled autoreg
            if plan_ex.is_autoreg_exempt:
                results.append(
                    {
                        "exercise_id": ex.id,
                        "name": ex.name,
                        "suggested_sets": plan_ex.target_sets,
                        "suggested_reps": plan_ex.target_reps,
                        "suggested_rpe": plan_ex.target_rpe or 8.0,
                        "weight_multiplier": 1.0,
                        "is_autoreg_exempt": True,
                        "reason": "Manually locked (exemption policy enabled).",
                    }
                )
                continue

            # Default CNS adjustments
            sets_adjust = 0
            weight_mult = 1.0
            rpe_adjust = 0.0
            reasons = []

            if overall > 75.0:
                sets_adjust = 1
                weight_mult = 1.05
                rpe_adjust = 0.5
                reasons.append(
                    f"Primed recovery ({overall:.0f}/100). Peak weights/volume recommended."
                )
            elif overall < 35.0:
                sets_adjust = -1
                weight_mult = 0.85
                rpe_adjust = -2.0
                reasons.append(
                    f"Underrecovered ({overall:.0f}/100). Deload recommended."
                )
            elif overall < 50.0:
                sets_adjust = -1
                weight_mult = 0.92
                rpe_adjust = -1.0
                reasons.append(
                    f"Moderate fatigue ({overall:.0f}/100). Conservative load recommended."
                )
            else:
                reasons.append("Standard recovery. Keep planned targets.")

            # Localized leg fatigue check (steps_z > 0 = more steps than baseline)
            if steps_score > 1.0:
                # Parse exercise target muscles
                primary = {
                    m.strip().lower()
                    for m in ex.primary_muscles.split(",")
                    if m.strip()
                }
                secondary = {
                    m.strip().lower()
                    for m in (ex.secondary_muscles or "").split(",")
                    if m.strip()
                }
                target_muscles = primary.union(secondary)

                # Check intersection with lower body muscles
                if target_muscles.intersection(lower_body_muscles):
                    # Legs are tired! Apply secondary localized deload
                    weight_mult *= 0.90
                    sets_adjust = min(sets_adjust, -1)
                    reasons.append("Localized leg fatigue (high steps count) applied.")

            final_sets = max(1, plan_ex.target_sets + sets_adjust)
            final_rpe = max(5.0, min(10.0, (plan_ex.target_rpe or 8.0) + rpe_adjust))

            results.append(
                {
                    "exercise_id": ex.id,
                    "name": ex.name,
                    "suggested_sets": final_sets,
                    "suggested_reps": plan_ex.target_reps,
                    "suggested_rpe": round(final_rpe, 1),
                    "weight_multiplier": round(weight_mult, 3),
                    "is_autoreg_exempt": False,
                    "reason": " ".join(reasons),
                }
            )

        return results
