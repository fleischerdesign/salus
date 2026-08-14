"""Time-zone helpers: local-day computation (ADR-009)."""
from datetime import date, datetime, timedelta, timezone

from zoneinfo import ZoneInfo

from salus.services.timezone import (
    local_date,
    local_day_range,
    resolve_timezone,
    start_of_local_day,
    today_in_tz,
    tz_for,
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


def test_make_dt_converts_wall_clock_to_naive_utc():
    from salus.services.medication import _make_dt

    # 08:00 local in Berlin (UTC+2 in August) == 06:00 UTC.
    assert _make_dt(date(2026, 8, 14), 8, 0, ZoneInfo("Europe/Berlin")) == datetime(
        2026, 8, 14, 6, 0, 0
    )


def test_tz_for_resolves_user_timezone(db_engine):
    from sqlmodel import Session

    from salus.models.user import User

    with Session(db_engine) as session:
        user = User(username="tzuser", password_hash="x", timezone="Europe/Berlin")
        session.add(user)
        session.commit()
        user_id = user.id

    with Session(db_engine) as session:
        assert str(tz_for(session, user_id)) == "Europe/Berlin"


def test_tz_for_falls_back_to_utc_for_unknown_user(db_engine):
    from sqlmodel import Session

    with Session(db_engine) as session:
        assert tz_for(session, "nonexistent") is timezone.utc
