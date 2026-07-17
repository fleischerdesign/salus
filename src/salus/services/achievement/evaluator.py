# pyright: reportArgumentType=false, reportOptionalMemberAccess=false, reportOptionalOperand=false, reportCallIssue=false, reportAttributeAccessIssue=false
import json
from datetime import date, datetime, timedelta

from sqlmodel import Session, func, select

from salus.models.achievement import AchievementDefinition
from salus.models.habit import Habit, HabitLog
from salus.models.measurement import Measurement
from salus.models.mood import MoodEntry
from salus.models.goal import Goal
from salus.models.sharing import SharingRelationship
from salus.models.workout import WorkoutSession
from salus.services.achievement.streak import compute_streak


def _count_entity(
    session: Session,
    user_id: str,
    entity: str,
    op: str,
    value: float,
    extra: dict,
) -> bool:
    match entity:
        case "measurement":
            stmt = select(func.count()).select_from(Measurement).where(
                Measurement.user_id == user_id,
                Measurement.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
            )
        case "habit":
            stmt = select(func.count()).select_from(Habit).where(
                Habit.user_id == user_id,
                Habit.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
            )
        case "habit_log":
            stmt = select(func.count()).select_from(HabitLog).where(
                HabitLog.user_id == user_id,
                HabitLog.completed == True,  # noqa: E712
                HabitLog.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
            )
        case "mood_entry":
            stmt = select(func.count()).select_from(MoodEntry).where(
                MoodEntry.user_id == user_id,
                MoodEntry.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
            )
        case "goal":
            stmt = select(func.count()).select_from(Goal).where(
                Goal.user_id == user_id,
                Goal.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
            )
        case "workout_session":
            stmt = select(func.count()).select_from(WorkoutSession).where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.completed_at.isnot(None),  # pyright: ignore[reportAttributeAccessIssue]
                WorkoutSession.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
            )
        case "sharing_relationship":
            stmt = select(func.count()).select_from(SharingRelationship).where(
                SharingRelationship.owner_id == user_id,
            )
        case _:
            return False

    if "hour_before" in extra and entity == "measurement":
        stmt = stmt.where(
            func.extract("hour", Measurement.start_time) < extra["hour_before"]  # pyright: ignore[reportAttributeAccessIssue]
        )
    if "hour_after" in extra and entity == "measurement":
        stmt = stmt.where(
            func.extract("hour", Measurement.start_time) >= extra["hour_after"]  # pyright: ignore[reportAttributeAccessIssue]
        )
    if "within_days" in extra:
        since = datetime.now() - timedelta(days=int(extra["within_days"]))
        if entity == "workout_session":
            stmt = stmt.where(WorkoutSession.completed_at >= since)  # pyright: ignore[reportAttributeAccessIssue]

    count_result = session.exec(stmt).one()
    count_val = float(count_result) if count_result is not None else 0.0

    match op:
        case "gte":
            return count_val >= value
        case "gt":
            return count_val > value
        case "eq":
            return count_val == value
        case _:
            return False


def _streak_entity(
    session: Session,  # pyright: ignore[reportArgumentType]
    user_id: str,
    entity: str,
    days: int,
) -> bool:
    today = date.today()

    match entity:
        case "measurement":
            rows = session.exec(
                select(Measurement.start_time).where(
                    Measurement.user_id == user_id,
                    Measurement.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(Measurement.start_time.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
            dates = [r.date() for r in rows if isinstance(r, datetime)]
        case "habit_log":
            rows = session.exec(
                select(HabitLog.log_date).where(  # pyright: ignore[reportArgumentType]
                    HabitLog.user_id == user_id,
                    HabitLog.completed == True,  # noqa: E712
                    HabitLog.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(HabitLog.log_date.desc())  # pyright: ignore[reportAttributeAccessIssue, reportArgumentType]
            ).all()
            dates = [r for r in rows if isinstance(r, date)]
        case "mood_entry":
            rows = session.exec(
                select(MoodEntry.entry_date).where(
                    MoodEntry.user_id == user_id,
                    MoodEntry.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(MoodEntry.entry_date.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
            dates = [r for r in rows if isinstance(r, date)]
        case "workout_session":
            rows = session.exec(
                select(WorkoutSession.completed_at).where(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.completed_at.isnot(None),  # pyright: ignore[reportAttributeAccessIssue]
                    WorkoutSession.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(WorkoutSession.completed_at.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
            dates = [r.date() for r in rows if isinstance(r, datetime)]
        case _:
            return False

    _, longest = compute_streak(dates, today)
    return longest >= days


def _compound_evaluate(
    session: Session,
    user_id: str,
    conditions: list[dict],
    op: str,
) -> bool:
    results = []
    for cond in conditions:
        cfg = cond.get("condition_config", "{}")
        config = json.loads(cfg) if isinstance(cfg, str) else cfg
        condition_type = cond["condition_type"]
        if condition_type == "count":
            extra = {k: v for k, v in cond.items() if k not in ("type", "entity", "op", "value")}
            extra.update({k: v for k, v in config.items() if k not in ("entity", "op", "value")})
            results.append(_count_entity(session, user_id, cond["entity"], cond.get("op", "gte"), float(cond.get("value", 1)), extra))
        elif condition_type == "streak":
            results.append(_streak_entity(session, user_id, cond["entity"], int(cond.get("days", 7))))
        else:
            results.append(False)

    if op == "and":
        return all(results)
    elif op == "or":
        return any(results)
    return False


def evaluate_achievement(
    session: Session,
    user_id: str,
    definition: AchievementDefinition,
) -> bool:
    try:
        config = json.loads(definition.condition_config)
    except (json.JSONDecodeError, TypeError):
        return False

    condition_type = definition.condition_type
    match condition_type:
        case "count":
            entity = config.get("entity", "")
            op_str = config.get("op", "gte")
            value = float(config.get("value", 1))
            extra = {k: v for k, v in config.items() if k not in ("entity", "op", "value", "type")}
            return _count_entity(session, user_id, entity, op_str, value, extra)
        case "streak":
            entity = config.get("entity", "")
            days = int(config.get("days", 7))
            return _streak_entity(session, user_id, entity, days)
        case "compound":
            conditions = config.get("conditions", [])
            op_str = config.get("op", "and")
            return _compound_evaluate(session, user_id, conditions, op_str)
        case _:
            return False
