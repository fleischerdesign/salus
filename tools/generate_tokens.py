#!/usr/bin/env python3
"""Generate CSS custom properties from DESIGN.md YAML front matter.

Usage:
    uv run python tools/generate_tokens.py          # → static/tokens.css
    uv run python tools/generate_tokens.py --check  # verify no changes needed

Outputs:
    static/tokens.css  — :root + [data-theme="dark"] blocks
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: pyyaml is required. Install with: uv sync", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
DESIGN_MD = ROOT / "DESIGN.md"
OUTPUT_CSS = ROOT / "src" / "salus" / "static" / "tokens.css"

PALETTE_SCALES = ("primary", "secondary", "tertiary", "error", "warning")

SECTION_TO_PREFIX = {
    "colors": "color",
    "rounded": "radius",
    "spacing": "space",
    "shadows": "shadow",
    "z-index": "z",
    "durations": "duration",
    "easings": "ease",
    "transitions": "transition",
    "nav-tokens": "nav",
    "breakpoints": "bp",
    "disabled": "disabled",
}

PROPERTY_MAP = {
    "backgroundColor": "bg",
    "textColor": "text",
    "borderColor": "border-color",
    "fontFamily": "font-family",
    "fontSize": "font-size",
    "border-radius": "radius",
}

# ---------------------------------------------------------------------------
# YAML parsing
# ---------------------------------------------------------------------------


def parse_design_md(path: Path) -> dict:
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            yaml_str = "\n".join(lines[1:i])
            return yaml.safe_load(yaml_str) or {}
    return {}


# ---------------------------------------------------------------------------
# Reference resolution
# ---------------------------------------------------------------------------

REF_RE = re.compile(r"\{(\w+)\.([\w-]+)\}")

SECTION_TO_REF_PREFIX = {
    "colors": "color",
    "typography": "font",
    "shadows": "shadow",
    "rounded": "radius",
    "spacing": "space",
}


def resolve_ref(value: str) -> str:
    """Resolve {section.key} references to var(--prefix-key)."""

    def _replace(m: re.Match) -> str:
        section, key = m.group(1), m.group(2)
        prefix = SECTION_TO_REF_PREFIX.get(section, section)
        return f"var(--{prefix}-{key})"

    return REF_RE.sub(_replace, value)


def to_kebab(name: str) -> str:
    """camelCase → kebab-case."""
    return re.sub(r"([A-Z])", r"-\1", name).lower()


def sub_prop_to_css(prop: str) -> str:
    """Map a YAML sub-property key to a CSS property suffix."""
    if prop in PROPERTY_MAP:
        return PROPERTY_MAP[prop]
    if prop == "rounded":
        return "radius"
    return to_kebab(prop)


# ---------------------------------------------------------------------------
# Token generation
# ---------------------------------------------------------------------------


def generate_global_tokens(design: dict) -> list[str]:
    """Generate :root CSS custom properties for all non-component sections."""
    lines: list[str] = []
    lines.append("  /* ── Colors ────────────────────────────────────────── */")

    for key, value in design.get("colors", {}).items():
        lines.append(f"  --color-{key}: {value};")

    lines.append("")
    lines.append("  /* ── Typography ───────────────────────────────────── */")

    for key, value in design.get("typography", {}).items():
        if isinstance(value, dict):
            family = value.get("fontFamily", "'Manrope', system-ui, sans-serif")
            weight = value.get("fontWeight", 400)
            size = value.get("fontSize", "16px")
            lh = value.get("lineHeight", "24px")
            ls = value.get("letterSpacing", None)
            shorthand = f"{weight} {size}/{lh} {family}"
            lines.append(f"  --font-{key}: {shorthand};")
            if ls:
                lines.append(f"  --font-{key}-letter-spacing: {ls};")
        else:
            lines.append(f"  --font-{key}: {value};")

    lines.append("")
    lines.append("  /* ── Border Radius ─────────────────────────────────── */")

    for key, value in design.get("rounded", {}).items():
        lines.append(f"  --radius-{key}: {value};")

    lines.append("")
    lines.append("  /* ── Spacing ───────────────────────────────────────── */")

    for key, value in design.get("spacing", {}).items():
        lines.append(f"  --space-{key}: {value};")

    lines.append("")
    lines.append("  /* ── Shadows ───────────────────────────────────────── */")

    for key, value in design.get("shadows", {}).items():
        lines.append(f"  --shadow-{key}: {value};")

    lines.append("")
    lines.append("  /* ── Z-Index ───────────────────────────────────────── */")

    for key, value in design.get("z-index", {}).items():
        lines.append(f"  --z-{key}: {value};")

    lines.append("")
    lines.append("  /* ── Durations ─────────────────────────────────────── */")

    for key, value in design.get("durations", {}).items():
        lines.append(f"  --duration-{key}: {value};")

    lines.append("")
    lines.append("  /* ── Easings ───────────────────────────────────────── */")

    for key, value in design.get("easings", {}).items():
        lines.append(f"  --ease-{key}: {value};")

    lines.append("")
    lines.append("  /* ── Transitions ───────────────────────────────────── */")

    for key, value in design.get("transitions", {}).items():
        resolved = resolve_ref(value)
        lines.append(f"  --transition-{key}: {resolved};")

    lines.append("")
    lines.append("  /* ── Navigation Shared Tokens ──────────────────────── */")

    for key, value in design.get("nav-tokens", {}).items():
        resolved = resolve_ref(value)
        lines.append(f"  --nav-{key}: {resolved};")

    lines.append("")
    lines.append("  /* ── Breakpoints ───────────────────────────────────── */")

    for key, value in design.get("breakpoints", {}).items():
        lines.append(f"  --bp-{key}: {value};")

    lines.append("")
    lines.append("  /* ── Disabled State ────────────────────────────────── */")

    for key, value in design.get("disabled", {}).items():
        lines.append(f"  --disabled-{key}: {value};")

    return lines


def generate_component_tokens(design: dict) -> list[str]:
    """Generate component-level CSS custom properties."""
    lines: list[str] = []
    lines.append("  /* ── Component Tokens ──────────────────────────────── */")

    for comp_name, comp_data in design.get("components", {}).items():
        if isinstance(comp_data, dict):
            for prop, value in comp_data.items():
                if prop == "responsive":
                    continue
                css_prop = sub_prop_to_css(prop)
                resolved = resolve_ref(value) if isinstance(value, str) else str(value)
                lines.append(f"  --{comp_name}-{css_prop}: {resolved};")
        elif isinstance(comp_data, str):
            resolved = resolve_ref(comp_data)
            lines.append(f"  --{comp_name}: {resolved};")

    return lines


# ---------------------------------------------------------------------------
# Dark mode derivation
# ---------------------------------------------------------------------------

PALETTE_REVERSAL = {50: 900, 100: 800, 200: 700, 300: 600, 400: 500, 500: 400, 600: 300, 700: 200, 800: 100, 900: 50}

DARK_SURFACE_MAP = {
    "surface": "#0f172a",
    "surface-dim": "#0f172a",
    "surface-bright": "#334155",
    "surface-container-lowest": "#0f172a",
    "surface-container-low": "#1e293b",
    "surface-container": "#1e293b",
    "surface-container-high": "#1e293b",
    "surface-container-highest": "#334155",
    "on-surface": "#e2e8f0",
    "on-surface-variant": "#94a3b8",
    "inverse-surface": "#eaf1ff",
    "inverse-on-surface": "#213145",
    "outline": "#475569",
    "outline-variant": "#334155",
    "surface-tint": "#a5b4fc",
    "background": "#0f172a",
    "on-background": "#e2e8f0",
    "on-primary": "#1e1b4b",
    "on-primary-container": "#e0e7ff",
    "on-secondary": "#0c4a6e",
    "on-secondary-container": "#bae6fd",
    "on-tertiary": "#064e3b",
    "on-tertiary-container": "#d1fae5",
    "on-error": "#7f1d1d",
    "on-error-container": "#fee2e2",
}


def derive_palette_dark(light_colors: dict, scale_name: str) -> dict[str, str]:
    """Derive dark palette by reversing scale positions."""
    dark: dict[str, str] = {}
    for shade, dark_shade in PALETTE_REVERSAL.items():
        light_key = f"{scale_name}-{shade}"
        dark_key = f"{scale_name}-{dark_shade}"
        if light_key in light_colors and dark_key in light_colors:
            dark[dark_key] = light_colors[light_key]
    return dark


def derive_dark_colors(light_colors: dict) -> dict[str, str]:
    """Generate a complete dark-mode color map."""
    dark: dict[str, str] = DARK_SURFACE_MAP.copy()

    for scale in PALETTE_SCALES:
        dark.update(derive_palette_dark(light_colors, scale))

    for key, value in light_colors.items():
        if key.startswith("metric-") or key.startswith("rank-"):
            dark[key] = _dim_metric(value)

    slate_keys = {k for k in light_colors if k.startswith("slate-")}
    for k in slate_keys:
        dark[k] = light_colors[k]

    for key, value in light_colors.items():
        if key in dark:
            continue
        if key in ("primary", "secondary", "tertiary", "error", "warning"):
            dark[key] = light_colors.get(f"{key}-300", light_colors[f"{key}-500"])
        elif key.endswith("-container"):
            continue
        elif any(key.startswith(f"{s}-") for s in PALETTE_SCALES):
            parts = key.rsplit("-", 1)
            try:
                shade = int(parts[1])
            except ValueError:
                continue
            if shade in PALETTE_REVERSAL:
                continue

    return dark


def _dim_metric(hex_color: str) -> str:
    """Slightly desaturate and brighten a metric color for dark backgrounds."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return f"#{hex_color}"
    try:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    except ValueError:
        return f"#{hex_color}"
    h, s, li = _rgb_to_hsl(r, g, b)
    li = min(li + 10, 85)
    s = max(s - 15, 30)
    nr, ng, nb = _hsl_to_rgb(h, s, li)
    return f"#{nr:02x}{ng:02x}{nb:02x}"


