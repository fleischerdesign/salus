## Visual Design

### Card
Standard card (white bg, border, radius-md), 24px padding.

### Header
- Plan name: `--font-headline-md` (20px, 600)
- Autoreg chip: right-aligned

| Mode | Chip Variant | Icon |
|------|------------|------|
| Disabled | Neutral | `block` |
| Advisory | Info (secondary) | `tips_and_updates` |
| Guided | Primary | `auto_fix_high` |

### Exercise List
- Each exercise: `--font-body-sm`, name + equipment badge (neutral chip, 14px) + "3×10 @ RPE 7" target
- Gap: 8px between exercises
- Empty state: "No exercises added" (inline, `--color-slate-400`)

### Actions
- Start Session: primary button, full-width, `play_arrow` icon 20px left
- Delete: ghost danger button, right-aligned, `delete` icon 16px

### States
| State | Card Shadow | Actions |
|-------|------------|---------|
| Default | None | Start Session visible, Delete hidden (shown on hover) |
| Hover | `--shadow-md` | Delete visible |
| Deleting | None, opacity 0.5 | Both disabled |

### Spacing
- Header↔Exercises: 16px
- Exercises↔Actions: 24px
- Exercise↔Exercise: 8px
