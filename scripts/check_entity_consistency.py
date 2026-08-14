#!/usr/bin/env python3
"""Check that backend ENTITY_META matches frontend types and Dexie stores.

The frontend discovers entity names dynamically via ``/api/v1/sync/entities``
(no hardcoded fallback list), so the static artifacts to keep in sync are the
TypeScript interfaces (``types.ts``) and the Dexie stores (``database.ts``).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_entity_meta_names() -> frozenset[str]:
    meta = (ROOT / "src" / "salus" / "repositories" / "entity_meta.py").read_text()
    names = re.findall(r'name="([^"]+)"', meta)
    return frozenset(names)


def parse_types_interface_names() -> frozenset[str]:
    types_src = (ROOT / "frontend" / "src" / "lib" / "db" / "types.ts").read_text()
    return frozenset(re.findall(r"export\s+interface\s+(\w+)", types_src))


def parse_database_store_names() -> frozenset[str]:
    db_src = (ROOT / "frontend" / "src" / "lib" / "db" / "database.ts").read_text()
    return frozenset(re.findall(r"(\w+)!:\s*EntityTable", db_src))


def snake_to_pascal(name: str) -> str:
    if name in ("user", "user_profile"):
        return "UserProfile"
    if name == "system_config":
        return "SystemConfigItem"
    return "".join(part.capitalize() for part in name.split("_"))


SPECIAL_ENTITIES = frozenset({
    "user_profile", "admin_user", "admin_stats", "system_config",
    "community_activity",
})


def main() -> int:
    errors = 0

    backend = parse_entity_meta_names()
    types = parse_types_interface_names()
    stores = parse_database_store_names()

    all_backend = backend | SPECIAL_ENTITIES

    print(f"ENTITY_META (backend):  {len(backend)} entities")
    print(f"special entities:       {len(SPECIAL_ENTITIES)} entities")
    print(f"interfaces (types.ts):  {len(types)} interfaces")
    print(f"stores (database.ts):   {len(stores)} stores")
    print()

    for name in sorted(all_backend):
        pascal = snake_to_pascal(name)
        if pascal not in types:
            print(f"  ERROR: entity '{name}' has no interface '{pascal}' in types.ts")
            errors += 1

    for name in sorted(backend):
        if name not in stores:
            print(f"  ERROR: entity '{name}' has no store definition in database.ts")
            errors += 1

    if errors:
        print(f"\n{errors} consistency error(s) found")
        return 1

    print("All entity definitions are consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
