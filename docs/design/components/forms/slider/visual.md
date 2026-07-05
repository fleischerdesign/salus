## Visual Design

### Appearance
- **Track:** 4px height, `--color-slate-200`, `--radius-full`
- **Fill (left of thumb):** `--color-primary-500`, `--radius-full`
- **Thumb:** 20px circle, `#ffffff` bg, `2px solid --color-primary`, `--shadow-sm`
- **Labels:** `--font-label-sm`, `--color-slate-500`, min left, max right

### States

| State | Thumb Size | Thumb Border | Thumb Shadow | Cursor |
|-------|-----------|-------------|-------------|--------|
| Default | 20px | `2px --color-primary` | `--shadow-sm` | pointer |
| Hover | 24px | `2px --color-primary` | `--shadow-md` | pointer |
| Active (dragging) | 24px | `2px --color-primary-600`, ring `0 0 0 4px --color-primary-200` | `--shadow-md` | grabbing |
| Disabled | 20px | `2px --color-slate-300` | none | not-allowed, opacity 0.5 |

Thumb transition: size 150ms ease-default. Fill transition: width 0ms (instant, follows thumb).

### Variants
| Variant | Thumbs | Ticks | Use |
|---------|--------|-------|-----|
| Single | 1 | No | Numeric input |
| Range | 2 | No | Min/max filter |
| Discrete | 1 or 2 | Yes (at step intervals) | Step-constrained values |

Tick mark: 8px height, 1px `--color-slate-300`, at each step position.

### Spacing
- Track↔Labels: 8px above/below
- Min/max label spacing: labels at track edges
