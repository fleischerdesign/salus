from sqlmodel import select, desc

from salus.models.sharing import FederatedAccessLog
from salus.repositories.base import Repository
from salus.repositories.protocols import IFederatedAccessLogRepository


class FederatedAccessLogRepository(Repository[FederatedAccessLog], IFederatedAccessLogRepository):
    model = FederatedAccessLog

    def find_by_owner(self, owner_id: int) -> list[FederatedAccessLog]:
        stmt = (
            select(FederatedAccessLog)
            .where(FederatedAccessLog.owner_id == owner_id)
            .order_by(desc(FederatedAccessLog.accessed_at))  # type: ignore[arg-type]
        )
        return list(self.session.exec(stmt).all())
