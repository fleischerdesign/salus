from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from salus.models.user import User
    from salus.repositories.unit_of_work import IUnitOfWork

T = TypeVar("T")


@dataclass
class CommandResult:
    status: str
    id: str | None = None
    record: dict[str, Any] | None = None
    message: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


class CommandHandler(Protocol):
    def execute(
        self,
        uow: IUnitOfWork,
        user: User,
        payload: dict[str, Any],
    ) -> CommandResult: ...


_COMMAND_REGISTRY: dict[str, type[CommandHandler]] = {}


def register(name: str):
    def decorator(cls: type[CommandHandler]) -> type[CommandHandler]:
        _COMMAND_REGISTRY[name] = cls
        return cls

    return decorator


def get_handler(name: str) -> type[CommandHandler] | None:
    return _COMMAND_REGISTRY.get(name)


def list_commands() -> list[str]:
    return sorted(_COMMAND_REGISTRY.keys())