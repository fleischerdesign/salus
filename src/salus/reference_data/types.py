from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

from sqlmodel import SQLModel

T = TypeVar("T", bound=SQLModel)


@dataclass(frozen=True)
class ReferenceSpec(Generic[T]):
    """Declarative specification for a code-defined reference dataset."""

    name: str
    model: type[T]
    unique_key: str
    items: list[dict[str, Any]]
    update_fields: tuple[str, ...] = ()
    user_scoped: bool = False
    instantiator: Callable[[dict[str, Any]], T] | None = None


@dataclass
class SeedingItemReport:
    """Seeding statistics for a single reference dataset."""

    name: str
    total: int = 0
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    skipped_by_hash: bool = False


@dataclass
class SeedingReport:
    """Aggregated seeding statistics across all reference datasets."""

    items: list[SeedingItemReport] = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def total_created(self) -> int:
        return sum(i.created for i in self.items)

    @property
    def total_updated(self) -> int:
        return sum(i.updated for i in self.items)
