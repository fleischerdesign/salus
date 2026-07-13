import pytest
from datetime import datetime, timezone, timedelta

from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from salus.models.workout import Exercise
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


# ---------------------------------------------------------------------------
# Service-level (business logic) tests — kept as-is
# ---------------------------------------------------------------------------


def test_exercise_catalog_and_creation(session: Session, workout_services):
    uow, _, workout_svc = workout_services

    with uow:
        user = UserModel(username="testuser", password_hash="hash")
        uow.users.add(user)
        uow.commit()
        user_id = user.id

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

    catalog = workout_svc.get_exercise_catalog(user_id=user_id)
    assert len(catalog) >= 1
    assert any(e.name == "Deficit Deadlift" for e in catalog)

    with pytest.raises(ValueError):
        workout_svc.create_exercise(user_id=user_id, data=custom_ex)


def test_plan_crud_and_autoregulated_targets(session: Session, workout_services):
    uow, autoreg_svc, workout_svc = workout_services

    with uow:
        user = UserModel(username="lifter", password_hash="hash")
        uow.users.add(user)
        uow.commit()
        user_id = user.id

        squat = Exercise(
            name="Squats",
            equipment="barbell",
            primary_muscles="quadriceps,gluteus_maximus",
            secondary_muscles="hamstrings",
            suggested_rest_seconds=120,
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

    plan_data = WorkoutPlanCreate(
        name="Push & Legs Day",
        description="Heavy compounds",
        autoreg_mode="advisory",
        exercises=[
            WorkoutPlanExerciseCreate(exercise_id=squat_id, sequence=0, target_sets=3, target_reps=8, target_rpe=8.0, rest_seconds=180),
            WorkoutPlanExerciseCreate(exercise_id=bench_id, sequence=1, target_sets=3, target_reps=8, target_rpe=7.5, is_autoreg_exempt=True),
        ]
    )
    plan = workout_svc.create_plan(user_id=user_id, data=plan_data)
    assert plan.id is not None
    assert len(plan.plan_exercises) == 2

    targets = workout_svc.get_session_targets(user_id=user_id, plan_id=plan.id)
    squat_target = next(t for t in targets if t["exercise_id"] == squat_id)
    bench_target = next(t for t in targets if t["exercise_id"] == bench_id)

    assert squat_target["suggested_sets"] == 3
    assert squat_target["weight_multiplier"] == 1.0
    assert squat_target["rest_seconds"] == 180
    assert bench_target["weight_multiplier"] == 1.0
    assert bench_target["is_autoreg_exempt"] is True
    assert bench_target["rest_seconds"] == 90

    now = datetime.now(timezone.utc)
    with uow:
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
    assert sleep_score < 50.0

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

    session_obj = workout_svc.start_session(user_id=user_id)
    assert session_obj.id is not None
    assert session_obj.completed_at is None

    workout_svc.log_set(user_id=user_id, session_id=session_obj.id, entry=WorkoutLogEntryCreate(
        exercise_id=ex_id, set_number=1, weight=14.0, reps=10, rpe=8.5
    ))
    workout_svc.log_set(user_id=user_id, session_id=session_obj.id, entry=WorkoutLogEntryCreate(
        exercise_id=ex_id, set_number=2, weight=14.0, reps=10, rpe=9.0
    ))

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

    sess1 = workout_svc.start_session(user_id=user_id)
    workout_svc.log_set(user_id=user_id, session_id=sess1.id, entry=WorkoutLogEntryCreate(
        exercise_id=ex_id, set_number=1, weight=50.0, reps=5, rpe=8.0
    ))
    workout_svc.complete_session(user_id=user_id, session_id=sess1.id)

    prs = workout_svc.uow.workout_sessions.get_personal_records(user_id, [ex_id])
    assert prs[ex_id]["max_weight"] == 50.0
    assert prs[ex_id]["max_est_1rm"] > 56.0

    sess2 = workout_svc.start_session(user_id=user_id)
    logged = workout_svc.log_set(user_id=user_id, session_id=sess2.id, entry=WorkoutLogEntryCreate(
        exercise_id=ex_id, set_number=1, weight=55.0, reps=5, rpe=9.0
    ))
    assert logged.id is not None

    with uow:
        assert len(sess2.logs) == 1

    workout_svc.delete_logged_set(user_id=user_id, session_id=sess2.id, exercise_id=ex_id, set_number=1)

    with uow:
        sess2_fresh = uow.workout_sessions.get_by_id(sess2.id)
        assert sess2_fresh is not None
        assert len(sess2_fresh.logs) == 0


def test_plan_conflict_resolution(session, workout_services):
    from salus.exceptions import ConflictError

    uow, _, workout_svc = workout_services

    with uow:
        user = UserModel(username="lww_lifter", password_hash="hash")
        uow.users.add(user)
        uow.commit()
        user_id = user.id

    plan_data = WorkoutPlanCreate(
        name="LWW Plan",
        description="Initial",
        autoreg_mode="disabled",
        exercises=[]
    )
    plan = workout_svc.create_plan(user_id=user_id, data=plan_data)
    plan_id = plan.id

    future_time = datetime.now(timezone.utc) + timedelta(minutes=5)
    plan_data.name = "Updated Name"
    updated_plan = workout_svc.update_plan(
        user_id=user_id,
        plan_id=plan_id,
        data=plan_data,
        client_updated_at=future_time
    )
    assert updated_plan.name == "Updated Name"

    past_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    plan_data.name = "Stale Update"
    with pytest.raises(ConflictError):
        workout_svc.update_plan(
            user_id=user_id,
            plan_id=plan_id,
            data=plan_data,
            client_updated_at=past_time
        )


# ---------------------------------------------------------------------------
# JSON API integration tests
# ---------------------------------------------------------------------------


def test_active_session_returns_logged_sets(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import Exercise

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        alice = db.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None

        ex = Exercise(name="Curls", equipment="dumbbell", primary_muscles="biceps")
        db.add(ex)
        db.commit()
        ex_id = ex.id

    resp = authenticated_client.post("/api/v1/workouts/sessions/start")
    assert resp.status_code == 200
    session_data = resp.json()
    session_id = session_data["id"]

    log_resp = authenticated_client.post(
        f"/api/v1/workouts/sessions/log?session_id={session_id}",
        json={"exercise_id": ex_id, "set_number": 1, "weight": 15.0, "reps": 8, "rpe": 8.0},
    )
    assert log_resp.status_code == 200

    active = authenticated_client.get("/api/v1/workouts/sessions/active")
    assert active.status_code == 200
    body = active.json()
    assert body is not None
    assert body["id"] == session_id
    assert len(body["logs"]) == 1
    assert body["logs"][0]["exercise_id"] == ex_id
    assert body["logs"][0]["weight"] == 15.0
    assert body["logs"][0]["reps"] == 8


def test_recent_sessions_includes_completed(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import Exercise, WorkoutPlan, WorkoutPlanExercise

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        alice = db.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None

        ex = Exercise(name="Curls", equipment="dumbbell", primary_muscles="biceps")
        db.add(ex)
        db.commit()
        ex_id = ex.id

        plan = WorkoutPlan(name="Test Plan A", user_id=alice.id, autoreg_mode="disabled")
        db.add(plan)
        db.commit()
        plan_id = plan.id

        plan_ex = WorkoutPlanExercise(plan_id=plan_id, exercise_id=ex_id, sequence=0, target_sets=3, target_reps=8, target_rpe=8.0)
        db.add(plan_ex)
        db.commit()

    start_resp = authenticated_client.post(f"/api/v1/workouts/sessions/start?plan_id={plan_id}")
    assert start_resp.status_code == 200
    session_id = start_resp.json()["id"]

    log_resp = authenticated_client.post(
        f"/api/v1/workouts/sessions/log?session_id={session_id}",
        json={"exercise_id": ex_id, "set_number": 1, "weight": 12.5, "reps": 10, "rpe": 8.0},
    )
    assert log_resp.status_code == 200

    complete_resp = authenticated_client.post(
        f"/api/v1/workouts/sessions/complete?session_id={session_id}&notes=Felt%20great%21"
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["notes"] == "Felt great!"

    recent = authenticated_client.get("/api/v1/workouts/sessions/recent")
    assert recent.status_code == 200
    sessions = recent.json()
    assert len(sessions) >= 1
    sess = next(s for s in sessions if s["id"] == session_id)
    assert sess["notes"] == "Felt great!"
    assert len(sess["logs"]) == 1
    assert sess["logs"][0]["exercise"]["name"] == "Curls"
    assert sess["logs"][0]["weight"] == 12.5
    assert sess["logs"][0]["reps"] == 10


def test_list_exercises_includes_created(authenticated_client):
    from sqlmodel import Session
    from salus.models.workout import Exercise

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        ex = Exercise(
            name="Deadlifts",
            equipment="barbell",
            primary_muscles="hamstrings,gluteus_maximus",
            instructions="Lift it up.",
        )
        db.add(ex)
        db.commit()
        ex_id = ex.id

    response = authenticated_client.get("/api/v1/workouts/exercises")
    assert response.status_code == 200
    exercises = response.json()
    deadlift = next(e for e in exercises if e["id"] == ex_id)
    assert deadlift["name"] == "Deadlifts"
    assert deadlift["equipment"] == "barbell"
    assert deadlift["instructions"] == "Lift it up."
    assert "hamstrings" in deadlift["primary_muscles"]


def test_get_plan_returns_plan(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import WorkoutPlan

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        alice = db.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None

        plan = WorkoutPlan(
            name="Hypertrophy Phase 1",
            description="High volume muscle building.",
            autoreg_mode="recovery_based",
            user_id=alice.id,
        )
        db.add(plan)
        db.commit()
        plan_id = plan.id

    response = authenticated_client.get(f"/api/v1/workouts/plans/{plan_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Hypertrophy Phase 1"
    assert body["description"] == "High volume muscle building."
    assert body["autoreg_mode"] == "recovery_based"


def test_create_exercise_via_api(authenticated_client):
    data = {
        "name": "API Curls",
        "equipment": "dumbbell",
        "primary_muscles": "biceps_brachii",
        "secondary_muscles": "brachialis",
        "description": "Created via JSON API.",
        "instructions": "Curl with control.",
    }
    resp = authenticated_client.post("/api/v1/workouts/exercises", json=data)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] is not None
    assert body["name"] == "API Curls"

    duplicate = authenticated_client.post("/api/v1/workouts/exercises", json=data)
    assert duplicate.status_code == 400


def test_delete_exercise_via_api(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import Exercise

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        alice = db.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None

        ex = Exercise(name="To Delete", equipment="bodyweight", primary_muscles="abs", user_id=alice.id)
        db.add(ex)
        db.commit()
        ex_id = ex.id

    resp = authenticated_client.delete(f"/api/v1/workouts/exercises/{ex_id}")
    assert resp.status_code == 204

    check = authenticated_client.get("/api/v1/workouts/exercises")
    assert not any(e["id"] == ex_id for e in check.json())


def test_create_plan_via_api(authenticated_client):
    from sqlmodel import Session
    from salus.models.workout import Exercise

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        ex = Exercise(name="Squat API", equipment="barbell", primary_muscles="quadriceps")
        db.add(ex)
        db.commit()
        ex_id = ex.id

    data = {
        "name": "API Plan",
        "description": "Created via JSON.",
        "autoreg_mode": "advisory",
        "exercises": [
            {"exercise_id": ex_id, "sequence": 0, "target_sets": 3, "target_reps": 5, "target_rpe": 8.5}
        ],
    }
    resp = authenticated_client.post("/api/v1/workouts/plans", json=data)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] is not None
    assert body["name"] == "API Plan"
    assert len(body["plan_exercises"]) == 1
    assert body["plan_exercises"][0]["exercise_id"] == ex_id


def test_delete_plan_via_api(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import WorkoutPlan

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        alice = db.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None

        plan = WorkoutPlan(name="To Remove", user_id=alice.id, autoreg_mode="disabled")
        db.add(plan)
        db.commit()
        plan_id = plan.id

    resp = authenticated_client.delete(f"/api/v1/workouts/plans/{plan_id}")
    assert resp.status_code == 204

    with Session(engine) as db:
        deleted = db.get(WorkoutPlan, plan_id)
        assert deleted is not None
        assert deleted.deleted_at is not None


def test_start_and_complete_session_via_api(authenticated_client):
    resp = authenticated_client.post("/api/v1/workouts/sessions/start")
    assert resp.status_code == 200
    session_id = resp.json()["id"]
    assert resp.json()["completed_at"] is None

    complete = authenticated_client.post(f"/api/v1/workouts/sessions/complete?session_id={session_id}&notes=Done.")
    assert complete.status_code == 200
    assert complete.json()["completed_at"] is not None
    assert complete.json()["notes"] == "Done."


def test_log_and_delete_set_via_api(authenticated_client):
    from sqlmodel import Session
    from salus.models.workout import Exercise

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        ex = Exercise(name="Press", equipment="barbell", primary_muscles="shoulders")
        db.add(ex)
        db.commit()
        ex_id = ex.id

    start = authenticated_client.post("/api/v1/workouts/sessions/start")
    session_id = start.json()["id"]

    log = authenticated_client.post(
        f"/api/v1/workouts/sessions/log?session_id={session_id}",
        json={"exercise_id": ex_id, "set_number": 1, "weight": 40.0, "reps": 8, "rpe": 7.5},
    )
    assert log.status_code == 200
    assert log.json()["weight"] == 40.0

    delete_resp = authenticated_client.delete(
        f"/api/v1/workouts/sessions/log?session_id={session_id}&exercise_id={ex_id}&set_number=1"
    )
    assert delete_resp.status_code == 204

    active = authenticated_client.get("/api/v1/workouts/sessions/active")
    assert len(active.json()["logs"]) == 0


def test_list_plans_via_api(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import WorkoutPlan

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        alice = db.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None

        plan = WorkoutPlan(name="List Test", user_id=alice.id, autoreg_mode="disabled")
        db.add(plan)
        db.commit()
        plan_id = plan.id

    resp = authenticated_client.get("/api/v1/workouts/plans")
    assert resp.status_code == 200
    plans = resp.json()
    assert any(p["id"] == plan_id for p in plans)
    plan_data = next(p for p in plans if p["id"] == plan_id)
    assert plan_data["name"] == "List Test"


def test_get_plan_targets_returns_targets(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import Exercise, WorkoutPlan, WorkoutPlanExercise

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        alice = db.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None
        user_id = alice.id

        ex = Exercise(name="Targeted Curls", equipment="dumbbell", primary_muscles="biceps")
        db.add(ex)
        db.commit()
        ex_id = ex.id

        plan = WorkoutPlan(name="Targets Plan", user_id=user_id, autoreg_mode="advisory")
        db.add(plan)
        db.commit()
        plan_id = plan.id

        plan_ex = WorkoutPlanExercise(
            plan_id=plan_id, exercise_id=ex_id, sequence=0,
            target_sets=4, target_reps=10, target_rpe=8.0,
        )
        db.add(plan_ex)
        db.commit()

    resp = authenticated_client.get(f"/api/v1/workouts/plans/{plan_id}/targets")
    assert resp.status_code == 200
    targets = resp.json()
    assert isinstance(targets, list)
    assert any(t["exercise_id"] == ex_id for t in targets)
    target = next(t for t in targets if t["exercise_id"] == ex_id)
    assert target["suggested_sets"] == 4
