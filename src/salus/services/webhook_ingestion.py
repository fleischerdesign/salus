from salus.repositories.measurement import MeasurementRepository
from salus.services.metric_type_mapping import MetricTypeMappingService
from salus.services.parser import FlexiblePayloadParser


class WebhookIngestionService:
    def __init__(
        self,
        parser: FlexiblePayloadParser,
        measurement_repo: MeasurementRepository,
        mapping_service: MetricTypeMappingService,
    ) -> None:
        self._parser = parser
        self._measurement_repo = measurement_repo
        self._mapping = mapping_service

    def ingest(self, payload: dict | list, user_id: int) -> tuple[int, int]:
        records = self._parser.parse(payload)
        for rec in records:
            rec.user_id = user_id
            rec.metric_type_id = self._mapping.resolve(rec.data_type, user_id)
        return self._measurement_repo.upsert_all(records)
