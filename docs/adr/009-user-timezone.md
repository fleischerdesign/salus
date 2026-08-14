# 9. User timezone as the single source for local-day boundaries

- Status: Proposed
- Date: 2026-08-14

## Context

Health data is day-based: the dashboard's "today", daily trends, streaks, goals,
meal/mood/habit logs, medication schedules, and cross-source comparisons all ask
"which calendar day does this instant belong to?". A timestamp is an instant; a
"day" is a calendar concept that depends on a timezone.

The codebase previously had *three* inconsistent answers:

- the frontend computed "today" in the **browser's local timezone** (per device),
- the backend's day filters (goals, sharing, data quality) used **UTC**,
- `medication.py` used `date.today()`, i.e. the **server's** clock.

These disagreed, so "today" differed across devices and between UI and backend,
and a user in UTC±N got goal/streak/medication results shifted by hours.

## Decision

### 1. `User.timezone` (IANA name) is the single source of truth

`User.timezone` holds an IANA zone name (`Europe/Berlin`), defaulting to `UTC`.
It is a cloud-synced profile field (`SAFE_PROFILE_FIELDS`, `update_profile`,
`user_profile` sync) and is auto-detected at registration from the client's
`Intl.DateTimeFormat().resolvedOptions().timeZone`, with an override in Settings.

### 2. Two helper modules — everything else routes through them

- **Backend** `services/timezone.py`: `resolve_timezone`, `user_tz`, `tz_for`,
  `user_today`, `local_date`, `today_in_tz`, `start_of_local_day`,
  `next_local_day_start`, `local_day_range`, `start_of_local_week`. All use stdlib
  `zoneinfo`; invalid/empty zones fall back to UTC.
- **Frontend** `$lib/utils/timezone.ts`: a synchronously-cached profile zone plus
  `dateStringInTz` and `startOfTodayMs` (via `Intl`), with a browser-local
  fallback before the profile loads. `todayString()` becomes tz-aware without
  changing any caller.

### 3. Day-boundary semantics

- Measurements are stored as **naive UTC**; `local_date(dt, tz)` normalizes naive
  (assumed UTC) and aware datetimes before converting.
- Day ranges are **half-open `[local_midnight, next_local_midnight)`**, computed
  through the zone — never `+ timedelta(days=1)` — so DST days of 23/25 hours are
  correct.
- Wall-clock times (medication doses) are converted via `datetime.combine(...,
  tzinfo=tz)`, with Python's `fold=0` default for ambiguous fall-back times.
- Date-string entities (`log_date`, `entry_date`, …) are created by the tz-aware
  `todayString()`; the backend treats them as opaque calendar dates.

### 4. What does *not* change

- **Display formatting** (`toLocaleString`) stays browser-local — showing local
  wall-clock time is natural; only *day boundaries* need the user zone.
- **`CircadianProfile.timezone_offset_hours`** remains sun-derived (a separate
  concern from calendar days); it is intentionally not coupled to `User.timezone`.

## Consequences

- `User` gains `timezone`; a migration adds the column (`server_default 'UTC'`).
- Goal, medication, habit, meal, mood, journal, lab, recipe, achievement streaks,
  sharing (federation), leaderboard, and data-quality checks now resolve day
  boundaries through the timezone helpers.
- Changing `timezone` re-buckets historical data on read (nothing is stored
  pre-bucketed), which is expected: the data is re-interpreted, not lost.
- Timezone-adjacent edge cases are covered by unit tests (DST day length, naive vs
  aware normalization, invalid-zone fallback).

## Alternatives considered

- **Browser-local everywhere** — rejected: device-dependent, breaks cross-device
  consistency (the core promise of a synced tracker).
- **UTC everywhere** — rejected: "today" is wrong by hours for most users.
- **Derive from `CircadianProfile.timezone_offset_hours`** — rejected: optional,
  DST-less, and sun-derived rather than a true calendar zone.
