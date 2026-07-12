from datetime import datetime, timedelta, timezone
from sqlmodel import select

from salus.models.sync_push_log import SyncPushLog
from salus.repositories.base import Repository


class SyncPushLogRepository(Repository[SyncPushLog]):
    model = SyncPushLog

    def cleanup_expired(self, ttl_hours: int = 24) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=ttl_hours)
        stmt = select(SyncPushLog).where(SyncPushLog.created_at < cutoff)
        expired = list(self.session.exec(stmt).all())
        for entry in expired:
            self.session.delete(entry)
        return len(expired)

    def find_by_client_ids(self, client_ids: list[str]) -> list[SyncPushLog]:
        stmt = select(SyncPushLog).where(
            SyncPushLog.client_id.in_(client_ids)  # type: ignore[arg-type]
        )
        return list(self.session.exec(stmt).all())
