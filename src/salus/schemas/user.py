from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    email: str | None = None
    display_name: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    email: str | None = None
    display_name: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str | None
    display_name: str | None
    height_cm: float | None
    is_admin: bool
    is_active: bool
    theme: str
    locale: str
    onboarding_dismissed: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    token: str
    user: UserResponse
