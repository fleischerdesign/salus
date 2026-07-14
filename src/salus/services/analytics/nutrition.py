from datetime import datetime, timedelta
import json

from salus.models.analytics import NutritionDay
from salus.repositories.protocols import IMeasurementRepository


class NutritionAnalysisService:
    def __init__(self, repo: IMeasurementRepository) -> None:
        self._repo = repo

    def daily_totals(
        self, days: int = 7, user_id: str | None = None
    ) -> list[NutritionDay]:
        since = datetime.today() - timedelta(days=days)
        records = self._repo.find_all(
            data_types=["nutrition"], user_id=user_id, since=since
        )
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

    def today(
        self, user_id: str | None = None, date_str: str | None = None
    ) -> NutritionDay | None:
        target = datetime.today().strftime("%Y-%m-%d") if date_str is None else date_str
        since = datetime.strptime(target, "%Y-%m-%d")
        until = datetime.strptime(target + "T23:59:59", "%Y-%m-%dT%H:%M:%S")
        records = self._repo.find_all(
            data_types=["nutrition"], user_id=user_id, since=since, until=until
        )
        if not records:
            return None
        totals = {"kcal": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
        for rec in records:
            d = json.loads(rec.value_json) if rec.value_json else {}
            totals["kcal"] += d.get("calories", 0) or 0
            totals["protein"] += d.get("protein_grams", 0) or 0
            totals["carbs"] += d.get("carbs_grams", 0) or 0
            totals["fat"] += d.get("fat_grams", 0) or 0
        return NutritionDay(
            date=target,
            total_kcal=round(totals["kcal"], 0),
            protein_g=round(totals["protein"], 1),
            carbs_g=round(totals["carbs"], 1),
            fat_g=round(totals["fat"], 1),
        )
