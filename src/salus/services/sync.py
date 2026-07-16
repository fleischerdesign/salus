from datetime import datetime, timezone
from typing import Any

from sqlalchemy import inspect as sa_inspect
from sqlmodel import func, or_, select

from salus.models.goal import Goal
from salus.models.measurement import Measurement
from salus.models.sharing import SharingRelationship
from salus.models.system_config import SystemConfig
from salus.models.user import User
from salus.models.workout import WorkoutSession
from salus.repositories.entity_meta import (
    EntityMeta,
    SYNC_ENTITY_SPECS,
    DELTA_ENTITY_SPECS,
    APPEND_ONLY_DELTA_SPECS,
)
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services._helpers import uid


def _delta_timestamp_filter(model: type, since: datetime):
    clauses = []
    if hasattr(model, "updated_at"):
        clauses.append(getattr(model, "updated_at") >= since)
    if hasattr(model, "created_at"):
        clauses.append(getattr(model, "created_at") >= since)
    return or_(*clauses) if clauses else None


def _owner_attr(model: type, spec: EntityMeta):
    field = spec.owner_field or "user_id"
    return getattr(model, field)


def _parent_ids(sess, spec: EntityMeta, user_id: str) -> list[str]:
    parent = spec.parent_model
    if parent is None:
        return []
    owner = spec.parent_owner_field or "user_id"
    pk = _pk_column(parent)
    stmt = select(pk).where(getattr(parent, owner) == user_id)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    if not spec.no_soft_delete and hasattr(parent, "deleted_at"):
        stmt = stmt.where(getattr(parent, "deleted_at").is_(None))  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    rows = sess.exec(stmt).all()
    return [r for r in rows if r is not None]


def _soft_delete_filter(model: type, stmt, spec: EntityMeta):
    if not spec.no_soft_delete and hasattr(model, "deleted_at"):
        return stmt.where(getattr(model, "deleted_at").is_(None))  # pyright: ignore[reportAttributeAccessIssue]
    return stmt


def _pk_column(model: type | None):
    if model is None:
        raise ValueError("Cannot get primary key of None")
    pk_cols = sa_inspect(model).primary_key
    return next(iter(pk_cols)) if pk_cols else None


def _pk_attr(model: type) -> str:
    pk = _pk_column(model)
    return pk.key if pk is not None else "id"


def _pk_value(instance) -> Any:
    model = type(instance)
    return getattr(instance, _pk_attr(model))


def _build_full_query(sess, spec: EntityMeta, user_id: str, cursor: str):
    model = spec.model
    if spec.strategy == "user_scoped":
        stmt = select(model).where(_owner_attr(model, spec) == user_id)
    elif spec.strategy == "shared_nullable":
        col = getattr(model, "user_id")
        stmt = select(model).where((col == user_id) | (col.is_(None)))
    elif spec.strategy == "relational":
        ids = _parent_ids(sess, spec, user_id)
        if not ids:
            return None
        stmt = select(model).where(getattr(model, spec.parent_field).in_(ids))  # pyright: ignore[reportArgumentType]
    elif spec.strategy == "global":
        stmt = select(model)
    elif spec.strategy == "append_only":
        stmt = select(model).where(_owner_attr(model, spec) == user_id)
    else:
        return None

    stmt = _soft_delete_filter(model, stmt, spec)
    pk = _pk_column(model)
    if pk is not None and cursor:
        stmt = stmt.where(pk > cursor).order_by(pk).limit(spec.batch_size + 1)
    elif pk is not None:
        stmt = stmt.order_by(pk).limit(spec.batch_size + 1)
    return stmt


def _admin_user_list(s, exclude_user_id: str) -> list[dict]:
    measurement_subq = (
        select(func.count())
        .select_from(Measurement)
        .where(Measurement.user_id == User.id)
        .correlate(User)
        .scalar_subquery()
        .label("measurement_count")
    )
    goal_subq = (
        select(func.count())
        .select_from(Goal)
        .where(Goal.user_id == User.id, Goal.deleted_at.is_(None))  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        .correlate(User)
        .scalar_subquery()
        .label("goal_count")
    )

    rows = s.exec(
        select(  # pyright: ignore[reportCallIssue]
            User.id,
            User.username,
            User.email,
            User.display_name,
            User.is_admin,
            User.is_active,
            User.created_at,
            measurement_subq,
            goal_subq,
        ).where(User.id != exclude_user_id)
    ).all()

    return [
        {
            "id": r[0],
            "username": r[1],
            "email": r[2],
            "display_name": r[3],
            "is_admin": r[4],
            "is_active": r[5],
            "created_at": r[6].isoformat() if r[6] else None,
            "measurement_count": r[7] or 0,
            "goal_count": r[8] or 0,
        }
        for r in rows
        if r[0] is not None
    ]


