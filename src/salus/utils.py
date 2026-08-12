"""Neutral utilities shared across layers (no salus imports)."""
import os
import time


def uuid7_str() -> str:
    """Generate a UUIDv7 string.

    Layout:
    - 48 bits: Unix timestamp (milliseconds)
    - 4 bits: Version (7)
    - 12 bits: rand_a (12 random bits)
    - 2 bits: Variant (2 bits: 10xxxxxx)
    - 62 bits: rand_b (62 random bits)
    """
    msec = int(time.time() * 1000)
    msec_bin = msec & 0xFFFFFFFFFFFF

    rand_a = int.from_bytes(os.urandom(2), byteorder="big") & 0x0FFF

    rand_b = int.from_bytes(os.urandom(8), byteorder="big") & 0x3FFFFFFFFFFFFFFF

    uuid_int = (msec_bin << 80) | (7 << 76) | (rand_a << 64) | (0x2 << 62) | rand_b

    h = f"{uuid_int:032x}"
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"
