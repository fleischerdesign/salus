from datetime import datetime, timezone, timedelta
from typing import Optional
from salus.models.workout import Exercise, WorkoutPlanExercise
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.activity import ActivityAnalysisService


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
        """
        Calculates user's recovery score out of 100.
        Returns: (overall_score, sleep_score, rhr_score, steps_score)
        """
        if date_str is None:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # 1. Sleep Score (centered at 80.0 for matching baseline)
        sleep_trend = self.sleep_svc.trend(days=7, user_id=user_id)
        if sleep_trend:
            baseline_sleep = sum(s.duration_hours for s in sleep_trend) / len(
                sleep_trend
            )
        else:
            baseline_sleep = 8.0

        last_night_sleep = self.sleep_svc.last_night(user_id=user_id, date_str=date_str)
        if last_night_sleep:
            duration = last_night_sleep.duration_hours
            if duration >= baseline_sleep:
                # Up to +20 points for sleeping more than average
                sleep_score = 80.0 + (duration - baseline_sleep) * 10.0
            else:
                # -15 points per hour of deficit
                sleep_score = 80.0 - (baseline_sleep - duration) * 15.0
        else:
            # If no sleep data is recorded, assume standard recovery (80.0)
            sleep_score = 80.0
        sleep_score = max(0.0, min(100.0, sleep_score))

        # 2. Resting Heart Rate Score (centered at 80.0)
        anchor = datetime.strptime(date_str, "%Y-%m-%d")
        rhrs = []
        for i in range(1, 8):
            day_str = (anchor - timedelta(days=i)).strftime("%Y-%m-%d")
            sum_hr = self.activity_svc.heart_rate_summary(
                user_id=user_id, date_str=day_str
            )
            if sum_hr and sum_hr.resting_bpm:
                rhrs.append(sum_hr.resting_bpm)
        baseline_rhr = sum(rhrs) / len(rhrs) if rhrs else 60.0

        today_hr = self.activity_svc.heart_rate_summary(
            user_id=user_id, date_str=date_str
        )
        if today_hr and today_hr.resting_bpm:
            today_rhr = today_hr.resting_bpm
            if today_rhr <= baseline_rhr:
                # Lower RHR indicates better recovery
                rhr_score = 80.0 + (baseline_rhr - today_rhr) * 5.0
            else:
                # Elevated RHR indicates fatigue
                rhr_score = 80.0 - (today_rhr - baseline_rhr) * 10.0
        else:
            rhr_score = 80.0
        rhr_score = max(0.0, min(100.0, rhr_score))

        # 3. Steps/Activity Local Fatigue (centered at 80.0)
        steps_trend = self.activity_svc.steps_trend(
            days=8, user_id=user_id, date=date_str
        )
        if len(steps_trend) >= 2:
            yesterday_steps = steps_trend[-2].count
            baseline_steps = sum(s.count for s in steps_trend[:-1]) / (
                len(steps_trend) - 1
            )
            if baseline_steps <= 0:
                baseline_steps = 10000.0

            if yesterday_steps > baseline_steps:
                steps_score = (
                    80.0 - ((yesterday_steps - baseline_steps) / baseline_steps) * 40.0
                )
            else:
                steps_score = (
                    80.0 + ((baseline_steps - yesterday_steps) / baseline_steps) * 10.0
                )
        else:
            steps_score = 80.0
        steps_score = max(0.0, min(100.0, steps_score))

        # Weighted recovery score
        overall = (0.5 * sleep_score) + (0.3 * rhr_score) + (0.2 * steps_score)
        return overall, sleep_score, rhr_score, steps_score

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

            if overall > 85.0:
                sets_adjust = 1
                weight_mult = 1.05
                rpe_adjust = 0.5
                reasons.append(
                    f"Excellent recovery ({overall:.0f}% score). Suggesting peak weights/volume."
                )
            elif overall < 40.0:
                sets_adjust = -1
                weight_mult = 0.85
                rpe_adjust = -2.0
                reasons.append(
                    f"Critical fatigue ({overall:.0f}% score). Suggesting deload."
                )
            elif overall < 60.0:
                sets_adjust = -1
                weight_mult = 0.92
                rpe_adjust = -1.0
                reasons.append(
                    f"Mild fatigue ({overall:.0f}% score). Suggesting conservative load."
                )
            else:
                reasons.append("Standard recovery. Keep planned targets.")

            # Localized steps/leg fatigue check
            if steps_score < 75.0:
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