def _rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    rr, gg, bb = r / 255.0, g / 255.0, b / 255.0
    mx = max(rr, gg, bb)
    mn = min(rr, gg, bb)
    li = (mx + mn) / 2
    if mx == mn:
        return 0.0, 0.0, round(li * 100, 1)
    d = mx - mn
    s = d / (2 - mx - mn) if li > 0.5 else d / (mx + mn)
    if mx == rr:
        h = (gg - bb) / d + (6 if gg < bb else 0)
    elif mx == gg:
        h = (bb - rr) / d + 2
    else:
        h = (rr - gg) / d + 4
    h /= 6
    return round(h * 360, 1), round(s * 100, 1), round(li * 100, 1)


def _hsl_to_rgb(h: float, s: float, li: float) -> tuple[int, int, int]:
    h /= 360
    s /= 100
    li /= 100
    if s == 0:
        v = round(li * 255)
        return v, v, v

    def hue_to_rgb(p: float, q: float, t: float) -> float:
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    q = li * (1 + s) if li < 0.5 else li + s - li * s
    p = 2 * li - q
    return (
        round(hue_to_rgb(p, q, h + 1 / 3) * 255),
        round(hue_to_rgb(p, q, h) * 255),
        round(hue_to_rgb(p, q, h - 1 / 3) * 255),
    )


