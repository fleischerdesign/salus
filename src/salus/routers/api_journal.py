from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from salus.dependencies import get_current_user, get_journal_service
from salus.models.user import User
from salus.schemas.journal import JournalEntryCreate, JournalEntryResponse, JournalEntryUpdate, JournalSearchResponse
from salus.services._helpers import uid
from salus.services.journal import JournalService

router = APIRouter(prefix="/api/v1/journal")


def _entry_to_response(e) -> dict:
    return {
        "id": e.id,
        "entry_date": e.entry_date.isoformat() if e.entry_date else "",
        "title": e.title,
        "content": e.content,
        "mood_score": e.mood_score,
        "is_private": e.is_private,
        "created_at": e.created_at.isoformat() if e.created_at else "",
        "updated_at": e.updated_at.isoformat() if e.updated_at else None,
    }


@router.get("", response_model=list[JournalEntryResponse])
async def list_entries(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    journal_svc: JournalService = Depends(get_journal_service),
):
    entries, _ = journal_svc.list_entries(uid(current_user), page, limit)
    return [_entry_to_response(e) for e in entries]


@router.post("", response_model=JournalEntryResponse, status_code=201)
async def create_entry(
    data: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    journal_svc: JournalService = Depends(get_journal_service),
):
    e = journal_svc.create(data, uid(current_user))
    return _entry_to_response(e)


@router.get("/date/{entry_date}", response_model=JournalEntryResponse)
async def get_by_date(
    entry_date: str,
    current_user: User = Depends(get_current_user),
    journal_svc: JournalService = Depends(get_journal_service),
):
    d = date.fromisoformat(entry_date)
    e = journal_svc.get_by_date(uid(current_user), d)
    if e is None:
        raise HTTPException(status_code=404, detail="No journal entry for this date")
    return _entry_to_response(e)


@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    journal_svc: JournalService = Depends(get_journal_service),
):
    e = journal_svc.get(entry_id, uid(current_user))
    return _entry_to_response(e)


@router.put("/{entry_id}", response_model=JournalEntryResponse)
async def update_entry(
    entry_id: str,
    data: JournalEntryUpdate,
    current_user: User = Depends(get_current_user),
    journal_svc: JournalService = Depends(get_journal_service),
):
    e = journal_svc.update(entry_id, uid(current_user), data)
    return _entry_to_response(e)


@router.delete("/{entry_id}", status_code=204)
async def delete_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    journal_svc: JournalService = Depends(get_journal_service),
):
    journal_svc.delete(entry_id, uid(current_user))
    return Response(status_code=204)


@router.get("/search/results", response_model=JournalSearchResponse)
async def search_entries(
    q: str = Query(..., min_length=2),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    journal_svc: JournalService = Depends(get_journal_service),
):
    items = journal_svc.search(uid(current_user), q, page, limit)
    return JournalSearchResponse(
        items=[_entry_to_response(e) for e in items],
        total=len(items),
    )
