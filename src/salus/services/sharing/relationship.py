import logging
import secrets
import hashlib
import threading
from datetime import datetime, timezone, timedelta
from typing import Optional

from salus.exceptions import NotFoundError, ConflictError
from salus.models.sharing import ConnectionStatus, SharingRelationship
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.sharing import PeerConnection, PeerMetricInfo
from salus.services._helpers import DEFAULT_METRIC_COLOR

logger = logging.getLogger("salus.services.sharing.relationship")


class RelationshipService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    @staticmethod
    def normalize_handle(handle: str) -> str:
        handle = handle.strip()
        if not handle.startswith("@"):
            handle = f"@{handle}"
        return handle

    @staticmethod
    def is_remote(handle: str) -> bool:
        return ":" in handle

    @staticmethod
    def format_sync_age(sync_time: datetime) -> str:
        delta = datetime.now(timezone.utc) - sync_time
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            mins = seconds // 60
            return f"{mins} min ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours}h ago"
        else:
            days = seconds // 86400
            return f"{days}d ago"

    def create_relationship(
        self,
        owner_id: str,
        grantee_handle: str,
        metric_type_id: str,
        aggregation_level: str = "daily_summary",
        expiration_days: Optional[int] = None,
    ) -> SharingRelationship:
        grantee_handle = self.normalize_handle(grantee_handle)

        with self.uow:
            metric = self.uow.metric_types.get_by_id(metric_type_id)
            if not metric or metric.user_id != owner_id:
                raise NotFoundError("Metric type not found or access denied")

            if not self.is_remote(grantee_handle):
                username = grantee_handle[1:]
                local_user = self.uow.users.get_by_username(username)
                if not local_user:
                    raise NotFoundError(f"Local user '{username}' not found")

            existing = self.uow.sharing_relationships.get_active_relationship(
                owner_id=owner_id,
                grantee_handle=grantee_handle,
                metric_type_id=metric_type_id,
            )
            if existing:
                raise ConflictError(
                    "Active sharing relationship already exists for this metric and user"
                )

            pending = self.uow.sharing_relationships.find_pending_relationship(
                owner_id, grantee_handle, metric_type_id
            )
            if pending:
                raise ConflictError(
                    "A pending sharing invitation already exists for this metric and user"
                )

            expiration_date = None
            if expiration_days is not None:
                expiration_date = datetime.now(timezone.utc) + timedelta(
                    days=expiration_days
                )

            raw_token = secrets.token_hex(20)
            token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

            rel = SharingRelationship(
                owner_id=owner_id,
                grantee_handle=grantee_handle,
                metric_type_id=metric_type_id,
                aggregation_level=aggregation_level,
                expiration_date=expiration_date,
                status=ConnectionStatus.PENDING,
                api_token_hash=token_hash,
            )
        self.uow.sharing_relationships.create(rel)
        object.__setattr__(rel, "raw_token", raw_token)
        return rel

    def accept_relationship(
        self,
        grantee_user_id: str,
        relationship_id: str,
        notify_callback: Optional[callable] = None,  # type: ignore[type-arg]
    ) -> SharingRelationship:
        with self.uow:
            user = self.uow.users.get_by_id(grantee_user_id)
            if not user:
                raise NotFoundError("User not found")
            grantee_handle = f"@{user.username}"

            rel = self.uow.sharing_relationships.get_by_id(relationship_id)
            if not rel or rel.grantee_handle != grantee_handle:
                raise NotFoundError("Sharing relationship not found")

            if rel.status != ConnectionStatus.PENDING:
                raise ConflictError("Sharing invitation is not in pending state")

            rel.status = ConnectionStatus.ACTIVE
            rel.updated_at = datetime.now(timezone.utc)
            self.uow.sharing_relationships.update(rel)

            if notify_callback:
                threading.Thread(
                    target=notify_callback, args=(rel,), daemon=True
                ).start()
            return rel

    def decline_relationship(
        self, grantee_user_id: str, relationship_id: str
    ) -> SharingRelationship:
        with self.uow:
            user = self.uow.users.get_by_id(grantee_user_id)
            if not user:
                raise NotFoundError("User not found")
            grantee_handle = f"@{user.username}"

            rel = self.uow.sharing_relationships.get_by_id(relationship_id)
            if not rel or rel.grantee_handle != grantee_handle:
                raise NotFoundError("Sharing relationship not found")

            if rel.status != ConnectionStatus.PENDING:
                raise ConflictError("Sharing invitation is not in pending state")

            rel.status = ConnectionStatus.DECLINED
            rel.updated_at = datetime.now(timezone.utc)
            self.uow.sharing_relationships.update(rel)
            return rel

    def list_relationships(self, owner_id: str) -> list[SharingRelationship]:
        with self.uow:
            return self.uow.sharing_relationships.find_by_owner(owner_id)

    def deactivate_relationship(self, owner_id: str, relationship_id: str) -> None:
        with self.uow:
            rel = self.uow.sharing_relationships.get_by_id(relationship_id)
            if not rel or rel.owner_id != owner_id:
                raise NotFoundError("Sharing relationship not found")
            rel.status = ConnectionStatus.REVOKED
            rel.updated_at = datetime.now(timezone.utc)
            self.uow.sharing_relationships.update(rel)

    def process_federation_accept(self, token: str, owner_handle: str) -> None:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        with self.uow:
            rel = self.uow.sharing_relationships.find_pending_by_token_hash(token_hash)
            if not rel:
                raise NotFoundError(
                    "Pending sharing relationship not found for the provided token"
                )
            rel.status = ConnectionStatus.ACTIVE
            rel.updated_at = datetime.now(timezone.utc)
            self.uow.sharing_relationships.update(rel)

    def get_peer_connections(self, user_id: str) -> list[PeerConnection]:
        peers: dict[str, PeerConnection] = {}

        def _peer_key(handle: str) -> str:
            return handle.lower()

        def _ensure_peer(handle: str, is_remote: bool) -> PeerConnection:
            key = _peer_key(handle)
            if key not in peers:
                peers[key] = PeerConnection(handle=handle, is_remote=is_remote)
            return peers[key]

        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("User not found")
            user_handle = f"@{user.username}"

            all_outgoing = self.uow.sharing_relationships.find_by_owner(user_id)
            all_incoming = self.uow.sharing_relationships.find_by_grantee(user_handle)

            peer_sync_times: dict[str, datetime] = {}

            for rel in all_outgoing:
                handle = rel.grantee_handle
                peer = _ensure_peer(handle, self.is_remote(handle))
                rel_is_pending = rel.status == ConnectionStatus.PENDING
                rel_is_active = rel.status == ConnectionStatus.ACTIVE
                if rel_is_pending:
                    peer.is_pending = True
                if rel_is_active or rel_is_pending:
                    peer.metrics.append(
                        PeerMetricInfo(
                            metric_name=rel.metric_type.name,
                            icon=getattr(rel.metric_type, "icon", "monitoring"),
                            color=getattr(rel.metric_type, "color", DEFAULT_METRIC_COLOR),
                            aggregation=rel.aggregation_level,
                            direction="outgoing",
                            relationship_id=rel.id or "",
                        )
                    )
                if rel.expiration_date and (
                    peer.expiration is None or rel.expiration_date < peer.expiration
                ):
                    peer.expiration = rel.expiration_date
                if rel.last_sync_at:
                    key = _peer_key(handle)
                    if (
                        key not in peer_sync_times
                        or rel.last_sync_at > peer_sync_times[key]
                    ):
                        peer_sync_times[key] = rel.last_sync_at

            for rel in all_incoming:
                if not rel.owner:
                    continue
                owner_username = rel.owner.username
                handle = f"@{owner_username}"
                peer = _ensure_peer(handle, False)
                rel_is_pending = rel.status == ConnectionStatus.PENDING
                rel_is_active = rel.status == ConnectionStatus.ACTIVE
                if rel_is_pending:
                    peer.is_pending = True
                if rel_is_active:
                    peer.metrics.append(
                        PeerMetricInfo(
                            metric_name=rel.metric_type.name,
                            icon=getattr(rel.metric_type, "icon", "monitoring"),
                            color=getattr(rel.metric_type, "color", DEFAULT_METRIC_COLOR),
                            aggregation=rel.aggregation_level,
                            direction="incoming",
                            relationship_id=rel.id or "",
                        )
                    )
                if rel.expiration_date and (
                    peer.expiration is None or rel.expiration_date < peer.expiration
                ):
                    peer.expiration = rel.expiration_date

        for peer in peers.values():
            has_out = any(m.direction == "outgoing" for m in peer.metrics)
            has_in = any(m.direction == "incoming" for m in peer.metrics)
            peer.is_mutual = has_out and has_in
            if peer.is_remote:
                sync_time = peer_sync_times.get(_peer_key(peer.handle))
                peer.last_sync = self.format_sync_age(sync_time) if sync_time else None

        return list(peers.values())

    def get_pending_invitations(self, user_id: str) -> list[SharingRelationship]:
        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("User not found")
            return self.uow.sharing_relationships.find_pending_by_grantee(
                f"@{user.username}"
            )
