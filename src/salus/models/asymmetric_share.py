from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from salus.models.user import User


class ShareRecipient(SQLModel, table=True):
    __tablename__ = "share_recipient"  # pyright: ignore[reportAssignmentType]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    public_key: str  # PEM format RSA public key
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    user: "User" = Relationship(back_populates="share_recipients")
    asymmetric_shares: list["AsymmetricShare"] = Relationship(
        back_populates="recipient",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class AsymmetricShare(SQLModel, table=True):
    __tablename__ = "asymmetric_share"  # pyright: ignore[reportAssignmentType]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    recipient_id: int = Field(foreign_key="share_recipient.id")
    encrypted_data: str  # Base64 encoded payload
    encrypted_key: str   # Base64 encoded AES key encrypted with recipient's public key
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="asymmetric_shares")
    recipient: "ShareRecipient" = Relationship(back_populates="asymmetric_shares")
