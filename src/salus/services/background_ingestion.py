import logging
from typing import Callable

from sqlmodel import Session

from salus.repositories.measurement import MeasurementRepository
from salus.repositories.metric_type import MetricTypeRepository
from salus.services.metric_type_mapping import MetricTypeMappingService
from salus.services.parser import FlexiblePayloadParser
from salus.services.webhook_ingestion import WebhookIngestionService

logger = logging.getLogger("salus.services.background_ingestion")


class BackgroundIngestionService:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def ingest(self, payload: dict | list, user_id: str) -> None:
        with self._session_factory() as session:
            parser = FlexiblePayloadParser()
            measurement_repo = MeasurementRepository(session)
            metric_type_repo = MetricTypeRepository(session)
            mapping_service = MetricTypeMappingService(metric_type_repo)

            service = WebhookIngestionService(
                parser, measurement_repo, mapping_service
            )
            records = parser.parse(payload)
            inserted, duplicates = service.ingest(payload, user_id)
            logger.info(
                "Background ingestion complete | user_id=%s | inserted=%d | duplicates=%d",
                user_id,
                inserted,
                duplicates,
            )

            if inserted > 0:
                from salus.repositories.unit_of_work import SqlUnitOfWork
                from salus.services.sharing import SharingService

                uow = SqlUnitOfWork(session)
                sharing_svc = SharingService.create(uow)

                unique_updates: set[tuple[str, str]] = set()
                for rec in records:
                    if rec.data_type and rec.start_time:
                        date_str = rec.start_time.date().strftime("%Y-%m-%d")
                        unique_updates.add((rec.data_type, date_str))

                for data_type, date_str in unique_updates:
                    try:
                        sharing_svc.notify_peers_of_update(
                            user_id, data_type, date_str
                        )
                    except Exception as exc:
                        logger.warning(
                            f"Failed to notify peer of webhook update: {exc}"
                        )
