#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Mapping of arbitrary var tokens to canonical Tailwind tokens
REPLACEMENTS = {
    # Surface & Canvas
    "bg-[var(--bg-surface-0)]": "bg-surface-0",
    "bg-[var(--bg-surface-50)]": "bg-surface-50",
    "bg-[var(--bg-surface-100)]": "bg-surface-100",
    "bg-[var(--bg-surface-200)]": "bg-surface-200",
    "bg-[var(--bg-canvas)]": "bg-canvas",
    "border-[var(--bg-canvas)]": "border-canvas",
    "from-[var(--bg-surface-50)]": "from-surface-50",
    "to-[var(--bg-surface-100)]": "to-surface-100",

    # Typography / Text
    "text-[var(--text-main)]": "text-text-main",
    "text-[var(--text-muted)]": "text-text-muted",
    "text-[var(--text-soft)]": "text-text-soft",
    "border-[var(--text-main)]": "border-text-main",

    # Borders & Dividers
    "border-[var(--border-subtle)]": "border-border-subtle",
    "border-[var(--border-strong)]": "border-border-strong",
    "divide-[var(--border-subtle)]": "divide-border-subtle",
    "bg-[var(--border-subtle)]": "bg-border-subtle",
    "bg-[var(--border-strong)]": "bg-border-strong",
    "text-[var(--border-strong)]": "text-border-strong",

    # Primary & Soft
    "text-[var(--color-primary)]": "text-primary",
    "bg-[var(--color-primary)]": "bg-primary",
    "border-[var(--color-primary)]": "border-primary",
    "ring-[var(--color-primary)]": "ring-primary",
    "outline-[var(--color-primary)]": "outline-primary",
    "fill-[var(--color-primary)]": "fill-primary",
    "from-[var(--color-primary)]": "from-primary",
    "bg-[var(--color-primary-soft)]": "bg-primary-soft",

    # Vital & Soft
    "text-[var(--color-vital)]": "text-vital",
    "bg-[var(--color-vital)]": "bg-vital",
    "border-[var(--color-vital)]": "border-vital",
    "bg-[var(--color-vital-soft)]": "bg-vital-soft",

    # Activity & Soft
    "text-[var(--color-activity)]": "text-activity",
    "bg-[var(--color-activity)]": "bg-activity",
    "to-[var(--color-activity)]": "to-activity",
    "bg-[var(--color-activity-soft)]": "bg-activity-soft",

    # Hydrate & Soft
    "text-[var(--color-hydrate)]": "text-hydrate",
    "bg-[var(--color-hydrate)]": "bg-hydrate",
    "border-[var(--color-hydrate)]": "border-hydrate",
    "bg-[var(--color-hydrate-soft)]": "bg-hydrate-soft",

    # Fasting & Soft
    "text-[var(--color-fasting)]": "text-fasting",
    "bg-[var(--color-fasting-soft)]": "bg-fasting-soft",

    # Circadian & Soft
    "text-[var(--color-circadian)]": "text-circadian",
    "bg-[var(--color-circadian)]": "bg-circadian",
    "border-[var(--color-circadian)]": "border-circadian",
    "bg-[var(--color-circadian-soft)]": "bg-circadian-soft",

    # Success & Soft
    "text-[var(--color-success)]": "text-success",
    "bg-[var(--color-success)]": "bg-success",
    "border-[var(--color-success)]": "border-success",
    "bg-[var(--color-success-soft)]": "bg-success-soft",

    # Dock Glass
    "bg-[var(--glass-dock-bg)]": "bg-glass-dock",

    # Shadows & Radii
    "shadow-[var(--shadow-card)]": "shadow-card",
    "shadow-[var(--shadow-dock)]": "shadow-dock",
    "rounded-[var(--radius-lg)]": "rounded-lg",
    "rounded-[var(--radius-sm)]": "rounded-sm",
}

# Regex to match exact base and optional opacity: (bg-[var(--bg-surface-50)])(/60)?
# Sort by length descending to match longer specific keys first
sorted_keys = sorted(REPLACEMENTS.keys(), key=len, reverse=True)

patterns = []
for k in sorted_keys:
    escaped_k = re.escape(k)
    target = REPLACEMENTS[k]
    # Match key followed by optional opacity /XX
    patterns.append((re.compile(escaped_k + r'(/\d+)?'), target))

def process_file(file_path: Path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    total_replaced = 0

    for regex, target in patterns:
        def repl(m):
            opacity = m.group(1) or ""
            return target + opacity
        
        content, count = regex.subn(repl, content)
        total_replaced += count

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {file_path}: {total_replaced} replacements")
        return total_replaced
    return 0

def main():
    src_dir = Path("/home/philipp/dev/salus/frontend/src")
    total_files = 0
    total_replacements = 0

    for ext in ["*.svelte", "*.ts"]:
        for file_path in src_dir.rglob(ext):
            # Skip node_modules or app.css
            if "node_modules" in str(file_path):
                continue
            rep = process_file(file_path)
            if rep > 0:
                total_files += 1
                total_replacements += rep

    print(f"\nDone! Replaced {total_replacements} instances across {total_files} files.")

if __name__ == "__main__":
    main()
