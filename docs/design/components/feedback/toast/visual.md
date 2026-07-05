## Visual Design

### Variants

| Variant | Background | Text | Border | Icon | Icon Color |
|---------|-----------|------|--------|------|------------|
| Success | `--color-tertiary-50` | `--color-tertiary-800` | `1px solid --color-tertiary-200` | check_circle | `--color-tertiary-600` |
| Error | `--color-error-50` | `--color-error-800` | `1px solid --color-error-200` | error | `--color-error-600` |
| Warning | `--color-warning-50` | `--color-warning-800` | `1px solid --color-warning-200` | warning | `--color-warning-600` |
| Info | `--color-secondary-50` | `--color-secondary-800` | `1px solid --color-secondary-200` | info | `--color-secondary-600` |

### Anatomy
- Icon (20px, left) + Message (`--font-body-sm`, flexible center) + Action button (optional, ghost sm) + Close × (20px, right)
- Horizontal row layout, 12px inner padding (left/right), 10px vertical

### Appearance
- **Shadow:** `--shadow-lg`
- **Radius:** `--radius-md` (8px)
- **Max-width:** 360px
- **Position:** fixed, top-right, 16px from edge. Stack: 8px gap between toasts
- **Z-index:** `--z-tooltip` (500)

### Animation
| Phase | Animation | Duration |
|-------|-----------|----------|
| Enter | Slide-in from right (translateX 100%→0) + fade (0→1) | 200ms ease-out |
| Exit | Slide-out to right (translateX 0→100%) + fade (1→0) | 200ms ease-in |

### States
| State | Behavior |
|-------|----------|
| Visible | Start auto-dismiss timer (5s for success/info, ∞ for error) |
| Hover | Pause auto-dismiss timer |
| Dismissing | Play exit animation, remove from DOM after |
| Overflow (>3) | Oldest dismisses immediately as new one enters |

### Spacing
- Toast↔Toast stack gap: 8px
- Viewport edge margin: 16px top, 16px right
- Icon↔Message: 8px. Message↔Action: 8px
- Padding: 10px 12px

### Responsive
`< --bp-mobile`: Full-width, 16px horizontal margin, position: top (not top-right). Stack from top.
