import logging
import threading
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import httpx

from salus.models.sharing import SharingRelationship
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.sharing.relationship import RelationshipService
from salus.services.sharing._http import retry_http_request

if TYPE_CHECKING:
    from salus.services.sharing.discovery import FederationDiscoveryService

logger = logging.getLogger("salus.services.sharing.notify")


class PeerNotificationService:
    def __init__(
        self,
        uow: IUnitOfWork,
        discovery_svc: "FederationDiscoveryService",
    ) -> None:
        self.uow = uow
        self.discovery_svc = discovery_svc

    def notify_federation_accept(self, rel: SharingRelationship) -> None:
        if not RelationshipService.is_remote(rel.grantee_handle):
            return
        endpoints = self.discovery_svc.resolve_remote_endpoints(rel.grantee_handle)
        url = endpoints["accept"]

        def _do_post():
            return httpx.post(
                url,
                json={
                    "token": rel.api_token_hash,
                    "owner_handle": f"@{rel.owner.username}" if rel.owner else "",
                },
                timeout=5.0,
            )

        retry_http_request(
            _do_post,
            operation_name=f"remote accept notification for {rel.grantee_handle}",
        )

    def notify_peers_of_update(
        self, user_id: str, data_type: str, date_str: str
    ) -> None:
        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                return
            owner_handle = f"@{user.username}"

            relationships = self.uow.sharing_relationships.find_active_by_owner_and_data_type(
                user_id, data_type
            )

            now = datetime.now(timezone.utc)
            remote_grantees = []

            for rel in relationships:
                if RelationshipService.is_remote(rel.grantee_handle):
                    rel.last_sync_at = now
                    self.uow.sharing_relationships.update(rel)
                    remote_grantees.append((rel.grantee_handle, rel.api_token_hash))
            self.uow.commit()

        for handle, token_hash in remote_grantees:
            if token_hash:
                threading.Thread(
                    target=self._send_push_notification,
                    args=(handle, token_hash, owner_handle, data_type, date_str),
                    daemon=True,
                ).start()

    def _send_push_notification(
        self,
        grantee_handle: str,
        token_hash: str,
        owner_handle: str,
        data_type: str,
        date_str: str,
    ) -> None:
        endpoints = self.discovery_svc.resolve_remote_endpoints(grantee_handle)
        url = endpoints["notify"]
        try:
            resp = httpx.post(
                url,
                json={
                    "owner_handle": owner_handle,
                    "data_type": data_type,
                    "date": date_str,
                },
                headers={"Authorization": f"Bearer {token_hash}"},
                timeout=5.0,
            )
            resp.raise_for_status()
            logger.debug(f"Successfully pushed update notification to {grantee_handle}")
        except Exception as exc:
            logger.warning(
                f"Failed to push update notification to {grantee_handle}: {exc}"
            )
