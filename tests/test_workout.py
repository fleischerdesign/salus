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
# Service-level (business logic) tests — writes via command handlers
# ---------------------------------------------------------------------------


def _make_user(uow, username: str = "testuser") -> UserModel:
    with uow:
        user = UserModel(username=username, password_hash="hash")
        uow.users.add(user)
        uow.commit()
        return user


def test_exercise_catalog_and_creation(session: Session, workout_services):
    uow, _, workout_svc = workout_services
    user = _make_user(uow, "testuser")
    from salus.schemas.sync import SyncOperation
    from salus.services.write_pipeline import WritePipeline

    pipeline = WritePipeline(uow, user)

    data = {
        "name": "Deficit Deadlift",
        "equipment": "barbell",
        "primary_muscles": "hamstrings,gluteus_maximus",
        "secondary_muscles": "erector_spinae",
        "description": "Deadlift standing on a plate.",
    }
    result = pipeline.process([SyncOperation(type="create", entity="exercise", data=data)])[0]
    assert result.status == "created"

    catalog = workout_svc.get_exercise_catalog(user_id=user.id)
    assert any(e.name == "Deficit Deadlift" for e in catalog)

    duplicate = pipeline.process([SyncOperation(type="create", entity="exercise", data=data)])[0]
    assert duplicate.status == "error"


def test_plan_crud_and_autoregulated_targets(session: Session, workout_services):
    uow, autoreg_svc, workout_svc = workout_services
    user = _make_user(uow, "lifter")
    from salus.services.commands.workout import CreateWorkoutHandler

    with uow:
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

    workout = CreateWorkoutHandler().execute(uow, user, {
        "name": "Push & Legs Day",
        "description": "Heavy compounds",
        "exercises": [
            {"exercise_id": squat_id, "sequence": 0, "target_sets": 3, "target_reps": 8, "target_rpe": 8.0, "rest_seconds": 180},
            {"exercise_id": bench_id, "sequence": 1, "target_sets": 3, "target_reps": 8, "target_rpe": 7.5, "is_autoreg_exempt": True},
        ],
    })
    assert workout.status == "created"
    workout_id = workout.id

    plan_obj = workout_svc.get_workout(user_id=user.id, workout_id=workout_id)
    assert len(plan_obj.exercises) == 2

    targets = workout_svc.get_session_targets(user_id=user.id, workout_id=workout_id)
    squat_target = next(t for t in targets if t["exercise_id"] == squat_id)
    bench_target = next(t for t in targets if t["exercise_id"] == bench_id)

    assert squat_target["suggested_sets"] == 4
    assert squat_target["weight_multiplier"] == 1.05
    assert squat_target["rest_seconds"] == 180
    assert bench_target["weight_multiplier"] == 1.0
    assert bench_target["is_autoreg_exempt"] is True
    assert bench_target["rest_seconds"] == 90

    now = datetime.now(timezone.utc)
    with uow:
        for i in range(1, 7):
            m = Measurement(
                user_id=user.id,
                source_data_type="sleep",
                value_numeric=8.0 * 3600,
                value_json='{"duration_seconds": 28800, "stages": []}',
                start_time=now - timedelta(days=i),
                source="fitbit",
                external_id=f"sleep-base-{i}"
            )
            uow.measurements.add(m)
        m_last = Measurement(
            user_id=user.id,
            source_data_type="sleep",
            value_numeric=4.0 * 3600,
            value_json='{"duration_seconds": 14400, "stages": []}',
            start_time=now,
            source="fitbit",
            external_id="sleep-last-night"
        )
        uow.measurements.add(m_last)
        uow.commit()

    score, sleep_score, _, _ = autoreg_svc.calculate_recovery_score(user.id)
    assert sleep_score < 50.0

    targets_fatigued = workout_svc.get_session_targets(user_id=user.id, workout_id=workout_id)
    squat_fatigued = next(t for t in targets_fatigued if t["exercise_id"] == squat_id)
    bench_fatigued = next(t for t in targets_fatigued if t["exercise_id"] == bench_id)

    assert squat_fatigued["suggested_sets"] < 3
    assert squat_fatigued["weight_multiplier"] < 1.0
    assert bench_fatigued["weight_multiplier"] == 1.0
    assert bench_fatigued["is_autoreg_exempt"] is True


