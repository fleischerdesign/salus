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


def test_personal_records_and_unlogging(session: Session, workout_services):
    uow, _, workout_svc = workout_services

    with uow:
        user = UserModel(username="pr_guy", password_hash="hash")
        uow.users.add(user)
        uow.commit()
        user_id = user.id

        ex = Exercise(name="Overhead Press", equipment="barbell", primary_muscles="shoulders")
        uow.exercises.add(ex)
        uow.commit()
        ex_id = ex.id

    # 1. Start and complete a session to establish historical records
    sess1 = workout_svc.start_session(user_id=user_id)
    workout_svc.log_set(user_id=user_id, session_id=sess1.id, entry=WorkoutLogEntryCreate(
        exercise_id=ex_id, set_number=1, weight=50.0, reps=5, rpe=8.0
    ))
    workout_svc.complete_session(user_id=user_id, session_id=sess1.id)

    # Calculate Est 1RM: 50.0 / (1.0278 - (0.0278 * 5)) = 50.0 / 0.8888 = ~56.25
    prs = workout_svc.uow.workout_sessions.get_personal_records(user_id, [ex_id])
    assert prs[ex_id]["max_weight"] == 50.0
    assert prs[ex_id]["max_est_1rm"] > 56.0

    # 2. Start a new session and verify unlogging a set
    sess2 = workout_svc.start_session(user_id=user_id)
    logged = workout_svc.log_set(user_id=user_id, session_id=sess2.id, entry=WorkoutLogEntryCreate(
        exercise_id=ex_id, set_number=1, weight=55.0, reps=5, rpe=9.0
    ))
    assert logged.id is not None

    # Verify log entry is in the database
    with uow:
        assert len(sess2.logs) == 1

    # Unlog the set
    workout_svc.delete_logged_set(user_id=user_id, session_id=sess2.id, exercise_id=ex_id, set_number=1)
    
    # Verify it is deleted
    with uow:
        # Get fresh session from DB
        sess2_fresh = uow.workout_sessions.get_by_id(sess2.id)
        assert sess2_fresh is not None
        assert len(sess2_fresh.logs) == 0


