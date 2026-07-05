## Visual Design

### Appearance
- **Box:** 20×20px, `--radius-sm` (4px)
- **Unchecked:** `#ffffff` bg, `2px solid --color-slate-300`
- **Checked:** `--color-primary-500` bg, white checkmark icon 14px
- **Indeterminate:** `--color-primary-500` bg, white minus icon 14px
- **Label:** `--font-body-md`, `--color-on-surface`, gap 8px from box

### States

| State | Box Bg | Box Border | Icon |
|-------|--------|------------|------|
| Unchecked | `#ffffff` | `--color-slate-300` | hidden |
| Unchecked hover | `#ffffff` | `--color-slate-400` | hidden |
| Checked | `--color-primary-500` | `--color-primary-500` | white ✓ |
| Checked hover | `--color-primary-600` | `--color-primary-600` | white ✓ |
| Indeterminate | `--color-primary-500` | `--color-primary-500` | white − |
| Disabled | `--color-slate-100` | `--color-slate-200` | `--color-slate-400` |
| Focus | Standard focus ring on box | — | — |

Transition: 150ms ease-default on all state changes.

### Spacing
- Box↔Label: 8px
- Vertical stack gap: 8px
- Inline horizontal gap: 16px

### Indeterminate
Set via JS (`checkbox.indeterminate = true`). Used for "select all" when some children selected.
