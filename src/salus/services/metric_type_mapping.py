from salus.models import DataType
from salus.repositories.protocols import IMetricDefinitionRepository

METRIC_GROUPS: list[dict[str, str]] = [
    {"key": "blood_pressure", "name": "Blood Pressure", "icon": "monitor-heart", "input_mode": "combined"},
    {"key": "body_measurements", "name": "Body Measurements", "icon": "fitness-center", "input_mode": "individual"},
]

METRIC_DEFINITIONS: list[dict] = [
    {"code": "steps", "name": "Steps", "unit": "steps", "data_type": DataType.NUMBER, "source_data_type": "steps", "sort_order": 10},
    {"code": "heart_rate", "name": "Heart Rate", "unit": "bpm", "data_type": DataType.NUMBER, "source_data_type": "heart_rate", "sort_order": 20},
    {"code": "sleep", "name": "Sleep", "unit": "", "data_type": DataType.TEXT, "source_data_type": "sleep", "sort_order": 30},
    {"code": "weight", "name": "Weight", "unit": "kg", "data_type": DataType.NUMBER, "source_data_type": "weight", "sort_order": 40},
    {"code": "systolic_bp", "name": "Systolic Blood Pressure", "unit": "mmHg", "data_type": DataType.NUMBER, "source_data_type": "blood_pressure", "sort_order": 51, "group_key": "blood_pressure"},
    {"code": "diastolic_bp", "name": "Diastolic Blood Pressure", "unit": "mmHg", "data_type": DataType.NUMBER, "source_data_type": "blood_pressure", "sort_order": 52, "group_key": "blood_pressure"},
    {"code": "exercise", "name": "Exercise", "unit": "minutes", "data_type": DataType.TEXT, "source_data_type": "exercise", "sort_order": 60},
    {"code": "nutrition", "name": "Nutrition", "unit": "", "data_type": DataType.TEXT, "source_data_type": "nutrition", "sort_order": 70},
    {"code": "blood_glucose", "name": "Blood Glucose", "unit": "mg/dL", "data_type": DataType.NUMBER, "source_data_type": "blood_glucose", "sort_order": 80},
    {"code": "body_fat", "name": "Body Fat", "unit": "%", "data_type": DataType.NUMBER, "source_data_type": "body_fat", "sort_order": 90},
    {"code": "water", "name": "Water", "unit": "ml", "data_type": DataType.NUMBER, "source_data_type": "water", "sort_order": 100},
    {"code": "stress", "name": "Stress", "unit": "", "data_type": DataType.NUMBER, "source_data_type": "stress", "sort_order": 110},
    {"code": "hrv", "name": "HRV", "unit": "ms", "data_type": DataType.NUMBER, "source_data_type": "hrv", "sort_order": 120},
    {"code": "readiness", "name": "Readiness", "unit": "", "data_type": DataType.NUMBER, "source_data_type": "readiness", "sort_order": 130},
    {"code": "waist", "name": "Waist", "unit": "cm", "data_type": DataType.NUMBER, "source_data_type": "body_measurement", "sort_order": 140, "group_key": "body_measurements"},
    {"code": "hip", "name": "Hip", "unit": "cm", "data_type": DataType.NUMBER, "source_data_type": "body_measurement", "sort_order": 150, "group_key": "body_measurements"},
    {"code": "chest", "name": "Chest", "unit": "cm", "data_type": DataType.NUMBER, "source_data_type": "body_measurement", "sort_order": 160, "group_key": "body_measurements"},
]

DEFAULT_METRIC_PREFERENCES: list[dict] = [
    {"code": "steps", "color": "#f59e0b", "icon": "directions-walk", "widget_size": "large", "widget_enabled": True, "position": 0},
    {"code": "heart_rate", "color": "#f43f5e", "icon": "monitor-heart", "widget_size": "medium", "widget_enabled": True, "position": 1},
    {"code": "sleep", "color": "#818cf8", "icon": "bedtime", "widget_size": "medium", "widget_enabled": True, "position": 2},
    {"code": "weight", "color": "#10b981", "icon": "monitor-weight", "widget_size": "small", "widget_enabled": True, "position": 3},
    {"code": "systolic_bp", "color": "#ef4444", "icon": "vital-signs", "widget_size": "small", "widget_enabled": False, "position": 5},
    {"code": "diastolic_bp", "color": "#dc2626", "icon": "vital-signs", "widget_size": "small", "widget_enabled": False, "position": 6},
    {"code": "exercise", "color": "#8b5cf6", "icon": "exercise", "widget_size": "medium", "widget_enabled": True, "position": 7},
    {"code": "nutrition", "color": "#10b981", "icon": "restaurant", "widget_size": "medium", "widget_enabled": True, "position": 8},
    {"code": "blood_glucose", "color": "#f97316", "icon": "bloodtype", "widget_size": "small", "widget_enabled": False, "position": 9},
    {"code": "body_fat", "color": "#ec4899", "icon": "body-fat", "widget_size": "small", "widget_enabled": False, "position": 10},
    {"code": "water", "color": "#06b6d4", "icon": "water-drop", "widget_size": "small", "widget_enabled": False, "position": 11},
    {"code": "stress", "color": "#f43f5e", "icon": "psychology", "widget_size": "small", "widget_enabled": False, "position": 12},
    {"code": "hrv", "color": "#06b6d4", "icon": "monitoring", "widget_size": "small", "widget_enabled": True, "position": 13},
    {"code": "readiness", "color": "#a78bfa", "icon": "checklist", "widget_size": "small", "widget_enabled": False, "position": 14},
    {"code": "waist", "color": "#f59e0b", "icon": "straighten", "widget_size": "small", "widget_enabled": False, "position": 15},
    {"code": "hip", "color": "#8b5cf6", "icon": "straighten", "widget_size": "small", "widget_enabled": False, "position": 16},
    {"code": "chest", "color": "#06b6d4", "icon": "straighten", "widget_size": "small", "widget_enabled": False, "position": 17},
]

DATA_TYPE_KEYWORD_TO_METRIC: dict[str, str] = {
    "steps": "steps",
    "step_count": "steps",
    "StepCount": "steps",
    "heart_rate": "heart_rate",
    "HeartRate": "heart_rate",
    "sleep": "sleep",
    "SleepAnalysis": "sleep",
    "weight": "weight",
    "BloodPressure": "systolic_bp",
    "exercise": "exercise",
    "nutrition": "nutrition",
    "blood_glucose": "blood_glucose",
    "BloodGlucose": "blood_glucose",
    "body_fat": "body_fat",
    "BodyFatPercentage": "body_fat",
    "water": "water",
    "stress": "stress",
    "readiness": "readiness",
    "hrv": "hrv",
    "HRV": "hrv",
    "heart_rate_variability": "hrv",
}


class MetricDefinitionMappingService:
    def __init__(self, metric_definition_repo: IMetricDefinitionRepository) -> None:
        self._repo = metric_definition_repo
        self._cache: dict[str, str | None] = {}

    def resolve(self, data_type: str, user_id: str | None = None) -> str | None:
        if data_type in self._cache:
            return self._cache[data_type]

        code = DATA_TYPE_KEYWORD_TO_METRIC.get(data_type)
        if code is None:
            lower = data_type.lower()
            for keyword, mc in DATA_TYPE_KEYWORD_TO_METRIC.items():
                if keyword.lower() in lower:
                    code = mc
                    break

        if code is not None:
            md = self._repo.find_by_code(code)
            if md is not None:
                self._cache[data_type] = code
                return code

        self._cache[data_type] = None
        return None
