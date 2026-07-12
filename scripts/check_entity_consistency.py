#!/usr/bin/env python3
"""Check that backend ENTITY_META matches frontend TABLE_NAMES and types."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_entity_meta_names() -> frozenset[str]:
    meta = (ROOT / "src" / "salus" / "repositories" / "entity_meta.py").read_text()
    names = re.findall(r'name="([^"]+)"', meta)
    return frozenset(names)


def parse_frontend_table_names() -> frozenset[str]:
    info = (ROOT / "frontend" / "src" / "lib" / "db" / "entity-info.ts").read_text()
    match = re.search(
        r"HARDCODED_FALLBACK.*?=.*?new\s+Set\(\[\s*(.*?)\s*\]\)",
        info, re.DOTALL,
    )
    if not match:
        return frozenset()
    return frozenset(re.findall(r"'([^']+)'", match.group(1)))


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
    frontend = parse_frontend_table_names()
    types = parse_types_interface_names()
    stores = parse_database_store_names()

    all_backend = backend | SPECIAL_ENTITIES

    print(f"ENTITY_META (backend):  {len(backend)} entities")
    print(f"special entities:       {len(SPECIAL_ENTITIES)} entities")
    print(f"TABLE_NAMES (frontend): {len(frontend)} entities")
    print(f"interfaces (types.ts):  {len(types)} interfaces")
    print(f"stores (database.ts):   {len(stores)} stores")
    print()

    in_backend_not_frontend = all_backend - frontend
    for name in sorted(in_backend_not_frontend):
        print(f"  ERROR: '{name}' in backend but NOT in frontend fallback list")
        errors += 1

    in_frontend_not_backend = frontend - all_backend
    for name in sorted(in_frontend_not_backend):
        print(f"  ERROR: '{name}' in frontend fallback but NOT in backend")
        errors += 1

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
