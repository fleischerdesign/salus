from pydantic import BaseModel
from typing import Optional


class OpenScienceSynthesizeRequest(BaseModel):
    metrics: list[str]  # e.g., ["steps", "sleep_duration", "resting_heart_rate"]
    weeks: int = 12  # number of past weeks to aggregate
    epsilon: float = 1.0  # privacy budget (0.1 to 5.0). Lower = more noise.
    include_demographics: bool = True
    user_birth_year: Optional[int] = None
    user_weight_kg: Optional[float] = None
