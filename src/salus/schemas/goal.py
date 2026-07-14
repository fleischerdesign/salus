from datetime import date

from pydantic import BaseModel, Field

from salus.models.goal import GoalDirection, GoalFrequency


class GoalCreate(BaseModel):
    metric_type_id: str
    target_value: float
    direction: GoalDirection = Field(default=GoalDirection.INCREASE)
    frequency: GoalFrequency = Field(default=GoalFrequency.DAILY)
    deadline: date | None = None
