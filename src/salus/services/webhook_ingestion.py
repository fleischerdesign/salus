import json
import logging

from salus.repositories.protocols import IMeasurementRepository
from salus.services.metric_type_mapping import MetricTypeMappingService
from salus.services.parser import FlexiblePayloadParser
from salus.services.plugin.hooks import HookRegistry

logger = logging.getLogger("salus.webhook.ingestion")


class WebhookIngestionService:
    def __init__(
        self,
        parser: FlexiblePayloadParser,
        measurement_repo: IMeasurementRepository,
        mapping_service: MetricTypeMappingService,
        registry: HookRegistry | None = None,
    ) -> None:
        self._parser = parser
        self._measurement_repo = measurement_repo
        self._mapping = mapping_service
        self._registry = registry

    def ingest(self, payload: dict | list, user_id: int) -> tuple[int, int]:
        records = self._parser.parse(payload)
        logger.info("Parsed %d records from payload", len(records))

        for rec in records:
            rec.user_id = user_id
            rec.metric_type_id = self._mapping.resolve(rec.data_type, user_id)
            parsed_val = json.loads(rec.value_json) if rec.value_json else None
            vj_keys = list(parsed_val.keys()) if isinstance(parsed_val, dict) else []
            logger.debug(
                "Record | data_type=%s | source=%s | metric_type_id=%s | "
                "value_numeric=%s | value_json_keys=%s | start_time=%s | external_id=%s",
                rec.data_type, rec.source, rec.metric_type_id,
                rec.value_numeric, vj_keys,
                rec.start_time.isoformat() if rec.start_time else None,
                rec.external_id,
            )

        # 1. Run Ingestion Interceptors (HookIngestionInterceptor)
        if self._registry:
            for interceptor in self._registry.ingestion_interceptors:
                try:
                    records = interceptor.intercept(records)
                except Exception as e:
                    logger.error(f"Error executing ingestion interceptor: {e}")

        # 2. Persist to database
        res = self._measurement_repo.upsert_all(records)

        # 3. Notify Event Subscribers (HookEventSubscriber)
        if self._registry:
            for sub in self._registry.event_subscribers:
                for rec in records:
                    try:
                        sub.on_measurement_created(rec)
                    except Exception as e:
                        logger.error(f"Error notifying event subscriber during ingestion: {e}")

        return res
