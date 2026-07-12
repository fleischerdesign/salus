#!/usr/bin/env python3
"""Export the OpenAPI schema from the FastAPI app without starting a server.

Usage:
    uv run python scripts/export_openapi.py [output_path]

Writes JSON to stdout or the given file path.
"""
import json
import sys
from pathlib import Path

from salus.main import app


def main() -> None:
    schema = app.openapi()
    output = sys.argv[1] if len(sys.argv) > 1 else None

    if output:
        Path(output).write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
        print(f"OpenAPI schema written to {output}", file=sys.stderr)
    else:
        print(json.dumps(schema, indent=2))


if __name__ == "__main__":
    main()
