from sqlmodel import select
from salus.models.sharing import LeaderboardGroup, LeaderboardMember
from salus.repositories.base import Repository
from salus.repositories.protocols import ILeaderboardGroupRepository, ILeaderboardMemberRepository


class LeaderboardGroupRepository(Repository[LeaderboardGroup], ILeaderboardGroupRepository):
    model = LeaderboardGroup

    def find_by_creator(self, creator_id: int) -> list[LeaderboardGroup]:
        stmt = select(LeaderboardGroup).where(
            LeaderboardGroup.creator_id == creator_id
        )
        return list(self.session.exec(stmt).all())

    def find_by_invite_code(self, code: str) -> LeaderboardGroup | None:
        stmt = select(LeaderboardGroup).where(
            LeaderboardGroup.invite_code == code
        )
        return self.session.exec(stmt).first()

    def find_joined_by_user(self, user_handle: str) -> list[LeaderboardGroup]:
        # Find all groups where user_handle is a member with active status
        stmt = (
            select(LeaderboardGroup)
            .join(LeaderboardMember)
            .where(
                LeaderboardMember.user_handle == user_handle,
                LeaderboardMember.status == "active"
            )
        )
        return list(self.session.exec(stmt).all())


class LeaderboardMemberRepository(Repository[LeaderboardMember], ILeaderboardMemberRepository):
    model = LeaderboardMember

    def find_by_group_id(self, group_id: int) -> list[LeaderboardMember]:
        stmt = select(LeaderboardMember).where(
            LeaderboardMember.group_id == group_id
        )
        return list(self.session.exec(stmt).all())

    def get_member(self, group_id: int, user_handle: str) -> LeaderboardMember | None:
        stmt = select(LeaderboardMember).where(
            LeaderboardMember.group_id == group_id,
            LeaderboardMember.user_handle == user_handle
        )
        return self.session.exec(stmt).first()
