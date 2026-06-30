import json

from salus.models.measurement import Measurement
from salus.services.parser import _to_dt, make_external_id


class AppleHealthExportParser:
    def can_handle(self, payload: dict | list) -> bool:
        if not isinstance(payload, dict):
            return False
        return "HealthData" in payload

    def parse(self, payload: dict | list) -> list[Measurement]:
        if not isinstance(payload, dict):
            return []
        health_data = payload.get("HealthData", {})
        records_data = health_data.get("Record", [])
        if isinstance(records_data, dict):
            records_data = [records_data]

        records: list[Measurement] = []
        for item in records_data:
            if not isinstance(item, dict):
                continue
            data_type = item.get("type", "").replace(
                "HKQuantityTypeIdentifier", ""
            ).replace("HKCategoryTypeIdentifier", "")
            start_time = item.get("startDate", "")
            ext_id = make_external_id("apple_health", data_type, start_time)
            records.append(Measurement(
                data_type=data_type,
                source="apple_health",
                value_json=json.dumps({"value": item.get("value", "")}),
                start_time=_to_dt(start_time),
                external_id=ext_id,
            ))
        return records