def _admin_system_stats(s) -> dict:
    import os

    from salus.config import settings as app_settings
    from salus.models.metric_definition import MetricDefinition

    total_users = s.scalar(select(func.count()).select_from(User)) or 0
    total_measurements = s.scalar(select(func.count()).select_from(Measurement)) or 0
    total_metric_types = s.scalar(select(func.count()).select_from(MetricDefinition)) or 0
    total_goals = s.scalar(select(func.count()).select_from(Goal)) or 0
    db_path = app_settings.database_url.replace("sqlite:///", "")
    db_size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    db_size = (
        f"{db_size_bytes / (1024 * 1024):.1f} MB"
        if db_size_bytes >= 1024 * 1024
        else (f"{db_size_bytes / 1024:.1f} KB" if db_size_bytes >= 1024 else f"{db_size_bytes} B")
    )
    return {
        "key": "global",
        "total_users": total_users,
        "total_measurements": total_measurements,
        "total_metric_types": total_metric_types,
        "total_goals": total_goals,
        "db_size": db_size,
    }


def _community_activity_feed(s, user_id: str, username: str) -> list[dict]:
    user_handle = f"@{username}"
    activities: list[dict] = []

    incoming = s.exec(
        select(SharingRelationship).where(
            SharingRelationship.grantee_handle == user_handle,
            SharingRelationship.status == "active",
        )
    ).all()

    for rel in incoming:
        owner = s.get(User, rel.owner_id)
        activities.append({
            "id": rel.id,
            "friend_name": owner.username if owner else f"user_{rel.owner_id}",
            "activity_type": "steps",
            "activity_description": "shared health data with you",
            "time": rel.created_at.isoformat() if rel.created_at else None,
        })

    outgoing = s.exec(
        select(SharingRelationship).where(
            SharingRelationship.owner_id == user_id,
            SharingRelationship.status == "active",
        )
    ).all()

    for rel in outgoing:
        activities.append({
            "id": rel.id,
            "friend_name": rel.grantee_handle,
            "activity_type": "steps",
            "activity_description": "started sharing health data",
            "time": rel.created_at.isoformat() if rel.created_at else None,
        })

    sessions = s.exec(
        select(WorkoutSession).where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.completed_at.is_not(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        ).order_by(WorkoutSession.completed_at.desc()).limit(20)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    ).all()

    for se in sessions:
        activities.append({
            "id": se.id,
            "friend_name": username,
            "activity_type": "workout",
            "activity_description": "completed a workout",
            "time": se.completed_at.isoformat() if se.completed_at else None,
        })

    activities.sort(key=lambda a: a.get("time") or "", reverse=True)
    return activities[:50]


def _system_config_enriched(s) -> list[dict]:
    import os

    rows = s.exec(select(SystemConfig)).all()
    result: list[dict] = []
    for r in rows:
        result.append({
            "key": r.key,
            "value": r.value,
            "description": r.description,
            "category": r.category,
            "is_secret": r.is_secret,
            "is_env_override": r.key.upper() in os.environ or f"SALUS_{r.key.upper()}" in os.environ,
            "db_has_value": r.value is not None,
        })
    return result


