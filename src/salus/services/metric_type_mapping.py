from salus.models import DataType
from salus.repositories.protocols import IMetricDefinitionRepository

METRIC_GROUPS: list[dict[str, str]] = [
    {"key": "blood_pressure", "name": "Blood Pressure", "icon": "monitor-heart", "input_mode": "combined"},
    {"key": "body_measurements", "name": "Body Measurements", "icon": "fitness-center", "input_mode": "individual"},
]

METRIC_DEFINITIONS: list[dict] = [
    {"code": "steps", "name": "Steps", "unit": "steps", "data_type": DataType.NUMBER, "source_data_type": "steps", "sort_order": 10},
    {"code": "heart_rate", "name": "Heart Rate", "unit": "bpm", "data_type": DataType.NUMBER, "source_data_type": "heart_rate", "sort_order": 20},
    {"code": "resting_heart_rate", "name": "Resting Heart Rate", "unit": "bpm", "data_type": DataType.NUMBER, "source_data_type": "resting_heart_rate", "sort_order": 25},
    {"code": "spo2", "name": "Blood Oxygen", "unit": "%", "data_type": DataType.NUMBER, "source_data_type": "spo2", "sort_order": 26},
    {"code": "respiratory_rate", "name": "Respiratory Rate", "unit": "rpm", "data_type": DataType.NUMBER, "source_data_type": "respiratory_rate", "sort_order": 27},
    {"code": "vo2_max", "name": "VO₂ Max", "unit": "ml/kg/min", "data_type": DataType.NUMBER, "source_data_type": "vo2_max", "sort_order": 28},
    {"code": "sleep", "name": "Sleep", "unit": "", "data_type": DataType.TEXT, "source_data_type": "sleep", "sort_order": 30},
    {"code": "weight", "name": "Weight", "unit": "kg", "data_type": DataType.NUMBER, "source_data_type": "weight", "sort_order": 40},
    {"code": "height", "name": "Height", "unit": "cm", "data_type": DataType.NUMBER, "source_data_type": "height", "sort_order": 41},
    {"code": "body_temperature", "name": "Body Temperature", "unit": "°C", "data_type": DataType.NUMBER, "source_data_type": "body_temperature", "sort_order": 45},
    {"code": "basal_body_temp", "name": "Basal Body Temperature", "unit": "°C", "data_type": DataType.NUMBER, "source_data_type": "basal_body_temp", "sort_order": 46},
    {"code": "systolic_bp", "name": "Systolic Blood Pressure", "unit": "mmHg", "data_type": DataType.NUMBER, "source_data_type": "blood_pressure", "sort_order": 51, "group_key": "blood_pressure"},
    {"code": "diastolic_bp", "name": "Diastolic Blood Pressure", "unit": "mmHg", "data_type": DataType.NUMBER, "source_data_type": "blood_pressure", "sort_order": 52, "group_key": "blood_pressure"},
    {"code": "exercise", "name": "Exercise", "unit": "minutes", "data_type": DataType.TEXT, "source_data_type": "exercise", "sort_order": 60},
    {"code": "calories_burned", "name": "Total Calories", "unit": "kcal", "data_type": DataType.NUMBER, "source_data_type": "calories_burned", "sort_order": 61},
    {"code": "active_calories", "name": "Active Calories", "unit": "kcal", "data_type": DataType.NUMBER, "source_data_type": "active_calories", "sort_order": 62},
    {"code": "distance", "name": "Distance", "unit": "km", "data_type": DataType.NUMBER, "source_data_type": "distance", "sort_order": 63},
    {"code": "elevation_gained", "name": "Elevation Gained", "unit": "m", "data_type": DataType.NUMBER, "source_data_type": "elevation_gained", "sort_order": 64},
    {"code": "floors_climbed", "name": "Floors Climbed", "unit": "floors", "data_type": DataType.NUMBER, "source_data_type": "floors_climbed", "sort_order": 65},
    {"code": "speed", "name": "Speed", "unit": "km/h", "data_type": DataType.NUMBER, "source_data_type": "speed", "sort_order": 66},
    {"code": "power", "name": "Power", "unit": "W", "data_type": DataType.NUMBER, "source_data_type": "power", "sort_order": 67},
    {"code": "cadence", "name": "Cadence", "unit": "rpm", "data_type": DataType.NUMBER, "source_data_type": "cadence", "sort_order": 68},
    {"code": "wheelchair_pushes", "name": "Wheelchair Pushes", "unit": "pushes", "data_type": DataType.NUMBER, "source_data_type": "wheelchair_pushes", "sort_order": 69},
    {"code": "nutrition", "name": "Nutrition", "unit": "", "data_type": DataType.TEXT, "source_data_type": "nutrition", "sort_order": 70},
    {"code": "blood_glucose", "name": "Blood Glucose", "unit": "mg/dL", "data_type": DataType.NUMBER, "source_data_type": "blood_glucose", "sort_order": 80},
    {"code": "body_fat", "name": "Body Fat", "unit": "%", "data_type": DataType.NUMBER, "source_data_type": "body_fat", "sort_order": 90},
    {"code": "bone_mass", "name": "Bone Mass", "unit": "kg", "data_type": DataType.NUMBER, "source_data_type": "bone_mass", "sort_order": 91},
    {"code": "lean_body_mass", "name": "Lean Body Mass", "unit": "kg", "data_type": DataType.NUMBER, "source_data_type": "lean_body_mass", "sort_order": 92},
    {"code": "body_water_mass", "name": "Body Water Mass", "unit": "kg", "data_type": DataType.NUMBER, "source_data_type": "body_water_mass", "sort_order": 93},
    {"code": "bmr", "name": "Basal Metabolic Rate", "unit": "kcal", "data_type": DataType.NUMBER, "source_data_type": "bmr", "sort_order": 94},
    {"code": "water", "name": "Water", "unit": "ml", "data_type": DataType.NUMBER, "source_data_type": "water", "sort_order": 100},
    {"code": "stress", "name": "Stress", "unit": "", "data_type": DataType.NUMBER, "source_data_type": "stress", "sort_order": 110},
    {"code": "hrv", "name": "HRV", "unit": "ms", "data_type": DataType.NUMBER, "source_data_type": "hrv", "sort_order": 120},
    {"code": "readiness", "name": "Readiness", "unit": "", "data_type": DataType.NUMBER, "source_data_type": "readiness", "sort_order": 130},
    {"code": "waist", "name": "Waist", "unit": "cm", "data_type": DataType.NUMBER, "source_data_type": "body_measurement", "sort_order": 140, "group_key": "body_measurements"},
    {"code": "hip", "name": "Hip", "unit": "cm", "data_type": DataType.NUMBER, "source_data_type": "body_measurement", "sort_order": 150, "group_key": "body_measurements"},
    {"code": "chest", "name": "Chest", "unit": "cm", "data_type": DataType.NUMBER, "source_data_type": "body_measurement", "sort_order": 160, "group_key": "body_measurements"},
    {"code": "menstruation_period", "name": "Menstruation Period", "unit": "", "data_type": DataType.TEXT, "source_data_type": "menstruation_period", "sort_order": 170},
    {"code": "menstruation_flow", "name": "Menstruation Flow", "unit": "", "data_type": DataType.TEXT, "source_data_type": "menstruation_flow", "sort_order": 171},
    {"code": "ovulation_test", "name": "Ovulation Test", "unit": "", "data_type": DataType.TEXT, "source_data_type": "ovulation_test", "sort_order": 172},
    {"code": "cervical_mucus", "name": "Cervical Mucus", "unit": "", "data_type": DataType.TEXT, "source_data_type": "cervical_mucus", "sort_order": 173},
    {"code": "spotting", "name": "Intermenstrual Bleeding", "unit": "", "data_type": DataType.TEXT, "source_data_type": "spotting", "sort_order": 174},
    {"code": "sexual_activity", "name": "Sexual Activity", "unit": "", "data_type": DataType.TEXT, "source_data_type": "sexual_activity", "sort_order": 175},
]

