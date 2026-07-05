## Visual Design

### Appearance
- **Shape:** `--radius-full` (pill), 24px height, 4px 12px padding
- **Font:** `--font-label-sm` (12px, 500)
- **Icon (optional):** 14px, left of label, gap 4px
- **Dismiss ×:** 14px, right, transparent → variant hover

### Variants

| Variant | Background | Text | Icon Color | Dismiss Hover |
|---------|-----------|------|------------|---------------|
| Success | `--color-tertiary-50` | `--color-tertiary-800` | `--color-tertiary-600` | `--color-tertiary-100` |
| Warning | `--color-warning-50` | `--color-warning-800` | `--color-warning-600` | `--color-warning-100` |
| Error | `--color-error-50` | `--color-error-800` | `--color-error-600` | `--color-error-100` |
| Neutral | `--color-slate-100` | `--color-slate-600` | `--color-slate-500` | `--color-slate-200` |

### Types
| Type | Default | Hover | Click |
|------|---------|-------|-------|
| Status | Variant default | No change | No action |
| Action | Variant default | Background darkens 1 shade | Executes action |
| Removable | Variant default | Dismiss × highlights | Removes chip |

### Spacing
- Icon↔Label: 4px. Chip↔Chip: 4px (row), 8px (wrap)
