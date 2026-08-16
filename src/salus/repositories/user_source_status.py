from sqlmodel import col, select

from salus.models.user_source_status import UserSourceStatus
from salus.repositories.base import Repository
from salus.repositories.protocols import IUserSourceStatusRepository


class UserSourceStatusRepository(
    Repository[UserSourceStatus], IUserSourceStatusRepository
):
    model = UserSourceStatus

    def find_by_user(self, user_id: str) -> list[UserSourceStatus]:
        return list(
            self.session.exec(
                select(UserSourceStatus)
                .where(
                    col(UserSourceStatus.user_id) == user_id,
                    UserSourceStatus.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
                .order_by(col(UserSourceStatus.source))
            ).all()
        )

    def find_by_user_source(
        self, user_id: str, source: str
    ) -> UserSourceStatus | None:
        stmt = select(UserSourceStatus).where(
            col(UserSourceStatus.user_id) == user_id,
            col(UserSourceStatus.source) == source,
            UserSourceStatus.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
        return self.session.exec(stmt).first()
