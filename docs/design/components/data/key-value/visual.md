## Visual Design

### Layout Variants

| Layout | Label Position | Gap | Label Font | Value Font |
|--------|---------------|-----|------------|------------|
| Vertical stack | Above value | 2px | `--font-label-sm`, `--color-slate-500` | `--font-body-md`, `--color-on-surface`, 600 |
| Horizontal inline | Left of value | 4px | `--font-body-sm`, `--color-slate-500` | `--font-body-md`, `--color-on-surface`, 600 |
| Card row | Left-aligned | — | `--font-label-sm`, `--color-slate-500` | `--font-body-md`, right-aligned, 600 |

### States

| State | Visual |
|-------|--------|
| Default | Label + value visible |
| Loading | Value replaced by skeleton (14px height, 60% width) |
| No data | Value shows "--" (em dash), `--color-slate-400`, not bold |

### Grid Layout (multiple pairs)
When presenting multiple key-value pairs:
- Label left, value right. Gap between pairs: 12px
- Divider between rows: 1px `--color-slate-100`
- Consistency: all labels same width (use CSS grid `minmax`)

### Spacing
- Vertical: 2px label↔value
- Horizontal: 4px label↔value
- Pair↔Pair gap: 12px
