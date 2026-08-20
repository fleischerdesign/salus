from datetime import date

from salus.services.workout.schedule import (
    ScheduleSlot,
    for_date,
    for_weekday,
    next_in_rotation,
)


def _rotation_slots() -> list[ScheduleSlot]:
    return [
        ScheduleSlot(workout_id="A", sequence=0),
        ScheduleSlot(workout_id="B", sequence=1),
        ScheduleSlot(workout_id="C", sequence=2),
    ]


def test_next_in_rotation_advances_in_sequence():
    slots = _rotation_slots()
    assert next_in_rotation(slots, after=0).workout_id == "B"


def test_next_in_rotation_wraps_to_first():
    slots = _rotation_slots()
    assert next_in_rotation(slots, after=2).workout_id == "A"


def test_next_in_rotation_none_returns_lowest_sequence():
    slots = _rotation_slots()
    assert next_in_rotation(slots).workout_id == "A"


def test_next_in_rotation_ignores_timing_rules():
    slots = [
        ScheduleSlot(workout_id="A", sequence=0),
        ScheduleSlot(workout_id="B", sequence=1, day_of_week=0),
        ScheduleSlot(workout_id="C", sequence=2, scheduled_date=date(2026, 4, 1)),
    ]
    assert next_in_rotation(slots, after=0).workout_id == "B"


def test_next_in_rotation_empty_returns_none():
    assert next_in_rotation([], after=0) is None


def test_for_weekday_returns_matching_slot():
    slots = [
        ScheduleSlot(workout_id="Push", sequence=0, day_of_week=0),
        ScheduleSlot(workout_id="Pull", sequence=1, day_of_week=2),
    ]
    assert for_weekday(slots, weekday=2).workout_id == "Pull"


def test_for_weekday_no_match_returns_none():
    slots = [ScheduleSlot(workout_id="Push", sequence=0, day_of_week=0)]
    assert for_weekday(slots, weekday=5) is None


def test_for_date_returns_matching_slot():
    slots = [ScheduleSlot(workout_id="Max", sequence=0, scheduled_date=date(2026, 4, 1))]
    assert for_date(slots, date(2026, 4, 1)).workout_id == "Max"


def test_for_date_no_match_returns_none():
    slots = [ScheduleSlot(workout_id="Max", sequence=0, scheduled_date=date(2026, 4, 1))]
    assert for_date(slots, date(2026, 4, 2)) is None
