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
    # 1. Build CSS
    css_files = sorted(COMPONENTS_DIR.rglob("style.css"))
    if css_files:
        css_parts: list[str] = []
        for f in css_files:
            rel = f.relative_to(ROOT)
            css = f.read_text(encoding="utf-8").strip()
            css_parts.append(f"/* @source {rel} */\n\n{css}\n")

        header = "/*\n * Salus Components CSS — AUTO-GENERATED\n * Source: templates/components/[component]/style.css\n * Regenerate: uv run python tools/build_components.py\n */\n\n"
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(header + "\n\n".join(css_parts) + "\n", encoding="utf-8")
        print(f"Built {OUTPUT.relative_to(ROOT)} from {len(css_files)} component(s)")
    else:
        print("No component style.css files found.")

    # 2. Build JS
    js_files = sorted(COMPONENTS_DIR.rglob("script.js"))
    output_js = OUTPUT.parent / "components.js"
    if js_files:
        js_parts: list[str] = []
        for f in js_files:
            rel = f.relative_to(ROOT)
            js = f.read_text(encoding="utf-8").strip()
            # Wrap in IIFE for local variable scoping isolation
            js_parts.append(f"/* @source {rel} */\n(function() {{\n{js}\n}})();\n")

        header_js = "/*\n * Salus Components JS — AUTO-GENERATED\n * Source: templates/components/[component]/script.js\n * Regenerate: uv run python tools/build_components.py\n */\n\n"
        output_js.write_text(header_js + "\n\n".join(js_parts) + "\n", encoding="utf-8")
        print(f"Built {output_js.relative_to(ROOT)} from {len(js_files)} component(s)")
    else:
        # Create a fallback empty file if none exist yet to avoid browser 404s
        if not output_js.exists():
            output_js.write_text("/* No component scripts found */\n", encoding="utf-8")


if __name__ == "__main__":
    main()
