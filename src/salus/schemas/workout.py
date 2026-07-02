from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ExerciseBase(BaseModel):
    name: str
    equipment: str = "barbell"
    primary_muscles: str
    secondary_muscles: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseResponse(ExerciseBase):
    id: int
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanExerciseCreate(BaseModel):
    exercise_id: int
    sequence: int = 0
    target_sets: int = 3
    target_reps: int = 8
    target_rpe: Optional[float] = 8.0
    is_autoreg_exempt: bool = False


class WorkoutPlanExerciseResponse(BaseModel):
    id: int
    plan_id: int
    exercise_id: int
    sequence: int
    target_sets: int
    target_reps: int
    target_rpe: Optional[float]
    is_autoreg_exempt: bool
    exercise: ExerciseResponse

    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanCreate(BaseModel):
    name: str
    description: Optional[str] = None
    autoreg_mode: str = "advisory"  # "guided", "advisory", "disabled"
    exercises: list[WorkoutPlanExerciseCreate] = Field(default_factory=list)


class WorkoutPlanResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    autoreg_mode: str
    created_at: datetime
    plan_exercises: list[WorkoutPlanExerciseResponse]

    model_config = ConfigDict(from_attributes=True)


class WorkoutLogEntryCreate(BaseModel):
    exercise_id: int
    set_number: int
    weight: float
    reps: int
    rpe: Optional[float] = None


class WorkoutLogEntryResponse(BaseModel):
    id: int
    session_id: int
    exercise_id: int
    set_number: int
    weight: float
    reps: int
    rpe: Optional[float]
    exercise: ExerciseResponse

    model_config = ConfigDict(from_attributes=True)


class WorkoutSessionCreate(BaseModel):
    plan_id: Optional[int] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    autoreg_mode: str = "advisory"
    recovery_score: Optional[float] = None
    notes: Optional[str] = None
    logs: list[WorkoutLogEntryCreate] = Field(default_factory=list)


class WorkoutSessionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: Optional[int]
    started_at: datetime
    completed_at: Optional[datetime]
    autoreg_mode: str
    recovery_score: Optional[float]
    notes: Optional[str] = None
    logs: list[WorkoutLogEntryResponse]

    model_config = ConfigDict(from_attributes=True)
