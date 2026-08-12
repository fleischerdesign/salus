"""Analytics strategies — each domain owns one strategy class.

The facade :class:`AnalyticsService` in ``orchestrator.py`` builds an
:class:`AnalyticsContext` and delegates to these strategies.
"""
from salus.services.analytics.strategies.context import AnalyticsContext
from salus.services.analytics.strategies.correlations import CorrelationsStrategy
from salus.services.analytics.strategies.forecast import ForecastStrategy
from salus.services.analytics.strategies.heatmap import HeatmapStrategy
from salus.services.analytics.strategies.overview import OverviewStrategy
from salus.services.analytics.strategies.progression import WorkoutProgressionStrategy
from salus.services.analytics.strategies.timeseries import TimeseriesStrategy
from salus.services.analytics.strategies.wellness import WellnessScoreStrategy

__all__ = [
    "AnalyticsContext",
    "CorrelationsStrategy",
    "ForecastStrategy",
    "HeatmapStrategy",
    "OverviewStrategy",
    "TimeseriesStrategy",
    "WellnessScoreStrategy",
    "WorkoutProgressionStrategy",
]
