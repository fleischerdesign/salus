from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlmodel import select

from salus.models.sharing import FederatedMeasurementCache
from salus.repositories.base import Repository


class FederatedMeasurementCacheRepository(Repository[FederatedMeasurementCache]):
    model = FederatedMeasurementCache

    def get_cache(
        self,
        owner_handle: str,
        data_type: str,
        date_str: str,
        max_age_seconds: int = 60,
    ) -> FederatedMeasurementCache | None:
        if max_age_seconds <= 0:
            return None
        freshness = datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds)
        stmt = select(FederatedMeasurementCache).where(
            FederatedMeasurementCache.owner_handle == owner_handle,
            FederatedMeasurementCache.data_type == data_type,
            FederatedMeasurementCache.date_str == date_str,
            FederatedMeasurementCache.fetched_at >= freshness,
        )
        return self.session.exec(stmt).first()

    def upsert_cache(
        self,
        owner_handle: str,
        data_type: str,
        date_str: str,
        value_numeric: Optional[float],
        value_json: Optional[str],
    ) -> FederatedMeasurementCache:
        stmt = select(FederatedMeasurementCache).where(
            FederatedMeasurementCache.owner_handle == owner_handle,
            FederatedMeasurementCache.data_type == data_type,
            FederatedMeasurementCache.date_str == date_str,
        )
        existing = self.session.exec(stmt).first()
        if existing:
            existing.value_numeric = value_numeric
            existing.value_json = value_json
            existing.fetched_at = datetime.now(timezone.utc)
            self.session.add(existing)
            return existing

        entry = FederatedMeasurementCache(
            owner_handle=owner_handle,
            data_type=data_type,
            date_str=date_str,
            value_numeric=value_numeric,
            value_json=value_json,
        )
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry
