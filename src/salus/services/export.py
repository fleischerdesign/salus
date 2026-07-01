import csv
import io
import json
from datetime import datetime

from salus.repositories.protocols import IMeasurementRepository


class ExportService:
    def __init__(self, repo: IMeasurementRepository) -> None:
        self._repo = repo

    def export_all(
        self,
        user_id: int,
        format: str = "csv",
        since: str | None = None,
        until: str | None = None,
    ) -> tuple[str, str, str]:
        dt_since = datetime.fromisoformat(since) if since else None
        dt_until = datetime.fromisoformat(until) if until else None
        records = self._repo.find_all(user_id=user_id, since=dt_since, until=dt_until)

        if format == "json":
            data = [
                {
                    "data_type": r.data_type,
                    "source": r.source,
                    "metric_type_id": r.metric_type_id,
                    "value_numeric": r.value_numeric,
                    "value_text": r.value_text,
                    "value_json": r.value_json,
                    "start_time": r.start_time.isoformat(),
                    "end_time": r.end_time.isoformat() if r.end_time else None,
                    "notes": r.notes,
                    "external_id": r.external_id,
                }
                for r in records
            ]
            return (
                json.dumps(data, indent=2, ensure_ascii=False, default=str),
                "salus-export.json",
                "application/json",
            )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "source", "data_type", "metric_type_id", "value_numeric",
            "value_text", "value_json", "start_time", "end_time", "notes",
        ])
        for r in records:
            writer.writerow([
                r.source, r.data_type, r.metric_type_id, r.value_numeric,
                r.value_text or "", (r.value_json or "")[:200],
                r.start_time.isoformat(),
                r.end_time.isoformat() if r.end_time else "",
                r.notes or "",
            ])
        return output.getvalue(), "salus-export.csv", "text/csv"
