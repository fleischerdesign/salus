"""Time-zone helpers: local-day computation (ADR-009)."""
from datetime import date, datetime, timedelta, timezone

from zoneinfo import ZoneInfo

from salus.services.timezone import (
    local_date,
    local_day_range,
    resolve_timezone,
    start_of_local_day,
    today_in_tz,
)


def test_resolve_timezone_valid():
    assert resolve_timezone("Europe/Berlin") == ZoneInfo("Europe/Berlin")


def test_resolve_timezone_invalid_falls_back_to_utc():
    assert resolve_timezone("Not/AZone") is timezone.utc
    assert resolve_timezone("") is timezone.utc
    assert resolve_timezone(None) is timezone.utc


def test_local_date_naive_is_interpreted_as_utc():
    instant = datetime(2026, 8, 14, 0, 30)  # naive, stored as UTC
    assert local_date(instant, ZoneInfo("Europe/Berlin")) == date(2026, 8, 14)
    assert local_date(instant, ZoneInfo("America/New_York")) == date(2026, 8, 13)


def test_local_date_aware_is_converted_not_relabelled():
    instant = datetime(2026, 8, 14, 0, 30, tzinfo=timezone.utc)
    assert local_date(instant, ZoneInfo("America/New_York")) == date(2026, 8, 13)


def test_start_of_local_day_returns_naive_utc():
    start = start_of_local_day(date(2026, 8, 14), ZoneInfo("Europe/Berlin"))
    assert start == datetime(2026, 8, 13, 22, 0, 0)
    assert start.tzinfo is None


def test_local_day_range_is_dst_aware():
    # Berlin DST begins 2026-03-29 02:00 → 03:00: the day is 23h long.
    start, end = local_day_range(date(2026, 3, 29), ZoneInfo("Europe/Berlin"))
    assert start == datetime(2026, 3, 28, 23, 0, 0)
    assert end == datetime(2026, 3, 29, 22, 0, 0)
    assert end - start == timedelta(hours=23)


def test_today_in_tz_matches_local_date_of_now():
    tz = ZoneInfo("UTC")
    assert today_in_tz(tz) == datetime.now(timezone.utc).date()
