from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class Exercise(SQLModel, table=True):
    """Catalog of exercises, editable by users."""

    __tablename__ = "exercise"  # pyright: ignore[reportAssignmentType]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    equipment: str = Field(
        default="barbell"
    )  # "barbell", "dumbbell", "machine", "bodyweight"

    # Atomic Anatomical Mapping (comma-separated lists of muscles)
    primary_muscles: str  # e.g., "quadriceps,gluteus_maximus"
    secondary_muscles: Optional[str] = Field(default=None)  # e.g., "hamstrings"

    # Rich Media & Instructions
    description: Optional[str] = Field(default=None)
    instructions: Optional[str] = Field(default=None)  # Markdown instructions
    video_url: Optional[str] = Field(default=None)  # e.g., YouTube/Vimeo tutorial link
    image_url: Optional[str] = Field(default=None)  # Local path or illustration URL
    suggested_rest_seconds: Optional[int] = Field(default=None)

    # Ownership (null if system-default)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")


class WorkoutPlan(SQLModel, table=True):
    """User-created training programs."""

    __tablename__ = "workout_plan"  # pyright: ignore[reportAssignmentType]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    user_id: int = Field(foreign_key="user.id")

    # Granular Autoregulation Policies
    autoreg_mode: str = Field(default="advisory")  # "guided", "advisory", "disabled"
    position: int = Field(default=0)  # Reorder position in plans grid

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    )

    # Relations
    plan_exercises: list["WorkoutPlanExercise"] = Relationship(
        back_populates="plan", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    user: "User" = Relationship(back_populates="workout_plans")


class WorkoutPlanExercise(SQLModel, table=True):
    """Bridge mapping exercises to plans with custom targets."""

    __tablename__ = "workout_plan_exercise"  # pyright: ignore[reportAssignmentType]

    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="workout_plan.id")
    exercise_id: int = Field(foreign_key="exercise.id")
    sequence: int = Field(default=0)  # Execution order
    target_sets: int = Field(default=3)
    target_reps: int = Field(default=8)
    target_rpe: Optional[float] = Field(
        default=8.0
    )  # Rate of Perceived Exertion (1-10)

    # Per-exercise exemption toggle
    is_autoreg_exempt: bool = Field(default=False)
    rest_seconds: Optional[int] = Field(default=None)

    # Relations
    plan: "WorkoutPlan" = Relationship(back_populates="plan_exercises")
    exercise: "Exercise" = Relationship()


class WorkoutSession(SQLModel, table=True):
    """An active or completed logging instance."""

    __tablename__ = "workout_session"  # pyright: ignore[reportAssignmentType]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    plan_id: Optional[int] = Field(default=None, foreign_key="workout_plan.id")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = Field(default=None)

    # Snapshot of recovery state
    autoreg_mode: str = Field(default="advisory")
    recovery_score: Optional[float] = Field(default=None)
    notes: Optional[str] = Field(default=None)

    # Relations
    logs: list["WorkoutLogEntry"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    user: "User" = Relationship(back_populates="workout_sessions")
    plan: Optional[WorkoutPlan] = Relationship()


class WorkoutLogEntry(SQLModel, table=True):
    """Raw sets completed."""

    __tablename__ = "workout_log_entry"  # pyright: ignore[reportAssignmentType]

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="workout_session.id")
    exercise_id: int = Field(foreign_key="exercise.id")
    set_number: int
    weight: float
    reps: int
    rpe: Optional[float] = Field(default=None)  # Actual RPE logged

    # Relations
    session: "WorkoutSession" = Relationship(back_populates="logs")
    exercise: "Exercise" = Relationship()
