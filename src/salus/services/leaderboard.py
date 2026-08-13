# pyright: reportOptionalOperand=false
import logging
import secrets
from datetime import date, datetime, timezone, timedelta
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from salus.services.sharing import SharingService

from salus.exceptions import ForbiddenError, NotFoundError, ConflictError
from salus.models.sharing import (
    LeaderboardGroup,
    LeaderboardMember,
)
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services._helpers import uid, make_handle, summarize_daily_values
from salus.services.sharing.relationship import RelationshipService

logger = logging.getLogger("salus.services.leaderboard")

WEEKLY_WINDOW_DAYS = 7
MONTHLY_WINDOW_DAYS = 30


class LeaderboardService:
    def __init__(
        self, uow: IUnitOfWork, sharing_svc: Optional["SharingService"] = None
    ) -> None:
        self.uow = uow
        self.sharing_svc = sharing_svc

    def create_group(
        self,
        creator_id: str,
        name: str,
        source_data_type: str = "steps",
        time_frame: str = "weekly",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> LeaderboardGroup:
        with self.uow:
            creator = self.uow.users.get_by_id(creator_id)
            if not creator:
                raise NotFoundError("Creator user not found")

            # Generate invite code
            invite_code = secrets.token_hex(6)

            # Create group
            group = LeaderboardGroup(
                name=name.strip(),
                creator_id=creator_id,
                source_data_type=source_data_type,
                time_frame=time_frame,
                start_date=start_date,
                end_date=end_date,
                invite_code=invite_code,
            )
            self.uow.leaderboard_groups.create(group)

            assert group.id is not None
            # Creator joins automatically as active member
            member = LeaderboardMember(
                group_id=group.id,
                user_handle=make_handle(creator),
                status="active",
            )
            self.uow.leaderboard_members.create(member)
            return group

    def join_by_code(self, user_id: str, invite_code: str) -> LeaderboardGroup:
        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("User not found")

            group = self.uow.leaderboard_groups.find_by_invite_code(invite_code)
            if not group:
                raise NotFoundError("Challenge group not found for this invite code")

            assert group.id is not None
            # Check if user is already a member
            user_handle = make_handle(user)
            existing = self.uow.leaderboard_members.get_member(group.id, user_handle)
            if existing:
                if existing.status == "active":
                    raise ConflictError("You are already a member of this challenge")
                else:
                    existing.status = "active"
                self.uow.leaderboard_members.update(existing)
                return group

            # Connection prerequisite check: user must have a connection with group creator
            creator = self.uow.users.get_by_id(group.creator_id)
            if not creator:
                raise NotFoundError("Creator of the group no longer exists")

            creator_handle = make_handle(creator)

            rel1 = self.uow.sharing_relationships.find_active_between(
                user_id, creator_handle
            )

            rel2 = self.uow.sharing_relationships.find_active_between(
                uid(creator), user_handle
            )

            # Exception if they aren't connected
            if not rel1 and not rel2 and creator.id != user_id:
                raise ForbiddenError(
                    "Prerequisite: You must be connected with the challenge creator to join."
                )

            assert group.id is not None
            # Join
            member = LeaderboardMember(
                group_id=group.id,
                user_handle=user_handle,
                status="active",
            )
            self.uow.leaderboard_members.create(member)
            return group

    def list_my_groups(self, user_id: str) -> list[LeaderboardGroup]:
        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                return []

            user_handle = make_handle(user)
            # Load created groups
            created = self.uow.leaderboard_groups.find_by_creator(user_id)
            # Load joined groups
            joined = self.uow.leaderboard_groups.find_joined_by_user(user_handle)

            # Deduplicate by group id
            seen = set()
            res = []
            for g in created + joined:
                if g.id not in seen:
                    seen.add(g.id)
                    res.append(g)
            return res

    def get_group_rankings(self, group_id: str, current_user_id: str) -> dict:
        with self.uow:
            group = self.uow.leaderboard_groups.get_by_id(group_id)
            if not group:
                raise NotFoundError("Challenge group not found")
            assert group.id is not None

            current_user = self.uow.users.get_by_id(current_user_id)
            if not current_user:
                raise NotFoundError("User not found")

            # Verify current user is a member
            current_handle = make_handle(current_user)
            member_check = self.uow.leaderboard_members.get_member(
                group.id, current_handle
            )
            if not member_check or member_check.status != "active":
                raise ForbiddenError("You are not a member of this challenge group")

            start_date, end_date = self._timeframe(group)

            members = self.uow.leaderboard_members.find_by_group_id(group.id)
            active_members = [m for m in members if m.status == "active"]

            rankings = []
            for m in active_members:
                handle = m.user_handle
                if not RelationshipService.is_remote(handle):
                    score = self._score_local_member(group, handle, start_date, end_date)
                else:
                    score = self._score_remote_member(
                        group, handle, start_date, end_date, current_user_id
                    )

                rankings.append(
                    {
                        "username": handle[1:],
                        "user_handle": handle,
                        "score": score,
                        "is_me": handle == current_handle,
                    }
                )

            # Sort by score desc
            rankings.sort(key=lambda x: x["score"], reverse=True)

            return {
                "group": group,
                "rankings": rankings,
                "start_date": start_date,
                "end_date": end_date,
            }

    def _timeframe(self, group: LeaderboardGroup) -> tuple[date, date]:
        now = datetime.now(timezone.utc)
        if group.time_frame == "weekly":
            start_date = (now - timedelta(days=WEEKLY_WINDOW_DAYS)).date()
        elif group.time_frame == "monthly":
            start_date = (now - timedelta(days=MONTHLY_WINDOW_DAYS)).date()
        else:
            start_date = (
                group.start_date.date()
                if group.start_date
                else (now - timedelta(days=WEEKLY_WINDOW_DAYS)).date()
            )
        end_date = group.end_date.date() if group.end_date else now.date()
        return start_date, end_date

    def _score_local_member(
        self,
        group: LeaderboardGroup,
        handle: str,
        start_date: date,
        end_date: date,
    ) -> float:
        username = handle[1:]
        local_user = self.uow.users.get_by_username(username)
        if not local_user:
            return 0.0

        if group.source_data_type == "workouts":
            since_dt = datetime.combine(
                start_date, datetime.min.time(), tzinfo=timezone.utc
            )
            until_dt = datetime.combine(
                end_date, datetime.max.time(), tzinfo=timezone.utc
            )
            return float(
                self.uow.workout_sessions.count_completed_in_range(
                    uid(local_user), since_dt, until_dt
                )
            )

        measurements = self.uow.measurements.find_all(
            user_id=uid(local_user),
            source_data_types=[group.source_data_type],
            since=datetime.combine(
                start_date, datetime.min.time(), tzinfo=timezone.utc
            ),
            until=datetime.combine(
                end_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc
            ),
        )
        day_values = [
            ms.value_numeric
            for ms in measurements
            if ms.start_time.date() >= start_date
            and ms.start_time.date() <= end_date
            and ms.value_numeric is not None
        ]
        if not day_values:
            return 0.0
        return summarize_daily_values(group.source_data_type, day_values) or 0.0

    def _score_remote_member(
        self,
        group: LeaderboardGroup,
        handle: str,
        start_date: date,
        end_date: date,
        requester_id: str,
    ) -> float:
        if not self.sharing_svc:
            return 0.0
        try:
            data = self.sharing_svc.resolve_and_fetch_range(
                requester_id=requester_id,
                owner_handle=handle,
                source_data_type=group.source_data_type,
                start_date=start_date,
                end_date=end_date,
            )
            day_values = []
            for item in data:
                val = item.get("value_numeric")
                if val is not None:
                    day_values.append(val)
            if not day_values:
                return 0.0
            return summarize_daily_values(group.source_data_type, day_values) or 0.0
        except Exception:
            return 0.0

    def leave_group(self, user_id: str, group_id: str) -> None:
        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("User not found")
            user_handle = make_handle(user)
            member = self.uow.leaderboard_members.get_member(group_id, user_handle)
            if not member:
                raise NotFoundError("You are not a member of this challenge")
            self.uow.leaderboard_members.delete(member)

    def delete_group(self, creator_id: str, group_id: str) -> None:
        with self.uow:
            group = self.uow.leaderboard_groups.get_by_id(group_id)
            if not group:
                raise NotFoundError("Challenge group not found")
            if group.creator_id != creator_id:
                raise ForbiddenError("Only the creator can disband this challenge")
        self.uow.leaderboard_groups.delete(group)
