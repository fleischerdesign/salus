from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool
import salus.models  # noqa: F401

from salus.models.metric_definition import MetricDefinition
from salus.models.workout import (
    Exercise,
    Program,
    ProgramWorkout,
    Workout,
    WorkoutExercise,
)
from salus.models.user import User
from salus.reference_data.engine import ReferenceDataEngine
from salus.reference_data.registry import REFERENCE_SPECS
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.services.sync import SyncService


DEFAULT_WORKOUT_IDS = {
    "wo-fb-a",
    "wo-fb-b",
    "wo-upper-a",
    "wo-lower-a",
    "wo-upper-b",
    "wo-lower-b",
    "wo-push-a",
    "wo-pull-a",
    "wo-legs-a",
}


def _workout_exercise_spec():
    return next(s for s in REFERENCE_SPECS if s.name == "common_workout_exercises")


def _count_instances(session: Session, model, *, user_id_none: bool = False) -> int:
    stmt = select(model)
    if user_id_none:
        stmt = stmt.where(model.user_id.is_(None))
    return len(session.exec(stmt).all())


def test_reference_data_engine_seeding():
    engine = create_engine(
        "sqlite://",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    session = Session(engine)
    try:
        ref_engine = ReferenceDataEngine(REFERENCE_SPECS)

        # 1. First run: Seeds all items
        report1 = ref_engine.seed_all(session)
        assert report1.total_created > 0
        assert report1.total_updated == 0

        # Verify a metric was created
        steps = session.get(MetricDefinition, "steps")
        assert steps is not None
        assert steps.unit == "steps"

        # 2. Second run: Fast SHA-256 skip
        report2 = ref_engine.seed_all(session)
        assert report2.total_created == 0
        assert report2.total_updated == 0
        assert all(item.skipped_by_hash for item in report2.items)

    finally:
        session.close()


def _seed_all_fresh() -> tuple[Session, object]:
    """Bootstrap a fresh SQLite engine, seed reference data, return (session, engine)."""
    engine = create_engine(
        "sqlite://",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    session.exec(
        select(Workout).where(Workout.id == "__none__")
    )  # ensure tables resolvable
    ReferenceDataEngine(REFERENCE_SPECS).seed_all(session)
    return session, engine


def test_seed_all_creates_default_workouts_and_programs():
    session, engine = _seed_all_fresh()
    try:
        # 1. Exactly 9 system workouts, all with user_id = null
        workouts = session.exec(select(Workout).where(Workout.user_id.is_(None))).all()
        assert len(workouts) == 9
        assert {w.id for w in workouts} == DEFAULT_WORKOUT_IDS
        assert all(w.user_id is None for w in workouts)

        # 2. Exactly 3 system programs, all with user_id = null
        programs = session.exec(select(Program).where(Program.user_id.is_(None))).all()
        assert len(programs) == 3
        assert all(p.user_id is None for p in programs)
        assert all(p.progression_scheme == "autoregulated" for p in programs)

        # 3. All workout_exercise bridges reference valid seeded exercises
        valid_exercise_ids = {e.id for e in session.exec(select(Exercise)).all()}
        bridges = session.exec(select(WorkoutExercise)).all()
        assert len(bridges) == len(_workout_exercise_spec().items)
        for b in bridges:
            assert b.exercise_id in valid_exercise_ids
            assert session.get(Workout, b.workout_id) is not None

        # 4. All program_workout bridges reference valid programs and workouts
        program_ids = {p.id for p in programs}
        workout_ids = {w.id for w in workouts}
        slots = session.exec(select(ProgramWorkout)).all()
        for sl in slots:
            assert sl.program_id in program_ids
            assert sl.workout_id in workout_ids

        # 5. Deterministic ids exist for a sample of bridges
        assert session.get(WorkoutExercise, "woex-fb-a-1") is not None
        assert session.get(ProgramWorkout, "prgw-fb-mon") is not None
        assert session.get(ProgramWorkout, "prgw-ppl-sat") is not None
    finally:
        session.close()


def test_seed_all_workouts_programs_idempotent():
    session, engine = _seed_all_fresh()
    try:
        workouts_before = _count_instances(session, Workout, user_id_none=True)
        programs_before = _count_instances(session, Program)

        report2 = ReferenceDataEngine(REFERENCE_SPECS).seed_all(session)
        assert report2.total_created == 0
        assert report2.total_updated == 0
        assert all(item.skipped_by_hash for item in report2.items)

        workouts_after = _count_instances(session, Workout, user_id_none=True)
        assert workouts_after == workouts_before == 9
        assert _count_instances(session, Program) == programs_before
    finally:
        session.close()


def test_full_sync_returns_system_workouts_programs_and_children():
    session, engine = _seed_all_fresh()
    try:
        user = User(username="athlete", password_hash="x")
        session.add(user)
        session.commit()
        svc = SyncService(SqlUnitOfWork(session))

        data = svc.full_sync(user)

        workout_ids = {w.id for w in data["workout"]}
        prog_ids = {p.id for p in data["program"]}
        for wid in ("wo-fb-a", "wo-push-a", "wo-legs-a"):
            assert wid in workout_ids
        for pid in ("prog-full-body-3d", "prog-upper-lower-4d", "prog-ppl-hypertrophy"):
            assert pid in prog_ids

        we_workouts = {we.workout_id for we in data["workout_exercise"]}
        assert "wo-fb-a" in we_workouts
        assert "wo-legs-a" in we_workouts

        pw_ids = {pw.program_id for pw in data["program_workout"]}
        pw_workouts = {pw.workout_id for pw in data["program_workout"]}
        assert "prog-upper-lower-4d" in pw_ids
        assert "wo-upper-a" in pw_workouts
    finally:
        session.close()


def test_delta_sync_returns_system_workouts_programs_and_children():
    from datetime import datetime, timezone, timedelta

    session, engine = _seed_all_fresh()
    try:
        user = User(username="bob", password_hash="x")
        session.add(user)
        session.commit()
        svc = SyncService(SqlUnitOfWork(session))

        since = datetime.now(timezone.utc) - timedelta(days=1)
        data = svc.delta_sync(user, since)
        changed = data["changed"]

        workout_ids = {w.id for w in changed.get("workout", [])}
        prog_ids = {p.id for p in changed.get("program", [])}
        assert "wo-fb-a" in workout_ids
        assert "prog-upper-lower-4d" in prog_ids

        we_workouts = {we.workout_id for we in changed.get("workout_exercise", [])}
        assert "wo-fb-a" in we_workouts
        pw_workouts = {pw.workout_id for pw in changed.get("program_workout", [])}
        assert "wo-upper-a" in pw_workouts
    finally:
        session.close()
