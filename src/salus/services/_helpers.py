import os
import time
from datetime import date, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from salus.models.user import User

DEFAULT_METRIC_COLOR = "#4f46e5"

__all__ = ["uid", "DEFAULT_METRIC_COLOR", "make_handle", "parse_date", "uuid7_str"]


def parse_date(date_str: str) -> date | None:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def make_handle(user: "User") -> str:
    return f"@{user.username}"


def uid(user: "User") -> str:
    """Return the user's database id, guaranteed present after first persist.

    SQLModel declares `id` as `str | None` because it is absent before
    the initial INSERT.  After `session.flush()` (which `Repository.create()`
    calls internally via `session.commit()` / `session.refresh()`), the
    primary key is always populated.  This helper makes that guarantee
    visible to the type-checker without sprinkling ``# type: ignore[arg-type]``
    through every caller.
    """
    if user.id is None:
        raise ValueError("User has no persisted id — call commit() first")
    return user.id


def uuid7_str() -> str:
    """Generate a UUIDv7 string.

    Layout:
    - 48 bits: Unix timestamp (milliseconds)
    - 4 bits: Version (7)
    - 12 bits: rand_a (12 random bits)
    - 2 bits: Variant (2 bits: 10xxxxxx)
    - 62 bits: rand_b (62 random bits)
    """
    # Get current time in milliseconds
    msec = int(time.time() * 1000)
    # Ensure it fits in 48 bits
    msec_bin = msec & 0xFFFFFFFFFFFF

    # 12 random bits for rand_a
    rand_a = int.from_bytes(os.urandom(2), byteorder="big") & 0x0FFF

    # 62 random bits for rand_b
    rand_b = int.from_bytes(os.urandom(8), byteorder="big") & 0x3FFFFFFFFFFFFFFF

    # Construct 128-bit integer
    uuid_int = (msec_bin << 80) | (7 << 76) | (rand_a << 64) | (0x2 << 62) | rand_b

    # Format as standard UUID string: 8-4-4-4-12 hex characters
    h = f"{uuid_int:032x}"
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"

