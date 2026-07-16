from datetime import date, datetime, timedelta, timezone

from salus.models.analytics import TDEEResult
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.analytics import (
    AnalyticsExerciseSession,
    AnalyticsOverview,
    AnalyticsSleepSummary,
    AnalyticsTdeeData,
    AnalyticsWeightPoint,
    AnalyticsWeightTrend,
    CorrelationMatrixResponse,
    CorrelationModel,
    ForecastPoint,
    ForecastResponse,
    HeatmapDay,
    HeatmapResponse,
    OneRMResultModel,
    TimeSeriesPoint,
    TimeSeriesResponse,
    WellnessComponent,
    WellnessScoreResponse,
    WorkoutProgressionResponse,
    WorkoutSessionItem,
)
from salus.services.analytics.activity import ActivityAnalysisService
from salus.services.analytics.nutrition import NutritionAnalysisService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.stats import (
    benjamini_hochberg,
    bmr_cunningham,
    bmr_mifflin_st_jeor,
    hrr_pct,
    linear_regression,
    mape,
    one_rm_regression,
    pal_from_hrr,
    pearson,
    prediction_interval,
    recovery_composite,
    tef_from_macros,
    tdee as kernel_tdee,
    tonnage_progression,
    hr_max_tanaka,
)
from salus.services.analytics.weight import WeightAnalysisService

RANGE_DAYS: dict[str, int] = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}


