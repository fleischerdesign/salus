import json

from salus.models.measurement import Measurement
from salus.services.parser import _parse_datetime, make_external_id
from salus.services.parsers.base import BaseParser


class GoogleFitParser(BaseParser):
    def _can_handle_impl(self, payload: dict) -> bool:
        return "bucket" in payload

    def _parse_impl(self, payload: dict) -> list[Measurement]:
        records: list[Measurement] = []
        for bucket in payload.get("bucket", []):
            if not isinstance(bucket, dict):
                continue
            start_time = bucket.get("startTimeMillis", "")
            for ds in bucket.get("dataset", []):
                ds_data = ds if isinstance(ds, dict) else {}
                data_type = ds_data.get("dataSourceId", "")
                for point in ds_data.get("point", []):
                    p_data = point if isinstance(point, dict) else {}
                    ext_id = make_external_id(
                        "google_fit",
                        data_type,
                        p_data.get("startTimeNanos", start_time),
                    )
                    records.append(
                        Measurement(
                            data_type=data_type,
                            source="google_fit",
                            value_json=json.dumps(p_data.get("value", [])),
                            start_time=_parse_datetime(start_time),
                            external_id=ext_id,
                        )
                    )
        return records
