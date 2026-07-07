from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class ShareRecipientCreate(BaseModel):
    name: str
    public_key: str


class ShareRecipientResponse(BaseModel):
    id: int
    user_id: int
    name: str
    public_key: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AsymmetricShareCreate(BaseModel):
    recipient_id: int
    encrypted_data: str  # Base64 encoded payload
    encrypted_key: str  # Base64 encoded key
    expires_in_hours: Optional[int] = None


class AsymmetricShareResponse(BaseModel):
    id: int
    user_id: int
    recipient_id: int
    encrypted_data: str
    encrypted_key: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
