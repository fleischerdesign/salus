#!/usr/bin/env python3
"""Validate Salus design system component specs for consistency and completeness.

Checks:
  1. Required sections per component file
  2. Broken cross-references in Related sections
  3. Token consistency (spec tokens vs DESIGN.md YAML components)
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
# Inline components (don't need Responsive section)
# ---------------------------------------------------------------------------
INLINE_COMPONENTS = {
    "icon", "badge", "status-dot", "chip", "link", "divider",
    "inline-code", "focus-ring", "back-link",
}

# ---------------------------------------------------------------------------
# Required sections for every component
# ---------------------------------------------------------------------------
REQUIRED_SECTIONS = [
    re.compile(r"^\*\*(?:Anatomy|Variants):\*\*", re.MULTILINE),
    re.compile(r"^\*\*States:\*\*", re.MULTILINE),
    re.compile(r"^\*\*Accessibility:\*\*", re.MULTILINE),
    re.compile(r"^\*\*Do:\*\*", re.MULTILINE),
    re.compile(r"^\*\*Don't:\*\*", re.MULTILINE),
    re.compile(r"^\*\*Related:\*\*", re.MULTILINE),
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
    """Extract YAML front matter from DESIGN.md."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        print(f"Warning: Could not parse YAML front matter in {path}: {e}", file=sys.stderr)
        return {}


def get_yaml_tokens(design_data: dict) -> set[str]:
    """Extract all token names from DESIGN.md YAML colors, typography, rounded, spacing, components."""
    tokens: set[str] = set()

    # colors
    for key in design_data.get("colors", {}):
        tokens.add(f"--color-{key}")

    # typography
    for key in design_data.get("typography", {}):
        tokens.add(f"--font-{key}")

    # rounded
    for key in design_data.get("rounded", {}):
        tokens.add(f"--radius-{key}")

    # spacing
    for key in design_data.get("spacing", {}):
        tokens.add(f"--space-{key}")

    # components
    for comp_name, comp_data in design_data.get("components", {}).items():
        if isinstance(comp_data, dict):
            for sub_key in comp_data:
                tokens.add(f"--{comp_name}-{sub_key}".replace("_", "-"))
        elif isinstance(comp_data, str):
            tokens.add(f"--{comp_name}")

    return tokens


def get_yaml_component_names(design_data: dict) -> set[str]:
    """Extract all component names from DESIGN.md YAML components section."""
    return set(design_data.get("components", {}).keys())


# ---------------------------------------------------------------------------
# Spec file parser
# ---------------------------------------------------------------------------

def iter_spec_files() -> list[Path]:
    """Return all component spec .md files."""
    files = sorted(COMPONENTS_DIR.rglob("*.md"))
    return [f for f in files if f.name != "README.md"]


def get_component_name(filepath: Path) -> str:
    """Extract normalized component name from file path. E.g. 'core/button.md' → 'button'."""
    return filepath.stem


def get_component_dir(filepath: Path) -> str:
    """Get the parent directory name, e.g. 'core', 'navigation'."""
    return filepath.parent.name


def has_section(content: str, pattern: re.Pattern) -> bool:
    """Check if content has a markdown bold section matching the pattern."""
    return bool(pattern.search(content))


def extract_related_refs(content: str) -> set[str]:
    """Extract file references from the Related section. E.g. 'button.md', 'icon.md'."""
    match = re.search(r"\*\*Related:\*\*\s*\n(.*?)(?=\n\*\*|\n#|\Z)", content, re.DOTALL)
    if not match:
        return set()

    related_text = match.group(1)
    refs = set()
    for m in re.finditer(r'`([^`]+\.md)`', related_text):
        refs.add(m.group(1))
    for m in re.finditer(r'\b([a-z0-9-]+\.md)\b', related_text):
        refs.add(m.group(1))
    return refs


def extract_token_refs(content: str) -> set[str]:
    """Extract token references (--token-name) from spec content."""
    return set(re.findall(r'(--[a-z][a-z0-9-]*(?:-[a-z][a-z0-9-]*)*)', content, re.IGNORECASE))


def is_new_component(content: str) -> bool:
    """Check if component is marked as design spec only (not yet implemented)."""
    return "> Status: **Design spec only" in content


