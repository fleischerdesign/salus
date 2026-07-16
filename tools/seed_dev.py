#!/usr/bin/env python3
"""Seed dashboard widgets + realistic health data for a dev user. Idempotent.

Usage: uv run python tools/seed_dev.py Fleischerinho [--data]"""

import json
import math
import random
import sys
from datetime import datetime, timedelta, timezone

from salus.database import get_session
from salus.repositories.dashboard import DashboardWidgetRepository
from salus.repositories.measurement import MeasurementRepository
from salus.repositories.metric_type import MetricTypeRepository
from salus.repositories.user import UserRepository
from salus.models.dashboard import DashboardWidget, WidgetSize
from salus.models.measurement import Measurement
from salus.services._helpers import uuid7_str

random.seed(42)


def seed_dashboard(session, user_id: str) -> None:
    dashboard_repo = DashboardWidgetRepository(session)
    existing = [w for w in dashboard_repo.find_by_user(user_id) if w.deleted_at is None]
    if existing:
        print(f"  Dashboard: {len(existing)} widgets (skip)")
        return
    metric_repo = MetricTypeRepository(session)
    metrics = metric_repo.find_all(user_id=None)
    large = {"steps", "sleep"}
    count = 0
    for m in metrics:
        if not m.widget_enabled or m.id is None:
            continue
        w = DashboardWidget(
            id=uuid7_str(),
            user_id=user_id,
            metric_type_id=m.id,
            size=WidgetSize.LARGE if m.name.lower() in large else WidgetSize.MEDIUM,
            position=count,
        )
        dashboard_repo.add(w)
        count += 1
    session.commit()
    print(f"  Dashboard: {count} widgets seeded")


def seed_data(session, user_id: str) -> None:
    measurement_repo = MeasurementRepository(session)
    existing = measurement_repo.find_all(user_id, limit=1)
    if existing:
        print(f"  Data: measurements exist (skip)")
        return

    metric_repo = MetricTypeRepository(session)
    metrics = {m.source_data_type: m for m in metric_repo.find_all(user_id=None) if m.id and m.source_data_type}
    now = datetime.now(timezone.utc)
    measurements: list[Measurement] = []

    weight = 78.5
    for days_ago in range(90, 0, -1):
        d = now - timedelta(days=days_ago)
        day_start = d.replace(hour=8, minute=0, second=0, microsecond=0)

        weight += random.uniform(-0.15, 0.05)
        weight = max(74.0, min(80.0, weight))
        mt = metrics.get("weight")
        if mt:
            measurements.append(Measurement(
                id=uuid7_str(), user_id=user_id, metric_type_id=mt.id,
                data_type=mt.source_data_type, source="seed",
                value_numeric=round(weight, 1),
                start_time=day_start,
            ))

        steps = int(random.gauss(9500, 2500))
        steps = max(2000, min(18000, steps))
        mt = metrics.get("steps")
        if mt:
            measurements.append(Measurement(
                id=uuid7_str(), user_id=user_id, metric_type_id=mt.id,
                data_type=mt.source_data_type, source="seed",
                value_numeric=float(steps),
                start_time=day_start,
            ))

        rhr = 62.0 + 3.0 * math.sin(days_ago / 7.0) + random.gauss(0, 2)
        mt = metrics.get("heart_rate")
        if mt:
            measurements.append(Measurement(
                id=uuid7_str(), user_id=user_id, metric_type_id=mt.id,
                data_type=mt.source_data_type, source="seed",
                value_numeric=round(rhr, 1),
                start_time=day_start,
            ))

        sleep_h = 7.5 + random.gauss(0, 0.6)
        sleep_h = max(5.0, min(9.5, sleep_h))
        total_sec = int(sleep_h * 3600)
        deep_sec = int(total_sec * random.uniform(0.18, 0.25))
        rem_sec = int(total_sec * random.uniform(0.18, 0.25))
        awake_sec = int(total_sec * random.uniform(0.02, 0.08))
        light_sec = total_sec - deep_sec - rem_sec - awake_sec
        mt = metrics.get("sleep")
        if mt:
            measurements.append(Measurement(
                id=uuid7_str(), user_id=user_id, metric_type_id=mt.id,
                data_type=mt.source_data_type, source="seed",
                start_time=day_start - timedelta(hours=8),
                end_time=day_start,
                value_json=json.dumps({
                    "duration_seconds": total_sec,
                    "stages": [
                        {"stage": "4", "duration_seconds": light_sec},
                        {"stage": "5", "duration_seconds": deep_sec},
                        {"stage": "6", "duration_seconds": rem_sec},
                        {"stage": "1", "duration_seconds": awake_sec},
                    ],
                }),
            ))

        if days_ago % 3 == 0:
            calories = int(random.uniform(2000, 2600))
            protein = int(calories * random.uniform(0.20, 0.30) / 4)
            carbs = int(calories * random.uniform(0.35, 0.50) / 4)
            fat = int(calories * random.uniform(0.20, 0.35) / 9)
            mt = metrics.get("nutrition")
            if mt:
                measurements.append(Measurement(
                    id=uuid7_str(), user_id=user_id, metric_type_id=mt.id,
                    data_type=mt.source_data_type, source="seed",
                    start_time=day_start + timedelta(hours=12),
                    value_json=json.dumps({
                        "calories": calories, "protein_grams": protein,
                        "carbs_grams": carbs, "fat_grams": fat,
                    }),
                ))

        if days_ago % 4 == 0:
            exercise_type = random.choice(["Running", "Cycling", "Strength Training"])
            dur = int(random.uniform(1800, 3600))
            dist = dur * random.uniform(2.5, 4.0) if exercise_type != "Strength Training" else 0
            cal = int(dur * random.uniform(0.12, 0.18))
            mt = metrics.get("exercise")
            if mt:
                measurements.append(Measurement(
                    id=uuid7_str(), user_id=user_id, metric_type_id=mt.id,
                    data_type=mt.source_data_type, source="seed",
                    start_time=day_start + timedelta(hours=17),
                    end_time=day_start + timedelta(hours=17, seconds=dur),
                    value_json=json.dumps({
                        "exercise_type_name": exercise_type,
                        "duration_seconds": dur,
                        "distance_meters": dist,
                        "calories": cal,
                    }),
                ))

        if days_ago % 5 == 0:
            mt = metrics.get("hrv")
            if mt:
                rmssd = 45 + random.gauss(0, 8)
                measurements.append(Measurement(
                    id=uuid7_str(), user_id=user_id, metric_type_id=mt.id,
                    data_type=mt.source_data_type, source="seed",
                    value_numeric=round(max(20, min(80, rmssd)), 1),
                    start_time=day_start,
                ))

    for batch in range(0, len(measurements), 200):
        measurement_repo.add_all(measurements[batch:batch + 200])
    session.commit()
    print(f"  Data: {len(measurements)} measurements seeded ({90} days)")


def main(username: str, with_data: bool = False) -> None:
    session = next(get_session())
    try:
        user_repo = UserRepository(session)
        user = user_repo.get_by_username(username)
        if user is None:
            print(f"User '{username}' not found.")
            sys.exit(1)

        seed_dashboard(session, user.id)
        if with_data:
            seed_data(session, user.id)
        print("Done.")
    finally:
        session.close()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: uv run python tools/seed_dev.py <username> [--data]")
        sys.exit(1)
    main(args[0], "--data" in args)
