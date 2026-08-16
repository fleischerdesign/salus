from datetime import datetime

from pydantic import BaseModel


class UserSourceStatusCreate(BaseModel):
    source: str
    connected: bool = False


class UserSourceStatusUpdate(BaseModel):
    connected: bool


class UserSourceStatusResponse(BaseModel):
    id: str
    user_id: str
    source: str
    connected: bool
    created_at: datetime
    updated_at: datetime | None = None
