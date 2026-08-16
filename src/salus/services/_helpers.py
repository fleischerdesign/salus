from datetime import date, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from salus.models.user import User

DEFAULT_METRIC_COLOR = "#4f46e5"

_SUMMABLE_METRIC_CODES = frozenset({"steps", "water", "exercise", "mindfulness", "planned_exercise"})

__all__ = [
    "uid",
    "DEFAULT_METRIC_COLOR",
    "make_handle",
    "parse_date",
    "summarize_daily_values",
]


def summarize_daily_values(metric_code: str, values: list[float]) -> float | None:
    """Aggregate a metric's values: sum for additive metrics, mean otherwise.

    Returns ``None`` when there are no values to aggregate.
    """
    if not values:
        return None
    total = sum(values)
    if metric_code in _SUMMABLE_METRIC_CODES:
        return float(total)
    return float(total / len(values))


def parse_date(date_str: str) -> date | None:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def make_handle(user: "User") -> str:
    return f"@{user.username}"


def uid(user: "User") -> str:
    """Return the user's database id, guaranteed present after first persist.

    SQLModel declares ``id`` as ``str | None`` because it is absent before
    the initial INSERT.  After ``session.flush()`` (triggered by
    ``UnitOfWork.commit()`` on context-manager exit), the primary key is
    always populated.  This helper makes that guarantee visible to the
    type-checker without sprinkling ``# type: ignore[arg-type]``
    through every caller.
    """
    if user.id is None:
        raise ValueError("User has no persisted id — call commit() first")
    return user.id
