"""Metric mapping service and backwards-compatibility re-exports."""

from salus.reference_data.definitions.metrics import (
    DATA_TYPE_KEYWORD_TO_METRIC,
    DEFAULT_METRIC_PREFERENCES,
    METRIC_BOUNDS,
    METRIC_DEFINITIONS,
    METRIC_GROUPS,
)
from salus.repositories.protocols import IMetricDefinitionRepository

__all__ = [
    "DATA_TYPE_KEYWORD_TO_METRIC",
    "DEFAULT_METRIC_PREFERENCES",
    "METRIC_BOUNDS",
    "METRIC_DEFINITIONS",
    "METRIC_GROUPS",
    "MetricDefinitionMappingService",
]


class MetricDefinitionMappingService:
    def __init__(self, metric_definition_repo: IMetricDefinitionRepository) -> None:
        self._repo = metric_definition_repo
        self._cache: dict[str, str | None] = {}

    def resolve(self, source_data_type: str, user_id: str | None = None) -> str | None:
        if source_data_type in self._cache:
            return self._cache[source_data_type]

        code = DATA_TYPE_KEYWORD_TO_METRIC.get(source_data_type)
        if code is None:
            lower = source_data_type.lower()
            for keyword, mc in DATA_TYPE_KEYWORD_TO_METRIC.items():
                if keyword.lower() in lower:
                    code = mc
                    break

        if code is not None:
            md = self._repo.find_by_code(code)
            if md is not None:
                self._cache[source_data_type] = code
                return code

        self._cache[source_data_type] = None
        return None
