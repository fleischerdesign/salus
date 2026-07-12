import logging
import threading
import time as _time
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import httpx

from salus.models.sharing import SharingRelationship
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.sharing.relationship import RelationshipService

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

        max_retries = 3
        backoff = 1.0

        for attempt in range(max_retries):
            try:
                resp = httpx.post(
                    url,
                    json={
                        "token": rel.api_token_hash,
                        "owner_handle": f"@{rel.owner.username}" if rel.owner else "",
                    },
                    timeout=5.0,
                )
                if resp.status_code in (401, 403, 404):
                    logger.warning(
                        f"Permanent remote accept notification failure {resp.status_code} for {rel.grantee_handle}"
                    )
                    break
                resp.raise_for_status()
                return
            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.NetworkError,
                httpx.RemoteProtocolError,
            ) as exc:
                if attempt == max_retries - 1:
                    logger.error(
                        f"Remote accept notification failed after {max_retries} attempts for {rel.grantee_handle}: {exc}"
                    )
                    break
                logger.warning(
                    f"Transient error calling remote accept (attempt {attempt + 1}/{max_retries}): {exc}. Retrying in {backoff}s..."
                )
                _time.sleep(backoff)
                backoff *= 2.0
            except Exception as exc:
                logger.exception(
                    f"Unexpected remote accept notification failure for {rel.grantee_handle}: {exc}"
                )
                break

    def notify_peers_of_update(
        self, user_id: int, data_type: str, date_str: str
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
