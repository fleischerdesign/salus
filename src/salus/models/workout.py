from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

from salus.utils import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class Exercise(SQLModel, table=True):
    """Catalog of exercises, editable by users."""

    __tablename__ = "exercise"  # pyright: ignore[reportAssignmentType]

    id: Optional[str] = Field(default_factory=uuid7_str, primary_key=True)
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
    user_id: Optional[str] = Field(default=None, foreign_key="user.id")
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)


class Workout(SQLModel, table=True):
    """A reusable training day (an ordered list of exercises with targets)."""

    __tablename__ = "workout"  # pyright: ignore[reportAssignmentType]

    id: Optional[str] = Field(default_factory=uuid7_str, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    user_id: str = Field(foreign_key="user.id")

    position: int = Field(default=0)  # Reorder position in workouts grid

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    )
    deleted_at: datetime | None = Field(default=None)

    # Relations
    exercises: list["WorkoutExercise"] = Relationship(
        back_populates="workout", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    user: "User" = Relationship(back_populates="workouts")


class WorkoutExercise(SQLModel, table=True):
    """Bridge mapping exercises to workouts with custom targets."""

    __tablename__ = "workout_exercise"  # pyright: ignore[reportAssignmentType]

    id: Optional[str] = Field(default_factory=uuid7_str, primary_key=True)
    workout_id: str = Field(foreign_key="workout.id")
    exercise_id: str = Field(foreign_key="exercise.id")
    sequence: int = Field(default=0)  # Execution order
    target_sets: int = Field(default=3)
    target_reps: int = Field(default=8)
    target_rpe: Optional[float] = Field(
        default=8.0
    )  # Rate of Perceived Exertion (1-10)

    # Per-exercise exemption toggle
    is_autoreg_exempt: bool = Field(default=False)
    rest_seconds: Optional[int] = Field(default=None)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    # Relations
    workout: "Workout" = Relationship(back_populates="exercises")
    exercise: "Exercise" = Relationship()


class WorkoutSession(SQLModel, table=True):
    """An active or completed logging instance."""

    __tablename__ = "workout_session"  # pyright: ignore[reportAssignmentType]

    id: Optional[str] = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    workout_id: Optional[str] = Field(default=None, foreign_key="workout.id")
    program_id: Optional[str] = Field(default=None, foreign_key="program.id")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = Field(default=None)

    # Snapshot of progression/recovery state
    progression_scheme: str = Field(default="autoregulated")
    recovery_score: Optional[float] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    # Relations
    sets: list["WorkoutSet"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "primaryjoin": "and_(WorkoutSet.session_id == WorkoutSession.id, WorkoutSet.deleted_at.is_(None))",
        },
    )
    user: "User" = Relationship(back_populates="workout_sessions")
    workout: Optional[Workout] = Relationship()
    program: Optional["Program"] = Relationship()


class WorkoutSet(SQLModel, table=True):
    """Raw sets completed."""

    __tablename__ = "workout_set"  # pyright: ignore[reportAssignmentType]

    id: Optional[str] = Field(default_factory=uuid7_str, primary_key=True)
    session_id: str = Field(foreign_key="workout_session.id")
    exercise_id: str = Field(foreign_key="exercise.id")
    set_number: int
    weight: float
    reps: int
    rpe: Optional[float] = Field(default=None)  # Actual RPE logged
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    # Relations
    session: "WorkoutSession" = Relationship(back_populates="sets")
    exercise: "Exercise" = Relationship()


class Program(SQLModel, table=True):
    """A multi-day training program: ordered workout slots + progression scheme."""

    __tablename__ = "program"  # pyright: ignore[reportAssignmentType]

    id: Optional[str] = Field(default_factory=uuid7_str, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    user_id: str = Field(foreign_key="user.id")

    # Progression scheme applied to this program's sessions
    # ("linear" | "autoregulated" | "none")
    progression_scheme: str = Field(default="autoregulated")
    position: int = Field(default=0)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    # Relations
    slots: list["ProgramWorkout"] = Relationship(
        back_populates="program", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    user: "User" = Relationship(back_populates="programs")


class ProgramWorkout(SQLModel, table=True):
    """Bridge mapping workouts to programs with a schedule slot."""

    __tablename__ = "program_workout"  # pyright: ignore[reportAssignmentType]

    id: Optional[str] = Field(default_factory=uuid7_str, primary_key=True)
    program_id: str = Field(foreign_key="program.id")
    workout_id: str = Field(foreign_key="workout.id")
    sequence: int = Field(default=0)
    day_of_week: Optional[int] = Field(default=None)  # 0=Monday .. 6=Sunday (ISO)
    scheduled_date: Optional[date] = Field(default=None)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    # Relations
    program: "Program" = Relationship(back_populates="slots")
    workout: "Workout" = Relationship()
