import logging

from salus.services.sharing.webfinger import (
    fetch_actor_document,
    infer_scheme,
    parse_handle,
)

logger = logging.getLogger("salus.services.sharing.discovery")


class FederationDiscoveryService:
    def __init__(self) -> None:
        self._endpoint_cache: dict[str, dict[str, str]] = {}

    def _fallback_endpoints(self, domain: str, scheme: str) -> dict[str, str]:
        base = f"{scheme}://{domain}"
        return {
            "sharing": f"{base}/api/v1/federation/sharing",
            "accept": f"{base}/api/v1/federation/accept",
            "notify": f"{base}/api/v1/federation/notify-update",
        }

    def resolve_remote_endpoints(self, owner_handle: str) -> dict[str, str]:
        if owner_handle in self._endpoint_cache:
            return self._endpoint_cache[owner_handle]

        username, domain = parse_handle(owner_handle)
        scheme = infer_scheme(domain)
        fallback = self._fallback_endpoints(domain, scheme)

        try:
            actor = fetch_actor_document(username, domain)
            endpoints = actor.get("endpoints", {})
            resolved = {
                "sharing": endpoints.get("sharing", fallback["sharing"]),
                "accept": endpoints.get("accept", fallback["accept"]),
                "notify": endpoints.get("notify", fallback["notify"]),
            }
        except Exception as exc:
            logger.debug(
                f"WebFinger resolution failed for {owner_handle}: {exc}. Using fallback paths."
            )
            return fallback

        self._endpoint_cache[owner_handle] = resolved
        return resolved
