## Visual Design

### Variants

| Variant | Background | Text Color | Border | Icon Color |
|---------|-----------|-----------|--------|------------|
| Success | `--color-tertiary-50` | `--color-tertiary-800` | `1px solid --color-tertiary-300` | `--color-tertiary-600` |
| Error | `--color-error-50` | `--color-error-800` | `1px solid --color-error-300` | `--color-error-600` |
| Warning | `--color-warning-50` | `--color-warning-800` | `1px solid --color-warning-300` | `--color-warning-600` |
| Info | `--color-secondary-50` | `--color-secondary-800` | `1px solid --color-secondary-300` | `--color-secondary-600` |

### Anatomy
- Icon (20px, left) + Message (`--font-body-sm`) + Action button (right, optional) + Close × (right, optional)
- Layout: horizontal row, icon 12px from left edge, message flexible, buttons right

### States
| State | Close Button | Auto-Dismiss |
|-------|-------------|-------------|
| Dismissible | Visible (×) | No (manual) |
| Persistent | Hidden | No |
| Dismissing | × fades with alert | 200ms fade + slide |

### Sizes & Spacing
- Padding: 12px 16px
- Icon size: 20px, gap to text: 12px
- Action button: ghost sm (right), gap: 8px from text
- Radius: `--radius-md` (8px)

### Responsive
Full-width. On `< --bp-mobile`: action button may wrap below text. Icon stays top-aligned.
