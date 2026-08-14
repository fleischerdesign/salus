from sqlmodel import select

from salus.models.fasting import FastingProtocol, FastingSession
from salus.repositories.base import Repository


class FastingSessionRepository(Repository[FastingSession]):
    model = FastingSession

    def find_active_by_user(self, user_id: str) -> FastingSession | None:
        return self.session.exec(
            select(FastingSession).where(
                FastingSession.user_id == user_id,
                FastingSession.ended_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                FastingSession.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
            )
        ).first()

    def find_by_user(self, user_id: str) -> list[FastingSession]:
        return list(
            self.session.exec(
                select(FastingSession).where(
                    FastingSession.user_id == user_id,
                    FastingSession.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(FastingSession.started_at.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )


class FastingProtocolRepository(Repository[FastingProtocol]):
    model = FastingProtocol

    def find_by_user(self, user_id: str) -> list[FastingProtocol]:
        return list(
            self.session.exec(
                select(FastingProtocol).where(
                    FastingProtocol.user_id == user_id,
                    FastingProtocol.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(FastingProtocol.name)  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )
