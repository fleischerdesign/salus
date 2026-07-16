from fastapi import APIRouter, Depends, Query, Response

from salus.dependencies import (
    get_analytics_service,
    get_current_user_or_api,
)
from salus.exceptions import ApiError
from salus.schemas.analytics import (
    AnalyticsComputeRequest,
    AnalyticsComputeResponse,
    AnalyticsOverview,
    CorrelationMatrixResponse,
    ForecastResponse,
    HeatmapResponse,
    MethodologyEntry,
    MethodologyIndexResponse,
    TimeSeriesResponse,
    WellnessScoreResponse,
    WorkoutProgressionResponse,
)
from salus.services._helpers import uid
from salus.services.analytics.orchestrator import AnalyticsService

router = APIRouter(prefix="/api/v1", tags=["Analytics"])


def _set_analytics_headers(response: Response) -> None:
    response.headers["X-Salus-Analytics-Version"] = "1"


@router.get("/analytics/overview", response_model=AnalyticsOverview)
def api_analytics_overview(
    range: str = Query(default="30d"),
    date: str = Query(default=""),
    current_user=Depends(get_current_user_or_api),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
    response: Response = None,  # type: ignore[assignment]
) -> AnalyticsOverview:
    _set_analytics_headers(response)
    return analytics_svc.overview(uid(current_user), range_key=range)


@router.get("/analytics/timeseries", response_model=TimeSeriesResponse)
def api_analytics_timeseries(
    metric: str = Query(...),
    range: str = Query(default="30d"),
    bucket: str = Query(default="daily"),
    current_user=Depends(get_current_user_or_api),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
    response: Response = None,  # type: ignore[assignment]
) -> TimeSeriesResponse:
    _set_analytics_headers(response)
    return analytics_svc.timeseries(
        uid(current_user), metric=metric, range_key=range, bucket=bucket
    )


@router.get("/analytics/correlations", response_model=CorrelationMatrixResponse)
def api_analytics_correlations(
    range: str = Query(default="90d"),
    min_n: int = Query(default=14),
    current_user=Depends(get_current_user_or_api),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
    response: Response = None,  # type: ignore[assignment]
) -> CorrelationMatrixResponse:
    _set_analytics_headers(response)
    return analytics_svc.correlations(
        uid(current_user), range_key=range, min_n=min_n
    )


@router.get("/analytics/forecast", response_model=ForecastResponse)
def api_analytics_forecast(
    metric: str = Query(...),
    horizon_days: int = Query(default=30),
    current_user=Depends(get_current_user_or_api),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
    response: Response = None,  # type: ignore[assignment]
) -> ForecastResponse:
    _set_analytics_headers(response)
    return analytics_svc.forecast(
        uid(current_user), metric=metric, horizon_days=horizon_days
    )


@router.get("/analytics/heatmap", response_model=HeatmapResponse)
def api_analytics_heatmap(
    metric: str = Query(...),
    year: int = Query(...),
    current_user=Depends(get_current_user_or_api),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
    response: Response = None,  # type: ignore[assignment]
) -> HeatmapResponse:
    _set_analytics_headers(response)
    return analytics_svc.heatmap(uid(current_user), metric=metric, year=year)


@router.get("/analytics/wellness-score", response_model=WellnessScoreResponse)
def api_analytics_wellness_score(
    date: str = Query(default=""),
    current_user=Depends(get_current_user_or_api),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
    response: Response = None,  # type: ignore[assignment]
) -> WellnessScoreResponse:
    _set_analytics_headers(response)
    from datetime import date as dt

    date_str = date or dt.today().isoformat()
    return analytics_svc.wellness_score(uid(current_user), date_str)