def test_active_session_page_shows_logged_sets(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import Exercise
    from salus.services.workout.planner import WorkoutService
    from salus.services.workout.autoregulation import AutoregulationService
    from salus.services.analytics.sleep import SleepAnalysisService
    from salus.services.analytics.activity import ActivityAnalysisService
    from salus.repositories.unit_of_work import SqlUnitOfWork

    engine = authenticated_client.app.state.engine
    with Session(engine) as session:
        uow = SqlUnitOfWork(session)
        sleep_svc = SleepAnalysisService(uow.measurements)
        activity_svc = ActivityAnalysisService(uow.measurements)
        autoreg_svc = AutoregulationService(sleep_svc, activity_svc)
        workout_svc = WorkoutService(uow, autoreg_svc)

        alice = session.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None
        user_id = alice.id

        ex = Exercise(name="Curls", equipment="dumbbell", primary_muscles="biceps")
        session.add(ex)
        session.commit()
        ex_id = ex.id

        # Start session
        sess = workout_svc.start_session(user_id=user_id)

        # Log a set
        workout_svc.log_set(user_id=user_id, session_id=sess.id, entry=WorkoutLogEntryCreate(
            exercise_id=ex_id, set_number=1, weight=15.0, reps=8, rpe=8.0
        ))

    # Request active session page
    response = authenticated_client.get("/workouts/sessions/active")
    assert response.status_code == 200
    assert 'data-logged="true"' in response.text


def test_rpe10_prompt_presence(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import Exercise, WorkoutPlan, WorkoutPlanExercise
    from salus.services.workout.planner import WorkoutService
    from salus.services.workout.autoregulation import AutoregulationService
    from salus.services.analytics.sleep import SleepAnalysisService
    from salus.services.analytics.activity import ActivityAnalysisService
    from salus.repositories.unit_of_work import SqlUnitOfWork

    engine = authenticated_client.app.state.engine
    with Session(engine) as session:
        uow = SqlUnitOfWork(session)
        sleep_svc = SleepAnalysisService(uow.measurements)
        activity_svc = ActivityAnalysisService(uow.measurements)
        autoreg_svc = AutoregulationService(sleep_svc, activity_svc)
        workout_svc = WorkoutService(uow, autoreg_svc)

        alice = session.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None
        user_id = alice.id

        ex = Exercise(name="Curls", equipment="dumbbell", primary_muscles="biceps")
        session.add(ex)
        session.commit()
        ex_id = ex.id

        plan = WorkoutPlan(name="Test Plan", user_id=user_id, autoreg_mode="disabled")
        session.add(plan)
        session.commit()
        plan_id = plan.id

        plan_ex = WorkoutPlanExercise(plan_id=plan_id, exercise_id=ex_id, order=0, target_sets=3, target_reps=8, target_rpe=8.0)
        session.add(plan_ex)
        session.commit()

        # Start session
        workout_svc.start_session(user_id=user_id, plan_id=plan_id)

    response = authenticated_client.get("/workouts/sessions/active")
    assert response.status_code == 200
    assert 'id="rpe-prompt-' in response.text


def test_completed_session_detail_page(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import Exercise, WorkoutPlan, WorkoutPlanExercise
    from salus.services.workout.planner import WorkoutService
    from salus.services.workout.autoregulation import AutoregulationService
    from salus.services.analytics.sleep import SleepAnalysisService
    from salus.services.analytics.activity import ActivityAnalysisService
    from salus.repositories.unit_of_work import SqlUnitOfWork
    from salus.schemas.workout import WorkoutLogEntryCreate

    engine = authenticated_client.app.state.engine
    with Session(engine) as session:
        uow = SqlUnitOfWork(session)
        sleep_svc = SleepAnalysisService(uow.measurements)
        activity_svc = ActivityAnalysisService(uow.measurements)
        autoreg_svc = AutoregulationService(sleep_svc, activity_svc)
        workout_svc = WorkoutService(uow, autoreg_svc)

        alice = session.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None
        user_id = alice.id

        ex = Exercise(name="Curls", equipment="dumbbell", primary_muscles="biceps")
        session.add(ex)
        session.commit()
        ex_id = ex.id

        plan = WorkoutPlan(name="Test Plan A", user_id=user_id, autoreg_mode="disabled")
        session.add(plan)
        session.commit()
        plan_id = plan.id

        plan_ex = WorkoutPlanExercise(plan_id=plan_id, exercise_id=ex_id, order=0, target_sets=3, target_reps=8, target_rpe=8.0)
        session.add(plan_ex)
        session.commit()

        # Start, log set, and complete session
        sess = workout_svc.start_session(user_id=user_id, plan_id=plan_id)
        session_id = sess.id
        workout_svc.log_set(
            user_id=user_id,
            session_id=session_id,
            entry=WorkoutLogEntryCreate(exercise_id=ex_id, set_number=1, weight=12.5, reps=10, rpe=8.0)
        )
        workout_svc.complete_session(user_id=user_id, session_id=session_id, notes="Felt great!")

    response = authenticated_client.get(f"/workouts/sessions/{session_id}")
    assert response.status_code == 200
    assert "Test Plan A" in response.text
    assert "Curls" in response.text
    assert "Felt great!" in response.text
    assert "Biceps" in response.text
    assert "125 kg" in response.text  # 12.5 * 10 = 125 volume


def test_new_plan_modal_route(authenticated_client):
    response = authenticated_client.get("/workouts/plans/new")
    assert response.status_code == 200


def test_exercise_instructions_modal_route(authenticated_client):
    from sqlmodel import Session
    from salus.models.workout import Exercise

    engine = authenticated_client.app.state.engine
    with Session(engine) as session:
        ex = Exercise(
            name="Squats", 
            equipment="barbell", 
            primary_muscles="quadriceps", 
            instructions="Keep back straight."
        )
        session.add(ex)
        session.commit()
        ex_id = ex.id

    response = authenticated_client.get(f"/workouts/exercises/{ex_id}/instructions")
    assert response.status_code == 200
    assert "Squats" in response.text
    assert "Quadriceps" in response.text
    assert "Keep back straight." in response.text



