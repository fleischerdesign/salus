import json
from datetime import datetime, timedelta

import pytest
from sqlmodel import Session, SQLModel, create_engine

from salus.models.measurement import Measurement
from salus.repositories.measurement import MeasurementRepository
from salus.services.analytics.activity import ActivityAnalysisService
from salus.services.analytics.dashboard import DashboardService
from salus.services.analytics.nutrition import NutritionAnalysisService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.weight import WeightAnalysisService


@pytest.fixture
def repo():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield MeasurementRepository(session)


def _dt(date_str: str) -> datetime:
    return datetime.fromisoformat(date_str)


def _insert(repo: MeasurementRepository, **kwargs):
    for k in ("start_time", "end_time", "created_at"):
        if k in kwargs and isinstance(kwargs[k], str):
            kwargs[k] = _dt(kwargs[k])
    m = Measurement(**kwargs)
    return repo.create(m)


class TestSleepAnalysisService:
    def test_last_night_returns_none_when_empty(self, repo):
        svc = SleepAnalysisService(repo)
        assert svc.last_night() is None

    def test_last_night_parses_sleep_stages(self, repo):
        svc = SleepAnalysisService(repo)
        today = datetime.today().strftime("%Y-%m-%d")
        _insert(repo,
            data_type="sleep", source="test", start_time=f"{today}T23:00:00",
            value_json=json.dumps({
                "duration_seconds": 27000,
                "stages": [
                    {"stage": "1", "duration_seconds": 1800},
                    {"stage": "4", "duration_seconds": 10800},
                    {"stage": "5", "duration_seconds": 9000},
                    {"stage": "6", "duration_seconds": 5400},
                ],
            }),
        )
        summary = svc.last_night()
        assert summary is not None
        assert summary.duration_hours == 7.5
        assert summary.awake_seconds == 1800
        assert summary.light_seconds == 10800
        assert summary.deep_seconds == 9000
        assert summary.rem_seconds == 5400

    def test_trend_returns_empty_when_no_data(self, repo):
        svc = SleepAnalysisService(repo)
        assert svc.trend(days=7) == []


class TestWeightAnalysisService:
    def test_current_returns_none_when_empty(self, repo):
        svc = WeightAnalysisService(repo)
        assert svc.current() is None

    def test_current_returns_latest_weight(self, repo):
        svc = WeightAnalysisService(repo)
        today = datetime.today().strftime("%Y-%m-%d")
        _insert(repo,
            data_type="weight", source="test", start_time=f"{today}T08:00:00",
            value_json=json.dumps({"kilograms": 80.5}),
        )
        result = svc.current()
        assert result is not None
        assert result.weight_kg == 80.5

    def test_trend_returns_empty_when_no_data(self, repo):
        svc = WeightAnalysisService(repo)
        trend = svc.trend(days=30)
        assert trend.points == []


class TestActivityAnalysisService:
    def test_heart_rate_summary_empty(self, repo):
        svc = ActivityAnalysisService(repo)
        assert svc.heart_rate_summary("2026-06-24") is None

    def test_heart_rate_summary_computes_stats(self, repo):
        svc = ActivityAnalysisService(repo)
        today = datetime.today().strftime("%Y-%m-%d")
        _insert(repo, data_type="heart_rate", source="test", start_time=f"{today}T08:00:00", value_numeric=72)
        _insert(repo, data_type="heart_rate", source="test", start_time=f"{today}T08:01:00", value_numeric=68)
        summary = svc.heart_rate_summary(today)
        assert summary is not None
        assert summary.measurement_count == 2
        assert summary.avg_bpm == 70.0
        assert summary.min_bpm == 68
        assert summary.max_bpm == 72

    def test_exercise_history_empty(self, repo):
        svc = ActivityAnalysisService(repo)
        assert svc.exercise_history(days=30) == []

    def test_exercise_history_parses(self, repo):
        svc = ActivityAnalysisService(repo)
        today = datetime.today().strftime("%Y-%m-%d")
        _insert(repo,
            data_type="exercise", source="test", start_time=f"{today}T08:00:00",
            value_json=json.dumps({
                "exercise_type": 56, "duration_seconds": 2700,
                "distance_meters": 5000, "calories": 320,
            }),
        )
        sessions = svc.exercise_history(days=365, limit=10)
        assert len(sessions) >= 1
        assert sessions[0].type_name == "Running"
        assert sessions[0].duration_seconds == 2700


class TestNutritionAnalysisService:
    def test_today_returns_none_when_empty(self, repo):
        svc = NutritionAnalysisService(repo)
        assert svc.today() is None

    def test_daily_totals_aggregates(self, repo):
        svc = NutritionAnalysisService(repo)
        today = datetime.today().strftime("%Y-%m-%d")
        _insert(repo,
            data_type="nutrition", source="test", start_time=f"{today}T08:00:00",
            value_json=json.dumps({
                "calories": 500, "protein_grams": 30,
                "carbs_grams": 50, "fat_grams": 20, "name": "breakfast",
            }),
        )
        daily = svc.daily_totals(days=365)
        assert len(daily) >= 1
        assert daily[0].total_kcal == 500


class TestSleepAnalysisServiceTrend:
    def test_trend_with_data(self, repo):
        svc = SleepAnalysisService(repo)
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        _insert(repo,
            data_type="sleep", source="test",
            start_time=f"{yesterday.strftime('%Y-%m-%d')}T23:00:00",
            value_json=json.dumps({
                "duration_seconds": 28800,
                "stages": [{"stage": "5", "duration_seconds": 7200}],
            }),
        )
        result = svc.trend(days=30)
        assert len(result) >= 1


class TestWeightAnalysisServiceTrend:
    def test_trend_with_data(self, repo):
        svc = WeightAnalysisService(repo)
        today = datetime.today().strftime("%Y-%m-%d")
        _insert(repo, data_type="weight", source="test", start_time=f"{today}T08:00:00",
            value_json=json.dumps({"kilograms": 80.5}))
        trend = svc.trend(days=30)
        assert len(trend.points) >= 1
        assert trend.current == 80.5
        assert trend.delta == 0.0


class TestActivityStepsTrend:
    def test_steps_trend_empty(self, repo):
        svc = ActivityAnalysisService(repo)
        result = svc.steps_trend(days=7)
        assert len(result) == 7

    def test_steps_trend_with_data(self, repo):
        svc = ActivityAnalysisService(repo)
        today = datetime.today().strftime("%Y-%m-%d")
        _insert(repo, data_type="steps", source="test", start_time=f"{today}T08:00:00",
            end_time=f"{today}T22:00:00", value_numeric=8500)
        result = svc.steps_trend(days=7)
        today_point = [s for s in result if s.date == today]
        assert len(today_point) == 1
        assert today_point[0].count == 8500


class TestDashboardService:
    def test_summary_returns_dashboard(self, repo):
        svc = DashboardService(
            sleep_svc=SleepAnalysisService(repo),
            activity_svc=ActivityAnalysisService(repo),
            weight_svc=WeightAnalysisService(repo),
            nutrition_svc=NutritionAnalysisService(repo),
        )
        summary = svc.summary()
        assert summary.steps_goal == 10000
