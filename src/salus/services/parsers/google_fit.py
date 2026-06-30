import json

from salus.models.measurement import Measurement
from salus.services.parser import _to_dt, make_external_id


class GoogleFitParser:
    def can_handle(self, payload: dict | list) -> bool:
        if not isinstance(payload, dict):
            return False
        return "bucket" in payload

    def parse(self, payload: dict | list) -> list[Measurement]:
        if not isinstance(payload, dict):
            return []
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
                    ext_id = make_external_id("google_fit", data_type, p_data.get("startTimeNanos", start_time))
                    records.append(Measurement(
                        data_type=data_type,
                        source="google_fit",
                        value_json=json.dumps(p_data.get("value", [])),
                        start_time=_to_dt(start_time),
                        external_id=ext_id,
                    ))
        return records