def generate_dark_tokens(design: dict) -> list[str]:
    """Generate [data-theme='dark'] block."""
    light_colors = design.get("colors", {})
    dark_colors = derive_dark_colors(light_colors)

    lines: list[str] = []
    lines.append("[data-theme=\"dark\"] {")
    lines.append("  color-scheme: dark;")
    lines.append("")
    lines.append("  /* ── Colors ────────────────────────────────────── */")

    for key in light_colors:
        dark_value = dark_colors.get(key, light_colors[key])
        lines.append(f"  --color-{key}: {dark_value};")

    lines.append("}")
    return lines


def generate_light_tokens(design: dict) -> list[str]:
    """Generate [data-theme='light'] block (overrides dark media query when user selects light)."""
    light_colors = design.get("colors", {})

    lines: list[str] = []
    lines.append("[data-theme=\"light\"] {")
    lines.append("  color-scheme: light;")
    lines.append("")
    lines.append("  /* ── Colors ────────────────────────────────────── */")

    for key in light_colors:
        lines.append(f"  --color-{key}: {light_colors[key]};")

    lines.append("}")
    return lines


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def generate_keyframes(design: dict) -> list[str]:
    lines: list[str] = []
    for key, value in design.get("keyframes", {}).items():
        lines.append(f"@keyframes --{key} {{")
        lines.append(f"  {value}")
        lines.append("}")
        lines.append("")
    return lines


