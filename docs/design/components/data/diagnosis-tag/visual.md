## Visual Design

### Variants

| Status | Background | Text | Border | Icon |
|--------|-----------|------|--------|------|
| Active | `--color-primary-100` | `--color-primary-800` | none | none |
| Chronic | `--color-warning-100` | `--color-warning-800` | none | `chronic` 16px left |
| Resolved | `--color-slate-100` | `--color-slate-500` | none | ✓ 14px |
| Primary complaint | `--color-primary-100` | `--color-primary-800` | `2px solid --color-primary-500` | `priority_high` 16px |

### Format
`<code>E11.9</code> — Type 2 Diabetes`. Code: `--font-code-sm` (13px), `--color-slate-700`. Name: `--font-body-sm` (14px).

### Shape
Chip-style pill: `--radius-full`, padding 6px 12px. Primary complaint: slightly larger padding (8px 14px).

### Spacing
- Code↔Dash↔Name: 4px gaps
- Tag padding: 6px 12px (standard), 8px 14px (primary)
