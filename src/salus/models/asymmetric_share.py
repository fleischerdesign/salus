from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from salus.services._helpers import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User


class ShareRecipient(SQLModel, table=True):
    __tablename__ = "share_recipient"  # pyright: ignore[reportAssignmentType]

    id: Optional[str] = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    name: str
    public_key: str  # PEM format RSA public key
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="share_recipients")
    asymmetric_shares: list["AsymmetricShare"] = Relationship(
        back_populates="recipient",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class AsymmetricShare(SQLModel, table=True):
    __tablename__ = "asymmetric_share"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    recipient_id: str = Field(foreign_key="share_recipient.id")
    encrypted_data: str  # Base64 encoded payload
    encrypted_key: str  # Base64 encoded AES key encrypted with recipient's public key
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = Field(default=None)
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="asymmetric_shares")
    recipient: "ShareRecipient" = Relationship(back_populates="asymmetric_shares")
