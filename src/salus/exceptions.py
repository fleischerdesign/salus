from __future__ import annotations


class NotFoundError(Exception):
    def __init__(self, message: str = "Resource not found") -> None:
        self.message = message
        super().__init__(message)


class ConflictError(Exception):
    def __init__(self, message: str = "Resource already exists") -> None:
        self.message = message
        super().__init__(message)


class AuthenticationError(Exception):
    def __init__(self, message: str = "Authentication required") -> None:
        self.message = message
        super().__init__(message)


class InvalidCredentialsError(Exception):
    def __init__(self, message: str = "Invalid username or password") -> None:
        self.message = message
        super().__init__(message)


class ForbiddenError(Exception):
    def __init__(self, message: str = "Forbidden") -> None:
        self.message = message
        super().__init__(message)


class ApiError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


_STATUS_MAP: dict[str, tuple[int, str | None]] = {
    "created": (201, None),
    "updated": (200, None),
    "deleted": (204, None),
    "ok": (200, None),
    "not_found": (404, None),
    "forbidden": (403, None),
    "conflict": (409, None),
    "error": (400, None),
}


def raise_from_command_result(status: str, message: str | None = None) -> None:
    entry = _STATUS_MAP.get(status)
    if entry is None:
        raise ApiError(code=status, message=message or status, status_code=500)
    http_status, override_message = entry
    if http_status in (200, 201, 204):
        return
    raise ApiError(code=status, message=override_message or message or status, status_code=http_status)
