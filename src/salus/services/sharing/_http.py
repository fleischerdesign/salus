import logging
import time as _time
from collections.abc import Callable

import httpx

logger = logging.getLogger(__name__)

__all__ = ["retry_http_request"]


def retry_http_request(
    make_request: Callable[[], httpx.Response],
    operation_name: str,
    max_retries: int = 3,
    backoff: float = 1.0,
) -> httpx.Response | None:
    for attempt in range(max_retries):
        try:
            resp = make_request()
            if resp.status_code in (401, 403, 404):
                logger.warning(
                    f"Permanent {operation_name} failure {resp.status_code}"
                )
                return resp
            resp.raise_for_status()
            return resp
        except (
            httpx.ConnectError,
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.RemoteProtocolError,
        ) as exc:
            if attempt == max_retries - 1:
                logger.error(
                    f"{operation_name} failed after {max_retries} attempts: {exc}"
                )
                return None
            logger.warning(
                f"Transient error in {operation_name} (attempt {attempt + 1}/{max_retries}): {exc}. Retrying in {backoff}s..."
            )
            _time.sleep(backoff)
            backoff *= 2.0
        except Exception as exc:
            logger.exception(f"Unexpected {operation_name} failure: {exc}")
            return None
    return None
