from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

from salus.models.sharing import (
    ConnectionStatus,
    LeaderboardGroup,
    LeaderboardMember,
    SharingRelationship,
)
from salus.services.command_registry import CommandResult, register
from salus.services._helpers import make_handle

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User


def _serialize_relationship(rel: SharingRelationship) -> dict[str, Any]:
    return {
        "id": rel.id, "owner_id": rel.owner_id, "grantee_handle": rel.grantee_handle,
        "metric_type_id": rel.metric_type_id, "aggregation_level": rel.aggregation_level,
        "expiration_date": rel.expiration_date, "status": rel.status,
        "created_at": rel.created_at, "updated_at": rel.updated_at,
        "last_sync_at": rel.last_sync_at, "deleted_at": rel.deleted_at,
    }


@register("create_connection")
class CreateConnectionHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        grantee_handle = payload.get("grantee_handle", "").strip()
        if not grantee_handle.startswith("@"):
            grantee_handle = f"@{grantee_handle}"

        metric_type_id = payload.get("metric_type_id") or ""
        aggregation_level = payload.get("aggregation_level", "summary")

        now = datetime.now(timezone.utc)
        rel = SharingRelationship(
            id=payload.get("id"),
            owner_id=user.id,  # pyright: ignore[reportArgumentType]
            grantee_handle=grantee_handle,
            metric_type_id=metric_type_id,
            aggregation_level=aggregation_level,
            status=ConnectionStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        uow.sharing_relationships.add(rel)
        uow.commit()
        uow.session.refresh(rel)
        return CommandResult(status="created", record=_serialize_relationship(rel), id=rel.id)


@register("accept_connection")
class AcceptConnectionHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        rel_id = payload.get("id")
        if not rel_id:
            return CommandResult(status="error", message="id is required")
        rel = uow.sharing_relationships.get_by_id(rel_id)  # pyright: ignore[reportArgumentType]
        if not rel:
            return CommandResult(status="not_found", id=rel_id)
        if rel.grantee_handle != make_handle(user):
            return CommandResult(status="forbidden", id=rel_id)
        rel.status = ConnectionStatus.ACTIVE
        rel.updated_at = datetime.now(timezone.utc)
        uow.sharing_relationships.update(rel)
        uow.commit()
        uow.session.refresh(rel)
        return CommandResult(status="updated", record=_serialize_relationship(rel), id=rel_id)


@register("decline_connection")
class DeclineConnectionHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        rel_id = payload.get("id")
        if not rel_id:
            return CommandResult(status="error", message="id is required")
        rel = uow.sharing_relationships.get_by_id(rel_id)  # pyright: ignore[reportArgumentType]
        if not rel:
            return CommandResult(status="not_found", id=rel_id)
        if rel.grantee_handle != make_handle(user):
            return CommandResult(status="forbidden", id=rel_id)
        rel.status = ConnectionStatus.DECLINED
        rel.updated_at = datetime.now(timezone.utc)
        uow.sharing_relationships.update(rel)
        uow.commit()
        uow.session.refresh(rel)
        return CommandResult(status="updated", record=_serialize_relationship(rel), id=rel_id)


@register("delete_connection")
class DeleteConnectionHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        rel_id = payload.get("id")
        if not rel_id:
            return CommandResult(status="error", message="id is required")
        rel = uow.sharing_relationships.get_by_id(rel_id)  # pyright: ignore[reportArgumentType]
        if not rel:
            return CommandResult(status="deleted", id=rel_id)
        if rel.owner_id != user.id and rel.grantee_handle != make_handle(user):  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", id=rel_id)
        rel.status = ConnectionStatus.REVOKED
        rel.updated_at = datetime.now(timezone.utc)
        uow.sharing_relationships.update(rel)
        uow.commit()
        return CommandResult(status="deleted", id=rel_id)


@register("create_leaderboard")
class CreateLeaderboardHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        name = payload.get("name", "").strip()
        if not name:
            return CommandResult(status="error", message="name is required")

        invite_code = secrets.token_hex(6)
        group = LeaderboardGroup(
            id=payload.get("id"),
            name=name,
            creator_id=user.id,  # pyright: ignore[reportArgumentType]
            metric_type_code=payload.get("metric_type_code", "steps"),
            time_frame=payload.get("time_frame", "weekly"),
            invite_code=invite_code,
        )
        uow.leaderboard_groups.create(group)
        uow.commit()
        uow.session.refresh(group)

        member = LeaderboardMember(
            group_id=group.id,  # pyright: ignore[reportArgumentType]
            user_handle=make_handle(user),
            status="active",
        )
        uow.leaderboard_members.create(member)
        uow.commit()

        record: dict[str, Any] = {
            "id": group.id, "name": group.name, "creator_id": group.creator_id,
            "metric_type_code": group.metric_type_code, "time_frame": group.time_frame,
            "invite_code": group.invite_code,
        }
        return CommandResult(status="created", record=record, id=group.id)  # pyright: ignore[reportAttributeAccessIssue]


@register("join_leaderboard")
class JoinLeaderboardHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        group_id = payload.get("group_id")
        invite_code = payload.get("invite_code")
        if not group_id:
            return CommandResult(status="error", message="group_id is required")

        group = uow.leaderboard_groups.get_by_id(group_id)  # pyright: ignore[reportArgumentType]
        if not group:
            return CommandResult(status="not_found", message="Leaderboard not found")
        if group.invite_code != invite_code:
            return CommandResult(status="error", message="Invalid invite code")

        handle = make_handle(user)
        existing = uow.leaderboard_members.get_member(group_id, handle)  # pyright: ignore[reportArgumentType]
        if existing:
            if existing.status == "active":
                return CommandResult(status="error", message="Already a member")
            existing.status = "active"  # pyright: ignore[reportAttributeAccessIssue]
            existing.joined_at = datetime.now(timezone.utc)  # pyright: ignore[reportAttributeAccessIssue]
            uow.leaderboard_members.update(existing)
        else:
            member = LeaderboardMember(
                group_id=group_id,
                user_handle=handle,
                status="active",
                joined_at=datetime.now(timezone.utc),
            )
            uow.leaderboard_members.create(member)
        uow.commit()
        return CommandResult(status="created", id=group_id)


@register("leave_leaderboard")
class LeaveLeaderboardHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        group_id = payload.get("group_id")
        if not group_id:
            return CommandResult(status="error", message="group_id is required")
        handle = make_handle(user)
        member = uow.leaderboard_members.get_member(group_id, handle)  # pyright: ignore[reportArgumentType]
        if not member:
            return CommandResult(status="not_found", message="Not a member")
        uow.leaderboard_members.delete(member)
        uow.commit()
        return CommandResult(status="deleted", id=group_id)


@register("delete_leaderboard")
class DeleteLeaderboardHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        group_id = payload.get("id")
        if not group_id:
            return CommandResult(status="error", message="id is required")
        group = uow.leaderboard_groups.get_by_id(group_id)  # pyright: ignore[reportArgumentType]
        if not group:
            return CommandResult(status="deleted", id=group_id)
        if group.creator_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", id=group_id)
        uow.leaderboard_groups.delete(group)
        uow.commit()
        return CommandResult(status="deleted", id=group_id)