@router.get("/analytics/methodology", response_model=MethodologyIndexResponse)
def api_analytics_methodology(response: Response = None) -> MethodologyIndexResponse:  # type: ignore[assignment]
    _set_analytics_headers(response)
    return MethodologyIndexResponse(
        methods=[
            MethodologyEntry(
                name="linear_regression",
                description="OLS linear regression (closed-form)",
                doi=None,
                citation="Kutner et al., Applied Linear Statistical Models, 5th ed., Ch. 1",
                invariants=["|r_squared| ≤ 1", "n ≥ 2, zero-variance guard"],
            ),
            MethodologyEntry(
                name="pearson",
                description="Pearson product-moment correlation with Fisher-z 95% CI",
                doi=None,
                citation="Fisher 1915, 1921",
                invariants=["|r| ≤ 1", "0 ≤ p ≤ 1", "CI contains r"],
            ),
            MethodologyEntry(
                name="spearman",
                description="Spearman rank correlation (Pearson on rank-transformed data, average-rank ties)",
                doi=None,
                citation="Spearman 1904",
                invariants=["|r| ≤ 1"],
            ),
            MethodologyEntry(
                name="benjamini_hochberg",
                description="Benjamini-Hochberg False Discovery Rate correction",
                doi="10.1098/rstb.1995.0152",
                citation="Benjamini & Hochberg 1995",
                invariants=["0 ≤ adjusted ≤ 1", "monotonicity enforced"],
            ),
            MethodologyEntry(
                name="mann_kendall",
                description="Nonparametric Mann-Kendall monotonic trend test with tie correction",
                doi=None,
                citation="Mann 1945, Kendall 1975",
                invariants=["n ≥ 3"],
            ),
            MethodologyEntry(
                name="prediction_interval",
                description="t-distribution prediction interval (incomplete-beta driven)",
                doi=None,
                citation="Kutner et al. §2.4",
                invariants=["lower ≤ estimate ≤ upper", "n ≥ 3"],
            ),
            MethodologyEntry(
                name="cohens_d_paired",
                description="Cohen's d for paired samples with Hedges' g small-sample correction",
                doi=None,
                citation="Cohen 1988; Hedges 1981",
                invariants=["n ≥ 2"],
            ),
            MethodologyEntry(
                name="resting_hr_windowed",
                description="Minimum 5-min moving average within 30 min post-wake (AASM-proximate)",
                doi="10.1136/bjsm.2004.015456",
                citation="Brage et al. 2005",
                invariants=["≥ 2 readings in window"],
            ),
            MethodologyEntry(
                name="sleep_efficiency",
                description="TST / TIB per AASM Scoring Manual v2.6",
                doi=None,
                citation="AASM v2.6, 2023",
                invariants=["0 ≤ efficiency ≤ 1", "warning on TIB=0"],
            ),
            MethodologyEntry(
                name="sleep_debt_cumulative",
                description="Running sleep debt vs. NSF age-adjusted baseline (Hirshkowitz 2015)",
                doi="10.1016/j.sleep.2014.07.014",
                citation="Hirshkowitz et al. 2015",
                invariants=["baseline per NSF age recommendation"],
            ),
            MethodologyEntry(
                name="recovery_composite",
                description="Weighted z-score composite (sleep / HRV / resting HR / steps) — documented heuristic",
                doi="10.1152/japplphysiol.00770.2013",
                citation="Plews et al. 2013 (synthesis); weights = heuristic, not authoritative",
                invariants=["0 ≤ score ≤ 100", "personalised 28-day baselines"],
            ),
        ]
    )


@router.get(
    "/analytics/workout/progression",
    response_model=WorkoutProgressionResponse,
)
def api_analytics_workout_progression(
    exercise_id: str = Query(...),
    range_days: int = Query(default=180),
    current_user=Depends(get_current_user_or_api),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
    response: Response = None,  # type: ignore[assignment]
) -> WorkoutProgressionResponse:
    _set_analytics_headers(response)
    result = analytics_svc.workout_progression(
        uid(current_user), exercise_id, range_days,
    )
    if result is None:
        raise ApiError(
            code="no_data",
            message="No workout data found for this exercise",
            status_code=404,
        )
    return result


@router.post("/analytics/compute", response_model=AnalyticsComputeResponse)
def api_analytics_compute(
    body: AnalyticsComputeRequest,
    current_user=Depends(get_current_user_or_api),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
    response: Response = None,  # type: ignore[assignment]
) -> AnalyticsComputeResponse:
    _set_analytics_headers(response)
    method = body.method
    metric = body.metric
    range_key = body.range
    user_id = uid(current_user)
    if method == "timeseries":
        result = analytics_svc.timeseries(user_id, metric, range_key)
    elif method == "forecast":
        result = analytics_svc.forecast(user_id, metric)
    elif method == "correlations":
        result = analytics_svc.correlations(user_id, range_key)
    elif method == "heatmap":
        year_val = 2026
        if body.params and "year" in body.params:
            year_val = int(str(body.params["year"]))
        result = analytics_svc.heatmap(user_id, metric, year_val)
    else:
        raise ApiError(
            code="unknown_method",
            message=f"Unknown compute method: {method}",
            status_code=400,
        )
    return AnalyticsComputeResponse(result=result.model_dump())
