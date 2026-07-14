#!/usr/bin/env python3
"""Seed realistic sample health data for a salus user.

Usage:
    PYTHONPATH=src uv run python scripts/seed_data.py --username Fleischerinho --days 7

The script creates the user (with default metric types) if they do not exist,
then inserts 7 days of data for: heart rate, steps, sleep, weight, nutrition,
and exercise.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "src")

# ---------------------------------------------------------------------------
#  Import all model modules so SQLAlchemy's registry discovers every mapper
# ---------------------------------------------------------------------------
import salus.models.api_token  # noqa: F401
import salus.models.dashboard  # noqa: F401
import salus.models.goal  # noqa: F401
import salus.models.measurement  # noqa: F401
import salus.models.system_config  # noqa: F401
import salus.models.user  # noqa: F401
import salus.models.user_identity  # noqa: F401
import salus.models.workout  # noqa: F401
from salus.database import engine
from salus.models import MetricType
from salus.models.measurement import Measurement
from salus.models.user import User
from salus.models.user_identity import UserIdentity
from salus.services.metric_type_mapping import DEFAULT_METRIC_TYPES
from salus.services.password import hash_password
from sqlmodel import Session, select

# ── Constants ──────────────────────────────────────────────────────────
_DAYS_OF_WEEK = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

# Heart-rate time-of-day templates: (hour_range, bpm_range, likelihood)
# Used to generate realistic intra-day HR curves.
_HR_TEMPLATES = [
    {"hours": (6, 7), "bpm": (54, 62), "label": "wake"},
    {"hours": (8, 9), "bpm": (62, 78), "label": "commute"},
    {"hours": (10, 11), "bpm": (65, 75), "label": "desk"},
    {"hours": (12, 13), "bpm": (72, 88), "label": "lunch-walk"},
    {"hours": (14, 15), "bpm": (65, 78), "label": "afternoon"},
    {"hours": (17, 18), "bpm": (60, 70), "label": "evening"},  # overridden on workout days
    {"hours": (20, 21), "bpm": (58, 66), "label": "relax"},
    {"hours": (22, 23), "bpm": (54, 60), "label": "bedtime"},
]

_WORKOUT_BPM_RANGE = (125, 148)
# Days 2 and 5 (index 3 and 6 from the end) will be workout days.
_WORKOUT_DAY_INDICES = {2, 5}


def _make_dt(day: datetime, hour: int, minute: int = 0) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, 0, tzinfo=timezone.utc)


# ── Heart Rate ──────────────────────────────────────────────────────────
def _generate_heart_rate(
    user_id: int,
    metric_type_id: int,
    anchor: datetime,
    day_offset: int,
) -> list[Measurement]:
    day = (anchor - timedelta(days=day_offset)).date()
    is_workout = day_offset in _WORKOUT_DAY_INDICES
    measurements: list[Measurement] = []

    for tmpl in _HR_TEMPLATES:
        h = random.randint(*tmpl["hours"])
        m = random.randint(0, 59)

        if tmpl["label"] == "evening" and is_workout:
            bpm = random.randint(*_WORKOUT_BPM_RANGE)
        else:
            bpm = random.randint(*tmpl["bpm"])

        measurements.append(
            Measurement(
                user_id=user_id,
                metric_type_id=metric_type_id,
                data_type="heart_rate",
                source="seed",
                value_numeric=float(bpm),
                start_time=_make_dt(day, h, m),
            )
        )

    return measurements


# ── Steps ───────────────────────────────────────────────────────────────
def _generate_steps(
    user_id: int,
    metric_type_id: int,
    anchor: datetime,
    day_offset: int,
) -> Measurement:
    day = (anchor - timedelta(days=day_offset)).date()
    base = [6200, 8500, 11200, 4300, 9800, 7100, 10500]
    count = base[day_offset % len(base)] + random.randint(-800, 800)
    return Measurement(
        user_id=user_id,
        metric_type_id=metric_type_id,
        data_type="steps",
        source="seed",
        value_numeric=float(max(0, count)),
        start_time=_make_dt(day, 22, 0),
    )


# ── Sleep ───────────────────────────────────────────────────────────────
_SLEEP_BASE = [
    (7.5, {"awake": 30, "light": 180, "deep": 90, "rem": 90}),
    (8.0, {"awake": 20, "light": 170, "deep": 110, "rem": 100}),
    (6.5, {"awake": 45, "light": 150, "deep": 75, "rem": 80}),
    (7.0, {"awake": 25, "light": 160, "deep": 95, "rem": 85}),
    (8.2, {"awake": 15, "light": 175, "deep": 120, "rem": 105}),
    (6.0, {"awake": 60, "light": 140, "deep": 60, "rem": 60}),
    (7.8, {"awake": 20, "light": 165, "deep": 105, "rem": 95}),
]


def _generate_sleep(
    user_id: int,
    metric_type_id: int,
    anchor: datetime,
    day_offset: int,
) -> Measurement:
    day = (anchor - timedelta(days=day_offset + 1)).date()
    hours, stages_min = _SLEEP_BASE[day_offset % len(_SLEEP_BASE)]
    total_s = int(hours * 3600)

    # Jitter each stage by ±15 %
    stages = {}
    for k, v in stages_min.items():
        jittered = int(v * 60 * random.uniform(0.85, 1.15))
        stages[k] = max(0, jittered)

    # Reconcile total
    stage_total = sum(stages.values())
    if stage_total > 0:
        for k in stages:
            stages[k] = int(stages[k] * total_s / stage_total)

    sleep_start = _make_dt(day, 23, random.randint(0, 30))
    sleep_end = sleep_start + timedelta(seconds=total_s)

    return Measurement(
        user_id=user_id,
        metric_type_id=metric_type_id,
        data_type="sleep",
        source="seed",
        start_time=sleep_start,
        end_time=sleep_end,
        value_json=json.dumps(
            {
                "duration_seconds": total_s,
                "stages": [
                    {"stage": "1", "duration_seconds": stages["awake"]},
                    {"stage": "2", "duration_seconds": stages["light"]},
                    {"stage": "3", "duration_seconds": stages["deep"]},
                    {"stage": "4", "duration_seconds": stages["rem"]},
                ],
            }
        ),
    )


# ── Weight ──────────────────────────────────────────────────────────────
def _generate_weight(
    user_id: int,
    metric_type_id: int,
    anchor: datetime,
    day_offset: int,
) -> Measurement:
    day = (anchor - timedelta(days=day_offset)).date()
    values = [79.2, 78.8, 78.5, 78.9, 78.6, 78.3, 78.1]
    kg = values[day_offset % len(values)] + random.uniform(-0.15, 0.15)
    return Measurement(
        user_id=user_id,
        metric_type_id=metric_type_id,
        data_type="weight",
        source="seed",
        value_numeric=round(kg, 1),
        start_time=_make_dt(day, 7, random.randint(0, 30)),
    )


# ── Nutrition ───────────────────────────────────────────────────────────
_NUTRITION_BASE = [
    (2450, 140, 220, 90),
    (1910, 120, 180, 60),
    (2180, 135, 195, 75),
    (2640, 155, 260, 95),
    (2030, 110, 175, 70),
    (2320, 145, 200, 80),
    (1900, 100, 160, 65),
]


def _generate_nutrition(
    user_id: int,
    metric_type_id: int,
    anchor: datetime,
    day_offset: int,
) -> Measurement:
    day = (anchor - timedelta(days=day_offset)).date()
    kcal, pro, carbs, fat_g = _NUTRITION_BASE[day_offset % len(_NUTRITION_BASE)]
    jitter = lambda v: max(0, v + random.randint(-80, 80))
    return Measurement(
        user_id=user_id,
        metric_type_id=metric_type_id,
        data_type="nutrition",
        source="seed",
        start_time=_make_dt(day, 19, random.randint(0, 30)),
        value_json=json.dumps(
            {
                "total_kcal": jitter(kcal),
                "protein_g": jitter(pro),
                "carbs_g": jitter(carbs),
                "fat_g": jitter(fat_g),
            }
        ),
    )


# ── Exercise ────────────────────────────────────────────────────────────
_EXERCISE_SESSIONS = [
    {"offset": 2, "type": 1, "duration": 2100, "calories": 320},
    {"offset": 2, "type": 3, "duration": 3600, "calories": 480},
    {"offset": 5, "type": 1, "duration": 2700, "calories": 390},
]


def _generate_exercise(
    user_id: int,
    metric_type_id: int,
    anchor: datetime,
) -> list[Measurement]:
    measurements: list[Measurement] = []
    for sess in _EXERCISE_SESSIONS:
        day = (anchor - timedelta(days=sess["offset"])).date()
        start = _make_dt(day, 17, random.randint(0, 30))
        measurements.append(
            Measurement(
                user_id=user_id,
                metric_type_id=metric_type_id,
                data_type="exercise",
                source="seed",
                start_time=start,
                value_json=json.dumps(
                    {
                        "exercise_type": sess["type"],
                        "duration_seconds": sess["duration"],
                        "distance_meters": random.randint(3000, 8000)
                        if sess["type"] == 1
                        else 0,
                        "calories": sess["calories"],
                    }
                ),
            )
        )
    return measurements


# ── User bootstrap ──────────────────────────────────────────────────────
def _resolve_user(session: Session, username: str, password: str) -> int:
    user = session.exec(select(User).where(User.username == username)).first()
    if user is not None:
        return user.id

    print(f"Creating user '{username}' …")
    user = User(
        username=username,
        password_hash=hash_password(password),
        email=f"{username}@seed.local",
        display_name=username,
        is_admin=False,
    )
    session.add(user)
    session.flush()

    identity = UserIdentity(
        user_id=user.id,
        provider="local",
        provider_user_id=username,
    )
    session.add(identity)

    # Seed default metric types
    for name, unit, data_type, color, source_data_type, icon, widget_size, widget_enabled in DEFAULT_METRIC_TYPES:
        mt = MetricType(
            name=name,
            unit=unit,
            data_type=data_type,
            color=color,
            user_id=user.id,
            is_system=True,
            source_data_type=source_data_type,
            icon=icon,
            widget_size=widget_size,
            widget_enabled=widget_enabled,
        )
        session.add(mt)

    session.flush()
    return user.id


def _seed_workout_plans_and_sessions(session: Session, user_id: int, dry_run: bool = False) -> None:
    from salus.models.workout import Exercise, WorkoutPlan, WorkoutPlanExercise, WorkoutSession, WorkoutLogEntry

    default_exercises = [
        {"name": "Squat", "equipment": "barbell", "primary_muscles": "quadriceps,gluteus_maximus", "secondary_muscles": "hamstrings,core"},
        {"name": "Bench Press", "equipment": "barbell", "primary_muscles": "pectoralis_major", "secondary_muscles": "triceps,deltoids"},
        {"name": "Deadlift", "equipment": "barbell", "primary_muscles": "hamstrings,gluteus_maximus,erector_spinae", "secondary_muscles": "forearms,core"},
        {"name": "Overhead Press", "equipment": "barbell", "primary_muscles": "deltoids", "secondary_muscles": "triceps"},
        {"name": "Pull-Up", "equipment": "bodyweight", "primary_muscles": "latissimus_dorsi,biceps", "secondary_muscles": "forearms"},
    ]

    exercise_objs = {}
    now = datetime.now(timezone.utc)
    for ex_data in default_exercises:
        ex = session.exec(select(Exercise).where(Exercise.name == ex_data["name"])).first()
        if not ex:
            if dry_run:
                print(f"  [DRY RUN] Would create exercise: {ex_data['name']}")
                # create a dummy so the rest of the dry run script doesn't key error
                ex = Exercise(id=999, name=ex_data["name"], equipment=ex_data["equipment"], primary_muscles=ex_data["primary_muscles"])
            else:
                ex = Exercise(
                    name=ex_data["name"],
                    equipment=ex_data["equipment"],
                    primary_muscles=ex_data["primary_muscles"],
                    secondary_muscles=ex_data["secondary_muscles"],
                    description=f"Standard {ex_data['name']} exercise.",
                    user_id=None,
                    created_at=now,
                    updated_at=now,
                )
                session.add(ex)
                session.flush()
        exercise_objs[ex_data["name"]] = ex

    plan_name = "Starting Strength"
    plan = session.exec(select(WorkoutPlan).where(WorkoutPlan.name == plan_name, WorkoutPlan.user_id == user_id)).first()
    if not plan:
        if dry_run:
            print(f"  [DRY RUN] Would create workout plan: {plan_name}")
            plan = WorkoutPlan(id=999, name=plan_name, user_id=user_id)
        else:
            print(f"Creating workout plan '{plan_name}'...")
            plan = WorkoutPlan(
                name=plan_name,
                description="Classic 3x5 barbell training program.",
                user_id=user_id,
                autoreg_mode="advisory",
            )
            session.add(plan)
            session.flush()

            plan_ex_data = [
                {"name": "Squat", "seq": 0, "sets": 3, "reps": 5, "rpe": 8.0},
                {"name": "Bench Press", "seq": 1, "sets": 3, "reps": 5, "rpe": 8.0},
                {"name": "Deadlift", "seq": 2, "sets": 1, "reps": 5, "rpe": 9.0},
            ]
            for item in plan_ex_data:
                ex = exercise_objs[item["name"]]
                pe = WorkoutPlanExercise(
                    plan_id=plan.id,
                    exercise_id=ex.id,
                    sequence=item["seq"],
                    target_sets=item["sets"],
                    target_reps=item["reps"],
                    target_rpe=item["rpe"],
                    created_at=now,
                    updated_at=now,
                )
                session.add(pe)
            session.flush()

    # Backfill missing timestamps on existing Exercise and WorkoutPlanExercise records
    if not dry_run:
        updated_any = False
        for ex in session.exec(select(Exercise).where(Exercise.created_at == None)).all():
            ex.created_at = now
            ex.updated_at = now
            session.add(ex)
            updated_any = True
        for pe in session.exec(select(WorkoutPlanExercise).where(WorkoutPlanExercise.created_at == None)).all():
            pe.created_at = now
            pe.updated_at = now
            session.add(pe)
            updated_any = True
        if updated_any:
            session.flush()

    existing_sessions = session.exec(select(WorkoutSession).where(WorkoutSession.user_id == user_id)).first()
    if not existing_sessions:
        if dry_run:
            print("  [DRY RUN] Would create 2 completed workout sessions and log entries.")
        else:
            print("Seeding past completed workout sessions...")
            now = datetime.now(timezone.utc)
            session_dates = [now - timedelta(days=5), now - timedelta(days=2)]
            
            for i, sess_dt in enumerate(session_dates):
                ws = WorkoutSession(
                    user_id=user_id,
                    plan_id=plan.id,
                    started_at=sess_dt - timedelta(minutes=60),
                    completed_at=sess_dt,
                    autoreg_mode="advisory",
                    recovery_score=82.0 + (i * 5.0),
                    notes=f"Workout session {i+1} completed successfully.",
                )
                session.add(ws)
                session.flush()

                for s in range(1, 4):
                    log = WorkoutLogEntry(
                        session_id=ws.id,
                        exercise_id=exercise_objs["Squat"].id,
                        set_number=s,
                        weight=80.0 + (i * 5.0),
                        reps=5,
                        rpe=8.0,
                    )
                    session.add(log)
                for s in range(1, 4):
                    log = WorkoutLogEntry(
                        session_id=ws.id,
                        exercise_id=exercise_objs["Bench Press"].id,
                        set_number=s,
                        weight=60.0 + (i * 2.5),
                        reps=5,
                        rpe=7.5,
                    )
                    session.add(log)
                log = WorkoutLogEntry(
                    session_id=ws.id,
                    exercise_id=exercise_objs["Deadlift"].id,
                    set_number=1,
                    weight=100.0 + (i * 10.0),
                    reps=5,
                    rpe=9.0,
                )
                session.add(log)
            session.flush()


# ── CLI ─────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Seed salus with sample health data.")
    parser.add_argument("--username", required=True, help="Target user (created if needed)")
    parser.add_argument("--days", type=int, default=7, help="Days of data to generate")
    parser.add_argument("--password", default="seed", help="Password for new users only")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print what would be inserted, do not commit"
    )
    args = parser.parse_args()

    anchor = datetime.now(timezone.utc)

    with Session(engine) as session:
        user_id = _resolve_user(session, args.username, args.password)

        # Metric-type ID lookup
        metric_types = session.exec(
            select(MetricType).where(
                MetricType.user_id == user_id,
                MetricType.source_data_type.in_(
                    ["steps", "heart_rate", "sleep", "weight", "nutrition", "exercise"]
                ),
            )
        ).all()
        mt_map: dict[str, int] = {mt.source_data_type: mt.id for mt in metric_types if mt.id is not None}

        all_measurements: list[Measurement] = []

        # Heart rate: intraday readings for each day
        for d in range(args.days):
            all_measurements.extend(
                _generate_heart_rate(user_id, mt_map["heart_rate"], anchor, d)
            )

        # Steps: daily totals
        for d in range(args.days):
            all_measurements.append(
                _generate_steps(user_id, mt_map["steps"], anchor, d)
            )

        # Sleep
        for d in range(args.days):
            all_measurements.append(
                _generate_sleep(user_id, mt_map["sleep"], anchor, d)
            )

        # Weight
        for d in range(args.days):
            all_measurements.append(
                _generate_weight(user_id, mt_map["weight"], anchor, d)
            )

        # Nutrition
        for d in range(args.days):
            all_measurements.append(
                _generate_nutrition(user_id, mt_map["nutrition"], anchor, d)
            )

        # Exercise
        all_measurements.extend(
            _generate_exercise(user_id, mt_map["exercise"], anchor)
        )

        # Summary
        from collections import Counter

        counts = Counter(m.data_type for m in all_measurements)
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Would insert {len(all_measurements)} measurements:")
        for dt, cnt in sorted(counts.items()):
            print(f"  {dt:>14s}: {cnt:>3d}")

        _seed_workout_plans_and_sessions(session, user_id, args.dry_run)

        if not args.dry_run:
            for m in all_measurements:
                session.add(m)
            session.commit()
            print("\nDone. Refresh your dashboard to see the new data.")
        else:
            print("\nNo changes committed (--dry-run).")


if __name__ == "__main__":
    main()
