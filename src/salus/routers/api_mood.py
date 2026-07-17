from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from salus.dependencies import get_current_user, get_mood_service
from salus.models.user import User
from salus.schemas.mood import MoodEntryCreate, MoodEntryResponse, MoodStatsResponse, MoodTagResponse
from salus.services._helpers import uid
from salus.services.mood import MoodService

router = APIRouter(prefix="/api/v1/mood")


def _tag_to_response(t) -> dict:
    return {
        "code": t.code,
        "label": t.label,
        "emoji": t.emoji,
        "category": t.category.value if hasattr(t.category, "value") else str(t.category),
    }


def _entry_to_response(e) -> dict:
    import json
    tags = None
    if e.tag_codes:
        try:
            tags = json.loads(e.tag_codes)
        except (json.JSONDecodeError, TypeError):
            tags = None
    return {
        "id": e.id,
        "entry_date": e.entry_date.isoformat() if e.entry_date else "",
        "mood_score": e.mood_score,
        "energy_level": e.energy_level,
        "stress_level": e.stress_level,
        "tag_codes": tags,
        "notes": e.notes,
        "created_at": e.created_at.isoformat() if e.created_at else "",
    }


@router.get("/tags", response_model=list[MoodTagResponse])
async def list_tags(
    current_user: User = Depends(get_current_user),
    mood_svc: MoodService = Depends(get_mood_service),
):
    return [_tag_to_response(t) for t in mood_svc.get_tags()]


@router.get("", response_model=list[MoodEntryResponse])
async def list_entries(
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
    current_user: User = Depends(get_current_user),
    mood_svc: MoodService = Depends(get_mood_service),
):
    since = date.fromisoformat(from_date) if from_date else None
    until = date.fromisoformat(to_date) if to_date else None
    entries = mood_svc.find_by_user_range(uid(current_user), since, until)
    return [_entry_to_response(e) for e in entries]


@router.post("", response_model=MoodEntryResponse, status_code=201)
async def log_mood(
    data: MoodEntryCreate,
    current_user: User = Depends(get_current_user),
    mood_svc: MoodService = Depends(get_mood_service),
):
    entry = mood_svc.log(data, uid(current_user))
    return _entry_to_response(entry)


@router.get("/stats", response_model=MoodStatsResponse)
async def get_stats(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    mood_svc: MoodService = Depends(get_mood_service),
):
    stats = mood_svc.get_stats(uid(current_user), days)
    return MoodStatsResponse(**stats)


@router.get("/{entry_date}", response_model=MoodEntryResponse)
async def get_by_date(
    entry_date: str,
    current_user: User = Depends(get_current_user),
    mood_svc: MoodService = Depends(get_mood_service),
):
    d = date.fromisoformat(entry_date)
    entry = mood_svc.get_by_date(uid(current_user), d)
    if entry is None:
        raise HTTPException(status_code=404, detail="No mood entry for this date")
    return _entry_to_response(entry)
