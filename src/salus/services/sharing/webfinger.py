import httpx

_HTTP_TIMEOUT_SECONDS = 3.0


def parse_handle(handle: str) -> tuple[str, str]:
    """Split a remote handle '@user@domain' into (username, domain)."""
    parts = handle[1:].split(":", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid remote handle format: {handle}")
    return parts[0], parts[1]


def infer_scheme(domain: str) -> str:
    if "localhost" in domain or "127.0.0.1" in domain or "testserver" in domain:
        return "http"
    return "https"


def fetch_actor_document(username: str, domain: str) -> dict:
    """Resolve a remote actor's document via WebFinger and return it."""
    scheme = infer_scheme(domain)
    webfinger_url = f"{scheme}://{domain}/.well-known/webfinger"

    resp = httpx.get(
        webfinger_url,
        params={"resource": f"acct:{username}@{domain}"},
        timeout=_HTTP_TIMEOUT_SECONDS,
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

    resp_actor = httpx.get(actor_url, timeout=_HTTP_TIMEOUT_SECONDS)
    resp_actor.raise_for_status()
    return resp_actor.json()
