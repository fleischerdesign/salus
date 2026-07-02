import pytest
from datetime import datetime, timezone, timedelta
from sqlmodel import Session

from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from salus.models.workout import Exercise, WorkoutPlan, WorkoutSession, WorkoutLogEntry
from salus.models.measurement import Measurement
from salus.models.user import User as UserModel
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.services.workout.autoregulation import AutoregulationService
from salus.services.workout.planner import WorkoutService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.activity import ActivityAnalysisService
from salus.schemas.workout import ExerciseCreate, WorkoutPlanCreate, WorkoutPlanExerciseCreate, WorkoutLogEntryCreate


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def workout_services(session: Session):
    uow = SqlUnitOfWork(session)
    sleep_svc = SleepAnalysisService(uow.measurements)
    activity_svc = ActivityAnalysisService(uow.measurements)
    autoreg_svc = AutoregulationService(sleep_svc, activity_svc)
    workout_svc = WorkoutService(uow, autoreg_svc)
    return uow, autoreg_svc, workout_svc


def test_exercise_catalog_and_creation(session: Session, workout_services):
    uow, _, workout_svc = workout_services

    with uow:
        user = UserModel(username="testuser", password_hash="hash")
        uow.users.add(user)
        uow.commit()
        user_id = user.id

    # 1. Create a custom exercise
    custom_ex = ExerciseCreate(
        name="Deficit Deadlift",
        equipment="barbell",
        primary_muscles="hamstrings,gluteus_maximus",
        secondary_muscles="erector_spinae",
        description="Deadlift standing on a plate.",
    )
    ex = workout_svc.create_exercise(user_id=user_id, data=custom_ex)
    assert ex.id is not None
    assert ex.user_id == user_id

    # 2. Get exercise catalog (should return custom exercise)
    catalog = workout_svc.get_exercise_catalog(user_id=user_id)
    assert len(catalog) >= 1
    assert any(e.name == "Deficit Deadlift" for e in catalog)

    # 3. Prevent duplicate names
    with pytest.raises(ValueError):
        workout_svc.create_exercise(user_id=user_id, data=custom_ex)


def test_plan_crud_and_autoregulated_targets(session: Session, workout_services):
    uow, autoreg_svc, workout_svc = workout_services

    with uow:
        # Create user
        user = UserModel(username="lifter", password_hash="hash")
        uow.users.add(user)
        uow.commit()
        user_id = user.id

        # Seed 2 system-like exercises
        squat = Exercise(
            name="Squats",
            equipment="barbell",
            primary_muscles="quadriceps,gluteus_maximus",
            secondary_muscles="hamstrings",
        )
        bench = Exercise(
            name="Bench Press",
            equipment="barbell",
            primary_muscles="pectoralis_major",
            secondary_muscles="triceps_brachii,anterior_deltoid",
        )
        uow.exercises.add(squat)
        uow.exercises.add(bench)
        uow.commit()
        squat_id = squat.id
        bench_id = bench.id

    # Create plan
    plan_data = WorkoutPlanCreate(
        name="Push & Legs Day",
        description="Heavy compounds",
        autoreg_mode="advisory",
        exercises=[
            WorkoutPlanExerciseCreate(exercise_id=squat_id, sequence=0, target_sets=3, target_reps=8, target_rpe=8.0),
            WorkoutPlanExerciseCreate(exercise_id=bench_id, sequence=1, target_sets=3, target_reps=8, target_rpe=7.5, is_autoreg_exempt=True),
        ]
    )
    plan = workout_svc.create_plan(user_id=user_id, data=plan_data)
    assert plan.id is not None
    assert len(plan.plan_exercises) == 2

    # 1. Base recovery case: No data (should default to standard recovery)
    targets = workout_svc.get_session_targets(user_id=user_id, plan_id=plan.id)
    squat_target = next(t for t in targets if t["exercise_id"] == squat_id)
    bench_target = next(t for t in targets if t["exercise_id"] == bench_id)

    assert squat_target["suggested_sets"] == 3
    assert squat_target["weight_multiplier"] == 1.0  # standard
    assert bench_target["weight_multiplier"] == 1.0
    assert bench_target["is_autoreg_exempt"] is True

    # 2. Seed severe fatigue last night (deficit sleep)
    # Average sleep = 8 hours, last night = 4 hours
    now = datetime.now(timezone.utc)
    with uow:
        # Seed 6 days of 8 hours sleep
        for i in range(1, 7):
            m = Measurement(
                user_id=user_id,
                data_type="sleep",
                value_numeric=8.0 * 3600,
                value_json='{"duration_seconds": 28800, "stages": []}',
                start_time=now - timedelta(days=i),
                source="fitbit",
                external_id=f"sleep-base-{i}"
            )
            uow.measurements.add(m)
        # Last night = 4 hours
        m_last = Measurement(
            user_id=user_id,
            data_type="sleep",
            value_numeric=4.0 * 3600,
            value_json='{"duration_seconds": 14400, "stages": []}',
            start_time=now,
            source="fitbit",
            external_id="sleep-last-night"
        )
        uow.measurements.add(m_last)
        uow.commit()

    score, sleep_score, _, _ = autoreg_svc.calculate_recovery_score(user_id)
    assert sleep_score < 50.0  # sleep score should be heavily penalized

    # Query targets again - should suggest deload for Squats (non-exempt), but Bench remains 1.0 (exempted!)
    targets_fatigued = workout_svc.get_session_targets(user_id=user_id, plan_id=plan.id)
    squat_fatigued = next(t for t in targets_fatigued if t["exercise_id"] == squat_id)
    bench_fatigued = next(t for t in targets_fatigued if t["exercise_id"] == bench_id)

    assert squat_fatigued["suggested_sets"] < 3
    assert squat_fatigued["weight_multiplier"] < 1.0
    assert bench_fatigued["weight_multiplier"] == 1.0
    assert bench_fatigued["is_autoreg_exempt"] is True


def test_session_starting_and_logging(session: Session, workout_services):
    uow, _, workout_svc = workout_services

    with uow:
        user = UserModel(username="gymbro", password_hash="hash")
        uow.users.add(user)
        uow.commit()
        user_id = user.id

        ex = Exercise(name="Curls", equipment="dumbbell", primary_muscles="biceps")
        uow.exercises.add(ex)
        uow.commit()
        ex_id = ex.id

    # Start session
    session_obj = workout_svc.start_session(user_id=user_id)
    assert session_obj.id is not None
    assert session_obj.completed_at is None

    # Log sets
    workout_svc.log_set(user_id=user_id, session_id=session_obj.id, entry=WorkoutLogEntryCreate(
        exercise_id=ex_id, set_number=1, weight=14.0, reps=10, rpe=8.5
    ))
    workout_svc.log_set(user_id=user_id, session_id=session_obj.id, entry=WorkoutLogEntryCreate(
        exercise_id=ex_id, set_number=2, weight=14.0, reps=10, rpe=9.0
    ))

    # Complete session
    completed = workout_svc.complete_session(user_id=user_id, session_id=session_obj.id, notes="Felt a good pump.")
    assert completed.completed_at is not None
    assert completed.notes == "Felt a good pump."
    assert len(completed.logs) == 2
