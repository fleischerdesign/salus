## Visual Design

### Desktop Layout
- **Sidebar:** 240px fixed width, `1px solid --color-slate-200` right border, full height
- **Content:** flex-1, left of sidebar
- **Link default:** `--font-label-md`, padding 12px 16px, `--color-slate-600`, full-width
- **Link hover:** `--color-slate-50` bg
- **Link active:** `--color-primary-50` bg, `--color-primary` text, `3px solid --color-primary` left border

### States

| State | Background | Text Color | Left Border |
|-------|-----------|------------|-------------|
| Default | transparent | `--color-slate-600` | none |
| Hover | `--color-slate-50` | `--color-slate-700` | none |
| Active | `--color-primary-50` | `--color-primary` | `3px solid --color-primary` |

### Mobile (< 900px)
Sidebar transforms to horizontal scrollable tab row above content. Same colors, but `2px solid --color-primary` bottom border (instead of left border) for active state. Font: `--font-body-sm`.

### Spacing
- Sidebar width: 240px
- Link padding: 12px 16px
- Left border: 3px, flush with sidebar left edge
