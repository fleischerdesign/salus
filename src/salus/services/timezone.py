"""Time-zone helpers — the single source for "local day" computation.

Salus stores ``datetime`` values as naive UTC (SQLite strips timezone info) and
stores calendar dates as opaque ``date`` strings. Any logic that asks "which
calendar day does this instant belong to?" must go through these helpers so the
answer is the *user's* local day (``User.timezone``, an IANA name), never UTC or
the server's own clock.

Design notes (see ADR-009):
- ``local_date`` normalizes both naive (assumed UTC) and aware datetimes.
- Day boundaries are computed through the zone, never as ``+ timedelta(days=1)``,
  so DST days of 23/25 hours are handled correctly (half-open intervals).
- Invalid/empty zone names fall back to UTC.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from typing import TYPE_CHECKING

from salus.models.user import User

if TYPE_CHECKING:
    from sqlmodel import Session

UTC: tzinfo = timezone.utc


def resolve_timezone(name: str | None) -> tzinfo:
    if not name:
        return UTC
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        return UTC


def user_tz(user: User) -> tzinfo:
    return resolve_timezone(user.timezone)


def tz_for(session: "Session", user_id: str) -> tzinfo:
    user = session.get(User, user_id)
    return user_tz(user) if user else UTC


def user_today(session: "Session", user_id: str) -> date:
    return today_in_tz(tz_for(session, user_id))


def local_date(dt: datetime, tz: tzinfo) -> date:
    """Calendar day ``dt`` belongs to in ``tz`` (``dt`` may be naive or aware)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(tz).date()


def today_in_tz(tz: tzinfo) -> date:
    return datetime.now(UTC).astimezone(tz).date()


def start_of_local_day(d: date, tz: tzinfo) -> datetime:
    """Naive-UTC instant of local midnight for date ``d`` in ``tz``."""
    return datetime.combine(d, time.min, tzinfo=tz).astimezone(UTC).replace(tzinfo=None)


def next_local_day_start(d: date, tz: tzinfo) -> datetime:
    return start_of_local_day(d + timedelta(days=1), tz)


def local_day_range(d: date, tz: tzinfo) -> tuple[datetime, datetime]:
    """Half-open [start, end) naive-UTC range covering local day ``d``."""
    return start_of_local_day(d, tz), next_local_day_start(d, tz)


def start_of_local_week(tz: tzinfo) -> date:
    today = today_in_tz(tz)
    return today - timedelta(days=today.weekday())