def generate_css(design: dict) -> str:
    header = [
        "/*",
        " * Salus Design Tokens",
        " * AUTO-GENERATED from DESIGN.md — do not edit by hand.",
        " * Regenerate: uv run python tools/generate_tokens.py",
        " */",
        "",
        ":root {",
    ]
    global_tokens = generate_global_tokens(design)
    component_tokens = generate_component_tokens(design)
    dark_tokens = generate_dark_tokens(design)
    keyframes = generate_keyframes(design)

    return (
        "\n".join(header)
        + "\n"
        + "\n".join(global_tokens)
        + "\n"
        + "\n".join(component_tokens)
        + "\n}\n\n"
        + "\n".join(keyframes)
        + "\n"
        + "@media (prefers-color-scheme: dark) {\n"
        + "  :root {\n"
        + "\n".join(_indent(generate_dark_color_tokens(design), 4))
        + "\n  }\n}\n\n"
        + "\n".join(dark_tokens)
        + "\n\n"
        + "\n".join(generate_light_tokens(design))
        + "\n"
    )


def _indent(lines: list[str], spaces: int) -> list[str]:
    return [" " * spaces + line for line in lines]


def generate_dark_color_tokens(design: dict) -> list[str]:
    """Generate just the dark color overrides (no [data-theme] wrapper)."""
    light_colors = design.get("colors", {})
    dark_colors = derive_dark_colors(light_colors)

    lines: list[str] = []
    lines.append("color-scheme: dark;")
    lines.append("")
    lines.append("/* Colors */")
    for key in light_colors:
        dark_value = dark_colors.get(key, light_colors[key])
        lines.append(f"--color-{key}: {dark_value};")
    return lines


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate CSS tokens from DESIGN.md")
    parser.add_argument("--check", action="store_true", help="Exit 1 if output differs from file on disk")
    parser.add_argument("--output", type=Path, default=OUTPUT_CSS, help=f"Output path (default: {OUTPUT_CSS})")
    args = parser.parse_args()

    design = parse_design_md(DESIGN_MD)
    if not design:
        print("Error: No YAML front matter found in DESIGN.md", file=sys.stderr)
        sys.exit(1)

    css = generate_css(design)

    if args.check:
        if args.output.exists():
            existing = args.output.read_text(encoding="utf-8")
            if existing.strip() == css.strip():
                print("tokens.css is up to date.")
                sys.exit(0)
            else:
                print("Error: tokens.css is out of date. Run: uv run python tools/generate_tokens.py", file=sys.stderr)
                sys.exit(1)
        else:
            print("Error: tokens.css does not exist. Run: uv run python tools/generate_tokens.py", file=sys.stderr)
            sys.exit(1)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(css, encoding="utf-8")
    print(f"Generated {args.output}")


if __name__ == "__main__":
    main()
