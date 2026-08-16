import logging
from datetime import date, datetime, tzinfo
from typing import TYPE_CHECKING, Optional

from sqlalchemy import desc, func
from sqlmodel import col, select

from salus.models.measurement import Measurement
from salus.repositories.base import Repository
from salus.repositories.protocols import IMeasurementRepository
from salus.services.timezone import local_date

if TYPE_CHECKING:
    from salus.services.plugin.hooks import HookRegistry

logger = logging.getLogger("salus.repositories.measurement")


class MeasurementRepository(Repository[Measurement], IMeasurementRepository):
    model = Measurement

    def __init__(self, session, registry: Optional["HookRegistry"] = None) -> None:
        super().__init__(session)
        self.registry = registry

    def count_by_metric_type(self, metric_code: str, user_id: str) -> int:
        count_stmt = (
            select(func.count())
            .select_from(Measurement)
            .where(
                Measurement.metric_code == metric_code,
                Measurement.user_id == user_id,
                Measurement.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
            )
        )
        return self.session.exec(count_stmt).one()

    def get_latest_by_metric_type(
        self, metric_code: str, user_id: str
    ) -> Measurement | None:
        stmt = (
            select(Measurement)
            .where(
                Measurement.metric_code == metric_code,
                Measurement.user_id == user_id,
                Measurement.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
            )
            .order_by(desc(Measurement.start_time))  # pyright: ignore[reportArgumentType]
            .limit(1)
        )
        return self.session.exec(stmt).first()

    def find_start_dates(self, user_id: str, tz: tzinfo | None = None) -> list[date]:
        stmt = select(col(Measurement.start_time)).where(
            Measurement.user_id == user_id,
            Measurement.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
        rows = [row for row in self.session.exec(stmt).all() if row is not None]
        if tz is None:
            return [row.date() for row in rows]
        return [local_date(row, tz) for row in rows]

    def find_by_metric_type(
        self, metric_code: str, user_id: str | None = None
    ) -> list[Measurement]:
        stmt = select(Measurement).where(Measurement.metric_code == metric_code)
        if user_id is not None:
            stmt = stmt.where(Measurement.user_id == user_id)
        stmt = stmt.order_by(desc(Measurement.start_time))  # pyright: ignore[reportArgumentType]
        results = list(self.session.exec(stmt).all())

        if self.registry and user_id is not None:
            for synth in self.registry.metric_synthesizers:
                try:
                    synth_records = synth.synthesize(user_id, results)
                    if synth_records:
                        # Filter to only return the ones matching the requested metric type if needed
                        results.extend(
                            [
                                r
                                for r in synth_records
                                if r.metric_code == metric_code
                            ]
                        )
                except Exception as e:
                    logger.error(f"Error in metric synthesizer: {e}")
        return results

    def find_all(
        self,
        user_id: str | None = None,
        source_data_types: list[str] | None = None,
        sources: list[str] | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int | None = None,
    ) -> list[Measurement]:
        stmt = select(Measurement)
        if user_id is not None:
            stmt = stmt.where(Measurement.user_id == user_id)
        stmt = stmt.where(Measurement.deleted_at.is_(None))  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        if source_data_types:
            stmt = stmt.where(Measurement.source_data_type.in_(source_data_types))  # pyright: ignore[reportAttributeAccessIssue]
        if sources:
            stmt = stmt.where(Measurement.source.in_(sources))  # pyright: ignore[reportAttributeAccessIssue]
        if since is not None:
            stmt = stmt.where(Measurement.start_time >= since)
        if until is not None:
            stmt = stmt.where(Measurement.start_time < until)
        stmt = stmt.order_by(desc(Measurement.start_time))  # pyright: ignore[reportArgumentType]
        if limit:
            stmt = stmt.limit(limit)
        results = list(self.session.exec(stmt).all())

        if self.registry and user_id is not None:
            for synth in self.registry.metric_synthesizers:
                try:
                    synth_records = synth.synthesize(user_id, results)
                    if synth_records:
                        filtered = synth_records
                        if source_data_types:
                            filtered = [
                                r for r in filtered if r.source_data_type in source_data_types
                            ]
                        results.extend(filtered)
                except Exception as e:
                    logger.error(f"Error in metric synthesizer: {e}")
        return results

    def find_latest(
        self, source_data_type: str, user_id: str | None = None
    ) -> Measurement | None:
        results = self.find_all(user_id=user_id, source_data_types=[source_data_type], limit=1)
        return results[0] if results else None

    def upsert_all(self, records: list[Measurement]) -> tuple[int, int, list[Measurement]]:
        """Insert-or-update by ``(external_id, source)``.

        Returns ``(inserted, duplicates, persisted)`` where ``persisted`` holds the
        final objects (new records for inserts, the matched rows for updates) so
        callers can post-process the actually-persisted entities.
        """
        inserted = 0
        duplicates = 0
        persisted: list[Measurement] = []

        # 1. Gather all external IDs to query existing records in chunks
        external_ids = [rec.external_id for rec in records if rec.external_id]
        existing_map: dict[tuple[str, str, str], Measurement] = {}

        if external_ids:
            # Chunking to avoid SQLite parameter limit (usually 999)
            chunk_size = 900
            for i in range(0, len(external_ids), chunk_size):
                chunk = external_ids[i : i + chunk_size]
                stmt = select(Measurement).where(
                    Measurement.external_id.in_(chunk)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
                chunk_existing = self.session.exec(stmt).all()
                for ext in chunk_existing:
                    if ext.external_id:
                        existing_map[(ext.user_id or "", ext.external_id, ext.source)] = ext

        # 2. Match and update/insert
        for rec in records:
            existing = None
            if rec.external_id:
                existing = existing_map.get((rec.user_id or "", rec.external_id, rec.source))

            if existing is not None:
                existing.value_numeric = rec.value_numeric
                existing.value_text = rec.value_text
                existing.value_json = rec.value_json
                existing.start_time = rec.start_time
                existing.end_time = rec.end_time
                self.session.add(existing)
                duplicates += 1
                persisted.append(existing)
            else:
                self.session.add(rec)
                if rec.external_id:
                    existing_map[(rec.user_id or "", rec.external_id, rec.source)] = rec
                inserted += 1
                persisted.append(rec)

        # 3. Commit the transaction once at the end
        self.session.commit()
        return inserted, duplicates, persisted

    def find_by_date_range(
        self, user_id: str, source_data_types: list[str], since: datetime, until: datetime
    ) -> list[Measurement]:
        return self.find_all(
            user_id=user_id, source_data_types=source_data_types, since=since, until=until
        )

    def find_recent_entries(self, user_id: str, limit: int = 20) -> list[Measurement]:
        stmt = (
            select(Measurement)
            .where(
                Measurement.user_id == user_id,
                Measurement.source == "manual",
                Measurement.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
            )
            .order_by(desc(Measurement.start_time))  # pyright: ignore[reportArgumentType]
            .limit(limit)
        )
        return list(self.session.exec(stmt).all())

    def find_by_external_id(self, external_id: str, source: str | None = None) -> Measurement | None:
        stmt = select(Measurement).where(
            Measurement.external_id == external_id,
            Measurement.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
        if source:
            stmt = stmt.where(Measurement.source == source)
        return self.session.exec(stmt).first()
