## Visual Design

### Appearance
- **Line:** 2px width, `--color-slate-200`, full height, 16px left margin
- **Dot:** 12px circle, `--color-primary-500`, filled. Centered on line
- **Active/latest dot:** 16px circle, `--color-primary-500` fill + `4px --color-primary-200` ring
- **Connector:** horizontal line 16px from dot to card, `--color-slate-200`
- **Card:** no shadow, no border. Padding: 8px 0

### Card Content
- Timestamp: `--font-caption` (11px), `--color-slate-500`, above
- Title: `--font-body-md` (16px, 600), `--color-on-surface`
- Description: `--font-body-sm` (14px), `--color-slate-600`, 2px below title
- Optional icon: 20px, left of title, colored by event type

### Connector States
| State | Line Style |
|-------|-----------|
| Completed | Solid `--color-slate-200` |
| Ongoing / In progress | Dashed `--color-slate-200` (2px dashes, 4px gaps) |
| Future / Pending | `--color-slate-300`, lighter |

### Spacing
- Line left: 16px
- Dot centered on line
- Connector: 16px from dot to card
- Card↔Card vertical gap: 0 (items touch). Padding within card: 8px top, 16px bottom

### Variants
| Variant | Dot Color | Line Color |
|---------|-----------|------------|
| Default (generic) | `--color-primary-500` | `--color-slate-200` |
| Success (completed) | `--color-tertiary-500` | `--color-tertiary-200` |
| Warning | `--color-warning-500` | `--color-warning-200` |
| Error | `--color-error-500` | `--color-error-200` |

### Responsive
- Mobile: cards full-width, line at minimal 8px left margin
- Connector: 8px on mobile
