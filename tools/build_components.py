#!/usr/bin/env python3
"""Build components.css from all component style.css files.

Concatenates all templates/components/**/style.css into static/components.css.
Run after any component CSS change.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = ROOT / "src" / "salus" / "templates" / "components"
OUTPUT = ROOT / "src" / "salus" / "static" / "components.css"


def main() -> None:
    files = sorted(COMPONENTS_DIR.rglob("style.css"))
    if not files:
        print("No component style.css files found.")
        return

    parts: list[str] = []
    for f in files:
        rel = f.relative_to(ROOT)
        css = f.read_text(encoding="utf-8").strip()
        parts.append(f"/* @source {rel} */\n\n{css}\n")

    header = "/*\n * Salus Components CSS — AUTO-GENERATED\n * Source: templates/components/**/style.css\n * Regenerate: uv run python tools/build_components.py\n */\n\n"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(header + "\n\n".join(parts) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT.relative_to(ROOT)} from {len(files)} component(s)")


if __name__ == "__main__":
    main()
