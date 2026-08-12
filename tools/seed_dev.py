#!/usr/bin/env python3
"""Comprehensive development seed script for Salus.

Idempotently populates realistic reference data and 90 days of historical data
across all 10 domain subsystems: Users, Dashboards, Exercises, Workouts,
Food/Nutrition, Measurements, Habits, Goals, Medications, Mood, and Journal.

Usage:
    uv run python tools/seed_dev.py [username] [--days 90] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlmodel import Session, select

from salus.database import get_session
from salus.models.circadian import CircadianProfile
from salus.models.dashboard import DashboardWidget, WidgetSize
from salus.models.food import FoodItem, Meal, MealItem, Recipe, RecipeIngredient
from salus.models.goal import Goal, GoalDirection, GoalFrequency
from salus.models.habit import Habit, HabitFrequency, HabitLog
from salus.models.journal import JournalEntry
from salus.models.measurement import Measurement
from salus.models.medication import (
    Medication,
    MedicationForm,
    MedicationInventory,
    MedicationLog,
    MedicationSchedule,
)
from salus.models.metric_definition import MetricDefinition
from salus.models.mood import MoodEntry, MoodTag
from salus.models.user import User
from salus.models.user_identity import UserIdentity
from salus.models.workout import (
    Exercise,
    WorkoutLogEntry,
    WorkoutPlan,
    WorkoutPlanExercise,
    WorkoutSession,
)
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.services._helpers import uuid7_str
from salus.services.password import hash_password
from salus.services.user import UserService

# Fixed random seed for deterministic generation
RANDOM_SEED = 42


# ── 1. SYSTEM EXERCISES ──────────────────────────────────────────────────
SYSTEM_EXERCISES = [
    {
        "name": "Barbell Squat",
        "equipment": "barbell",
        "primary_muscles": "quadriceps,gluteus_maximus",
        "secondary_muscles": "hamstrings,core,erector_spinae",
        "description": "Fundamental lower body compound exercise targeting quads and glutes.",
        "instructions": "1. Position bar on upper back. 2. Squat down until thighs are parallel. 3. Drive up through mid-foot.",
        "suggested_rest_seconds": 180,
    },
    {
        "name": "Bench Press",
        "equipment": "barbell",
        "primary_muscles": "pectoralis_major",
        "secondary_muscles": "triceps,anterior_deltoid",
        "description": "Primary horizontal pushing exercise for chest and triceps strength.",
        "instructions": "1. Lie flat on bench. 2. Lower bar to mid-chest. 3. Press up until arms are fully extended.",
        "suggested_rest_seconds": 180,
    },
    {
        "name": "Deadlift",
        "equipment": "barbell",
        "primary_muscles": "hamstrings,gluteus_maximus,erector_spinae",
        "secondary_muscles": "latissimus_dorsi,forearms,core",
        "description": "Ultimate posterior chain exercise pulling weight from the floor.",
        "instructions": "1. Stand with shins near bar. 2. Hinge hips, grip bar. 3. Pull bar upward keeping back flat.",
        "suggested_rest_seconds": 240,
    },
    {
        "name": "Overhead Press",
        "equipment": "barbell",
        "primary_muscles": "anterior_deltoid,lateral_deltoid",
        "secondary_muscles": "triceps,core,upper_chest",
        "description": "Strict vertical press for overhead strength and shoulder health.",
        "instructions": "1. Hold bar at collarbone level. 2. Press straight overhead until elbows lock out.",
        "suggested_rest_seconds": 120,
    },
    {
        "name": "Barbell Row",
        "equipment": "barbell",
        "primary_muscles": "latissimus_dorsi,rhomboids",
        "secondary_muscles": "biceps,posterior_deltoid",
        "description": "Horizontal pulling exercise building back thickness and lats.",
        "instructions": "1. Hinge torso forward to ~45 deg. 2. Pull bar to upper abdomen. 3. Squeeze shoulder blades.",
        "suggested_rest_seconds": 120,
    },
    {
        "name": "Pull-Up",
        "equipment": "bodyweight",
        "primary_muscles": "latissimus_dorsi",
        "secondary_muscles": "biceps,brachialis,core",
        "description": "Bodyweight vertical pull targeting back width and arm strength.",
        "instructions": "1. Grip bar slightly wider than shoulder-width. 2. Pull chin over bar. 3. Lower with control.",
        "suggested_rest_seconds": 120,
    },
    {
        "name": "Tricep Dip",
        "equipment": "bodyweight",
        "primary_muscles": "triceps",
        "secondary_muscles": "pectoralis_major,anterior_deltoid",
        "description": "Bodyweight pushing exercise targeting triceps and lower chest.",
        "instructions": "1. Support weight on parallel bars. 2. Lower body until elbows reach 90 degrees. 3. Push back up.",
        "suggested_rest_seconds": 90,
    },
    {
        "name": "Leg Press",
        "equipment": "machine",
        "primary_muscles": "quadriceps",
        "secondary_muscles": "gluteus_maximus",
        "description": "Machine-based leg exercise allowing heavy quad loading with back support.",
        "instructions": "1. Place feet hip-width on sled. 2. Lower weight smoothly. 3. Press back without locking knees.",
        "suggested_rest_seconds": 120,
    },
    {
        "name": "Dumbbell Bicep Curl",
        "equipment": "dumbbell",
        "primary_muscles": "biceps",
        "secondary_muscles": "brachialis,forearms",
        "description": "Isolation exercise for bicep hypertrophy.",
        "instructions": "1. Hold dumbbells at sides. 2. Curl weights up toward shoulders keeping elbows still.",
        "suggested_rest_seconds": 60,
    },
    {
        "name": "Plank",
        "equipment": "bodyweight",
        "primary_muscles": "rectus_abdominis,transverse_abdominis",
        "secondary_muscles": "gluteus_maximus,shoulders",
        "description": "Isometric core stability exercise.",
        "instructions": "1. Hold body in straight line supported on forearms and toes. 2. Engage core and glutes.",
        "suggested_rest_seconds": 60,
    },
    {
        "name": "Treadmill Running",
        "equipment": "machine",
        "primary_muscles": "quadriceps,calves,cardiovascular",
        "secondary_muscles": "hamstrings,gluteus_maximus",
        "description": "Cardiovascular endurance training on treadmill.",
        "instructions": "Maintain steady aerobic rhythm at 60-80% max heart rate.",
        "suggested_rest_seconds": 0,
    },
]


# ── 2. SYSTEM FOOD ITEMS ─────────────────────────────────────────────────
SYSTEM_FOODS = [
    {
        "name": "Hähnchenbrustfilet",
        "brand": "GenussPur",
        "serving_size": 100.0,
        "serving_unit": "g",
        "calories_per_serving": 165.0,
        "protein_g": 31.0,
        "carbs_g": 0.0,
        "fat_g": 3.6,
        "is_verified": True,
    },
    {
        "name": "Haferflocken Zart",
        "brand": "Kölln",
        "serving_size": 100.0,
        "serving_unit": "g",
        "calories_per_serving": 372.0,
        "protein_g": 13.5,
        "carbs_g": 58.7,
        "fat_g": 7.0,
        "fiber_g": 10.0,
        "is_verified": True,
    },
    {
        "name": "Magerquark",
        "brand": "Landliebe",
        "serving_size": 100.0,
        "serving_unit": "g",
        "calories_per_serving": 68.0,
        "protein_g": 12.0,
        "carbs_g": 4.0,
        "fat_g": 0.2,
        "is_verified": True,
    },
    {
        "name": "Hühnereier (Größe M)",
        "brand": "Freiland",
        "serving_size": 55.0,
        "serving_unit": "g",
        "calories_per_serving": 78.0,
        "protein_g": 6.3,
        "carbs_g": 0.4,
        "fat_g": 5.3,
        "is_verified": True,
    },
    {
        "name": "Vollkorn Basmati Reis",
        "brand": "Reishunger",
        "serving_size": 100.0,
        "serving_unit": "g",
        "calories_per_serving": 354.0,
        "protein_g": 8.5,
        "carbs_g": 72.0,
        "fat_g": 2.2,
        "fiber_g": 3.8,
        "is_verified": True,
    },
    {
        "name": "Whey Protein Isolate Vanille",
        "brand": "ESN",
        "serving_size": 30.0,
        "serving_unit": "g",
        "calories_per_serving": 112.0,
        "protein_g": 26.1,
        "carbs_g": 0.9,
        "fat_g": 0.4,
        "is_verified": True,
    },
    {
        "name": "Banane Frisch",
        "brand": "Bio",
        "serving_size": 120.0,
        "serving_unit": "g",
        "calories_per_serving": 105.0,
        "protein_g": 1.3,
        "carbs_g": 27.0,
        "fat_g": 0.3,
        "sugar_g": 14.4,
        "is_verified": True,
    },
    {
        "name": "Avocado",
        "brand": "Hass",
        "serving_size": 150.0,
        "serving_unit": "g",
        "calories_per_serving": 240.0,
        "protein_g": 3.0,
        "carbs_g": 12.0,
        "fat_g": 22.0,
        "fiber_g": 10.0,
        "is_verified": True,
    },
    {
        "name": "Mandeln Naturbelassen",
        "brand": "Seeberger",
        "serving_size": 30.0,
        "serving_unit": "g",
        "calories_per_serving": 178.0,
        "protein_g": 6.3,
        "carbs_g": 2.7,
        "fat_g": 15.0,
        "fiber_g": 3.5,
        "is_verified": True,
    },
    {
        "name": "Brokkoli Tiefgekühlt",
        "brand": "Iglos",
        "serving_size": 100.0,
        "serving_unit": "g",
        "calories_per_serving": 34.0,
        "protein_g": 2.8,
        "carbs_g": 7.0,
        "fat_g": 0.4,
        "fiber_g": 2.6,
        "is_verified": True,
    },
    {
        "name": "Lachsfilet",
        "brand": "Deutsche See",
        "serving_size": 125.0,
        "serving_unit": "g",
        "calories_per_serving": 260.0,
        "protein_g": 25.0,
        "carbs_g": 0.0,
        "fat_g": 17.5,
        "is_verified": True,
    },
    {
        "name": "Olivenöl Extra Vergine",
        "brand": "Bertolli",
        "serving_size": 10.0,
        "serving_unit": "ml",
        "calories_per_serving": 82.0,
        "protein_g": 0.0,
        "carbs_g": 0.0,
        "fat_g": 9.2,
        "is_verified": True,
    },
]


def seed_system_catalogs(session: Session) -> dict[str, dict[str, Any]]:
    """Seeds global reference catalogs for Exercise and FoodItem (user_id=null)."""
    exercises_map: dict[str, Exercise] = {}
    for ex_data in SYSTEM_EXERCISES:
        existing = session.exec(
            select(Exercise).where(Exercise.name == ex_data["name"])
        ).first()
        if existing is None:
            ex = Exercise(
                id=uuid7_str(),
                user_id=None,
                **ex_data,
                created_at=datetime.now(timezone.utc),
            )
            session.add(ex)
            session.flush()
            exercises_map[ex_data["name"]] = ex
        else:
            exercises_map[ex_data["name"]] = existing

    foods_map: dict[str, FoodItem] = {}
    for food_data in SYSTEM_FOODS:
        existing = session.exec(
            select(FoodItem).where(FoodItem.name == food_data["name"])
        ).first()
        if existing is None:
            f = FoodItem(
                id=uuid7_str(),
                user_id=None,
                source="system_seed",
                **food_data,
                created_at=datetime.now(timezone.utc),
            )
            session.add(f)
            session.flush()
            foods_map[food_data["name"]] = f
        else:
            foods_map[food_data["name"]] = existing

    print(
        f"  [1/10] System Catalogs: {len(exercises_map)} exercises, {len(foods_map)} food items ready"
    )
    return {"exercises": exercises_map, "foods": foods_map}


def seed_user_and_identity(session: Session, identifier: str) -> User:
    """Ensures target user exists with registered metrics and local identity."""
    uow = SqlUnitOfWork(session)
    user_service = UserService(uow)

    user = user_service.get_by_username(identifier) or user_service.get_by_email(identifier)
    if user is None:
        email = identifier if "@" in identifier else f"{identifier.lower()}@salus.local"
        username = identifier.split("@")[0] if "@" in identifier else identifier
        user = user_service.register(
            username=username,
            password="seedpassword123",
            email=email,
            display_name=username,
        )
        user.height_cm = 182.0
        session.add(user)
        session.commit()
        print(f"  [2/10] User: Created '{username}' ({email}) with default preferences")
    else:
        print(f"  [2/10] User: Resolved existing user '{user.username}' (id={user.id})")

    # Circadian profile default
    circ = session.exec(
        select(CircadianProfile).where(CircadianProfile.user_id == user.id)
    ).first()
    if circ is None:
        session.add(
            CircadianProfile(
                id=uuid7_str(),
                user_id=user.id,
                configured_chronotype="intermediate",
            )
        )
        session.commit()

    return user


def seed_dashboard(session: Session, user_id: str) -> None:
    """Seeds default dashboard widgets if user has none."""
    existing = session.exec(
        select(DashboardWidget).where(
            DashboardWidget.user_id == user_id, DashboardWidget.deleted_at == None
        )
    ).all()
    if existing:
        print(f"  [3/10] Dashboard: {len(existing)} widgets present (skip)")
        return

    metric_codes = ["steps", "sleep", "heart_rate", "weight", "nutrition", "exercise", "hrv"]
    large = {"steps", "sleep"}
    count = 0
    for code in metric_codes:
        widget = DashboardWidget(
            id=uuid7_str(),
            user_id=user_id,
            widget_type="metric",
            metric_code=code,
            size=WidgetSize.LARGE if code in large else WidgetSize.MEDIUM,
            position=count,
        )
        session.add(widget)
        count += 1
    session.commit()
    print(f"  [3/10] Dashboard: {count} widgets seeded")


def seed_workout_plans_and_history(
    session: Session, user: User, exercises: dict[str, Exercise], days: int
) -> None:
    """Seeds WorkoutPlan, WorkoutPlanExercise, WorkoutSession, and WorkoutLogEntry."""
    existing_plan = session.exec(
        select(WorkoutPlan).where(
            WorkoutPlan.user_id == user.id, WorkoutPlan.deleted_at == None
        )
    ).first()

    plan_a: WorkoutPlan
    if existing_plan is None:
        plan_a = WorkoutPlan(
            id=uuid7_str(),
            name="Starting Strength 3x5",
            description="Classic novice linear progression strength training program.",
            user_id=user.id,
            autoreg_mode="advisory",
            position=0,
        )
        session.add(plan_a)
        session.flush()

        plan_exs = [
            ("Barbell Squat", 0, 3, 5, 8.0),
            ("Bench Press", 1, 3, 5, 8.0),
            ("Deadlift", 2, 1, 5, 9.0),
        ]
        for ex_name, seq, sets, reps, rpe in plan_exs:
            if ex_name in exercises:
                pe = WorkoutPlanExercise(
                    id=uuid7_str(),
                    plan_id=plan_a.id,
                    exercise_id=exercises[ex_name].id,
                    sequence=seq,
                    target_sets=sets,
                    target_reps=reps,
                    target_rpe=rpe,
                )
                session.add(pe)
        session.commit()
    else:
        plan_a = existing_plan

    # Seed workout sessions every ~3 days
    existing_sessions = session.exec(
        select(WorkoutSession).where(WorkoutSession.user_id == user.id)
    ).all()
    if existing_sessions:
        print(f"  [4/10] Workouts: {len(existing_sessions)} sessions present (skip)")
        return

    now = datetime.now(timezone.utc)
    sessions_count = 0
    logs_count = 0

    for day_offset in range(days, 0, -3):
        sess_dt = now - timedelta(days=day_offset)
        ws = WorkoutSession(
            id=uuid7_str(),
            user_id=user.id,
            plan_id=plan_a.id,
            started_at=sess_dt - timedelta(minutes=65),
            completed_at=sess_dt,
            autoreg_mode="advisory",
            recovery_score=80.0 + random.uniform(-10.0, 10.0),
            notes="Solid training session. Progressive overload on main lifts.",
        )
        session.add(ws)
        session.flush()
        sessions_count += 1

        weeks_elapsed = (days - day_offset) / 7.0
        squat_wt = 70.0 + (weeks_elapsed * 2.5)
        bench_wt = 50.0 + (weeks_elapsed * 1.5)
        dead_wt = 90.0 + (weeks_elapsed * 3.0)

        # Squat 3x5
        for s in range(1, 4):
            session.add(
                WorkoutLogEntry(
                    id=uuid7_str(),
                    session_id=ws.id,
                    exercise_id=exercises["Barbell Squat"].id,
                    set_number=s,
                    weight=round(squat_wt, 1),
                    reps=5,
                    rpe=7.5 + (s * 0.5),
                )
            )
            logs_count += 1

        # Bench Press 3x5
        for s in range(1, 4):
            session.add(
                WorkoutLogEntry(
                    id=uuid7_str(),
                    session_id=ws.id,
                    exercise_id=exercises["Bench Press"].id,
                    set_number=s,
                    weight=round(bench_wt, 1),
                    reps=5,
                    rpe=7.0 + (s * 0.5),
                )
            )
            logs_count += 1

        # Deadlift 1x5
        session.add(
            WorkoutLogEntry(
                id=uuid7_str(),
                session_id=ws.id,
                exercise_id=exercises["Deadlift"].id,
                set_number=1,
                weight=round(dead_wt, 1),
                reps=5,
                rpe=8.5,
            )
        )
        logs_count += 1

    session.commit()
    print(
        f"  [4/10] Workouts: 1 plan, {sessions_count} sessions ({logs_count} log entries) seeded"
    )


def seed_food_and_nutrition(
    session: Session, user: User, foods: dict[str, FoodItem], days: int
) -> None:
    """Seeds Recipe, Meal, MealItem, and Measurement nutrition bridge entries."""
    existing_recipes = session.exec(
        select(Recipe).where(Recipe.user_id == user.id)
    ).all()
    if not existing_recipes:
        rec = Recipe(
            id=uuid7_str(),
            user_id=user.id,
            name="High-Protein Hafer-Bowl",
            description="Schnelles Post-Workout Frühstück mit Magerquark & Whey",
            servings=1,
            prep_time_min=5,
            cook_time_min=0,
            is_favorite=True,
        )
        session.add(rec)
        session.flush()

        if "Haferflocken Zart" in foods:
            session.add(
                RecipeIngredient(
                    id=uuid7_str(),
                    recipe_id=rec.id,
                    user_id=user.id,
                    food_item_id=foods["Haferflocken Zart"].id,
                    amount_g=80.0,
                )
            )
        if "Magerquark" in foods:
            session.add(
                RecipeIngredient(
                    id=uuid7_str(),
                    recipe_id=rec.id,
                    user_id=user.id,
                    food_item_id=foods["Magerquark"].id,
                    amount_g=150.0,
                )
            )
        session.commit()

    existing_meals = session.exec(
        select(Meal).where(Meal.user_id == user.id)
    ).all()
    if existing_meals:
        print(f"  [5/10] Nutrition: {len(existing_meals)} meals present (skip)")
        return

    today = date.today()
    meals_seeded = 0
    items_seeded = 0

    # Seed meals for recent 14 days
    for d in range(min(14, days)):
        meal_date = today - timedelta(days=d)

        # Breakfast
        m_b = Meal(
            id=uuid7_str(),
            user_id=user.id,
            log_date=meal_date,
            meal_type="breakfast",
            name="Fitness Frühstück",
        )
        session.add(m_b)
        session.flush()
        meals_seeded += 1

        if "Haferflocken Zart" in foods:
            session.add(
                MealItem(
                    id=uuid7_str(),
                    meal_id=m_b.id,
                    user_id=user.id,
                    food_item_id=foods["Haferflocken Zart"].id,
                    servings=0.8,
                    amount_g=80.0,
                )
            )
            items_seeded += 1

        # Lunch
        m_l = Meal(
            id=uuid7_str(),
            user_id=user.id,
            log_date=meal_date,
            meal_type="lunch",
            name="Chicken & Rice Bowl",
        )
        session.add(m_l)
        session.flush()
        meals_seeded += 1

        if "Hähnchenbrustfilet" in foods:
            session.add(
                MealItem(
                    id=uuid7_str(),
                    meal_id=m_l.id,
                    user_id=user.id,
                    food_item_id=foods["Hähnchenbrustfilet"].id,
                    servings=1.5,
                    amount_g=150.0,
                )
            )
            items_seeded += 1

    session.commit()
    print(
        f"  [5/10] Nutrition: {meals_seeded} meals logged ({items_seeded} meal items, 1 recipe)"
    )


def seed_health_measurements(session: Session, user: User, days: int) -> None:
    """Seeds 90 days of continuous Measurement time-series health records."""
    existing = session.exec(
        select(Measurement).where(
            Measurement.user_id == user.id, Measurement.source == "dev_seed"
        )
    ).first()
    if existing:
        print("  [6/10] Measurements: Time-series measurements exist (skip)")
        return

    now = datetime.now(timezone.utc)
    measurements: list[Measurement] = []

    weight = 81.5
    for d in range(days, 0, -1):
        dt_day = now - timedelta(days=d)
        morning_ts = dt_day.replace(hour=7, minute=30, second=0, microsecond=0)

        # Weight: gradual trend downward from 81.5 to ~77.5
        weight += random.uniform(-0.15, 0.08)
        weight = max(76.0, min(83.0, weight))
        measurements.append(
            Measurement(
                id=uuid7_str(),
                user_id=user.id,
                metric_code="weight",
                source_data_type="weight",
                source="dev_seed",
                value_numeric=round(weight, 1),
                start_time=morning_ts,
            )
        )

        # Steps: 6000-15000 range
        steps = int(random.gauss(10500, 2200))
        steps = max(3500, min(18000, steps))
        measurements.append(
            Measurement(
                id=uuid7_str(),
                user_id=user.id,
                metric_code="steps",
                source_data_type="steps",
                source="dev_seed",
                value_numeric=float(steps),
                start_time=morning_ts.replace(hour=21, minute=30),
            )
        )

        # Resting Heart Rate
        rhr = 60.0 + 4.0 * math.sin(d / 7.0) + random.gauss(0, 1.5)
        measurements.append(
            Measurement(
                id=uuid7_str(),
                user_id=user.id,
                metric_code="heart_rate",
                source_data_type="heart_rate",
                source="dev_seed",
                value_numeric=round(rhr, 1),
                start_time=morning_ts,
            )
        )

        # HRV (RMSSD)
        hrv = 55.0 + random.gauss(0, 7.0)
        measurements.append(
            Measurement(
                id=uuid7_str(),
                user_id=user.id,
                metric_code="hrv",
                source_data_type="hrv",
                source="dev_seed",
                value_numeric=round(max(25.0, min(95.0, hrv)), 1),
                start_time=morning_ts,
            )
        )

        # Sleep JSON
        sleep_hours = 7.6 + random.gauss(0, 0.5)
        sleep_hours = max(5.5, min(9.2, sleep_hours))
        total_sec = int(sleep_hours * 3600)
        deep_sec = int(total_sec * random.uniform(0.20, 0.26))
        rem_sec = int(total_sec * random.uniform(0.20, 0.25))
        awake_sec = int(total_sec * random.uniform(0.02, 0.06))
        light_sec = total_sec - deep_sec - rem_sec - awake_sec

        measurements.append(
            Measurement(
                id=uuid7_str(),
                user_id=user.id,
                metric_code="sleep",
                source_data_type="sleep",
                source="dev_seed",
                start_time=morning_ts - timedelta(hours=8),
                end_time=morning_ts,
                value_json=json.dumps({
                    "duration_seconds": total_sec,
                    "stages": [
                        {"stage": "4", "duration_seconds": light_sec},
                        {"stage": "5", "duration_seconds": deep_sec},
                        {"stage": "6", "duration_seconds": rem_sec},
                        {"stage": "1", "duration_seconds": awake_sec},
                    ],
                }),
            )
        )

        # Nutrition summary (every day)
        kcal = int(random.uniform(2200, 2600))
        pro = int(kcal * 0.28 / 4)
        carbs = int(kcal * 0.45 / 4)
        fat = int(kcal * 0.27 / 9)
        measurements.append(
            Measurement(
                id=uuid7_str(),
                user_id=user.id,
                metric_code="nutrition",
                source_data_type="nutrition",
                source="dev_seed",
                start_time=morning_ts.replace(hour=20, minute=0),
                value_json=json.dumps({
                    "calories": kcal,
                    "protein_grams": pro,
                    "carbs_grams": carbs,
                    "fat_grams": fat,
                }),
            )
        )

    for i in range(0, len(measurements), 300):
        session.add_all(measurements[i : i + 300])
    session.commit()
    print(
        f"  [6/10] Measurements: {len(measurements)} entries seeded ({days} days time-series)"
    )


def seed_habits_and_logs(session: Session, user: User, days: int) -> None:
    """Seeds Habit and historical HabitLog records with realistic completion streaks."""
    existing_habits = session.exec(
        select(Habit).where(Habit.user_id == user.id)
    ).all()
    if existing_habits:
        print(f"  [7/10] Habits: {len(existing_habits)} habits present (skip)")
        return

    habits_data = [
        ("10.000 Schritte gehen", "Tägliche Mindestbewegung für Herzkreislauf", "#10b981", "directions-walk"),
        ("3 Liter Wasser trinken", "Optimale Hydration über den Tag verteilt", "#3b82f6", "water-drop"),
        ("15 Min Stretching", "Mobilität nach dem Training & Büroarbeit", "#8b5cf6", "self-improvement"),
        ("Kein Zucker nach 20 Uhr", "Regenerativer Schlaf & Blutzuckerkontrolle", "#f59e0b", "no-food"),
    ]

    habit_objs: list[Habit] = []
    for name, desc, color, icon in habits_data:
        h = Habit(
            id=uuid7_str(),
            user_id=user.id,
            name=name,
            description=desc,
            color=color,
            icon=icon,
            frequency=HabitFrequency.DAILY,
            target_count=1,
        )
        session.add(h)
        session.flush()
        habit_objs.append(h)

    today = date.today()
    logs_seeded = 0
    for h in habit_objs:
        # High completion rate ~85% for realistic streak visualization
        for d in range(days):
            if random.random() < 0.85:
                log_date = today - timedelta(days=d)
                session.add(
                    HabitLog(
                        id=uuid7_str(),
                        habit_id=h.id,
                        user_id=user.id,
                        log_date=log_date,
                        completed=True,
                        completed_at=datetime.combine(log_date, datetime.min.time(), tzinfo=timezone.utc),
                    )
                )
                logs_seeded += 1

    session.commit()
    print(
        f"  [7/10] Habits: {len(habit_objs)} habits ({logs_seeded} completed logs) seeded"
    )


def seed_goals(session: Session, user: User) -> None:
    """Seeds active Goal targets."""
    existing_goals = session.exec(
        select(Goal).where(Goal.user_id == user.id)
    ).all()
    if existing_goals:
        print(f"  [8/10] Goals: {len(existing_goals)} goals present (skip)")
        return

    goals = [
        Goal(
            id=uuid7_str(),
            user_id=user.id,
            metric_code="steps",
            target_value=10000.0,
            direction=GoalDirection.INCREASE,
            frequency=GoalFrequency.DAILY,
            is_active=True,
        ),
        Goal(
            id=uuid7_str(),
            user_id=user.id,
            metric_code="weight",
            target_value=76.0,
            direction=GoalDirection.DECREASE,
            frequency=GoalFrequency.ONCE,
            is_active=True,
        ),
        Goal(
            id=uuid7_str(),
            user_id=user.id,
            metric_code="sleep",
            target_value=8.0,
            direction=GoalDirection.INCREASE,
            frequency=GoalFrequency.DAILY,
            is_active=True,
        ),
    ]
    for g in goals:
        session.add(g)
    session.commit()
    print(f"  [8/10] Goals: {len(goals)} active goals seeded")


def seed_medications(session: Session, user: User, days: int) -> None:
    """Seeds Medication, Schedule, Inventory, and MedicationLog entries."""
    existing_meds = session.exec(
        select(Medication).where(Medication.user_id == user.id)
    ).all()
    if existing_meds:
        print(f"  [9/10] Medications: {len(existing_meds)} medications present (skip)")
        return

    med = Medication(
        id=uuid7_str(),
        user_id=user.id,
        name="Creatin Monohydrat",
        active_ingredient="Creatine Pyruvate",
        strength="5000 mg",
        form=MedicationForm.TABLET,
        instructions="Täglich morgens mit reichlich Wasser einnehmen.",
        color_hex="#4f46e5",
        icon="medication",
        is_active=True,
    )
    session.add(med)
    session.flush()

    today = date.today()
    sched = MedicationSchedule(
        id=uuid7_str(),
        medication_id=med.id,
        user_id=user.id,
        dosage="1 Tabletten (5g)",
        times=["08:00"],
        start_date=today - timedelta(days=days),
    )
    session.add(sched)
    session.flush()

    inv = MedicationInventory(
        id=uuid7_str(),
        medication_id=med.id,
        user_id=user.id,
        initial_count=200,
        remaining_count=110,
        refill_at_count=30,
    )
    session.add(inv)

    logs_seeded = 0
    for d in range(days):
        log_date = today - timedelta(days=d)
        dt_taken = datetime.combine(log_date, datetime.min.time().replace(hour=8, minute=15), tzinfo=timezone.utc)
        session.add(
            MedicationLog(
                id=uuid7_str(),
                medication_id=med.id,
                user_id=user.id,
                schedule_id=sched.id,
                taken_at=dt_taken,
                dosage_taken="5g",
                skipped=False,
            )
        )
        logs_seeded += 1

    session.commit()
    print(f"  [9/10] Medications: 1 supplement schedule ({logs_seeded} logs) seeded")


def seed_mood_and_journal(session: Session, user: User, days: int) -> None:
    """Seeds MoodEntry and JournalEntry logs."""
    existing_moods = session.exec(
        select(MoodEntry).where(MoodEntry.user_id == user.id)
    ).all()
    if existing_moods:
        print(f"  [10/10] Mood & Journal: {len(existing_moods)} entries present (skip)")
        return

    today = date.today()
    mood_count = 0
    journal_count = 0

    for d in range(days):
        log_date = today - timedelta(days=d)

        # Daily Mood Entry
        score = random.randint(6, 9)
        energy = random.randint(6, 9)
        stress = random.randint(2, 5)
        session.add(
            MoodEntry(
                id=uuid7_str(),
                user_id=user.id,
                entry_date=log_date,
                mood_score=score,
                energy_level=energy,
                stress_level=stress,
                tag_codes="happy,energetic,productive",
                notes="Guter Tag, Training lief sehr gut." if d % 3 == 0 else None,
            )
        )
        mood_count += 1

        # Weekly Journal Entry
        if d % 7 == 0:
            session.add(
                JournalEntry(
                    id=uuid7_str(),
                    user_id=user.id,
                    entry_date=log_date,
                    title=f"Wochen-Reflektion (Woche {int(d / 7) + 1})",
                    content="Erfolgreiche Trainingswoche. Schlaf war konsistent gut und die Regeneration fühlt sich optimal an.",
                    mood_score=score,
                    is_private=True,
                )
            )
            journal_count += 1

    session.commit()
    print(
        f"  [10/10] Mood & Journal: {mood_count} mood logs, {journal_count} weekly journal entries seeded"
    )


def ensure_database_initialized() -> None:
    """Ensures all SQLModel tables and Alembic stamps are initialized on fresh DBs."""
    import salus.models.achievement  # noqa: F401
    import salus.models.analytics  # noqa: F401
    import salus.models.api_token  # noqa: F401
    import salus.models.asymmetric_share  # noqa: F401
    import salus.models.circadian  # noqa: F401
    import salus.models.dashboard  # noqa: F401
    import salus.models.food  # noqa: F401
    import salus.models.goal  # noqa: F401
    import salus.models.habit  # noqa: F401
    import salus.models.insight  # noqa: F401
    import salus.models.journal  # noqa: F401
    import salus.models.measurement  # noqa: F401
    import salus.models.medication  # noqa: F401
    import salus.models.metric_definition  # noqa: F401
    import salus.models.metric_preference  # noqa: F401
    import salus.models.mood  # noqa: F401
    import salus.models.notification  # noqa: F401
    import salus.models.sharing  # noqa: F401
    import salus.models.system_config  # noqa: F401
    import salus.models.user  # noqa: F401
    import salus.models.user_identity  # noqa: F401
    import salus.models.workout  # noqa: F401
    from salus.database import engine
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)

    try:
        from alembic import command
        from alembic.config import Config

        alembic_cfg = Config("alembic.ini")
        command.stamp(alembic_cfg, "head")
    except Exception:
        pass


# ── MAIN ORCHESTRATOR ───────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Comprehensive development seed orchestrator for Salus."
    )
    parser.add_argument(
        "username",
        nargs="?",
        default="Fleischerinho",
        help="Target dev username (default: Fleischerinho)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Days of historical data to generate (default: 90)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate seeding logic without committing DB changes",
    )
    args = parser.parse_args()

    random.seed(RANDOM_SEED)

    print(
        f"🚀 Seeding Salus database for user '{args.username}' ({args.days} days history)..."
    )
    if args.dry_run:
        print("⚠️ DRY RUN MODE: No database commits will be performed.")

    ensure_database_initialized()
    session = next(get_session())
    try:
        catalogs = seed_system_catalogs(session)
        user = seed_user_and_identity(session, args.username)
        seed_dashboard(session, user.id)
        seed_workout_plans_and_history(session, user, catalogs["exercises"], args.days)
        seed_food_and_nutrition(session, user, catalogs["foods"], args.days)
        seed_health_measurements(session, user, args.days)
        seed_habits_and_logs(session, user, args.days)
        seed_goals(session, user)
        seed_medications(session, user, args.days)
        seed_mood_and_journal(session, user, args.days)

        if args.dry_run:
            session.rollback()
            print("\n✅ Dry run completed cleanly.")
        else:
            print("\n✅ Database seeding completed successfully!")
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error during database seeding: {e}")
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    main()
