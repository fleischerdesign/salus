from datetime import date, datetime

from salus.models import DEFAULT_METRIC_COLOR
from salus.models.user import User

__all__ = ["uid", "DEFAULT_METRIC_COLOR", "make_handle", "parse_date"]


def parse_date(date_str: str) -> date | None:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def make_handle(user: User) -> str:
    return f"@{user.username}"


def uid(user: User) -> int:
    """Return the user's database id, guaranteed present after first persist.

    SQLModel declares `id` as `int | None` because it is absent before
    the initial INSERT.  After `session.flush()` (which `Repository.create()`
    calls internally via `session.commit()` / `session.refresh()`), the
    primary key is always populated.  This helper makes that guarantee
    visible to the type-checker without sprinkling ``# type: ignore[arg-type]``
    through every caller.
    """
    if user.id is None:
        raise ValueError("User has no persisted id — call commit() first")
    return user.id
