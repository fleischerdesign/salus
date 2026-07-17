from datetime import date

from pydantic import BaseModel, Field


class JournalEntryCreate(BaseModel):
    entry_date: date | None = None
    title: str | None = None
    content: str
    mood_score: int | None = Field(default=None, ge=1, le=10)
    is_private: bool = Field(default=True)


class JournalEntryUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    mood_score: int | None = Field(default=None, ge=1, le=10)
    is_private: bool | None = None


class JournalEntryResponse(BaseModel):
    id: str
    entry_date: str
    title: str | None = None
    content: str
    mood_score: int | None = None
    is_private: bool
    created_at: str
    updated_at: str | None = None


class JournalSearchResponse(BaseModel):
    items: list[JournalEntryResponse]
    total: int
