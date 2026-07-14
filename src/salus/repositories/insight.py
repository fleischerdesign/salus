from sqlalchemy import desc
from sqlmodel import select

from salus.models.insight import Insight
from salus.repositories.base import Repository
from salus.repositories.protocols import IInsightRepository


class InsightRepository(Repository[Insight], IInsightRepository):
    model = Insight

    def find_by_user_and_date(self, user_id: str, query_date: str) -> Insight | None:
        stmt = (
            select(Insight)
            .where(Insight.user_id == user_id, Insight.query_date == query_date)
            .limit(1)
        )
        return self.session.exec(stmt).first()

    def list_by_user(self, user_id: str, limit: int = 30) -> list[Insight]:
        stmt = (
            select(Insight)
            .where(Insight.user_id == user_id)
            .order_by(desc(Insight.created_at))  # pyright: ignore[reportArgumentType]
            .limit(limit)
        )
        return list(self.session.exec(stmt).all())
