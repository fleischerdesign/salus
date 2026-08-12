from datetime import datetime, timedelta, timezone

from sqlalchemy import delete
from sqlmodel import select

from salus.models.sync_push_log import SyncPushLog
from salus.repositories.base import Repository
from salus.services.constants import DEDUP_TTL_HOURS
from salus.repositories.protocols import ISyncPushLogRepository


class SyncPushLogRepository(Repository[SyncPushLog], ISyncPushLogRepository):
    model = SyncPushLog

    def cleanup_expired(self, ttl_hours: int = DEDUP_TTL_HOURS) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=ttl_hours)
        result = self.session.execute(
            delete(SyncPushLog).where(SyncPushLog.created_at < cutoff)  # type: ignore[reportArgumentType]
        )
        return result.rowcount or 0  # type: ignore[reportAttributeAccessIssue]

    def find_by_client_ids(self, client_ids: list[str]) -> list[SyncPushLog]:
        stmt = select(SyncPushLog).where(
            SyncPushLog.client_id.in_(client_ids)  # type: ignore[arg-type]
        )
        return list(self.session.exec(stmt).all())