def test_session_starting_and_logging(session: Session, workout_services):
    uow, _, workout_svc = workout_services
    user = _make_user(uow, "gymbro")
    from salus.services.commands.workout import (
        StartWorkoutHandler,
        LogSetHandler,
        CompleteWorkoutHandler,
    )

    with uow:
        ex = Exercise(name="Curls", equipment="dumbbell", primary_muscles="biceps")
        uow.exercises.add(ex)
        uow.commit()
        ex_id = ex.id

    started = StartWorkoutHandler().execute(uow, user, {})
    assert started.status == "created"
    session_id = started.id

    LogSetHandler().execute(uow, user, {
        "session_id": session_id, "exercise_id": ex_id, "set_number": 1,
        "weight": 14.0, "reps": 10, "rpe": 8.5,
    })
    LogSetHandler().execute(uow, user, {
        "session_id": session_id, "exercise_id": ex_id, "set_number": 2,
        "weight": 14.0, "reps": 10, "rpe": 9.0,
    })

    completed = CompleteWorkoutHandler().execute(uow, user, {
        "session_id": session_id, "notes": "Felt a good pump.",
    })
    assert completed.status == "updated"

    session_obj = workout_svc.get_session(user_id=user.id, session_id=session_id)
    assert session_obj.completed_at is not None
    assert session_obj.notes == "Felt a good pump."
    assert len(session_obj.sets) == 2


def test_personal_records_and_unlogging(session: Session, workout_services):
    uow, _, workout_svc = workout_services
    user = _make_user(uow, "pr_guy")
    from salus.services.commands.workout import (
        StartWorkoutHandler,
        LogSetHandler,
        CompleteWorkoutHandler,
        DeleteLogSetHandler,
    )

    with uow:
        ex = Exercise(name="Overhead Press", equipment="barbell", primary_muscles="shoulders")
        uow.exercises.add(ex)
        uow.commit()
        ex_id = ex.id

    sess1 = StartWorkoutHandler().execute(uow, user, {})
    LogSetHandler().execute(uow, user, {
        "session_id": sess1.id, "exercise_id": ex_id, "set_number": 1,
        "weight": 50.0, "reps": 5, "rpe": 8.0,
    })
    CompleteWorkoutHandler().execute(uow, user, {"session_id": sess1.id})

    prs = workout_svc.uow.workout_sessions.get_personal_records(user.id, [ex_id])
    assert prs[ex_id]["max_weight"] == 50.0
    assert prs[ex_id]["max_est_1rm"] > 56.0

    sess2 = StartWorkoutHandler().execute(uow, user, {})
    LogSetHandler().execute(uow, user, {
        "session_id": sess2.id, "exercise_id": ex_id, "set_number": 1,
        "weight": 55.0, "reps": 5, "rpe": 9.0,
    })

    with uow:
        sess2_obj = uow.workout_sessions.get_by_id(sess2.id)
        assert len(sess2_obj.sets) == 1

    deleted = DeleteLogSetHandler().execute(uow, user, {
        "session_id": sess2.id, "exercise_id": ex_id, "set_number": 1,
    })
    assert deleted.status == "deleted"

    with uow:
        sess2_fresh = uow.workout_sessions.get_by_id(sess2.id)
        assert sess2_fresh is not None
        assert all(log.deleted_at is not None for log in sess2_fresh.sets)


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
    assert len(body["sets"]) == 1
    assert body["sets"][0]["exercise_id"] == ex_id
    assert body["sets"][0]["weight"] == 15.0
    assert body["sets"][0]["reps"] == 8


def test_recent_sessions_includes_completed(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import Exercise, Workout, WorkoutExercise

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        alice = db.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None

        ex = Exercise(name="Curls", equipment="dumbbell", primary_muscles="biceps")
        db.add(ex)
        db.commit()
        ex_id = ex.id

        workout = Workout(name="Test Plan A", user_id=alice.id)
        db.add(workout)
        db.commit()
        workout_id = workout.id

        plan_ex = WorkoutExercise(workout_id=workout_id, exercise_id=ex_id, sequence=0, target_sets=3, target_reps=8, target_rpe=8.0)
        db.add(plan_ex)
        db.commit()

    start_resp = authenticated_client.post(f"/api/v1/workouts/sessions/start?workout_id={workout_id}")
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
    assert len(sess["sets"]) == 1
    assert sess["sets"][0]["exercise"]["name"] == "Curls"
    assert sess["sets"][0]["weight"] == 12.5
    assert sess["sets"][0]["reps"] == 10


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


def test_get_workout_returns_plan(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import Workout

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        alice = db.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None

        workout = Workout(
            name="Hypertrophy Phase 1",
            description="High volume muscle building.",
            user_id=alice.id,
        )
        db.add(workout)
        db.commit()
        workout_id = workout.id

    response = authenticated_client.get(f"/api/v1/workouts/{workout_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Hypertrophy Phase 1"
    assert body["description"] == "High volume muscle building."


def test_create_exercise_via_api(authenticated_client):
    data = {
        "name": "API Curls",
        "equipment": "dumbbell",
        "primary_muscles": "biceps_brachii",
        "secondary_muscles": "brachialis",
        "description": "Created via JSON API.",
        "instructions": "Curl with control.",
    }
    resp = authenticated_client.post("/api/v1/exercises", json=data)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] is not None
    assert body["name"] == "API Curls"

    duplicate = authenticated_client.post("/api/v1/exercises", json=data)
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

    resp = authenticated_client.delete(f"/api/v1/exercises/{ex_id}")
    assert resp.status_code == 204

    check = authenticated_client.get("/api/v1/workouts/exercises")
    assert not any(e["id"] == ex_id for e in check.json())


def test_create_workout_via_api(authenticated_client):
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
        "exercises": [
            {"exercise_id": ex_id, "sequence": 0, "target_sets": 3, "target_reps": 5, "target_rpe": 8.5}
        ],
    }
    resp = authenticated_client.post("/api/v1/workouts", json=data)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] is not None
    assert body["name"] == "API Plan"
    assert len(body["exercises"]) == 1
    assert body["exercises"][0]["exercise_id"] == ex_id


