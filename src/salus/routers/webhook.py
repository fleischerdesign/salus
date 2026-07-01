import logging
from json import JSONDecodeError

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from salus.dependencies import verify_webhook_token
from salus.models.user import User
from salus.services._helpers import uid

logger = logging.getLogger("salus.webhook")

router = APIRouter()


def run_background_ingest(payload: dict | list, user_id: int, db_engine):
    from sqlmodel import Session
    from salus.repositories.measurement import MeasurementRepository
    from salus.repositories.metric_type import MetricTypeRepository
    from salus.services.metric_type_mapping import MetricTypeMappingService
    from salus.services.parser import FlexiblePayloadParser
    from salus.services.webhook_ingestion import WebhookIngestionService

    try:
        with Session(db_engine) as session:
            parser = FlexiblePayloadParser()
            measurement_repo = MeasurementRepository(session)
            metric_type_repo = MetricTypeRepository(session)
            mapping_service = MetricTypeMappingService(metric_type_repo)

            service = WebhookIngestionService(parser, measurement_repo, mapping_service)
            inserted, duplicates = service.ingest(payload, user_id)
            logger.info(
                "Background ingestion complete | user_id=%d | inserted=%d | duplicates=%d",
                user_id, inserted, duplicates
            )
    except Exception as e:
        logger.error("Background ingestion failed | user_id=%d | error=%s", user_id, str(e), exc_info=True)


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

    keys = list(payload) if isinstance(payload, dict) else f"[list, {len(payload)} items]"
    logger.info("Webhook received | user=%s | keys=%s", current_user.username, keys)

    background_tasks.add_task(run_background_ingest, payload, uid(current_user), request.app.state.engine)
    return {"status": "accepted", "message": "Ingestion task queued successfully"}
