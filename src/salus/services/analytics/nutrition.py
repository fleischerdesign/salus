from datetime import datetime, timedelta
import json

from salus.models.analytics import NutritionDay
from salus.repositories.measurement import MeasurementRepository


class NutritionAnalysisService:
    def __init__(self, repo: MeasurementRepository) -> None:
        self._repo = repo

    def daily_totals(self, days: int = 7) -> list[NutritionDay]:
        since = datetime.today() - timedelta(days=days)
        records = self._repo.find_all(data_types=["nutrition"], since=since)
        daily: dict[str, dict[str, float]] = {}
        for rec in records:
            date = rec.start_time.strftime("%Y-%m-%d")
            if date not in daily:
                daily[date] = {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0}
            d = json.loads(rec.value_json) if rec.value_json else {}
            daily[date]["kcal"] += d.get("calories", 0) or 0
            daily[date]["protein"] += d.get("protein_grams", 0) or 0
            daily[date]["carbs"] += d.get("carbs_grams", 0) or 0
            daily[date]["fat"] += d.get("fat_grams", 0) or 0
        return sorted(
            [
                NutritionDay(
                    date=date,
                    total_kcal=round(v["kcal"], 0),
                    protein_g=round(v["protein"], 1),
                    carbs_g=round(v["carbs"], 1),
                    fat_g=round(v["fat"], 1),
                )
                for date, v in daily.items()
            ],
            key=lambda n: n.date,
        )

    def today(self) -> NutritionDay | None:
        today = datetime.today().strftime("%Y-%m-%d")
        daily = self.daily_totals(days=1)
        for day in daily:
            if day.date == today:
                return day
        return None
