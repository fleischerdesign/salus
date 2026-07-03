import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from sqlmodel import select

from salus.exceptions import NotFoundError, ConflictError
from salus.models.sharing import ConnectionStatus, SharingRelationship
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.sharing import PeerConnection, PeerMetricInfo
from salus.services._helpers import uid

logger = logging.getLogger("salus.services.sharing")


class SharingService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    # ------------------------------------------------------------------
    # Handle helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_handle(handle: str) -> str:
        handle = handle.strip()
        if not handle.startswith("@"):
            handle = f"@{handle}"
        return handle

    @staticmethod
    def _is_remote(handle: str) -> bool:
        return ":" in handle

    # ------------------------------------------------------------------
    # Relationship CRUD
    # ------------------------------------------------------------------

    def create_relationship(
        self,
        owner_id: int,
        grantee_handle: str,
        metric_type_id: int,
        aggregation_level: str = "daily_summary",
        expiration_days: Optional[int] = None,
    ) -> SharingRelationship:
        grantee_handle = self._normalise_handle(grantee_handle)

        with self.uow:
            metric = self.uow.metric_types.get_by_id(metric_type_id)
            if not metric or metric.user_id != owner_id:
                raise NotFoundError("Metric type not found or access denied")

            if not self._is_remote(grantee_handle):
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

            ctx_pending = select(SharingRelationship).where(
                SharingRelationship.owner_id == owner_id,
                SharingRelationship.grantee_handle == grantee_handle,
                SharingRelationship.metric_type_id == metric_type_id,
                SharingRelationship.status == ConnectionStatus.PENDING,
            )
            pending = self.uow.session.exec(ctx_pending).first()
            if pending:
                raise ConflictError(
                    "A pending sharing invitation already exists for this metric and user"
                )

            expiration_date = None
            if expiration_days is not None:
                expiration_date = datetime.now(timezone.utc) + timedelta(days=expiration_days)

            token = secrets.token_hex(20)

            rel = SharingRelationship(
                owner_id=owner_id,
                grantee_handle=grantee_handle,
                metric_type_id=metric_type_id,
                aggregation_level=aggregation_level,
                expiration_date=expiration_date,
                status=ConnectionStatus.PENDING,
                api_token_hash=token,
            )
            self.uow.sharing_relationships.create(rel)
            self.uow.commit()
            return rel

    def accept_relationship(self, grantee_user_id: int, relationship_id: int) -> SharingRelationship:
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
            self.uow.commit()

            self._notify_federation_accept(rel)
            return rel

    def decline_relationship(self, grantee_user_id: int, relationship_id: int) -> SharingRelationship:
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
            self.uow.commit()
            return rel

    def list_relationships(self, owner_id: int) -> list[SharingRelationship]:
        with self.uow:
            return self.uow.sharing_relationships.find_by_owner(owner_id)

    def deactivate_relationship(self, owner_id: int, relationship_id: int) -> None:
        with self.uow:
            rel = self.uow.sharing_relationships.get_by_id(relationship_id)
            if not rel or rel.owner_id != owner_id:
                raise NotFoundError("Sharing relationship not found")
            rel.status = ConnectionStatus.REVOKED
            rel.updated_at = datetime.now(timezone.utc)
            self.uow.sharing_relationships.update(rel)
            self.uow.commit()

    # ------------------------------------------------------------------
    # Peer connections (merged view)
    # ------------------------------------------------------------------

    def get_peer_connections(self, user_id: int) -> list[PeerConnection]:
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

            for rel in all_outgoing:
                handle = rel.grantee_handle
                peer = _ensure_peer(handle, self._is_remote(handle))
                rel_is_pending = rel.status == ConnectionStatus.PENDING
                rel_is_active = rel.status == ConnectionStatus.ACTIVE
                if rel_is_pending:
                    peer.is_pending = True
                if rel_is_active or rel_is_pending:
                    peer.metrics.append(
                        PeerMetricInfo(
                            metric_name=rel.metric_type.name,
                            icon=getattr(rel.metric_type, "icon", "monitoring"),
                            color=getattr(rel.metric_type, "color", "#4f46e5"),
                            aggregation=rel.aggregation_level,
                            direction="outgoing",
                            relationship_id=rel.id or 0,
                        )
                    )
                if rel.expiration_date and (
                    peer.expiration is None or rel.expiration_date < peer.expiration
                ):
                    peer.expiration = rel.expiration_date
                if (rel_is_active or rel_is_pending) and rel.api_token_hash and self._is_remote(handle):
                    peer.api_token = rel.api_token_hash

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
                            color=getattr(rel.metric_type, "color", "#4f46e5"),
                            aggregation=rel.aggregation_level,
                            direction="incoming",
                            relationship_id=rel.id or 0,
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

        return list(peers.values())

    def get_pending_invitations(self, user_id: int) -> list[SharingRelationship]:
        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("User not found")
            return self.uow.sharing_relationships.find_pending_by_grantee(
                f"@{user.username}"
            )

    # ------------------------------------------------------------------
    # Data resolution
    # ------------------------------------------------------------------

    def resolve_and_fetch(
        self,
        requester_id: int,
        owner_handle: str,
        data_type: str,
        date_str: str,
    ) -> list[dict]:
        owner_handle = self._normalise_handle(owner_handle)

        with self.uow:
            req_user = self.uow.users.get_by_id(requester_id)
            if not req_user:
                raise NotFoundError("Requester not found")
            requester_handle = f"@{req_user.username}"

        if not self._is_remote(owner_handle):
            return self._resolve_local(owner_handle, requester_handle, data_type, date_str)
        else:
            return self._fetch_remote(owner_handle, data_type, date_str)

    def _resolve_local(
        self, owner_handle: str, requester_handle: str, data_type: str, date_str: str
    ) -> list[dict]:
        owner_username = owner_handle[1:]
        with self.uow:
            owner_user = self.uow.users.get_by_username(owner_username)
            if not owner_user:
                raise NotFoundError(f"User {owner_username} not found")

            metric_types = self.uow.metric_types.find_all(owner_user.id)
            metric = next((m for m in metric_types if m.source_data_type == data_type), None)
            if not metric:
                return []
            if metric.id is None:
                raise ValueError("Metric has no persisted id")
            metric_id = metric.id

            rel = self.uow.sharing_relationships.get_active_relationship(
                owner_id=uid(owner_user),
                grantee_handle=requester_handle,
                metric_type_id=metric_id,
            )
            if not rel:
                raise PermissionError(
                    f"Access denied: no active sharing relationship from {owner_handle}"
                )

            raw_measurements = self.uow.measurements.find_all(
                user_id=uid(owner_user),
                data_types=[data_type],
            )

            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                target_date = datetime.now(timezone.utc).date()

            day_measurements = [
                m for m in raw_measurements if m.start_time.date() == target_date
            ]

            if rel.aggregation_level == "daily_summary":
                if not day_measurements:
                    return []
                values = [
                    m.value_numeric
                    for m in day_measurements
                    if m.value_numeric is not None
                ]
                val = (
                    sum(values)
                    if data_type in ("steps", "water")
                    else (sum(values) / len(values) if values else None)
                )
                return [
                    {
                        "data_type": data_type,
                        "value_numeric": val,
                        "start_time": date_str,
                        "source": "summary",
                        "external_id": f"summary-{owner_username}-{data_type}-{date_str}",
                    }
                ]
            else:
                return [
                    {
                        "data_type": m.data_type,
                        "value_numeric": m.value_numeric,
                        "value_json": m.value_json,
                        "start_time": m.start_time.isoformat(),
                        "source": m.source,
                        "external_id": m.external_id,
                    }
                    for m in day_measurements
                ]

    def _fetch_remote(
        self, owner_handle: str, data_type: str, date_str: str
    ) -> list[dict]:
        parts = owner_handle[1:].split(":", 1)
        if len(parts) != 2:
            logger.warning(f"Invalid remote handle format: {owner_handle}")
            return []

        username, domain = parts
        remote_url = f"https://{domain}/api/v1/federation/sharing"

        with self.uow:
            ctx = select(SharingRelationship).where(
                SharingRelationship.grantee_handle == owner_handle,
                SharingRelationship.status == ConnectionStatus.ACTIVE,
            )
            active_rels = self.uow.session.exec(ctx).all()

        token = active_rels[0].api_token_hash if active_rels else None
        if not token:
            logger.warning(f"No active federation token for {owner_handle}")
            return []

        try:
            resp = httpx.get(
                remote_url,
                params={
                    "owner_username": username,
                    "data_type": data_type,
                    "date": date_str,
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0,
            )
            resp.raise_for_status()
            payload = resp.json()
            return payload.get("data", [])
        except Exception as exc:
            logger.warning(f"Remote federation fetch failed for {owner_handle}: {exc}")
            return []

    # ------------------------------------------------------------------
    # Federation handshake
    # ------------------------------------------------------------------

    def _notify_federation_accept(self, rel: SharingRelationship) -> None:
        if not self._is_remote(rel.grantee_handle):
            return
        _, domain = rel.grantee_handle[1:].split(":", 1)
        url = f"https://{domain}/api/v1/federation/accept"
        try:
            httpx.post(
                url,
                json={
                    "token": rel.api_token_hash,
                    "owner_handle": f"@{rel.owner.username}" if rel.owner else "",
                },
                timeout=10.0,
            )
        except Exception as exc:
            logger.warning(f"Federation accept notification failed: {exc}")

    def process_federation_accept(self, token: str, owner_handle: str) -> None:
        with self.uow:
            ctx = select(SharingRelationship).where(
                SharingRelationship.api_token_hash == token,
                SharingRelationship.status == ConnectionStatus.PENDING,
            )
            rel = self.uow.session.exec(ctx).first()
            if rel:
                rel.status = ConnectionStatus.ACTIVE
                rel.updated_at = datetime.now(timezone.utc)
                self.uow.sharing_relationships.update(rel)
                self.uow.commit()