# ---------------------------------------------------------------------------
# Resolve cross-references
# ---------------------------------------------------------------------------

def resolve_related_ref(ref: str, all_files: list[Path]) -> Path | None:
    """Try to find a referenced file in the components tree."""
    for f in all_files:
        if f.name == ref:
            return f
    return None


# ---------------------------------------------------------------------------
# Check 1: Required Sections
# ---------------------------------------------------------------------------

def check_required_sections(filepath: Path, report: Report) -> None:
    """Check that each spec file has all required sections."""
    content = filepath.read_text(encoding="utf-8")
    name = get_component_name(filepath)
    relpath = str(filepath.relative_to(ROOT))

    for i, pattern in enumerate(REQUIRED_SECTIONS):
        section_name = pattern.pattern.split(":")[0].replace(r"\*\*", "").replace(r"\*\*:\*\*", "")
        if not has_section(content, pattern):
            report.findings.append(Finding(
                severity="error",
                file=relpath,
                section=section_name,
                message=f"Missing required section: {section_name}"
            ))

    # Composition (only for container components)
    if name in CONTAINER_COMPONENTS:
        if not has_section(content, re.compile(r"^\*\*Composition:\*\*", re.MULTILINE)):
            report.findings.append(Finding(
                severity="error",
                file=relpath,
                section="Composition",
                message=f"Container component '{name}' must have a Composition section"
            ))

    # Token Values (only for NEW components)
    if is_new_component(content):
        if not has_section(content, re.compile(r"^\*\*Token Values:\*\*", re.MULTILINE)):
            report.findings.append(Finding(
                severity="error",
                file=relpath,
                section="Token Values",
                message="NEW component (design spec only) must have Token Values section"
            ))

    # Responsive (for non-inline components)
    if name not in INLINE_COMPONENTS:
        if not has_section(content, re.compile(r"^\*\*Responsive:\*\*", re.MULTILINE)):
            report.findings.append(Finding(
                severity="warning",
                file=relpath,
                section="Responsive",
                message=f"Non-inline component '{name}' should have a Responsive section"
            ))


# ---------------------------------------------------------------------------
# Check 2: Broken Cross-References
# ---------------------------------------------------------------------------

def check_cross_references(filepath: Path, all_files: list[Path], report: Report) -> None:
    """Check that all Related references point to existing files."""
    content = filepath.read_text(encoding="utf-8")
    relpath = str(filepath.relative_to(ROOT))
    refs = extract_related_refs(content)

    for ref in refs:
        if not resolve_related_ref(ref, all_files):
            report.findings.append(Finding(
                severity="error",
                file=relpath,
                section="Related",
                message=f"Cross-reference '{ref}' does not exist in any component directory"
            ))


# ---------------------------------------------------------------------------
# Check 3: Token Consistency
# ---------------------------------------------------------------------------

def check_token_consistency(files: list[Path], design_data: dict, report: Report) -> None:
    """Check that tokens referenced in specs are defined in DESIGN.md YAML."""
    yaml_tokens = get_yaml_tokens(design_data)
    yaml_components = get_yaml_component_names(design_data)

    for filepath in files:
        content = filepath.read_text(encoding="utf-8")
        relpath = str(filepath.relative_to(ROOT))
        spec_tokens = extract_token_refs(content)

        # Filter out var() references and {path} references
        actual_tokens = {t for t in spec_tokens if not t.startswith("--var")}

        for token in actual_tokens:
            # Strip known prefixes for comparison
            token_base = token.replace("--", "")

            # Check if token exists in YAML (direct match or partial match)
            token_matches = [
                yt for yt in yaml_tokens
                if yt.replace("--", "") == token_base
                or yt.replace("--", "") == token_base.replace("-bg", "").replace("-text", "")
                .replace("-border", "").replace("-color", "").replace("-radius", "")
                .replace("-padding", "").replace("-font", "").replace("-size", "")
                .replace("-shadow", "").replace("-gap", "").replace("-duration", "")
                .replace("-easing", "").replace("-z-index", "").replace("-filter", "")
                .replace("-max-width", "").replace("-transition", "")
            ]

            if not token_matches and token not in DESIGN_KNOWN_TOKENS:
                report.findings.append(Finding(
                    severity="warning",
                    file=relpath,
                    section="Token Values",
                    message=f"Token '{token}' not found in DESIGN.md YAML front matter"
                ))


