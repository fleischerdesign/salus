"""Shared record serialization for sync responses and command results."""
from datetime import date, datetime
from typing import Any


def serialize_record(obj: Any, fields: list[str] | None = None) -> dict[str, Any]:
    """Serialize a SQLModel instance to a JSON-safe dict.

    ``fields`` restricts the output to a subset of the model's columns.
    Datetimes are emitted as naive ISO-8601 strings, matching the values
    SQLite returns on read.
    """
    if hasattr(obj, "model_dump"):
        dumped = obj.model_dump()
        result = (
            {k: dumped[k] for k in dumped if k in fields}
            if fields is not None
            else dumped
        )
    elif hasattr(obj, "__dict__"):
        result = {
            k: v
            for k, v in obj.__dict__.items()
            if not k.startswith("_") and (fields is None or k in fields)
        }
    else:
        return {}
    for k, v in result.items():
        if isinstance(v, datetime):
            result[k] = v.replace(tzinfo=None).isoformat()
        elif isinstance(v, date):
            result[k] = v.isoformat()
    return result
