## Visual Design

### Ring (Small Widget)
- **SVG:** 90×90px circle, `8px` stroke
- **Track:** `--color-slate-100`, full circle
- **Fill:** `--color-primary`, stroke-dasharray proportional to progress
- **Center text:** percentage (`--font-headline-md`, bold) + label (`--font-caption`, `--color-slate-500`)

### Bar (Medium+ Widget)
- **Track:** `--color-slate-100`, `--radius-full`, 22px height
- **Fill:** `--color-primary`, `--radius-full`, proportional width
- **Overlay text:** percentage, `--font-label-sm` (12px, 700), `--color-on-primary` when bar > 40%, else `--color-slate-700`

### Fill Colors by Status
| State | Fill Color |
|-------|-----------|
| Below target | `--color-primary` |
| At target | `--color-tertiary` |
| Over target | `--color-warning` |

### Animation
| Element | Duration |
|---------|----------|
| Ring fill (stroke-dasharray) | 800ms ease-out |
| Bar width | 600ms ease-default |

### Spacing
- Ring: 90×90px, 8px stroke
- Bar: 22px height
- Sub-label: 4px above bar, `--font-body-sm`, `--color-slate-500`
