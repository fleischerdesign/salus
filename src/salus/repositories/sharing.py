from datetime import datetime, timezone
from sqlmodel import select
from salus.models.sharing import ConnectionStatus, SharingRelationship
from salus.repositories.base import Repository
from salus.repositories.protocols import ISharingRepository


class SharingRepository(Repository[SharingRelationship], ISharingRepository):
    model = SharingRelationship

    def find_by_owner(self, owner_id: int) -> list[SharingRelationship]:
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
        self, owner_id: int, grantee_handle: str, metric_type_id: int
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
