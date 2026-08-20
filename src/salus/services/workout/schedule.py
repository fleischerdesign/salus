"""Program schedule resolution — the sequence/timing "secret" of a Program.

A program is an ordered list of slots; each slot references a workout and
carries an optional timing rule:

- no rule      → rotation (next in sequence, wraps)
- day_of_week  → weekly (0=Monday .. 6=Sunday, ISO)
- scheduled_date → dated (a specific calendar day)

This module is pure: it answers "what is next / scheduled?" from slot data
without touching the database.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ScheduleSlot:
    """A program slot: a workout with an optional timing rule."""

    workout_id: str
    sequence: int
    day_of_week: int | None = None
    scheduled_date: date | None = None


def _ordered(slots: Sequence[ScheduleSlot]) -> list[ScheduleSlot]:
    return sorted(slots, key=lambda slot: slot.sequence)


def next_in_rotation(
    slots: Sequence[ScheduleSlot], after: int | None = None
) -> ScheduleSlot | None:
    """Return the slot with the next sequence after `after`, wrapping.

    `after=None` returns the first slot in sequence order.
    """
    ordered = _ordered(slots)
    if not ordered:
        return None
    if after is None:
        return ordered[0]
    for slot in ordered:
        if slot.sequence > after:
            return slot
    return ordered[0]


def for_weekday(slots: Sequence[ScheduleSlot], weekday: int) -> ScheduleSlot | None:
    """Return the first slot scheduled for the given ISO weekday (0=Monday)."""
    for slot in _ordered(slots):
        if slot.day_of_week == weekday:
            return slot
    return None


def for_date(slots: Sequence[ScheduleSlot], d: date) -> ScheduleSlot | None:
    """Return the first slot scheduled for the given calendar date."""
    for slot in _ordered(slots):
        if slot.scheduled_date == d:
            return slot
    return None