DEFAULT_METRIC_PREFERENCES: list[dict] = [
    {"code": "steps", "color": "#f59e0b", "icon": "directions-walk", "widget_size": "large", "widget_enabled": True, "position": 0},
    {"code": "heart_rate", "color": "#f43f5e", "icon": "monitor-heart", "widget_size": "medium", "widget_enabled": True, "position": 1},
    {"code": "resting_heart_rate", "color": "#e11d48", "icon": "monitor-heart", "widget_size": "small", "widget_enabled": True, "position": 2},
    {"code": "spo2", "color": "#0ea5e9", "icon": "vital-signs", "widget_size": "small", "widget_enabled": True, "position": 3},
    {"code": "sleep", "color": "#818cf8", "icon": "bedtime", "widget_size": "medium", "widget_enabled": True, "position": 4},
    {"code": "weight", "color": "#10b981", "icon": "monitor-weight", "widget_size": "small", "widget_enabled": True, "position": 5},
    {"code": "systolic_bp", "color": "#ef4444", "icon": "vital-signs", "widget_size": "small", "widget_enabled": False, "position": 6},
    {"code": "diastolic_bp", "color": "#dc2626", "icon": "vital-signs", "widget_size": "small", "widget_enabled": False, "position": 7},
    {"code": "exercise", "color": "#8b5cf6", "icon": "exercise", "widget_size": "medium", "widget_enabled": True, "position": 8},
    {"code": "calories_burned", "color": "#f97316", "icon": "local-fire-department", "widget_size": "medium", "widget_enabled": True, "position": 9},
    {"code": "active_calories", "color": "#fb923c", "icon": "local-fire-department", "widget_size": "small", "widget_enabled": False, "position": 10},
    {"code": "distance", "color": "#3b82f6", "icon": "straighten", "widget_size": "small", "widget_enabled": False, "position": 11},
    {"code": "nutrition", "color": "#10b981", "icon": "restaurant", "widget_size": "medium", "widget_enabled": True, "position": 12},
    {"code": "blood_glucose", "color": "#f97316", "icon": "bloodtype", "widget_size": "small", "widget_enabled": False, "position": 13},
    {"code": "body_fat", "color": "#ec4899", "icon": "body-fat", "widget_size": "small", "widget_enabled": False, "position": 14},
    {"code": "water", "color": "#06b6d4", "icon": "water-drop", "widget_size": "small", "widget_enabled": False, "position": 15},
    {"code": "stress", "color": "#f43f5e", "icon": "psychology", "widget_size": "small", "widget_enabled": False, "position": 16},
    {"code": "hrv", "color": "#06b6d4", "icon": "monitoring", "widget_size": "small", "widget_enabled": True, "position": 17},
    {"code": "readiness", "color": "#a78bfa", "icon": "checklist", "widget_size": "small", "widget_enabled": False, "position": 18},
    {"code": "waist", "color": "#f59e0b", "icon": "straighten", "widget_size": "small", "widget_enabled": False, "position": 19},
    {"code": "hip", "color": "#8b5cf6", "icon": "straighten", "widget_size": "small", "widget_enabled": False, "position": 20},
    {"code": "chest", "color": "#06b6d4", "icon": "straighten", "widget_size": "small", "widget_enabled": False, "position": 21},
]

