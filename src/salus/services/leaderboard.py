# pyright: reportOptionalOperand=false
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from salus.services.sharing import SharingService

from salus.exceptions import ForbiddenError, NotFoundError, ConflictError
from salus.models.sharing import (
    LeaderboardGroup,
    LeaderboardMember,
)
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services._helpers import uid


class LeaderboardService:
    def __init__(
        self, uow: IUnitOfWork, sharing_svc: Optional["SharingService"] = None
    ) -> None:
        self.uow = uow
        self.sharing_svc = sharing_svc

    def create_group(
        self,
        creator_id: int,
        name: str,
        metric_type_code: str = "steps",
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
                metric_type_code=metric_type_code,
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
                user_handle=f"@{creator.username}",
                status="active",
            )
            self.uow.leaderboard_members.create(member)
            self.uow.commit()
            return group

    def join_by_code(self, user_id: int, invite_code: str) -> LeaderboardGroup:
        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("User not found")

            group = self.uow.leaderboard_groups.find_by_invite_code(invite_code)
            if not group:
                raise NotFoundError("Challenge group not found for this invite code")

            assert group.id is not None
            # Check if user is already a member
            user_handle = f"@{user.username}"
            existing = self.uow.leaderboard_members.get_member(group.id, user_handle)
            if existing:
                if existing.status == "active":
                    raise ConflictError("You are already a member of this challenge")
                else:
                    existing.status = "active"
                    self.uow.leaderboard_members.update(existing)
                    self.uow.commit()
                    return group

            # Connection prerequisite check: user must have a connection with group creator
            creator = self.uow.users.get_by_id(group.creator_id)
            if not creator:
                raise NotFoundError("Creator of the group no longer exists")

            creator_handle = f"@{creator.username}"

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
            self.uow.commit()
            return group

    def list_my_groups(self, user_id: int) -> list[LeaderboardGroup]:
        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                return []

            user_handle = f"@{user.username}"
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

    def get_group_rankings(self, group_id: int, current_user_id: int) -> dict:
        with self.uow:
            group = self.uow.leaderboard_groups.get_by_id(group_id)
            if not group:
                raise NotFoundError("Challenge group not found")
            assert group.id is not None

            current_user = self.uow.users.get_by_id(current_user_id)
            if not current_user:
                raise NotFoundError("User not found")

            # Verify current user is a member
            current_handle = f"@{current_user.username}"
            member_check = self.uow.leaderboard_members.get_member(
                group.id, current_handle
            )
            if not member_check or member_check.status != "active":
                raise ForbiddenError("You are not a member of this challenge group")

            # Determine timeframe start/end dates
            now = datetime.now(timezone.utc)
            if group.time_frame == "weekly":
                start_date = (now - timedelta(days=7)).date()
            elif group.time_frame == "monthly":
                start_date = (now - timedelta(days=30)).date()
            else:
                start_date = (
                    group.start_date.date()
                    if group.start_date
                    else (now - timedelta(days=7)).date()
                )

            end_date = group.end_date.date() if group.end_date else now.date()

            # Retrieve active members
            members = self.uow.leaderboard_members.find_by_group_id(group.id)
            active_members = [m for m in members if m.status == "active"]

            rankings = []
            for m in active_members:
                handle = m.user_handle
                score = 0.0

                if ":" not in handle:
                    # Local User query
                    username = handle[1:]
                    local_user = self.uow.users.get_by_username(username)
                    if local_user:
                        if group.metric_type_code == "workouts":
                            since_dt = datetime.combine(
                                start_date, datetime.min.time(), tzinfo=timezone.utc
                            )
                            until_dt = datetime.combine(
                                end_date, datetime.max.time(), tzinfo=timezone.utc
                            )
                            score = float(
                                self.uow.workout_sessions.count_completed_in_range(
                                    uid(local_user), since_dt, until_dt
                                )
                            )
                        else:
                            # Sum/Avg measurement metrics
                            measurements = self.uow.measurements.find_all(
                                user_id=uid(local_user),
                                data_types=[group.metric_type_code],
                            )
                            day_values = [
                                ms.value_numeric
                                for ms in measurements
                                if ms.start_time.date() >= start_date
                                and ms.start_time.date() <= end_date
                                and ms.value_numeric is not None
                            ]
                            if day_values:
                                if group.metric_type_code in ("steps", "water"):
                                    score = float(sum(day_values))
                                else:
                                    score = float(sum(day_values) / len(day_values))
                else:
                    # Remote User query
                    score = 0.0
                    if self.sharing_svc:
                        try:
                            day_values = []
                            curr_date = start_date
                            while curr_date <= end_date:
                                date_str = curr_date.strftime("%Y-%m-%d")
                                try:
                                    data = self.sharing_svc.resolve_and_fetch(
                                        requester_id=current_user_id,
                                        owner_handle=handle,
                                        data_type=group.metric_type_code,
                                        date_str=date_str,
                                    )
                                    for item in data:
                                        val = item.get("value_numeric")
                                        if val is not None:
                                            day_values.append(val)
                                except Exception:
                                    pass
                                curr_date += timedelta(days=1)

                            if day_values:
                                if group.metric_type_code in ("steps", "water"):
                                    score = float(sum(day_values))
                                else:
                                    score = float(sum(day_values) / len(day_values))
                        except Exception:
                            score = 0.0

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

    def leave_group(self, user_id: int, group_id: int) -> None:
        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("User not found")
            user_handle = f"@{user.username}"
            member = self.uow.leaderboard_members.get_member(group_id, user_handle)
            if not member:
                raise NotFoundError("You are not a member of this challenge")
            self.uow.leaderboard_members.delete(member)
            self.uow.commit()

    def delete_group(self, creator_id: int, group_id: int) -> None:
        with self.uow:
            group = self.uow.leaderboard_groups.get_by_id(group_id)
            if not group:
                raise NotFoundError("Challenge group not found")
            if group.creator_id != creator_id:
                raise ForbiddenError("Only the creator can disband this challenge")
            self.uow.leaderboard_groups.delete(group)
            self.uow.commit()
