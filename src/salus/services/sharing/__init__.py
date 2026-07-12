from typing import Optional

from salus.models.sharing import SharingRelationship
from salus.schemas.sharing import PeerConnection
from salus.services.sharing.relationship import RelationshipService
from salus.services.sharing.keys import FederationKeyService
from salus.services.sharing.discovery import FederationDiscoveryService
from salus.services.sharing.resolver import FederationDataResolver
from salus.services.sharing.notify import PeerNotificationService

__all__ = [
    "SharingService",
    "RelationshipService",
    "FederationKeyService",
    "FederationDiscoveryService",
    "FederationDataResolver",
    "PeerNotificationService",
]


class SharingService:
    def __init__(
        self,
        relationship_svc: RelationshipService,
        key_svc: FederationKeyService,
        discovery_svc: FederationDiscoveryService,
        resolver_svc: FederationDataResolver,
        notify_svc: PeerNotificationService,
    ) -> None:
        self.uow = relationship_svc.uow
        self._relationship = relationship_svc
        self._keys = key_svc
        self._discovery = discovery_svc
        self._resolver = resolver_svc
        self._notify = notify_svc

    @classmethod
    def create(cls, uow) -> "SharingService":
        assert hasattr(uow, "session"), "uow must be an IUnitOfWork instance"
        relationship_svc = RelationshipService(uow)  # type: ignore[arg-type]
        key_svc = FederationKeyService(uow)  # type: ignore[arg-type]
        discovery_svc = FederationDiscoveryService()
        resolver_svc = FederationDataResolver(
            uow, key_svc, discovery_svc, relationship_svc,  # type: ignore[arg-type]
        )
        notify_svc = PeerNotificationService(uow, discovery_svc)  # type: ignore[arg-type]
        return cls(relationship_svc, key_svc, discovery_svc, resolver_svc, notify_svc)

    @staticmethod
    def _normalize_handle(handle: str) -> str:
        return RelationshipService.normalize_handle(handle)

    @staticmethod
    def _is_remote(handle: str) -> bool:
        return RelationshipService.is_remote(handle)

    # ── Relationship CRUD ──

    def create_relationship(
        self,
        owner_id: int,
        grantee_handle: str,
        metric_type_id: int,
        aggregation_level: str = "daily_summary",
        expiration_days: Optional[int] = None,
    ) -> SharingRelationship:
        return self._relationship.create_relationship(
            owner_id, grantee_handle, metric_type_id,
            aggregation_level, expiration_days,
        )

    def accept_relationship(
        self, grantee_user_id: int, relationship_id: int
    ) -> SharingRelationship:
        return self._relationship.accept_relationship(
            grantee_user_id, relationship_id,
            notify_callback=self._notify.notify_federation_accept,
        )

    def decline_relationship(
        self, grantee_user_id: int, relationship_id: int
    ) -> SharingRelationship:
        return self._relationship.decline_relationship(grantee_user_id, relationship_id)

    def list_relationships(self, owner_id: int) -> list[SharingRelationship]:
        return self._relationship.list_relationships(owner_id)

    def deactivate_relationship(self, owner_id: int, relationship_id: int) -> None:
        self._relationship.deactivate_relationship(owner_id, relationship_id)

    def process_federation_accept(self, token: str, owner_handle: str) -> None:
        self._relationship.process_federation_accept(token, owner_handle)

    def get_peer_connections(self, user_id: int) -> list[PeerConnection]:
        return self._relationship.get_peer_connections(user_id)

    def get_pending_invitations(self, user_id: int) -> list[SharingRelationship]:
        return self._relationship.get_pending_invitations(user_id)

    # ── Data resolution ──

    def resolve_and_fetch(
        self,
        requester_id: int,
        owner_handle: str,
        data_type: str,
        date_str: str,
        force_refresh: bool = False,
    ) -> list[dict]:
        return self._resolver.resolve_and_fetch(
            requester_id, owner_handle, data_type, date_str, force_refresh,
        )

    def get_feed_activities(self, user_id: int) -> list[dict]:
        return self._resolver.get_feed_activities(user_id)

    # ── Federation keys ──

    def get_instance_keys(self) -> tuple[str, str]:
        return self._keys.get_instance_keys()

    def resolve_actor_public_key(self, sender_handle: str) -> str:
        return self._keys.resolve_actor_public_key(sender_handle)

    def sign_request(
        self, sender_handle: str, method: str, url_str: str, body: bytes | None = None
    ) -> dict[str, str]:
        return self._keys.sign_request(sender_handle, method, url_str, body)

    def verify_request_signature(
        self,
        headers_dict: dict[str, str],
        method: str,
        path_with_query: str,
        authority: str,
        body: bytes | None = None,
    ) -> str:
        return self._keys.verify_request_signature(
            headers_dict, method, path_with_query, authority, body,
        )

    # ── Discovery ──

    def _resolve_remote_endpoints(self, owner_handle: str) -> dict[str, str]:
        return self._discovery.resolve_remote_endpoints(owner_handle)

    # ── Notifications ──

    def notify_peers_of_update(
        self, user_id: int, data_type: str, date_str: str
    ) -> None:
        self._notify.notify_peers_of_update(user_id, data_type, date_str)

    # ── Internal method pass-throughs (for backward compat in tests) ──

    def _fetch_remote(
        self, owner_handle: str, data_type: str, date_str: str
    ) -> list[dict]:
        return self._resolver._fetch_remote(owner_handle, data_type, date_str)

    def _resolve_local(
        self, owner_handle: str, requester_handle: str, data_type: str, date_str: str
    ) -> list[dict]:
        return self._resolver._resolve_local(
            owner_handle, requester_handle, data_type, date_str,
        )
