import json

from salus.models.measurement import Measurement
from salus.services.parser import _parse_datetime, make_external_id
from salus.services.parsers.base import BaseParser


class AppleHealthExportParser(BaseParser):
    def _can_handle_impl(self, payload: dict) -> bool:
        return "HealthData" in payload

    def _parse_impl(self, payload: dict) -> list[Measurement]:
        health_data = payload.get("HealthData", {})
        records_data = health_data.get("Record", [])
        if isinstance(records_data, dict):
            records_data = [records_data]

        records: list[Measurement] = []
        for item in records_data:
            if not isinstance(item, dict):
                continue
            data_type = (
                item.get("type", "")
                .replace("HKQuantityTypeIdentifier", "")
                .replace("HKCategoryTypeIdentifier", "")
            )
            start_time = item.get("startDate", "")
            ext_id = make_external_id("apple_health", data_type, start_time)
            records.append(
                Measurement(
                    data_type=data_type,
                    source="apple_health",
                    value_json=json.dumps({"value": item.get("value", "")}),
                    start_time=_parse_datetime(start_time),
                    external_id=ext_id,
                )
            )
        return records
