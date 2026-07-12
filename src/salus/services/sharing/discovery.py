import logging

import httpx

logger = logging.getLogger("salus.services.sharing.discovery")


class FederationDiscoveryService:
    def __init__(self) -> None:
        self._endpoint_cache: dict[str, dict[str, str]] = {}

    def resolve_remote_endpoints(self, owner_handle: str) -> dict[str, str]:
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
