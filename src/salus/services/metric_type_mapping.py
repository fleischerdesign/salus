from salus.models import DataType
from salus.repositories.metric_type import MetricTypeRepository

DEFAULT_METRIC_TYPES: list[tuple[str, str, DataType, str, str | None, str, str, bool]] = [
    ("Steps", "steps", DataType.NUMBER, "#f59e0b", "steps", "directions_walk", "large", True),
    ("Heart Rate", "bpm", DataType.NUMBER, "#f43f5e", "heart_rate", "monitor_heart", "medium", True),
    ("Sleep", "", DataType.TEXT, "#818cf8", "sleep", "bedtime", "medium", True),
    ("Weight", "kg", DataType.NUMBER, "#10b981", "weight", "monitor_weight", "small", True),
    ("Blood Pressure", "mmHg", DataType.TEXT, "#ef4444", "blood_pressure", "vital_signs", "medium", False),
    ("Exercise", "minutes", DataType.TEXT, "#8b5cf6", "exercise", "exercise", "medium", True),
    ("Nutrition", "", DataType.TEXT, "#10b981", "nutrition", "restaurant", "medium", True),
    ("Blood Glucose", "mg/dL", DataType.NUMBER, "#f97316", "blood_glucose", "bloodtype", "small", False),
    ("Body Fat", "%", DataType.NUMBER, "#ec4899", "body_fat", "body_fat", "small", False),
    ("Water", "ml", DataType.NUMBER, "#06b6d4", "water", "water_drop", "small", False),
    ("Stress", "", DataType.NUMBER, "#f43f5e", "stress", "psychology", "small", False),
    ("Readiness", "", DataType.NUMBER, "#a78bfa", "readiness", "checklist", "small", False),
]

DATA_TYPE_KEYWORD_TO_METRIC: dict[str, str] = {
    "steps": "Steps",
    "step_count": "Steps",
    "StepCount": "Steps",
    "heart_rate": "Heart Rate",
    "HeartRate": "Heart Rate",
    "sleep": "Sleep",
    "SleepAnalysis": "Sleep",
    "weight": "Weight",
    "blood_pressure": "Blood Pressure",
    "BloodPressure": "Blood Pressure",
    "exercise": "Exercise",
    "nutrition": "Nutrition",
    "blood_glucose": "Blood Glucose",
    "BloodGlucose": "Blood Glucose",
    "body_fat": "Body Fat",
    "BodyFatPercentage": "Body Fat",
    "water": "Water",
    "stress": "Stress",
    "readiness": "Readiness",
}


class MetricTypeMappingService:
    def __init__(self, metric_type_repo: MetricTypeRepository) -> None:
        self._repo = metric_type_repo
        self._cache: dict[tuple[str, int], int | None] = {}

    def resolve(self, data_type: str, user_id: int) -> int | None:
        cache_key = (data_type, user_id)
        if cache_key in self._cache:
            return self._cache[cache_key]

        resolved_id = self._resolve_uncached(data_type, user_id)
        self._cache[cache_key] = resolved_id
        return resolved_id

    def _resolve_uncached(self, data_type: str, user_id: int) -> int | None:
        name = DATA_TYPE_KEYWORD_TO_METRIC.get(data_type)
        if name is not None:
            mt = self._repo.find_by_name_and_user(name, user_id)
            if mt is not None:
                return mt.id

        lower = data_type.lower()
        for keyword, name in DATA_TYPE_KEYWORD_TO_METRIC.items():
            if keyword.lower() in lower:
                mt = self._repo.find_by_name_and_user(name, user_id)
                if mt is not None:
                    return mt.id

        return None
