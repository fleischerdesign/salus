from pydantic import BaseModel, ConfigDict


class CircadianProfileCreate(BaseModel):
    latitude: float
    longitude: float
    timezone_offset_hours: float = 1.0
    configured_chronotype: str = "intermediate"


class CircadianProfileResponse(BaseModel):
    id: str
    user_id: str
    latitude: float
    longitude: float
    timezone_offset_hours: float
    configured_chronotype: str

    model_config = ConfigDict(from_attributes=True)


class SolarTimes(BaseModel):
    sunrise: str  # HH:MM format
    sunset: str
    solar_noon: str
    dawn: str
    dusk: str


class CircadianAdviceResponse(BaseModel):
    solar_times: SolarTimes
    chronotype: str
    alignment_score: int  # 0 to 100
    sleep_window: dict  # target onset/offset, actual onset/offset, advice
    light_advice: list[dict]  # morning window, evening window, etc.
    eating_window: dict  # optimal window, advice
