from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class CircadianProfile(SQLModel, table=True):
    __tablename__ = "circadian_profile"  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True, unique=True)
    latitude: float = Field(default=52.52)  # Default Berlin
    longitude: float = Field(default=13.40)
    timezone_offset_hours: float = Field(default=1.0)
    configured_chronotype: str = Field(default="intermediate")  # lark, owl, intermediate

    user: "User" = Relationship(back_populates="circadian_profile")
