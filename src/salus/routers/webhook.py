from json import JSONDecodeError

from fastapi import APIRouter, Depends, HTTPException, Request

from salus.dependencies import get_webhook_ingestion_service, verify_webhook_token
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.webhook_ingestion import WebhookIngestionService

router = APIRouter()


@router.post("/webhook")
async def webhook_ingest(
    request: Request,
    current_user: User = Depends(verify_webhook_token),
    service: WebhookIngestionService = Depends(get_webhook_ingestion_service),
):
    try:
        payload = await request.json()
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    inserted, duplicates = service.ingest(payload, uid(current_user))
    return {"status": "ok", "inserted": inserted, "duplicates": duplicates}
