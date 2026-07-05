## Visual Design

### Row Layout
- Time (`--font-body-md`, bold, 60px width) + Drug name (`--font-body-md`) + Dosage (`--font-body-md`, bold) + Status chip (right)

### Status Chips

| Status | Chip Variant | Icon | Highlight |
|--------|------------|------|-----------|
| Upcoming | Neutral | none | none |
| Due now | Warning | `schedule` 16px | `--color-warning-50` bg row |
| Taken | Success | ✓ 14px | none |
| Missed | Error | `warning` 14px | none |
| Skipped | Neutral, strikethrough | none | none |

### Adherence Ring
- 48px SVG ring, 6px stroke, `--color-slate-100` track
- Fill: `--color-tertiary` proportional to adherence %
- Center: percentage text, `--font-label-sm` (12px, 700)
- Position: right of schedule title

### Time Display
- Absolute: "08:00", `--font-body-md`, bold
- Relative (hover): "in 30 min", `--font-caption`, `--color-slate-500`

### Spacing
- Row height: 40px, padding 8px 0
- Time column: 60px
- Row gap: 2px (`1px --color-slate-100` divider between rows)
