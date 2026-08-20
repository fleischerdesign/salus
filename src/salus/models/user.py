from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from salus.utils import uuid7_str

if TYPE_CHECKING:
    from salus.models.goal import Goal  # noqa: F401
    from salus.models.insight import Insight  # noqa: F401
    from salus.models.measurement import Measurement  # noqa: F401
    from salus.models.user_identity import UserIdentity  # noqa: F401
    from salus.models.sharing import SharingRelationship  # noqa: F401
    from salus.models.workout import Program, Workout, WorkoutSession  # noqa: F401
    from salus.models.asymmetric_share import ShareRecipient, AsymmetricShare  # noqa: F401
    from salus.models.circadian import CircadianProfile  # noqa: F401
    from salus.models.notification import Notification  # noqa: F401
    from salus.models.metric_preference import UserMetricPreference  # noqa: F401


class User(SQLModel, table=True):
    __tablename__ = "user"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str | None = Field(default=None)
    email: str | None = Field(default=None, unique=True)
    display_name: str | None = Field(default=None)
    height_cm: float | None = Field(default=None)
    is_admin: bool = Field(default=False)
    is_active: bool = Field(default=True)
    theme: str = Field(default="system")
    locale: str = Field(default="en")
    timezone: str = Field(default="UTC")
    colorblind: bool = Field(default=False)
    accent_hue: int | None = Field(default=None)
    onboarding_dismissed: bool = Field(default=False)
    dq_notify_hard_bound: bool = Field(default=True)
    dq_notify_cross_source: bool = Field(default=True)
    dq_notify_anomaly: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    metric_preferences: list["UserMetricPreference"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    measurements: list["Measurement"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    identities: list["UserIdentity"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    goals: list["Goal"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    insights: list["Insight"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    sharing_relationships: list["SharingRelationship"] = Relationship(
        back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    workouts: list["Workout"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    programs: list["Program"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    workout_sessions: list["WorkoutSession"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    share_recipients: list["ShareRecipient"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    asymmetric_shares: list["AsymmetricShare"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    circadian_profile: Optional["CircadianProfile"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )
    notifications: list["Notification"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @property
    def active_workout_session(self) -> Optional["WorkoutSession"]:
        for s in self.workout_sessions:
            if s.completed_at is None:
                return s
        return None
