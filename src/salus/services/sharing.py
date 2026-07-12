import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from sqlmodel import select

from salus.exceptions import ForbiddenError, NotFoundError, ConflictError
from salus.models.sharing import ConnectionStatus, SharingRelationship
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.sharing import PeerConnection, PeerMetricInfo
from salus.services._helpers import uid

logger = logging.getLogger("salus.services.sharing")


class SharingService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow
        self._endpoint_cache: dict[str, dict[str, str]] = {}
        self._public_key_cache: dict[str, str] = {}

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

    @staticmethod
    def _format_sync_age(sync_time: datetime) -> str:
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
            self.uow.commit()
            object.__setattr__(rel, "raw_token", raw_token)
            return rel

    def accept_relationship(
        self, grantee_user_id: int, relationship_id: int
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
            self.uow.commit()

            import threading

            threading.Thread(
                target=self._notify_federation_accept, args=(rel,), daemon=True
            ).start()
            return rel

    def decline_relationship(
        self, grantee_user_id: int, relationship_id: int
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

            peer_sync_times: dict[str, datetime] = {}

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
            if peer.is_remote:
                sync_time = peer_sync_times.get(_peer_key(peer.handle))
                peer.last_sync = self._format_sync_age(sync_time) if sync_time else None

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
        force_refresh: bool = False,
    ) -> list[dict]:
        owner_handle = self._normalise_handle(owner_handle)

        with self.uow:
            req_user = self.uow.users.get_by_id(requester_id)
            if not req_user:
                raise NotFoundError("Requester not found")
            requester_handle = f"@{req_user.username}"

        if not self._is_remote(owner_handle):
            return self._resolve_local(
                owner_handle, requester_handle, data_type, date_str
            )
        else:
            if not force_refresh:
                from salus.models.sharing import FederatedMeasurementCache
                from datetime import timedelta

                cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
                with self.uow:
                    stmt = select(FederatedMeasurementCache).where(
                        FederatedMeasurementCache.owner_handle == owner_handle,
                        FederatedMeasurementCache.data_type == data_type,
                        FederatedMeasurementCache.date_str == date_str,
                        FederatedMeasurementCache.fetched_at >= cutoff,
                    )
                    cached = self.uow.session.exec(stmt).first()
                    if cached:
                        import json

                        try:
                            return (
                                json.loads(cached.value_json)
                                if cached.value_json
                                else []
                            )
                        except Exception:
                            logger.debug("Failed to parse cached measurement JSON", exc_info=True)

            data = self._fetch_remote(owner_handle, data_type, date_str)

            from salus.models.sharing import FederatedMeasurementCache
            import json

            with self.uow:
                stmt_exist = select(FederatedMeasurementCache).where(
                    FederatedMeasurementCache.owner_handle == owner_handle,
                    FederatedMeasurementCache.data_type == data_type,
                    FederatedMeasurementCache.date_str == date_str,
                )
                existing = self.uow.session.exec(stmt_exist).first()
                if existing:
                    existing.value_json = json.dumps(data)
                    existing.fetched_at = datetime.now(timezone.utc)
                    self.uow.session.add(existing)
                else:
                    new_cache = FederatedMeasurementCache(
                        owner_handle=owner_handle,
                        data_type=data_type,
                        date_str=date_str,
                        value_json=json.dumps(data),
                        fetched_at=datetime.now(timezone.utc),
                    )
                    self.uow.session.add(new_cache)
                self.uow.commit()

            return data

    def _resolve_local(
        self, owner_handle: str, requester_handle: str, data_type: str, date_str: str
    ) -> list[dict]:
        owner_username = owner_handle[1:]
        with self.uow:
            owner_user = self.uow.users.get_by_username(owner_username)
            if not owner_user:
                raise NotFoundError(f"User {owner_username} not found")

            metric_types = self.uow.metric_types.find_all(owner_user.id)
            metric = next(
                (m for m in metric_types if m.source_data_type == data_type), None
            )
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
                raise ForbiddenError(
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

    def get_instance_keys(self) -> tuple[str, str]:
        with self.uow:
            priv_conf = self.uow.system_configs.get_by_key(
                "federation_private_key_pem"
            )
            pub_conf = self.uow.system_configs.get_by_key(
                "federation_public_key_pem"
            )

            if priv_conf and pub_conf:
                return priv_conf.value, pub_conf.value

            from cryptography.hazmat.primitives.asymmetric import ed25519
            from cryptography.hazmat.primitives import serialization

            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()

            priv_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ).decode("utf-8")

            pub_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode("utf-8")

            self.uow.system_configs.upsert(
                key="federation_private_key_pem",
                value=priv_pem,
                description="Federation instance Ed25519 private key",
                category="federation",
                is_secret=True,
            )
            self.uow.system_configs.upsert(
                key="federation_public_key_pem",
                value=pub_pem,
                description="Federation instance Ed25519 public key",
                category="federation",
                is_secret=False,
            )

            self.uow.commit()
            return priv_pem, pub_pem

    def resolve_actor_public_key(self, sender_handle: str) -> str:
        if sender_handle in self._public_key_cache:
            return self._public_key_cache[sender_handle]

        parts = sender_handle[1:].split(":", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid remote handle: {sender_handle}")
        username, domain = parts

        scheme = (
            "http"
            if "localhost" in domain or "127.0.0.1" in domain or "testserver" in domain
            else "https"
        )
        webfinger_url = f"{scheme}://{domain}/.well-known/webfinger"

        try:
            resp = httpx.get(
                webfinger_url,
                params={"resource": f"acct:{username}@{domain}"},
                timeout=3.0,
            )
            resp.raise_for_status()
            jrd = resp.json()
            actor_url = None
            for link in jrd.get("links", []):
                if link.get("rel") == "self":
                    actor_url = link.get("href")
                    break

            if not actor_url:
                raise ValueError("No actor link found")

            resp_actor = httpx.get(actor_url, timeout=3.0)
            resp_actor.raise_for_status()
            actor = resp_actor.json()
            pub_key_pem = actor.get("publicKey", {}).get("publicKeyPem")
            if not pub_key_pem:
                raise ValueError("No publicKeyPem in Actor profile")

            self._public_key_cache[sender_handle] = pub_key_pem
            return pub_key_pem
        except Exception as exc:
            logger.error(f"Failed to resolve public key for {sender_handle}: {exc}")
            raise ValueError(f"Could not resolve public key for {sender_handle}")

    def sign_request(
        self, sender_handle: str, method: str, url_str: str, body: bytes | None = None
    ) -> dict[str, str]:
        import uuid
        import time
        import hashlib
        import base64
        from urllib.parse import urlparse

        parsed = urlparse(url_str)
        authority = parsed.netloc
        path = parsed.path
        if parsed.query:
            path = f"{path}?{parsed.query}"

        nonce = uuid.uuid4().hex
        timestamp = str(int(time.time()))

        headers = {
            "X-Salus-Nonce": nonce,
            "X-Salus-Timestamp": timestamp,
        }

        if body is not None:
            body_hash = hashlib.sha256(body).digest()
            digest_str = "sha-256=:" + base64.b64encode(body_hash).decode("utf-8") + ":"
            headers["Content-Digest"] = digest_str

        signed_fields = [
            "@method",
            "@path",
            "@authority",
            "x-salus-nonce",
            "x-salus-timestamp",
        ]
        if body is not None:
            signed_fields.append("content-digest")

        base_lines = []
        base_lines.append(f'"@method": {method}')
        base_lines.append(f'"@path": {path}')
        base_lines.append(f'"@authority": {authority}')
        base_lines.append(f'"x-salus-nonce": {nonce}')
        base_lines.append(f'"x-salus-timestamp": {timestamp}')
        if body is not None:
            base_lines.append(f'"content-digest": {headers["Content-Digest"]}')

        fields_list_str = " ".join(f'"{f}"' for f in signed_fields)
        sig_input_val = f'sig1=({fields_list_str});keyid="{sender_handle}";created={timestamp};nonce="{nonce}";alg="ed25519"'
        base_lines.append(f'"@signature-params": {sig_input_val}')
        signature_base = "\n".join(base_lines).encode("utf-8")

        priv_pem, _ = self.get_instance_keys()
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.hazmat.primitives import serialization

        private_key = serialization.load_pem_private_key(
            priv_pem.encode("utf-8"), password=None
        )
        assert isinstance(private_key, ed25519.Ed25519PrivateKey)

        sig_bytes = private_key.sign(signature_base)
        sig_str = ":" + base64.b64encode(sig_bytes).decode("utf-8") + ":"

        headers["Signature-Input"] = sig_input_val
        headers["Signature"] = sig_str
        return headers

    def verify_request_signature(
        self,
        headers_dict: dict[str, str],
        method: str,
        path_with_query: str,
        authority: str,
        body: bytes | None = None,
    ) -> str:
        import time
        import base64
        import hashlib
        import re

        headers_lower = {k.lower(): v for k, v in headers_dict.items()}

        sig_input = headers_lower.get("signature-input")
        signature = headers_lower.get("signature")
        nonce = headers_lower.get("x-salus-nonce")
        timestamp_str = headers_lower.get("x-salus-timestamp")

        if not sig_input or not signature or not nonce or not timestamp_str:
            raise ValueError("Missing required signature headers")

        try:
            ts = int(timestamp_str)
            now = int(time.time())
            if abs(now - ts) > 30:
                raise ValueError("Signature timestamp expired or skewed (> 30s)")
        except ValueError:
            raise ValueError("Invalid X-Salus-Timestamp")

        match_keyid = re.search(r'keyid="([^"]+)"', sig_input)
        if not match_keyid:
            raise ValueError("Missing keyid in Signature-Input")
        sender_handle = match_keyid.group(1)

        match_fields = re.search(r"sig1=\(([^)]+)\)", sig_input)
        if not match_fields:
            raise ValueError("Invalid sig1 format in Signature-Input")
        fields_str = match_fields.group(1)
        signed_fields = [f.strip('"') for f in fields_str.split(" ")]

        pub_pem = self.resolve_actor_public_key(sender_handle)

        base_lines = []
        for field in signed_fields:
            if field == "@method":
                base_lines.append(f'"@method": {method}')
            elif field == "@path":
                base_lines.append(f'"@path": {path_with_query}')
            elif field == "@authority":
                base_lines.append(f'"@authority": {authority}')
            elif field in ("x-salus-nonce", "x-salus-timestamp", "content-digest"):
                val = headers_lower.get(field)
                if not val:
                    raise ValueError(f"Signed field {field} not present in headers")
                base_lines.append(f'"{field}": {val}')
            else:
                val = headers_lower.get(field)
                if not val:
                    raise ValueError(f"Signed header {field} not present in request")
                base_lines.append(f'"{field}": {val}')

        base_lines.append(f'"@signature-params": {sig_input}')
        signature_base = "\n".join(base_lines).encode("utf-8")

        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.hazmat.primitives import serialization

        try:
            public_key = serialization.load_pem_public_key(pub_pem.encode("utf-8"))
            assert isinstance(public_key, ed25519.Ed25519PublicKey)

            clean_sig = signature.strip(":")
            sig_bytes = base64.b64decode(clean_sig)

            public_key.verify(sig_bytes, signature_base)
        except Exception as exc:
            logger.warning(f"Signature verification failed for {sender_handle}: {exc}")
            raise ValueError("Invalid cryptographic signature")

        if body is not None and "content-digest" in signed_fields:
            digest_val = headers_lower.get("content-digest", "")
            if not digest_val.startswith("sha-256=:"):
                raise ValueError("Invalid Content-Digest format")
            clean_digest = digest_val.split("sha-256=:", 1)[1].strip(":")
            expected_hash = hashlib.sha256(body).digest()
            if base64.b64decode(clean_digest) != expected_hash:
                raise ValueError("Content-Digest mismatch")

        return sender_handle

    def _resolve_remote_endpoints(self, owner_handle: str) -> dict[str, str]:
        if owner_handle in self._endpoint_cache:
            return self._endpoint_cache[owner_handle]

        parts = owner_handle[1:].split(":", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid remote handle format: {owner_handle}")
        username, domain = parts

        scheme = (
            "http"
            if "localhost" in domain or "127.0.0.1" in domain or "testserver" in domain
            else "https"
        )
        webfinger_url = f"{scheme}://{domain}/.well-known/webfinger"

        try:
            resp = httpx.get(
                webfinger_url,
                params={"resource": f"acct:{username}@{domain}"},
                timeout=3.0,
            )
            resp.raise_for_status()
            jrd = resp.json()
            actor_url = None
            for link in jrd.get("links", []):
                if link.get("rel") == "self":
                    actor_url = link.get("href")
                    break

            if not actor_url:
                raise ValueError("No actor link found in WebFinger profile")

            resp_actor = httpx.get(actor_url, timeout=3.0)
            resp_actor.raise_for_status()
            actor = resp_actor.json()
            endpoints = actor.get("endpoints", {})
            resolved = {
                "sharing": endpoints.get(
                    "sharing", f"{scheme}://{domain}/api/v1/federation/sharing"
                ),
                "accept": endpoints.get(
                    "accept", f"{scheme}://{domain}/api/v1/federation/accept"
                ),
                "notify": endpoints.get(
                    "notify", f"{scheme}://{domain}/api/v1/federation/notify-update"
                ),
            }
            self._endpoint_cache[owner_handle] = resolved
            return resolved
        except Exception as exc:
            logger.debug(
                f"WebFinger resolution failed for {owner_handle}: {exc}. Using fallback paths."
            )
            fallback = {
                "sharing": f"{scheme}://{domain}/api/v1/federation/sharing",
                "accept": f"{scheme}://{domain}/api/v1/federation/accept",
                "notify": f"{scheme}://{domain}/api/v1/federation/notify-update",
            }
            return fallback

    def _fetch_remote(
        self, owner_handle: str, data_type: str, date_str: str
    ) -> list[dict]:
        parts = owner_handle[1:].split(":", 1)
        if len(parts) != 2:
            logger.warning(f"Invalid remote handle format: {owner_handle}")
            return []

        username, _ = parts
        endpoints = self._resolve_remote_endpoints(owner_handle)
        remote_url = endpoints["sharing"]

        with self.uow:
            from salus.models import MetricType

            ctx = (
                select(SharingRelationship)
                .join(MetricType)
                .where(
                    SharingRelationship.grantee_handle == owner_handle,
                    SharingRelationship.status == ConnectionStatus.ACTIVE,
                    MetricType.source_data_type == data_type,
                )
            )
            active_rel = self.uow.session.exec(ctx).first()
            local_user = active_rel.owner if active_rel else None
            local_username = local_user.username if local_user else None

        if not active_rel or not local_username:
            logger.warning(f"No active federation relationship for {owner_handle}")
            return []

        from urllib.parse import urlparse
        from salus.config import settings

        local_domain = urlparse(settings.oauth_redirect_base).netloc
        requester_handle = f"@{local_username}:{local_domain}"

        query_params = {
            "owner_username": username,
            "data_type": data_type,
            "date": date_str,
        }
        req_url = httpx.URL(remote_url, params=query_params)
        sig_headers = self.sign_request(requester_handle, "GET", str(req_url))

        token = active_rel.api_token_hash
        if token:
            sig_headers["Authorization"] = f"Bearer {token}"

        import time

        max_retries = 3
        backoff = 1.0

        for attempt in range(max_retries):
            try:
                resp = httpx.get(
                    remote_url,
                    params=query_params,
                    headers=sig_headers,
                    timeout=5.0,
                )
                if resp.status_code in (401, 403, 404):
                    logger.warning(
                        f"Permanent remote federation failure {resp.status_code} for {owner_handle}"
                    )
                    break
                resp.raise_for_status()
                payload = resp.json()
                return payload.get("data", [])
            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.NetworkError,
                httpx.RemoteProtocolError,
            ) as exc:
                if attempt == max_retries - 1:
                    logger.error(
                        f"Remote federation fetch failed after {max_retries} attempts for {owner_handle}: {exc}"
                    )
                    break
                logger.warning(
                    f"Transient error fetching from {owner_handle} (attempt {attempt + 1}/{max_retries}): {exc}. Retrying in {backoff}s..."
                )
                time.sleep(backoff)
                backoff *= 2.0
            except Exception as exc:
                logger.exception(
                    f"Unexpected remote federation fetch failure for {owner_handle}: {exc}"
                )
                break

        return []

    # ------------------------------------------------------------------
    # Federation handshake
    # ------------------------------------------------------------------

    def _notify_federation_accept(self, rel: SharingRelationship) -> None:
        if not self._is_remote(rel.grantee_handle):
            return
        endpoints = self._resolve_remote_endpoints(rel.grantee_handle)
        url = endpoints["accept"]

        import time

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
                time.sleep(backoff)
                backoff *= 2.0
            except Exception as exc:
                logger.exception(
                    f"Unexpected remote accept notification failure for {rel.grantee_handle}: {exc}"
                )
                break

    def process_federation_accept(self, token: str, owner_handle: str) -> None:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        with self.uow:
            ctx = select(SharingRelationship).where(
                SharingRelationship.api_token_hash == token_hash,
                SharingRelationship.status == ConnectionStatus.PENDING,
            )
            rel = self.uow.session.exec(ctx).first()
            if not rel:
                raise NotFoundError(
                    "Pending sharing relationship not found for the provided token"
                )
            rel.status = ConnectionStatus.ACTIVE
            rel.updated_at = datetime.now(timezone.utc)
            self.uow.sharing_relationships.update(rel)
            self.uow.commit()

    def get_feed_activities(self, user_id: int) -> list[dict]:
        today = datetime.now(timezone.utc).date()
        three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
        activities = []

        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("User not found")
            user_handle = f"@{user.username}"

            stmt_local = select(SharingRelationship).where(
                SharingRelationship.grantee_handle == user_handle,
                SharingRelationship.status == ConnectionStatus.ACTIVE,
            )
            local_incoming = self.uow.session.exec(stmt_local).all()

            stmt_remote = select(SharingRelationship).where(
                SharingRelationship.owner_id == user_id,
                SharingRelationship.status == ConnectionStatus.ACTIVE,
            )
            remote_connections = self.uow.session.exec(stmt_remote).all()

            friends_dict: dict[int, dict] = {}
            for rel in local_incoming:
                if rel.owner_id not in friends_dict:
                    friends_dict[rel.owner_id] = {
                        "user": rel.owner,
                        "metrics": [],
                    }
                friends_dict[rel.owner_id]["metrics"].append(
                    rel.metric_type.source_data_type
                )

            for friend_id, friend_data in friends_dict.items():
                friend_user = friend_data["user"]
                shared_types = friend_data["metrics"]

                from salus.models.workout import WorkoutSession

                stmt_sessions = (
                    select(WorkoutSession)
                    .where(
                        WorkoutSession.user_id == friend_id,
                        WorkoutSession.completed_at.is_not(None),  # type: ignore
                        WorkoutSession.completed_at >= three_days_ago,  # type: ignore
                    )
                    .order_by(WorkoutSession.completed_at.desc())  # type: ignore
                )
                sessions = self.uow.session.exec(stmt_sessions).all()

                for sess in sessions:
                    activities.append(
                        {
                            "type": "workout",
                            "friend_name": friend_user.username,
                            "time": sess.completed_at,
                            "title": sess.plan.name if sess.plan else "Workout Session",
                            "notes": sess.notes,
                            "id": f"workout-{sess.id}",
                        }
                    )

                for data_type in shared_types:
                    if data_type not in ("steps", "weight"):
                        continue
                    raw_measurements = self.uow.measurements.find_all(
                        user_id=friend_id,
                        data_types=[data_type],
                    )
                    for offset in range(3):
                        day = today - timedelta(days=offset)
                        day_measurements = [
                            m
                            for m in raw_measurements
                            if m.start_time.date() == day
                            and m.value_numeric is not None
                        ]
                        if day_measurements:
                            if data_type == "steps":
                                val = sum(
                                    m.value_numeric
                                    for m in day_measurements
                                    if m.value_numeric is not None
                                )
                                if val > 0:
                                    activities.append(
                                        {
                                            "type": "steps",
                                            "friend_name": friend_user.username,
                                            "time": datetime.combine(
                                                day,
                                                datetime.min.time(),
                                                tzinfo=timezone.utc,
                                            ),
                                            "value": int(val),
                                            "id": f"steps-{friend_id}-{day.isoformat()}",
                                        }
                                    )
                            elif data_type == "weight":
                                val = day_measurements[-1].value_numeric
                                if val is not None and val > 0:
                                    activities.append(
                                        {
                                            "type": "weight",
                                            "friend_name": friend_user.username,
                                            "time": datetime.combine(
                                                day,
                                                datetime.min.time(),
                                                tzinfo=timezone.utc,
                                            ),
                                            "value": val,
                                            "id": f"weight-{friend_id}-{day.isoformat()}",
                                        }
                                    )

            remote_peers = {}
            for rel in remote_connections:
                if self._is_remote(rel.grantee_handle):
                    if rel.grantee_handle not in remote_peers:
                        remote_peers[rel.grantee_handle] = []
                    remote_peers[rel.grantee_handle].append(
                        rel.metric_type.source_data_type
                    )

        for remote_handle, shared_types in remote_peers.items():
            for data_type in shared_types:
                if data_type not in ("steps", "weight"):
                    continue
                for offset in range(3):
                    day = today - timedelta(days=offset)
                    day_str = day.strftime("%Y-%m-%d")
                    try:
                        data = self.resolve_and_fetch(
                            requester_id=user_id,
                            owner_handle=remote_handle,
                            data_type=data_type,
                            date_str=day_str,
                        )
                        for item in data:
                            val = item.get("value_numeric")
                            if val is not None and val > 0:
                                activities.append(
                                    {
                                        "type": data_type,
                                        "friend_name": remote_handle,
                                        "time": datetime.combine(
                                            day,
                                            datetime.min.time(),
                                            tzinfo=timezone.utc,
                                        ),
                                        "value": int(val)
                                        if data_type == "steps"
                                        else val,
                                        "id": f"{data_type}-{remote_handle}-{day_str}",
                                    }
                                )
                    except Exception as exc:
                        logger.warning(
                            f"Failed to fetch remote data for {remote_handle}: {exc}"
                        )

        activities.sort(
            key=lambda x: (
                x["time"]
                if isinstance(x["time"], datetime)
                else datetime.now(timezone.utc)
            ),
            reverse=True,
        )
        return activities

    def notify_peers_of_update(
        self, user_id: int, data_type: str, date_str: str
    ) -> None:
        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                return
            owner_handle = f"@{user.username}"

            from salus.models import MetricType

            stmt = (
                select(SharingRelationship)
                .join(MetricType)
                .where(
                    SharingRelationship.owner_id == user_id,
                    SharingRelationship.status == ConnectionStatus.ACTIVE,
                    MetricType.source_data_type == data_type,
                )
            )
            relationships = self.uow.session.exec(stmt).all()

            now = datetime.now(timezone.utc)
            remote_grantees = []
            for rel in relationships:
                if self._is_remote(rel.grantee_handle):
                    rel.last_sync_at = now
                    self.uow.sharing_relationships.update(rel)
                    remote_grantees.append((rel.grantee_handle, rel.api_token_hash))
            self.uow.commit()

        import threading

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
        endpoints = self._resolve_remote_endpoints(grantee_handle)
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
