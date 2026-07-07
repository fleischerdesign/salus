import json

from salus.models.measurement import Measurement
from salus.services.parser import _to_dt


class OuraParser:
    def can_handle(self, payload: dict | list) -> bool:
        if not isinstance(payload, dict):
            return False
        return "sleep" in payload and "readiness" in payload

    def parse(self, payload: dict | list) -> list[Measurement]:
        if not isinstance(payload, dict):
            return []
        records: list[Measurement] = []

        sleep_data = payload.get("sleep", [])
        if isinstance(sleep_data, dict):
            sleep_data = [sleep_data]
        for item in sleep_data:
            if not isinstance(item, dict):
                continue
            records.append(
                Measurement(
                    data_type="sleep",
                    source="oura",
                    value_json=json.dumps(
                        {
                            "duration_seconds": item.get("total_sleep_duration", 0),
                            "deep_sleep_seconds": item.get("deep_sleep_duration", 0),
                            "rem_sleep_seconds": item.get("rem_sleep_duration", 0),
                            "efficiency": item.get("efficiency", 0),
                            "score": item.get("score", 0),
                        }
                    ),
                    start_time=_to_dt(item.get("bedtime_start", "")),
                    end_time=_to_dt(item.get("bedtime_end", "")),
                    external_id=str(item.get("id", "")),
                )
            )

        readiness_data = payload.get("readiness", [])
        if isinstance(readiness_data, dict):
            readiness_data = [readiness_data]
        for item in readiness_data:
            if not isinstance(item, dict):
                continue
            records.append(
                Measurement(
                    data_type="readiness",
                    source="oura",
                    value_json=json.dumps(
                        {
                            "score": item.get("score", 0),
                            "temperature_deviation": item.get(
                                "temperature_deviation", 0
                            ),
                        }
                    ),
                    start_time=_to_dt(item.get("day", "")),
                    external_id=str(item.get("id", "")),
                )
            )

        return records
