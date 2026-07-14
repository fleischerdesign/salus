from datetime import datetime, timezone
from sqlmodel import select
from salus.models import MetricType
from salus.models.sharing import ConnectionStatus, SharingRelationship
from salus.repositories.base import Repository
from salus.repositories.protocols import ISharingRepository


class SharingRepository(Repository[SharingRelationship], ISharingRepository):
    model = SharingRelationship

    def find_by_owner(self, owner_id: str) -> list[SharingRelationship]:
        stmt = select(SharingRelationship).where(
            SharingRelationship.owner_id == owner_id
        )
        return list(self.session.exec(stmt).all())

    def find_by_grantee(self, grantee_handle: str) -> list[SharingRelationship]:
        stmt = select(SharingRelationship).where(
            SharingRelationship.grantee_handle == grantee_handle
        )
        return list(self.session.exec(stmt).all())

    def get_active_relationship(
        self, owner_id: str, grantee_handle: str, metric_type_id: str
    ) -> SharingRelationship | None:
        now = datetime.now(timezone.utc)
        stmt = select(SharingRelationship).where(
            SharingRelationship.owner_id == owner_id,
            SharingRelationship.grantee_handle == grantee_handle,
            SharingRelationship.metric_type_id == metric_type_id,
            SharingRelationship.status == ConnectionStatus.ACTIVE,
            (SharingRelationship.expiration_date == None)  # type: ignore # noqa: E711
            | (SharingRelationship.expiration_date > now),  # type: ignore
        )
        return self.session.exec(stmt).first()

    def find_pending_by_grantee(self, grantee_handle: str) -> list[SharingRelationship]:
        stmt = select(SharingRelationship).where(
            SharingRelationship.grantee_handle == grantee_handle,
            SharingRelationship.status == ConnectionStatus.PENDING,
        )
        return list(self.session.exec(stmt).all())

    def find_active_by_grantee(self, grantee_handle: str) -> list[SharingRelationship]:
        now = datetime.now(timezone.utc)
        stmt = select(SharingRelationship).where(
            SharingRelationship.grantee_handle == grantee_handle,
            SharingRelationship.status == ConnectionStatus.ACTIVE,
            (SharingRelationship.expiration_date == None)  # type: ignore # noqa: E711
            | (SharingRelationship.expiration_date > now),  # type: ignore
        )
        return list(self.session.exec(stmt).all())

    def find_active_between(
        self, user_a_id: str, user_b_handle: str
    ) -> SharingRelationship | None:
        now = datetime.now(timezone.utc)
        stmt = select(SharingRelationship).where(
            SharingRelationship.owner_id == user_a_id,
            SharingRelationship.grantee_handle == user_b_handle,
            SharingRelationship.status == ConnectionStatus.ACTIVE,
            (SharingRelationship.expiration_date == None)  # type: ignore # noqa: E711
            | (SharingRelationship.expiration_date > now),  # type: ignore
        )
        return self.session.exec(stmt).first()

    def find_pending_relationship(
        self, owner_id: str, grantee_handle: str, metric_type_id: str
    ) -> SharingRelationship | None:
        stmt = select(SharingRelationship).where(
            SharingRelationship.owner_id == owner_id,
            SharingRelationship.grantee_handle == grantee_handle,
            SharingRelationship.metric_type_id == metric_type_id,
            SharingRelationship.status == ConnectionStatus.PENDING,
        )
        return self.session.exec(stmt).first()

    def find_active_for_remote_owner(
        self, owner_handle: str, data_type: str
    ) -> SharingRelationship | None:
        stmt = (
            select(SharingRelationship)
            .join(MetricType, SharingRelationship.metric_type_id == MetricType.id)  # type: ignore[arg-type]
            .where(
                SharingRelationship.grantee_handle == owner_handle,
                SharingRelationship.status == ConnectionStatus.ACTIVE,
                MetricType.source_data_type == data_type,
            )
        )
        return self.session.exec(stmt).first()

    def find_pending_by_token_hash(
        self, token_hash: str
    ) -> SharingRelationship | None:
        stmt = select(SharingRelationship).where(
            SharingRelationship.api_token_hash == token_hash,
            SharingRelationship.status == ConnectionStatus.PENDING,
        )
        return self.session.exec(stmt).first()

    def find_active_by_owner_id(
        self, owner_id: str
    ) -> list[SharingRelationship]:
        now = datetime.now(timezone.utc)
        stmt = select(SharingRelationship).where(
            SharingRelationship.owner_id == owner_id,
            SharingRelationship.status == ConnectionStatus.ACTIVE,
            (SharingRelationship.expiration_date == None)  # type: ignore # noqa: E711
            | (SharingRelationship.expiration_date > now),  # type: ignore
        )
        return list(self.session.exec(stmt).all())

    def find_active_by_owner_and_data_type(
        self, owner_id: str, data_type: str
    ) -> list[SharingRelationship]:
        stmt = (
            select(SharingRelationship)
            .join(MetricType, SharingRelationship.metric_type_id == MetricType.id)  # type: ignore[arg-type]
            .where(
                SharingRelationship.owner_id == owner_id,
                SharingRelationship.status == ConnectionStatus.ACTIVE,
                MetricType.source_data_type == data_type,
            )
        )
        return list(self.session.exec(stmt).all())

    def find_active_by_token_hash(
        self, token_hash: str
    ) -> SharingRelationship | None:
        now = datetime.now(timezone.utc)
        stmt = select(SharingRelationship).where(
            SharingRelationship.api_token_hash == token_hash,
            SharingRelationship.status == ConnectionStatus.ACTIVE,
            (SharingRelationship.expiration_date == None)  # type: ignore # noqa: E711
            | (SharingRelationship.expiration_date > now),  # type: ignore
        )
        return self.session.exec(stmt).first()

    def find_active_with_owner_metric_and_grantee(
        self, owner_id: str, grantee_handle: str, metric_type_id: str
    ) -> SharingRelationship | None:
        now = datetime.now(timezone.utc)
        stmt = select(SharingRelationship).where(
            SharingRelationship.owner_id == owner_id,
            SharingRelationship.grantee_handle == grantee_handle,
            SharingRelationship.metric_type_id == metric_type_id,
            SharingRelationship.status == ConnectionStatus.ACTIVE,
            (SharingRelationship.expiration_date == None)  # type: ignore # noqa: E711
            | (SharingRelationship.expiration_date > now),  # type: ignore
        )
        return self.session.exec(stmt).first()
