import logging
import hashlib
import base64
import time as _time
import uuid as _uuid
from urllib.parse import urlparse

import httpx

from salus.repositories.unit_of_work import IUnitOfWork

logger = logging.getLogger("salus.services.sharing.keys")


class FederationKeyService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow
        self._public_key_cache: dict[str, str] = {}

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
        parsed = urlparse(url_str)
        authority = parsed.netloc
        path = parsed.path
        if parsed.query:
            path = f"{path}?{parsed.query}"

        nonce = _uuid.uuid4().hex
        timestamp = str(int(_time.time()))

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
            now = int(_time.time())
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
