from sqlmodel import col, select

from salus.models.user_source_preference import UserSourcePreference
from salus.repositories.base import Repository
from salus.repositories.protocols import IUserSourcePreferenceRepository


class UserSourcePreferenceRepository(
    Repository[UserSourcePreference], IUserSourcePreferenceRepository
):
    model = UserSourcePreference

    def find_by_user(self, user_id: str) -> list[UserSourcePreference]:
        return list(
            self.session.exec(
                select(UserSourcePreference)
                .where(
                    col(UserSourcePreference.user_id) == user_id,
                    UserSourcePreference.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
                .order_by(col(UserSourcePreference.metric_code), col(UserSourcePreference.priority_rank))
            ).all()
        )

    def find_by_user_and_metric(self, user_id: str, metric_code: str) -> list[UserSourcePreference]:
        return list(
            self.session.exec(
                select(UserSourcePreference)
                .where(
                    col(UserSourcePreference.user_id) == user_id,
                    col(UserSourcePreference.metric_code) == metric_code,
                    UserSourcePreference.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
                .order_by(col(UserSourcePreference.priority_rank))
            ).all()
        )

    def find_by_user_metric_source(
        self, user_id: str, metric_code: str, source: str
    ) -> UserSourcePreference | None:
        stmt = select(UserSourcePreference).where(
            col(UserSourcePreference.user_id) == user_id,
            col(UserSourcePreference.metric_code) == metric_code,
            col(UserSourcePreference.source) == source,
            UserSourcePreference.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
        return self.session.exec(stmt).first()
