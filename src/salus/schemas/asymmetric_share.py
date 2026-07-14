from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class ShareRecipientCreate(BaseModel):
    name: str
    public_key: str


class ShareRecipientResponse(BaseModel):
    id: str
    user_id: str
    name: str
    public_key: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AsymmetricShareCreate(BaseModel):
    recipient_id: str
    encrypted_data: str  # Base64 encoded payload
    encrypted_key: str  # Base64 encoded key
    expires_in_hours: Optional[int] = None


class AsymmetricShareResponse(BaseModel):
    id: str
    user_id: str
    recipient_id: str
    encrypted_data: str
    encrypted_key: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
