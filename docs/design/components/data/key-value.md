# Key Value

**Anatomy:** Label (muted, label-sm, above or inline) + Value (body-md/bold, on-surface)

**Layout variants:**
- Vertical stack: label above value, 2px gap
- Horizontal inline: label: value side-by-side, 4px gap (label: muted, value: bold)
- Card row: multiple key-value pairs in a card, label left-aligned, value right-aligned

**States:** Default · Loading (value shows skeleton) · Error (value shows "--" or "N/A", muted)

**Do:** Align labels consistently in lists · Use bold for values · Show "--" for missing data, not blank

**Don't:** Use generic labels ("Value: 42") · Omit unit for measured values · Vary alignment in same list

**Accessibility:**
- Use `<dl>` (description list), `<dt>` (term/label), `<dd>` (description/value) for semantic structure
- Label: `<dt>`. Value: `<dd>`. Multiple values per term: multiple `<dd>` elements
- Horizontal layout: CSS grid or flex, not table (this is not tabular data)

**Related:** `stat.md`, `table.md`, `lab-result.md`, `compare.md`

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