# Tokens that are compound/derived and won't appear verbatim in DESIGN.md YAML
DESIGN_KNOWN_TOKENS: set[str] = set()


# ---------------------------------------------------------------------------
# Check 4: Component Coverage
# ---------------------------------------------------------------------------

def check_component_coverage(files: list[Path], design_data: dict, report: Report) -> None:
    """Check that YAML components have spec files and vice versa."""
    yaml_names = get_yaml_component_names(design_data)
    spec_names = {get_component_name(f) for f in files}

    for name in yaml_names:
        if name not in spec_names:
            report.findings.append(Finding(
                severity="warning",
                file="DESIGN.md",
                section="components",
                message=f"YAML component '{name}' has no corresponding spec file in docs/design/components/"
            ))

    for name in spec_names:
        if name not in yaml_names:
            report.findings.append(Finding(
                severity="info",
                file=f"components/*/{name}.md",
                section="components",
                message=f"Spec file exists but no YAML component definition in DESIGN.md for '{name}'"
            ))


# ---------------------------------------------------------------------------
# Check 5: Section Ordering (--strict)
# ---------------------------------------------------------------------------

SECTION_ORDER = [
    "Tokens",
    "Status",
    "Anatomy",
    "Variants",
    "States",
    "Sizes",
    "Spacing",
    "Appearance",
    "Placement",
    "Implementation",
    "Responsive",
    "Composition",
    "Accessibility",
    "Token Values",
    "Do",
    "Don't",
    "Related",
]

def check_section_order(filepath: Path, report: Report) -> None:
    """Check that sections appear in the recommended order."""
    content = filepath.read_text(encoding="utf-8")
    relpath = str(filepath.relative_to(ROOT))

    section_matches = list(re.finditer(r"^\*\*(.+?):\*\*", content, re.MULTILINE))
    found_sections = []

    for m in section_matches:
        name = m.group(1).strip()
        for known in SECTION_ORDER:
            if name.startswith(known):
                found_sections.append(known)
                break
        else:
            found_sections.append(name)

    # Check relative ordering
    positions = {s: i for i, s in enumerate(SECTION_ORDER)}
    last_pos = -1
    for sec in found_sections:
        pos = positions.get(sec, 999)
        if pos < last_pos:
            report.findings.append(Finding(
                severity="info",
                file=relpath,
                section="Order",
                message=f"Section '{sec}' appears out of recommended order"
            ))
            break
        last_pos = pos


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_human(report: Report, files_count: int) -> str:
    lines = []
    error_findings = [f for f in report.findings if f.severity == "error"]
    warning_findings = [f for f in report.findings if f.severity == "warning"]
    info_findings = [f for f in report.findings if f.severity == "info"]

    if error_findings:
        lines.append("\nERRORS:")
        for f in error_findings:
            lines.append(f"  ✗ {f.file}")
            lines.append(f"    → {f.message}")

    if warning_findings:
        lines.append("\nWARNINGS:")
        for f in warning_findings:
            lines.append(f"  ⚠ {f.file}")
            lines.append(f"    → {f.message}")

    if info_findings:
        lines.append("\nINFO:")
        for f in info_findings:
            lines.append(f"  ℹ {f.file}")
            lines.append(f"    → {f.message}")

    passed = files_count - report.errors
    lines.insert(0, f"\nSummary: {files_count} files checked, "
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

    # Parse DESIGN.md
    design_data = parse_design_md(DESIGN_MD)
    if not design_data:
        print("Error: Could not parse DESIGN.md YAML front matter", file=sys.stderr)
        return 1

    # Collect all spec files
    files = iter_spec_files()
    if not files:
        print("Error: No spec files found in docs/design/components/", file=sys.stderr)
        return 1

    report = Report()

    # Run checks
    for filepath in files:
        check_required_sections(filepath, report)
        check_cross_references(filepath, files, report)

    check_token_consistency(files, design_data, report)
    check_component_coverage(files, design_data, report)

    if args.strict:
        for filepath in files:
            check_section_order(filepath, report)

    # Output
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
        print(format_human(report, len(files)))

    return 1 if (args.only_errors and report.errors > 0) else 0


if __name__ == "__main__":
    sys.exit(main())
