"""Shared dependencies for analytics strategy classes."""
from dataclasses import dataclass

from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.analytics.activity import ActivityAnalysisService
from salus.services.analytics.nutrition import NutritionAnalysisService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.weight import WeightAnalysisService


@dataclass
class AnalyticsContext:
    uow: IUnitOfWork
    sleep: SleepAnalysisService
    activity: ActivityAnalysisService
    weight: WeightAnalysisService
    nutrition: NutritionAnalysisService
