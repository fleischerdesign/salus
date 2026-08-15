from datetime import date

from pydantic import BaseModel, Field

from salus.models.goal import GoalDirection, GoalFrequency, NutritionField


class GoalCreate(BaseModel):
    metric_code: str
    target_value: float
    direction: GoalDirection = Field(default=GoalDirection.INCREASE)
    frequency: GoalFrequency = Field(default=GoalFrequency.DAILY)
    nutrition_field: NutritionField | None = None
    deadline: date | None = None
