import logging
from json import JSONDecodeError

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from salus.dependencies import verify_webhook_token
from salus.models.user import User
from salus.services._helpers import uid

logger = logging.getLogger("salus.webhook")

router = APIRouter()


def run_background_ingest(payload: dict | list, user_id: str, ingestion_svc):
    ingestion_svc.ingest(payload, user_id)


@router.post("/webhook", status_code=202)
async def webhook_ingest(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(verify_webhook_token),
):
    try:
        payload = await request.json()
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    keys = (
        list(payload) if isinstance(payload, dict) else f"[list, {len(payload)} items]"
    )
    logger.info("Webhook received | user=%s | keys=%s", current_user.username, keys)

    svc = request.app.state.background_ingestion
    background_tasks.add_task(
        run_background_ingest, payload, uid(current_user), svc
    )
    return {"status": "accepted", "message": "Ingestion task queued successfully"}
