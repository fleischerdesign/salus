#!/usr/bin/env python3
"""Validate Salus design system component specs for consistency and completeness.

Checks:
  1. Required sections per component file
  2. Broken cross-references in Related sections
  3. Token consistency (spec tokens vs DESIGN.md YAML)
  4. Component coverage (YAML components ↔ spec files)
  5. Section ordering (optional, --strict)

Usage:
    uv run python tools/validate_specs.py
    uv run python tools/validate_specs.py --only-errors
    uv run python tools/validate_specs.py --json
    uv run python tools/validate_specs.py --strict
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field

try:
    import yaml
except ImportError:
    print("Error: pyyaml is required. Install with: uv sync", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DESIGN_MD = ROOT / "DESIGN.md"
COMPONENTS_DIR = ROOT / "docs" / "design" / "components"

# ---------------------------------------------------------------------------
# Container components (must have Composition section)
# ---------------------------------------------------------------------------
CONTAINER_COMPONENTS = {
    "card", "modal", "widget", "table", "accordion", "tab-bar",
    "wizard", "invite-modal", "confirmation-dialog", "peer-card",
    "plan-card", "form-layout",
}

# ---------------------------------------------------------------------------
# Required sections for every component
# ---------------------------------------------------------------------------
REQUIRED_SECTIONS = [
    (re.compile(r"^\*\*(?:Anatomy|Variants):\*\*", re.MULTILINE), "Anatomy/Variants"),
    (re.compile(r"^\*\*States:\*\*", re.MULTILINE), "States"),
    (re.compile(r"^\*\*Accessibility:\*\*", re.MULTILINE), "Accessibility"),
    (re.compile(r"^\*\*Do:\*\*", re.MULTILINE), "Do"),
    (re.compile(r"^\*\*Don't:\*\*", re.MULTILINE), "Don't"),
    (re.compile(r"^\*\*Related:\*\*", re.MULTILINE), "Related"),
]

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    severity: str  # error, warning, info
    file: str
    section: str
    message: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> int:
        return sum(1 for f in self.findings if f.severity == "error")

    @property
    def warnings(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warning")

    @property
    def infos(self) -> int:
        return sum(1 for f in self.findings if f.severity == "info")

    @property
    def summary(self) -> dict:
        return {"errors": self.errors, "warnings": self.warnings, "info": self.infos}


# ---------------------------------------------------------------------------
# YAML front matter parser
# ---------------------------------------------------------------------------

def parse_design_md(path: Path) -> dict:
    """Extract YAML front matter from DESIGN.md using line-boundary fence matching."""
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            yaml_str = "\n".join(lines[1:i])
            try:
                return yaml.safe_load(yaml_str) or {}
            except yaml.YAMLError as e:
                print(f"Warning: YAML parse error in {path}: {e}", file=sys.stderr)
                return {}
    return {}


def get_yaml_component_names(design_data: dict) -> set[str]:
    """Return component names that are dict entries (real components, not variant strings)."""
    return {k for k, v in design_data.get("components", {}).items() if isinstance(v, dict)}


def get_yaml_tokens(design_data: dict) -> set[str]:
    """Generate CSS token names from YAML structure: --{section}-{key} for each section."""
    tokens: set[str] = set()

    section_prefixes = {
        "colors": "--color-",
        "typography": "--font-",
        "rounded": "--radius-",
        "spacing": "--space-",
        "shadows": "--shadow-",
        "z-index": "--z-",
        "durations": "--duration-",
        "easings": "--ease-",
        "transitions": "--transition-",
        "nav-tokens": "--nav-",
        "breakpoints": "--bp-",
        "disabled": "--disabled-",
    }

    for section, prefix in section_prefixes.items():
        for key in design_data.get(section, {}):
            tokens.add(f"{prefix}{key}")

    # components: --{name}-{subkey}
    for comp_name, comp_data in design_data.get("components", {}).items():
        if isinstance(comp_data, dict):
            for sub_key in comp_data:
                tokens.add(f"--{comp_name}-{sub_key.replace('_', '-')}")

    return tokens


def is_inline_component(design_data: dict, name: str) -> bool:
    """Check if a component is marked as inline (no Responsive section needed)."""
    comp = design_data.get("components", {}).get(name)
    if isinstance(comp, dict):
        return comp.get("responsive") is False
    return False


def is_new_component(content: str) -> bool:
    """Check if component is marked as design spec only."""
    return "> Status: **Design spec only" in content


# ---------------------------------------------------------------------------
# Spec file parsers
# ---------------------------------------------------------------------------

def iter_spec_files() -> list[Path]:
    """Return all component directories that have both overview.md and visual.md."""
    dirs: list[Path] = []
    for d in sorted(COMPONENTS_DIR.rglob("*")):
        if d.is_dir() and (d / "overview.md").exists() and (d / "visual.md").exists():
            dirs.append(d)
    return dirs


def get_component_name(filepath: Path) -> str:
    """Extract component name from directory path. E.g. 'core/btn' → 'btn'."""
    return filepath.name


def get_component_relpath(filepath: Path) -> str:
    """Relative path from repo root."""
    return str(filepath.relative_to(ROOT))


def read_overview(dirpath: Path) -> str:
    """Read the overview.md content for a component directory."""
    return (dirpath / "overview.md").read_text(encoding="utf-8")


def read_visual(dirpath: Path) -> str:
    """Read the visual.md content for a component directory."""
    vf = dirpath / "visual.md"
    return vf.read_text(encoding="utf-8") if vf.exists() else ""


def read_all_content(dirpath: Path) -> str:
    """Read overview + visual combined for token reference scanning."""
    return read_overview(dirpath) + "\n" + read_visual(dirpath)


def has_section(content: str, pattern: re.Pattern) -> bool:
    """Check if content has a markdown bold section."""
    return bool(pattern.search(content))


def extract_token_refs(content: str) -> set[str]:
    """Extract all --css-token references from spec content."""
    return set(re.findall(r'(--[a-z][a-z0-9-]*(?:-[a-z][a-z0-9-]*)*)', content, re.IGNORECASE))


def extract_related_refs(content: str) -> set[str]:
    """Extract file references from the Related section."""
    match = re.search(r"\*\*Related:\*\*\s*\n(.*?)(?=\n\*\*|\n#|\Z)", content, re.DOTALL)
    if not match:
        return set()
    related_text = match.group(1)
    return {m.group(1) for m in re.finditer(r'`?([a-z0-9-]+\.md)`?', related_text)}


def resolve_related_ref(ref: str, all_dirs: list[Path]) -> Path | None:
    """Find a referenced component directory."""
    clean = ref.removesuffix(".md")
    for d in all_dirs:
        if d.name == clean:
            return d
    return None


# ---------------------------------------------------------------------------
# Check 1: Required Sections
# ---------------------------------------------------------------------------

def check_required_sections(dirpath: Path, design_data: dict, report: Report) -> None:
    """Check that overview.md has all required sections."""
    content = read_overview(dirpath)
    name = get_component_name(dirpath)
    relpath = get_component_relpath(dirpath)

    for pattern, section_name in REQUIRED_SECTIONS:
        if not has_section(content, pattern):
            report.findings.append(Finding(
                severity="error", file=f"{relpath}/overview.md", section=section_name,
                message=f"Missing required section: {section_name}"
            ))

    if name in CONTAINER_COMPONENTS:
        if not has_section(content, re.compile(r"^\*\*Composition:\*\*", re.MULTILINE)):
            report.findings.append(Finding(
                severity="error", file=f"{relpath}/overview.md", section="Composition",
                message=f"Container component '{name}' must have a Composition section"
            ))

    if is_new_component(content):
        if not has_section(content, re.compile(r"^\*\*Token Values:\*\*", re.MULTILINE)):
            report.findings.append(Finding(
                severity="error", file=f"{relpath}/overview.md", section="Token Values",
                message="NEW component (design spec only) must have Token Values section"
            ))

    if not is_inline_component(design_data, name):
        if not has_section(content, re.compile(r"^\*\*Responsive:\*\*", re.MULTILINE)):
            report.findings.append(Finding(
                severity="info", file=f"{relpath}/overview.md", section="Responsive",
                message=f"Component '{name}' could benefit from a Responsive section (or set responsive: false in YAML)"
            ))


# ---------------------------------------------------------------------------
# Check 2: Broken Cross-References
# ---------------------------------------------------------------------------

def check_cross_references(dirpath: Path, all_dirs: list[Path], report: Report) -> None:
    """Check that all Related references point to existing directories."""
    content = read_overview(dirpath)
    relpath = get_component_relpath(dirpath)
    refs = extract_related_refs(content)

    for ref in refs:
        if not resolve_related_ref(ref, all_dirs):
            report.findings.append(Finding(
                severity="error", file=f"{relpath}/overview.md", section="Related",
                message=f"Cross-reference '{ref}' does not exist in any component directory"
            ))


# ---------------------------------------------------------------------------
# Check 3: Token Consistency
# ---------------------------------------------------------------------------

def check_token_consistency(dirs: list[Path], design_data: dict, report: Report) -> None:
    """Check that tokens referenced in specs are defined in DESIGN.md YAML."""
    yaml_tokens = get_yaml_tokens(design_data)
    yaml_components = design_data.get("components", {})

    for dirpath in dirs:
        content = read_all_content(dirpath)
        relpath = get_component_relpath(dirpath)
        spec_tokens = extract_token_refs(content)

        for token in spec_tokens:
            # 1. Exact match
            if token in yaml_tokens:
                continue

            # 2. Derivative: --{prefix}-{...} where prefix matches a YAML component
            parts = token.replace("--", "").split("-")
            matched = False
            for end in range(len(parts), 0, -1):
                candidate = "-".join(parts[:end])
                if candidate in yaml_components:
                    matched = True
                    break
                # Candidate is a component family prefix (e.g. "btn" for "btn-primary")
                if any(k.startswith(candidate + "-") for k in yaml_components):
                    matched = True
                    break
            if matched:
                continue

            report.findings.append(Finding(
                severity="info", file=f"{relpath}/overview.md", section="Token Values",
                message=f"Token '{token}' not found in DESIGN.md YAML — may need YAML entry or prefix alignment"
            ))


# ---------------------------------------------------------------------------
# Check 4: Component Coverage
# ---------------------------------------------------------------------------

def check_component_coverage(dirs: list[Path], design_data: dict, report: Report) -> None:
    """Check that every spec directory has a YAML component entry."""
    yaml_names = get_yaml_component_names(design_data)
    spec_names = {get_component_name(d) for d in dirs}

    for name in spec_names - yaml_names:
        report.findings.append(Finding(
            severity="error", file=f"components/*/{name}/overview.md", section="components",
            message=f"Spec directory has no YAML component definition for '{name}' — add it to DESIGN.md components"
        ))


# ---------------------------------------------------------------------------
# Check 5: Section Ordering (--strict)
# ---------------------------------------------------------------------------

SECTION_ORDER = {
    "Tokens": 1, "Status": 2, "Anatomy": 3, "Variants": 4, "States": 5,
    "Sizes": 6, "Spacing": 7, "Appearance": 8, "Placement": 9, "Implementation": 10,
    "Responsive": 11, "Composition": 12, "Accessibility": 13, "Token Values": 14,
    "Do": 15, "Don't": 16, "Related": 17,
}

def check_section_order(dirpath: Path, report: Report) -> None:
    """Check that sections appear in the recommended order."""
    content = read_overview(dirpath)
    relpath = get_component_relpath(dirpath)
    last_pos = -1

    for m in re.finditer(r"^\*\*(.+?):\*\*", content, re.MULTILINE):
        name = m.group(1).strip()
        pos = SECTION_ORDER.get(name, 999)
        if pos < last_pos:
            report.findings.append(Finding(
                severity="info", file=f"{relpath}/overview.md", section="Order",
                message=f"Section '{name}' appears out of recommended order"
            ))
            break
        last_pos = pos


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_human(report: Report, dirs_count: int) -> str:
    lines = []
    by_severity = {"error": ("ERRORS:", "✗"), "warning": ("WARNINGS:", "⚠"), "info": ("INFO:", "ℹ")}
    for sev, (label, icon) in by_severity.items():
        findings = [f for f in report.findings if f.severity == sev]
        if findings:
            lines.append(f"\n{label}")
            for f in findings:
                lines.append(f"  {icon} {f.file}")
                lines.append(f"    → {f.message}")

    passed = dirs_count - report.errors
    lines.insert(0, f"\nSummary: {dirs_count} directories checked, "
                    f"{report.errors} errors, {report.warnings} warnings, "
                    f"{report.infos} info, {passed} passed")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Salus design system component specs")
    parser.add_argument("--only-errors", action="store_true", help="Only show errors")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--strict", action="store_true", help="Also check section ordering")
    args = parser.parse_args()

    design_data = parse_design_md(DESIGN_MD)
    if not design_data:
        print("Error: Could not parse DESIGN.md YAML front matter", file=sys.stderr)
        return 1

    dirs = iter_spec_files()
    if not dirs:
        print("Error: No component directories found in docs/design/components/", file=sys.stderr)
        return 1

    report = Report()

    for dirpath in dirs:
        check_required_sections(dirpath, design_data, report)
        check_cross_references(dirpath, dirs, report)

    check_token_consistency(dirs, design_data, report)
    check_component_coverage(dirs, design_data, report)

    if args.strict:
        for dirpath in dirs:
            check_section_order(dirpath, report)

    if args.json:
        output = {
            "findings": [
                {"severity": f.severity, "file": f.file, "section": f.section, "message": f.message}
                for f in report.findings
            ],
            "summary": report.summary,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(report, len(dirs)))

    return 1 if (args.only_errors and report.errors > 0) else 0


if __name__ == "__main__":
    sys.exit(main())