DATA_TYPE_KEYWORD_TO_METRIC: dict[str, str] = {
    "steps": "steps",
    "step_count": "steps",
    "StepCount": "steps",
    "heart_rate": "heart_rate",
    "HeartRate": "heart_rate",
    "resting_heart_rate": "resting_heart_rate",
    "RestingHeartRate": "resting_heart_rate",
    "spo2": "spo2",
    "oxygen_saturation": "spo2",
    "OxygenSaturation": "spo2",
    "respiratory_rate": "respiratory_rate",
    "RespiratoryRate": "respiratory_rate",
    "vo2_max": "vo2_max",
    "Vo2Max": "vo2_max",
    "sleep": "sleep",
    "SleepAnalysis": "sleep",
    "weight": "weight",
    "height": "height",
    "BloodPressure": "systolic_bp",
    "exercise": "exercise",
    "calories_burned": "calories_burned",
    "total_calories": "calories_burned",
    "active_calories": "active_calories",
    "ActiveCalories": "active_calories",
    "distance": "distance",
    "Distance": "distance",
    "elevation_gained": "elevation_gained",
    "floors_climbed": "floors_climbed",
    "speed": "speed",
    "power": "power",
    "nutrition": "nutrition",
    "blood_glucose": "blood_glucose",
    "BloodGlucose": "blood_glucose",
    "body_fat": "body_fat",
    "BodyFatPercentage": "body_fat",
    "bone_mass": "bone_mass",
    "lean_body_mass": "lean_body_mass",
    "bmr": "bmr",
    "water": "water",
    "stress": "stress",
    "readiness": "readiness",
    "hrv": "hrv",
    "HRV": "hrv",
    "heart_rate_variability": "hrv",
    "body_temperature": "body_temperature",
    "BodyTemperature": "body_temperature",
    "basal_body_temp": "basal_body_temp",
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
