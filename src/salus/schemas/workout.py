from datetime import date, datetime
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


class ExerciseResponse(ExerciseBase):
    id: str
    user_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class WorkoutExerciseCreate(BaseModel):
    exercise_id: str
    sequence: int = 0
    target_sets: int = 3
    target_reps: int = 8
    target_rpe: Optional[float] = 8.0
    is_autoreg_exempt: bool = False
    rest_seconds: Optional[int] = None


class WorkoutExerciseResponse(BaseModel):
    id: str
    workout_id: str
    exercise_id: str
    sequence: int
    target_sets: int
    target_reps: int
    target_rpe: Optional[float]
    is_autoreg_exempt: bool
    rest_seconds: Optional[int] = None
    exercise: ExerciseResponse

    model_config = ConfigDict(from_attributes=True)


class WorkoutCreate(BaseModel):
    name: str
    description: Optional[str] = None
    position: int = 0
    exercises: list[WorkoutExerciseCreate] = Field(default_factory=list)


class WorkoutResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    position: int
    created_at: datetime
    exercises: list[WorkoutExerciseResponse]

    model_config = ConfigDict(from_attributes=True)


class WorkoutSetCreate(BaseModel):
    exercise_id: str
    set_number: int
    weight: float
    reps: int
    rpe: Optional[float] = None


class WorkoutSetResponse(BaseModel):
    id: str
    session_id: str
    exercise_id: str
    set_number: int
    weight: float
    reps: int
    rpe: Optional[float]
    exercise: ExerciseResponse

    model_config = ConfigDict(from_attributes=True)


class WorkoutSessionResponse(BaseModel):
    id: str
    user_id: str
    workout_id: Optional[str]
    program_id: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime]
    progression_scheme: str
    recovery_score: Optional[float]
    notes: Optional[str] = None
    sets: list[WorkoutSetResponse]

    model_config = ConfigDict(from_attributes=True)


class ExerciseHistoryEntry(BaseModel):
    date: Optional[str] = None
    set_number: int
    weight: float
    reps: int
    rpe: Optional[float] = None
    est_one_rm: float


class ProgramWorkoutCreate(BaseModel):
    workout_id: str
    sequence: int = 0
    day_of_week: Optional[int] = None
    scheduled_date: Optional[date] = None


class ProgramCreate(BaseModel):
    name: str
    description: Optional[str] = None
    progression_scheme: str = "autoregulated"
    position: int = 0
    slots: list[ProgramWorkoutCreate] = Field(default_factory=list)


class ProgramWorkoutResponse(BaseModel):
    id: str
    program_id: str
    workout_id: str
    sequence: int
    day_of_week: Optional[int]
    scheduled_date: Optional[date]
    workout: WorkoutResponse

    model_config = ConfigDict(from_attributes=True)


class ProgramResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    progression_scheme: str
    position: int
    created_at: datetime
    slots: list[ProgramWorkoutResponse]

    model_config = ConfigDict(from_attributes=True)


class ExerciseDetailResponse(BaseModel):
    exercise: ExerciseResponse
    history: list[ExerciseHistoryEntry]
    pr_max_weight: float
    pr_est_one_rm: float
    total_sets: int
    total_reps: int
