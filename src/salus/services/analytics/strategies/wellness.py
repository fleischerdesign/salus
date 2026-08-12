"""Composite wellness score strategy."""
from datetime import date, datetime, timezone, timedelta

from salus.schemas.analytics import WellnessComponent, WellnessScoreResponse
from salus.services.analytics.stats import recovery_composite
from salus.services.analytics.strategies._helpers import safe_std
from salus.services.analytics.strategies.context import AnalyticsContext


class WellnessScoreStrategy:
    def compute(
        self, ctx: AnalyticsContext, user_id: str, date_str: str
    ) -> WellnessScoreResponse:
        target_date = date.fromisoformat(date_str)
        since_dt = datetime.combine(
            target_date - timedelta(days=28), datetime.min.time(), tzinfo=timezone.utc
        )
        until_dt = datetime.combine(
            target_date, datetime.max.time(), tzinfo=timezone.utc
        )
        repo = ctx.uow.measurements
        hr_records = repo.find_all(
            user_id=user_id, data_types=["heart_rate"], since=since_dt, until=until_dt
        )
        step_records = repo.find_all(
            user_id=user_id, data_types=["steps"], since=since_dt, until=until_dt
        )
        hr_values = [m.value_numeric for m in hr_records if m.value_numeric is not None]
        step_values = [
            m.value_numeric for m in step_records if m.value_numeric is not None
        ]
        n_baseline = 0
        if hr_values:
            hr_resting = min(hr_values)
            hr_std = safe_std(hr_values)
            n_baseline = max(n_baseline, len(hr_values))
        else:
            hr_resting = 70.0
            hr_std = 5.0
        if step_values:
            log_vals = [max(v, 1.0) for v in step_values]
            log_mean = sum(log_vals) / len(log_vals)
            log_std = safe_std(log_vals)
            n_baseline = max(n_baseline, len(step_values))
        else:
            log_mean = 8.0
            log_std = 1.0
        score_args = recovery_composite(
            sleep_score=7.0,
            hrv_rmssd=50.0,
            resting_hr=hr_resting,
            steps=int(sum(step_values)) if step_values else 5000,
            baselines={
                "sleep": (7.0, 1.0),
                "hrv": (50.0, 10.0),
                "resting_hr": (hr_resting, hr_std),
                "log_steps": (log_mean, log_std),
            },
        )
        return WellnessScoreResponse(
            date=date_str,
            score=round(score_args.score, 1),
            interpretation=score_args.interpretation,
            sleep=WellnessComponent(
                z_score=round(score_args.sleep_z, 2), raw_value=7.0
            ),
            hrv=WellnessComponent(
                z_score=round(score_args.hrv_z, 2), raw_value=50.0
            ),
            resting_hr=WellnessComponent(
                z_score=round(score_args.hr_z, 2), raw_value=hr_resting
            ),
            steps=WellnessComponent(
                z_score=round(score_args.steps_z, 2),
                raw_value=float(sum(step_values)) if step_values else 5000.0,
            ),
            n_baseline_days=n_baseline,
        )
