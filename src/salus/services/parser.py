import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

from salus.models.measurement import Measurement

logger = logging.getLogger("salus.parser")


def _to_dt(time_str: str) -> datetime:
    if not time_str:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


METADATA_KEYS = {"timestamp", "app_version", "date", "user_id", "source"}

RECORD_SKIP_KEYS = {
    "start_time", "startTime", "end_time", "endTime",
    "id", "uuid", "stages", "session_end_time",
    "created_at", "updated_at",
}


@runtime_checkable
class RecordParser(Protocol):
    def parse(self, payload: dict | list) -> list[Measurement]:
        ...

    def can_handle(self, payload: dict | list) -> bool:
        ...


def make_external_id(source: str, data_type: str, start_time: str) -> str:
    raw = f"{source}|{data_type}|{start_time}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _safe_json(value_str: str) -> str:
    try:
        return json.dumps(json.loads(value_str), ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        return value_str


class HealthConnectWebhookParser:
    def can_handle(self, payload: dict | list) -> bool:
        if not isinstance(payload, dict):
            return False
        data_type_keys = [k for k in payload if k not in METADATA_KEYS]
        return bool(data_type_keys) and any(
            isinstance(payload[k], list) for k in data_type_keys
        )

    def parse(self, payload: dict | list) -> list[Measurement]:
        if not isinstance(payload, dict):
            return []
        records: list[Measurement] = []
        data_type_keys = [k for k in payload if k not in METADATA_KEYS]

        for dtype in data_type_keys:
            items = payload[dtype]
            if not isinstance(items, list):
                continue

            for item in items:
                if not isinstance(item, dict):
                    continue

                start_time = (
                    item.get("start_time") or item.get("startTime")
                    or item.get("time") or item.get("timestamp")
                    or item.get("date") or item.get("session_end_time") or ""
                )
                end_time = item.get("end_time") or item.get("endTime") or ""
                rec_id = item.get("id") or item.get("uuid") or ""

                value = {k: v for k, v in item.items() if k not in RECORD_SKIP_KEYS}
                if "stages" in item:
                    value["stages"] = item["stages"]

                external_id = rec_id if rec_id else make_external_id(
                    "samsung_health", dtype, start_time
                )
                value_json = json.dumps(value, ensure_ascii=False)

                records.append(Measurement(
                    data_type=dtype,
                    source="samsung_health",
                    value_json=value_json,
                    start_time=_to_dt(start_time),
                    end_time=_to_dt(end_time) if end_time else None,
                    external_id=external_id,
                ))

        return records


class FlatArrayParser:
    def can_handle(self, payload: dict | list) -> bool:
        if isinstance(payload, list):
            return True
        if isinstance(payload, dict) and (
            "type" in payload or "dataType" in payload or "id" in payload
        ):
            return True
        return False

    def parse(self, payload: dict | list) -> list[Measurement]:
        if isinstance(payload, dict):
            payload = [payload]
        if not isinstance(payload, list):
            return []
        records: list[Measurement] = []

        for item in payload:
            if not isinstance(item, dict):
                continue

            rec_id = item.get("id") or item.get("uuid") or ""
            start_time = (
                item.get("startTime") or item.get("start_time")
                or item.get("timestamp") or item.get("date") or ""
            )
            data_type = item.get("type") or item.get("dataType") or item.get("name") or ""
            end_time = item.get("endTime") or item.get("end_time") or ""
            raw_val = item.get("value") or item.get("data")
            if raw_val is None:
                raw_val = {}

            if isinstance(raw_val, str):
                value_json = _safe_json(raw_val)
            else:
                try:
                    value_json = json.dumps(raw_val, ensure_ascii=False)
                except (TypeError, ValueError):
                    continue

            external_id = rec_id if rec_id else make_external_id(
                "flat_array", data_type, start_time
            )

            records.append(Measurement(
                data_type=data_type,
                source="flat_array",
                value_json=value_json,
                start_time=_to_dt(start_time),
                end_time=_to_dt(end_time) if end_time else None,
                external_id=external_id,
            ))

        return records


class FlexiblePayloadParser:
    def __init__(self, parsers: list[RecordParser] | None = None) -> None:
        if parsers is not None:
            self._parsers = list(parsers)
        else:
            self._parsers: list[RecordParser] = [
                HealthConnectWebhookParser(),
                FlatArrayParser(),
            ]

    def can_handle(self, payload: dict | list) -> bool:
        return isinstance(payload, (dict, list))

    def parse(self, payload: dict | list) -> list[Measurement]:
        if not isinstance(payload, (dict, list)):
            return []

        for parser in self._parsers:
            if parser.can_handle(payload):
                result = parser.parse(payload)
                if result:
                    return result

        if isinstance(payload, dict):
            if "records" in payload and isinstance(payload["records"], list):
                return self.parse(payload["records"])
            if "data" in payload and isinstance(payload["data"], list):
                return self.parse(payload["data"])

        keys = list(payload) if isinstance(payload, dict) else []
        logger.warning("Unknown payload format. Keys: %s", keys)
        raise ValueError(f"unexpected payload format: {keys}" if keys else "unknown payload format")
