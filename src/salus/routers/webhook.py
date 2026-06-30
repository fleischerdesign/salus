from json import JSONDecodeError

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlmodel import Session

from salus.config import settings
from salus.database import get_session
from salus.models.measurement import Measurement
from salus.repositories.measurement import MeasurementRepository
from salus.services.parser import FlexiblePayloadParser

router = APIRouter()


@router.post("/webhook")
async def webhook_ingest(
    request: Request,
    authorization: str | None = Header(None),
    x_api_token: str | None = Header(None, alias="X-API-Token"),
    session: Session = Depends(get_session),
):
    token: str | None = x_api_token or (
        authorization[7:].strip()
        if authorization and authorization.lower().startswith("bearer ")
        else None
    )
    if token != settings.api_token:
        raise HTTPException(status_code=401, detail="Invalid webhook token")

    try:
        payload = await request.json()
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    parser = FlexiblePayloadParser()
    records: list[Measurement] = parser.parse(payload)

    repo = MeasurementRepository(session)
    inserted = 0
    duplicates = 0
    for rec in records:
        if rec.external_id:
            from sqlmodel import select

            existing = session.exec(
                select(Measurement).where(
                    Measurement.external_id == rec.external_id,
                    Measurement.source == rec.source,
                )
            ).first()
            if existing is not None:
                existing.value_numeric = rec.value_numeric
                existing.value_text = rec.value_text
                existing.value_json = rec.value_json
                existing.start_time = rec.start_time
                existing.end_time = rec.end_time
                repo.update(existing)
                duplicates += 1
                continue
        repo.create(rec)
        inserted += 1

    return {"status": "ok", "inserted": inserted, "duplicates": duplicates}
