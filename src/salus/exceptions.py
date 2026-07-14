from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from salus.services.command_registry import CommandResult


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


_CMD_STATUS_MAP: dict[str, int] = {
    "created": 201,
    "updated": 200,
    "deleted": 204,
    "not_found": 404,
    "forbidden": 403,
    "error": 400,
}


def raise_from_command_result(result: CommandResult) -> None:
    if result.status in ("created", "updated", "ok"):
        return
    if result.status == "deleted":
        return
    status_code = _CMD_STATUS_MAP.get(result.status, 500)
    code = result.status
    message = result.message or result.status
    raise ApiError(code=code, message=message, status_code=status_code)