def test_delete_workout_via_api(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import Workout

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        alice = db.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None

        workout = Workout(name="To Remove", user_id=alice.id)
        db.add(workout)
        db.commit()
        workout_id = workout.id

    resp = authenticated_client.delete(f"/api/v1/workouts/{workout_id}")
    assert resp.status_code == 204

    with Session(engine) as db:
        deleted = db.get(Workout, workout_id)
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
    assert len(active.json()["sets"]) == 0


def test_list_workouts_via_api(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import Workout

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        alice = db.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None

        workout = Workout(name="List Test", user_id=alice.id)
        db.add(workout)
        db.commit()
        workout_id = workout.id

    resp = authenticated_client.get("/api/v1/workouts")
    assert resp.status_code == 200
    plans = resp.json()
    assert any(p["id"] == workout_id for p in plans)
    plan_data = next(p for p in plans if p["id"] == workout_id)
    assert plan_data["name"] == "List Test"


def test_get_workout_targets_returns_targets(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import Exercise, Workout, WorkoutExercise

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        alice = db.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None
        user_id = alice.id

        ex = Exercise(name="Targeted Curls", equipment="dumbbell", primary_muscles="biceps")
        db.add(ex)
        db.commit()
        ex_id = ex.id

        workout = Workout(name="Targets Plan", user_id=user_id)
        db.add(workout)
        db.commit()
        workout_id = workout.id

        plan_ex = WorkoutExercise(
            workout_id=workout_id, exercise_id=ex_id, sequence=0,
            target_sets=4, target_reps=10, target_rpe=8.0,
        )
        db.add(plan_ex)
        db.commit()

    resp = authenticated_client.get(f"/api/v1/workouts/{workout_id}/targets")
    assert resp.status_code == 200
    targets = resp.json()
    assert isinstance(targets, list)
    assert any(t["exercise_id"] == ex_id for t in targets)
    target = next(t for t in targets if t["exercise_id"] == ex_id)
    assert target["suggested_sets"] == 5


def test_create_program_with_slots_and_scheme(authenticated_client):
    from sqlmodel import Session, select
    from salus.models.user import User as UserModel
    from salus.models.workout import Exercise, Workout

    engine = authenticated_client.app.state.engine
    with Session(engine) as db:
        alice = db.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None

        db.add(Exercise(name="Bench Press", equipment="barbell", primary_muscles="chest"))
        db.commit()

        workout_a = Workout(name="Push Day", user_id=alice.id)
        workout_b = Workout(name="Pull Day", user_id=alice.id)
        db.add(workout_a)
        db.add(workout_b)
        db.commit()
        a_id = workout_a.id
        b_id = workout_b.id

    resp = authenticated_client.post("/api/v1/programs", json={
        "name": "Push-Pull",
        "progression_scheme": "linear",
        "slots": [
            {"workout_id": a_id, "sequence": 0, "day_of_week": 0},
            {"workout_id": b_id, "sequence": 1, "day_of_week": 2},
        ],
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Push-Pull"
    assert body["progression_scheme"] == "linear"
    assert [s["day_of_week"] for s in body["slots"]] == [0, 2]
    program_id = body["id"]

    listed = authenticated_client.get("/api/v1/programs").json()
    assert any(p["id"] == program_id for p in listed)

    start = authenticated_client.post(
        f"/api/v1/workouts/sessions/start?workout_id={a_id}&program_id={program_id}"
    )
    assert start.status_code == 200
    assert start.json()["progression_scheme"] == "linear"
    assert start.json()["program_id"] == program_id