class AnalyticsService:
    def __init__(
        self,
        uow: IUnitOfWork,
        sleep_svc: SleepAnalysisService,
        activity_svc: ActivityAnalysisService,
        weight_svc: WeightAnalysisService,
        nutrition_svc: NutritionAnalysisService,
    ) -> None:
        self._uow = uow
        self._sleep = sleep_svc
        self._activity = activity_svc
        self._weight = weight_svc
        self._nutrition = nutrition_svc

    def overview(self, user_id: str, range_key: str = "30d") -> AnalyticsOverview:
        days = RANGE_DAYS.get(range_key, 30)

        steps = self._activity.steps_trend(days=days, user_id=user_id)
        sleep_list = self._sleep.trend(days=days, user_id=user_id)
        weight_trend = self._weight.trend(days=days, user_id=user_id)
        exercise_sessions = self._activity.exercise_history(
            days=days, user_id=user_id, limit=5
        )
        tdee = self._compute_tdee(user_id=user_id, weight_trend=weight_trend)

        return AnalyticsOverview(
            steps_points=[
                {"date": s.date, "count": s.count} for s in steps
            ],
            weight_points=[
                {"date": w.date, "weight_kg": round(w.weight_kg, 1)}
                for w in weight_trend.points
            ],
            sleep_summaries=[
                AnalyticsSleepSummary(
                    date=s.date,
                    duration_hours=round(s.duration_hours, 2),
                    awake_pct=round(s.awake_pct, 1),
                    light_pct=round(s.light_pct, 1),
                    deep_pct=round(s.deep_pct, 1),
                    rem_pct=round(s.rem_pct, 1),
                )
                for s in sleep_list
            ],
            latest_sleep=(
                AnalyticsSleepSummary(
                    date=sleep_list[-1].date,
                    duration_hours=round(sleep_list[-1].duration_hours, 2),
                    awake_pct=round(sleep_list[-1].awake_pct, 1),
                    light_pct=round(sleep_list[-1].light_pct, 1),
                    deep_pct=round(sleep_list[-1].deep_pct, 1),
                    rem_pct=round(sleep_list[-1].rem_pct, 1),
                )
                if sleep_list
                else None
            ),
            weight_trend=AnalyticsWeightTrend(
                points=[
                    AnalyticsWeightPoint(
                        date=p.date, weight_kg=round(p.weight_kg, 1)
                    )
                    for p in weight_trend.points
                ],
                current=weight_trend.current,
                start=weight_trend.start,
                delta=weight_trend.delta,
            ),
            tdee=(
                AnalyticsTdeeData(
                    tdee_kcal=tdee.tdee_kcal,
                    bmr_kcal=tdee.bmr_kcal,
                    pal_factor=tdee.pal_factor,
                    hrr_pct=tdee.hrr_pct,
                )
                if tdee
                else None
            ),
            exercise_sessions=[
                AnalyticsExerciseSession(
                    type_name=s.type_name if s else "",
                    date=s.date if s else "",
                    time=s.time if s else "",
                    duration_seconds=s.duration_seconds if s else 0,
                    distance_meters=s.distance_meters if s else 0,
                    calories=s.calories if s else 0,
                )
                for s in exercise_sessions
            ],
            days=days,
            range_key=range_key,
        )

    def timeseries(
        self, user_id: str, metric: str, range_key: str = "30d", bucket: str = "daily"
    ) -> TimeSeriesResponse:
        days = RANGE_DAYS.get(range_key, 30)
        since = datetime.now(timezone.utc) - timedelta(days=days)
        repo = self._uow.measurements
        records = repo.find_all(
            user_id=user_id, data_types=[metric], since=since
        )
        records.sort(key=lambda m: m.start_time)
        bucket_values: dict[str, list[float]] = {}
        for m in records:
            key = m.start_time.strftime("%Y-%m-%d")
            if bucket == "weekly":
                iso = m.start_time.isocalendar()
                key = f"{iso[0]}-W{iso[1]:02d}"
            elif bucket == "monthly":
                key = m.start_time.strftime("%Y-%m")
            if key not in bucket_values:
                bucket_values[key] = []
            bucket_values[key].append(
                m.value_numeric if m.value_numeric is not None else 0.0
            )
        aggregated: list[tuple[str, float]] = []
        for k, vals in sorted(bucket_values.items()):
            if metrics_require_sum(metric):
                aggregated.append((k, sum(vals)))
            else:
                aggregated.append((k, sum(vals) / len(vals)))
        ts_points = [TimeSeriesPoint(date=d, value=v) for d, v in aggregated]
        return TimeSeriesResponse(
            metric=metric,
            points=ts_points,
            n=len(ts_points),
            bucket=bucket,
            range_key=range_key,
        )

    def correlations(
        self, user_id: str, range_key: str = "90d", min_n: int = 14
    ) -> CorrelationMatrixResponse:
        days = RANGE_DAYS.get(range_key, 90)
        since = datetime.now(timezone.utc) - timedelta(days=days)
        repo = self._uow.measurements
        records = repo.find_all(user_id=user_id, since=since)
        if not records:
            return CorrelationMatrixResponse(
                pairs=[], n_comparisons=0, correction="Benjamini-Hochberg FDR",
                min_n=min_n, range_key=range_key,
            )
        metric_types = self._uow.metric_types.find_all(user_id=None)
        type_map = {mt.id: mt.name for mt in metric_types}
        pivot: dict[str, list[float]] = {}
        for m in records:
            if m.value_numeric is None:
                continue
            name = type_map.get(m.metric_type_id, m.data_type)
            if name not in pivot:
                pivot[name] = []
            pivot[name].append(m.value_numeric)
        metrics = [name for name, vals in pivot.items() if len(vals) >= min_n]
        pairs: list[CorrelationModel] = []
        for i, ma in enumerate(metrics):
            for mb in metrics[i + 1:]:
                xs = pivot[ma]
                ys = pivot[mb]
                pr = pearson(xs, ys)
                if pr is None:
                    continue
                pairs.append(
                    CorrelationModel(
                        metric_a=ma,
                        metric_b=mb,
                        pearson_r=round(pr.r, 4),
                        pearson_p=round(pr.p_value, 4),
                        spearman_r=0.0,
                        spearman_p=0.0,
                        p_adjusted_bh=1.0,
                        effect_size_d=round(abs(pr.r), 4),
                        ci_95_lower=round(pr.ci_lower, 4),
                        ci_95_upper=round(pr.ci_upper, 4),
                        n=pr.n,
                        interpretation="",
                    )
                )
        if pairs:
            p_values = [p.pearson_p for p in pairs]
            fdr = benjamini_hochberg(p_values)
            pairs = [
                CorrelationModel(
                    metric_a=p.metric_a,
                    metric_b=p.metric_b,
                    pearson_r=p.pearson_r,
                    pearson_p=p.pearson_p,
                    spearman_r=p.spearman_r,
                    spearman_p=p.spearman_p,
                    p_adjusted_bh=round(fdr.adjusted[i], 4),
                    effect_size_d=p.effect_size_d,
                    ci_95_lower=p.ci_95_lower,
                    ci_95_upper=p.ci_95_upper,
                    n=p.n,
                    interpretation=_interpret_cohens(p.effect_size_d),
                )
                for i, p in enumerate(pairs)
            ]
        return CorrelationMatrixResponse(
            pairs=pairs,
            n_comparisons=len(pairs),
            correction="Benjamini-Hochberg FDR",
            min_n=min_n,
            range_key=range_key,
        )

    def forecast(
        self, user_id: str, metric: str, horizon_days: int = 30
    ) -> ForecastResponse:
        since = datetime.now(timezone.utc) - timedelta(days=365)
        repo = self._uow.measurements
        records = repo.find_all(
            user_id=user_id, data_types=[metric], since=since
        )
        records.sort(key=lambda m: m.start_time)
        if len(records) < 3:
            return ForecastResponse(
                metric=metric, points=[], method="linear",
                r_squared=0.0, mape=None, n_train=0, horizon_days=horizon_days,
            )
        values = [
            m.value_numeric if m.value_numeric is not None else 0.0
            for m in records
        ]
        xs_idx = [float(i) for i in range(len(values))]
        reg = linear_regression(xs_idx, values)
        if reg is None:
            return ForecastResponse(
                metric=metric, points=[], method="linear",
                r_squared=0.0, mape=None, n_train=0, horizon_days=horizon_days,
            )
        last_date = records[-1].start_time
        forecast_points: list[ForecastPoint] = []
        for h_val in range(1, horizon_days + 1):
            pi = prediction_interval(reg, float(len(values) + h_val - 1))
            point = ForecastPoint(
                date=(last_date + timedelta(days=h_val)).strftime("%Y-%m-%d"),
                predicted=round(pi.point_estimate, 2) if pi else 0.0,
                ci_lower=round(pi.lower, 2) if pi else 0.0,
                ci_upper=round(pi.upper, 2) if pi else 0.0,
            )
            if pi:
                forecast_points.append(point)
            forecast_points.append(point)
            if len(forecast_points) >= 2:
                if forecast_points[-1] is forecast_points[-2]:
                    forecast_points.pop()
        actual = values[-horizon_days:] if len(values) >= horizon_days else values
        pred = [fp.predicted for fp in forecast_points[:len(actual)]]
        mape_val = mape(actual, pred) if actual and pred else None
        return ForecastResponse(
            metric=metric,
            points=forecast_points,
            method="linear",
            r_squared=round(reg.r_squared, 4),
            mape=mape_val,
            n_train=len(values),
            horizon_days=horizon_days,
        )

    def heatmap(
        self, user_id: str, metric: str, year: int
    ) -> HeatmapResponse:
        start = datetime(year, 1, 1, tzinfo=timezone.utc)
        end = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        repo = self._uow.measurements
        records = repo.find_all(
            user_id=user_id, data_types=[metric], since=start, until=end
        )
        daily: dict[str, float] = {}
        for m in records:
            ds = m.start_time.strftime("%Y-%m-%d")
            daily[ds] = max(daily.get(ds, float("-inf")), m.value_numeric or 0.0)
        all_values = list(daily.values())
        max_val = max(all_values) if all_values else None
        n_vals = len(all_values)
        days_data: list[HeatmapDay] = []
        current = start.date()
        last = end.date()
        while current <= last:
            ds = current.isoformat()
            if ds in daily:
                v = daily[ds]
                rank = sum(1 for x in all_values if x < v) / max(n_vals, 1)
                days_data.append(
                    HeatmapDay(date=ds, value=v, percentile_rank=round(rank, 4))
                )
            else:
                days_data.append(HeatmapDay(date=ds, value=None, percentile_rank=None))
            current += timedelta(days=1)
        return HeatmapResponse(
            metric=metric,
            year=year,
            days=days_data,
            max_value=max_val,
            method="daily_max",
        )

    def wellness_score(
        self, user_id: str, date_str: str
    ) -> WellnessScoreResponse:
        target_date = date.fromisoformat(date_str)
        since_dt = datetime.combine(
            target_date - timedelta(days=28), datetime.min.time(), tzinfo=timezone.utc
        )
        until_dt = datetime.combine(
            target_date, datetime.max.time(), tzinfo=timezone.utc
        )
        repo = self._uow.measurements
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
            hr_std = _safe_std(hr_values)
            n_baseline = max(n_baseline, len(hr_values))
        else:
            hr_resting = 70.0
            hr_std = 5.0
        if step_values:
            log_vals = [max(v, 1.0) for v in step_values]
            log_mean = sum(log_vals) / len(log_vals)
            log_std = _safe_std(log_vals)
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

    def workout_progression(
        self, user_id: str, exercise_id: str, range_days: int = 180,
    ) -> WorkoutProgressionResponse | None:
        since = datetime.now(timezone.utc) - timedelta(days=range_days)
        repo = self._uow.workout_log_entries
        rows = repo.get_exercise_progression(user_id, exercise_id, since=since)
        if not rows:
            return None
        exercise = self._uow.exercises.get_by_id(exercise_id)
        exercise_name = exercise.name if exercise else "unknown"
        session_items = [
            WorkoutSessionItem(
                date=str(r["date"]),
                total_tonnage=float(r["total_tonnage"]),
                max_weight=float(r["max_weight"]),
                sets_count=int(r["sets_count"]),
            )
            for r in rows
        ]
        weeks: list[int] = []
        tonnages: list[float] = []
        all_sets: list[tuple[float, float]] = []
        week_idx = 0
        last_week = ""
        for si in session_items:
            iso = si.date[:7]
            if iso != last_week:
                week_idx += 1
                last_week = iso
            weeks.append(week_idx)
            tonnages.append(si.total_tonnage)
            if si.max_weight > 0:
                for _ in range(si.sets_count):
                    all_sets.append((si.max_weight, 5.0))
        session_tonnages = list(zip(weeks, tonnages))
        prog = tonnage_progression(session_tonnages)
        one_rm = one_rm_regression(all_sets)
        if prog is None:
            return None
        return WorkoutProgressionResponse(
            exercise_name=exercise_name,
            sessions=session_items,
            one_rm=OneRMResultModel(
                one_rm=one_rm.one_rm if one_rm else 0.0,
                ci_lower=one_rm.ci_lower if one_rm else 0.0,
                ci_upper=one_rm.ci_upper if one_rm else 0.0,
                n_sets=one_rm.n_sets if one_rm else 0,
                r_squared=round(one_rm.r_squared, 4) if one_rm else 0.0,
            ),
            slope_kg_per_week=round(prog.slope_kg_per_week, 4),
            r_squared=round(prog.r_squared, 4),
            is_plateaued=prog.is_plateaued,
        )

    def _compute_tdee(
        self, user_id: str, weight_trend
    ) -> TDEEResult | None:
        weight_kg = weight_trend.current if weight_trend else None
        if not weight_kg:
            return None
        bmr = bmr_cunningham(weight_kg)
        if bmr is None:
            ml = bmr_mifflin_st_jeor(weight_kg, 170.0, 30.0, None)
            bmr = ml
        hr_summary = self._activity.heart_rate_summary(user_id=user_id)
        hr_rest = hr_summary.resting_bpm if hr_summary else 60.0
        hr_awake = hr_summary.avg_bpm if hr_summary else 75.0
        hr_max = hr_max_tanaka(30.0)
        hrr_pct_val = hrr_pct(hr_awake, hr_rest, hr_max)
        pal = pal_from_hrr(hrr_pct_val)
        nutrition_today = self._nutrition.today(user_id=user_id)
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


def metrics_require_sum(name: str) -> bool:
    return name in {"steps"}


def _interpret_cohens(d_val: float) -> str:
    abs_d = abs(d_val)
    if abs_d >= 0.8:
        return "large"
    if abs_d >= 0.5:
        return "medium"
    if abs_d >= 0.2:
        return "small"
    return "negligible"


def _safe_std(values: list[float]) -> float:
    if len(values) < 2:
        return 1.0
    m = sum(values) / len(values)
    var = sum((v - m) ** 2 for v in values) / (len(values) - 1)
    return var ** 0.5