def _user_profile_dict(user: User) -> dict[str, Any]:
    user_id = uid(user)
    return {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "display_name": user.display_name,
        "theme": user.theme,
        "locale": user.locale,
        "onboarding_dismissed": user.onboarding_dismissed,
        "is_admin": user.is_admin,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def _special_entities(s, user: User) -> dict[str, Any]:
    user_id = uid(user)
    profile = _user_profile_dict(user)
    result: dict[str, Any] = {
        "user_profile": profile,
        "user": dict(profile),
        "community_activity": _community_activity_feed(s, user_id, user.username),
    }
    if user.is_admin:
        result["admin_user"] = _admin_user_list(s, user_id)
        result["admin_stats"] = _admin_system_stats(s)
        result["system_config"] = _system_config_enriched(s)
    else:
        result["admin_user"] = None
        result["admin_stats"] = None
        result["system_config"] = None
    return result


class SyncService:

    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def full_sync(self, user: User, cursors: dict[str, str] | None = None) -> dict[str, Any]:
        user_id = uid(user)
        s = self.uow.session
        now = datetime.now(timezone.utc)
        cursors = cursors or {}

        result: dict[str, Any] = {}
        next_cursors: dict[str, str] = {}
        has_more = False

        for spec in SYNC_ENTITY_SPECS:
            cursor = cursors.get(spec.name, "")
            query = _build_full_query(s, spec, user_id, cursor)
            if query is None:
                result[spec.name] = []
                next_cursors[spec.name] = cursor
                continue

            rows = s.exec(query).all()

            if len(rows) > spec.batch_size:
                has_more = True
                rows = rows[:spec.batch_size]

            if rows:
                last_id = _pk_value(rows[-1])
                next_cursors[spec.name] = str(last_id) if last_id is not None else cursor
                if len(rows) == spec.batch_size:
                    pass
            else:
                next_cursors[spec.name] = cursor

            result[spec.name] = rows

        is_first_page = not cursors or len(cursors) == 0
        if is_first_page:
            result.update(_special_entities(s, user))

        result["cursors"] = next_cursors
        result["has_more"] = has_more
        result["synced_at"] = now.isoformat()
        return result

    def delta_sync(self, user: User, since: datetime) -> dict[str, Any]:
        user_id = uid(user)
        s = self.uow.session
        now = datetime.now(timezone.utc)

        changed: dict[str, list[Any]] = {}
        deleted: dict[str, list[int]] = {}

        for spec in DELTA_ENTITY_SPECS:
            model = spec.model
            name = spec.name
            pk_col = _pk_column(model)

            if spec.strategy in ("user_scoped", "shared_nullable"):
                owner_attr = _owner_attr(model, spec)

                if spec.strategy == "shared_nullable":
                    col = getattr(model, "user_id")
                    base_filter = (col == user_id) | (col.is_(None))
                else:
                    base_filter = owner_attr == user_id

                ts_filter = _delta_timestamp_filter(model, since)
                if ts_filter is not None:
                    changed[name] = list(s.exec(
                        select(model).where(
                            base_filter,
                            ts_filter,
                            getattr(model, "deleted_at").is_(None),
                        )
                    ).all())  # type: ignore[reportArgumentType]
                if hasattr(model, "deleted_at") and pk_col is not None:
                    delete_ids = [
                        row[0] for row in s.exec(
                            select(pk_col).where(  # pyright: ignore[reportArgumentType]
                                base_filter,
                                getattr(model, "deleted_at") >= since,
                            )
                        ).all()
                    ]
                    if delete_ids:
                        deleted[name] = delete_ids

            elif spec.strategy == "relational":
                parent_ids = _parent_ids(s, spec, user_id)
                if not parent_ids:
                    continue
                parent_filter = getattr(model, spec.parent_field).in_(parent_ids)  # pyright: ignore[reportArgumentType]

                ts_filter = _delta_timestamp_filter(model, since)
                if ts_filter is not None:
                    changed[name] = list(s.exec(
                        select(model).where(
                            parent_filter,
                            ts_filter,
                            getattr(model, "deleted_at").is_(None),
                        )
                    ).all())
                if hasattr(model, "deleted_at") and pk_col is not None:
                    delete_ids = [
                        row[0] for row in s.exec(
                            select(pk_col).where(  # pyright: ignore[reportArgumentType]
                                parent_filter,
                                getattr(model, "deleted_at") >= since,
                            )
                        ).all()
                    ]
                    if delete_ids:
                        deleted[name] = delete_ids

            elif spec.strategy == "global":
                ts_filter = _delta_timestamp_filter(model, since)
                if ts_filter is not None:
                    changed[name] = list(s.exec(
                        select(model).where(
                            ts_filter,
                            getattr(model, "deleted_at").is_(None),
                        )
                    ).all())
                if hasattr(model, "deleted_at") and pk_col is not None:
                    delete_ids = [
                        row[0] for row in s.exec(
                            select(pk_col).where(  # pyright: ignore[reportArgumentType]
                                getattr(model, "deleted_at") >= since,
                            )
                        ).all()
                    ]
                    if delete_ids:
                        deleted[name] = delete_ids

        for spec in APPEND_ONLY_DELTA_SPECS:
            model = spec.model
            name = spec.name
            ts_field = spec.timestamp_field or "created_at"
            owner_attr = _owner_attr(model, spec)

            changed[name] = list(s.exec(
                select(model).where(
                    owner_attr == user_id,
                    getattr(model, ts_field) >= since,
                )
            ).all())  # type: ignore[reportArgumentType]

        special = _special_entities(s, user)
        for key, value in special.items():
            if key in ("admin_user", "admin_stats", "system_config") and value is None:
                continue
            if value is not None:
                changed[key] = value if isinstance(value, list) else [value]

        return {
            "changed": {k: v for k, v in changed.items() if v},
            "deleted": {k: v for k, v in deleted.items() if v},
            "synced_at": now.isoformat(),
        }
