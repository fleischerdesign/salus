import json

from salus.models.measurement import Measurement
from salus.services.parser import _parse_datetime, make_external_id
from salus.services.parsers.base import BaseParser


class FitbitParser(BaseParser):
    def _can_handle_impl(self, payload: dict) -> bool:
        return "activities-heart" in payload

    def _parse_impl(self, payload: dict) -> list[Measurement]:
        records: list[Measurement] = []
        activities = payload.get("activities-heart", [])
        if isinstance(activities, dict):
            activities = [activities]
        for item in activities:
            if not isinstance(item, dict):
                continue
            date_time = item.get("dateTime", "")
            ext_id = make_external_id("fitbit", "heart_rate", date_time)
            records.append(
                Measurement(
                    data_type="heart_rate",
                    source="fitbit",
                    value_json=json.dumps(
                        {
                            "zones": item.get("value", {}).get("heartRateZones", []),
                            "resting": item.get("value", {}).get("restingHeartRate"),
                        }
                    ),
                    start_time=_parse_datetime(date_time),
                    external_id=ext_id,
                )
            )
        return records
