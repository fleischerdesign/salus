import json
import logging

from salus.repositories.protocols import IMeasurementRepository
from salus.services.metric_type_mapping import MetricTypeMappingService
from salus.services.parser import FlexiblePayloadParser

logger = logging.getLogger("salus.webhook.ingestion")


class WebhookIngestionService:
    def __init__(
        self,
        parser: FlexiblePayloadParser,
        measurement_repo: IMeasurementRepository,
        mapping_service: MetricTypeMappingService,
    ) -> None:
        self._parser = parser
        self._measurement_repo = measurement_repo
        self._mapping = mapping_service

    def ingest(self, payload: dict | list, user_id: int) -> tuple[int, int]:
        records = self._parser.parse(payload)
        logger.info("Parsed %d records from payload", len(records))

        for rec in records:
            rec.user_id = user_id
            rec.metric_type_id = self._mapping.resolve(rec.data_type, user_id)
            vj_keys = list(json.loads(rec.value_json).keys()) if rec.value_json else []
            logger.debug(
                "Record | data_type=%s | source=%s | metric_type_id=%s | "
                "value_numeric=%s | value_json_keys=%s | start_time=%s | external_id=%s",
                rec.data_type, rec.source, rec.metric_type_id,
                rec.value_numeric, vj_keys,
                rec.start_time.isoformat() if rec.start_time else None,
                rec.external_id,
            )
        return self._measurement_repo.upsert_all(records)
