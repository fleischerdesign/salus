## Visual Design

### Variants

| Variant | Step Shape | Size | Content | Max Steps |
|---------|-----------|------|---------|-----------|
| Dots | Circle | 8px | None | 2-5 |
| Numbers | Circle with number | 24px | White number, `--font-label-sm` (10px, 700) | 3-10 |
| Labels | Circle + text below | 24px circle + `--font-body-sm` label | Step title below | 3-6 |

### Colors

| State | Dot/Number Fill | Number Color | Connector Line | Icon |
|-------|----------------|-------------|----------------|------|
| Pending | `--color-slate-300` | `--color-slate-500` | `--color-slate-200` | — |
| Active | `--color-primary-500` | `#ffffff` | In progress (left: primary, right: slate-200) | — |
| Completed | `--color-tertiary-500` | `#ffffff` | `--color-tertiary-200` | white ✓ 12px |
| Error | `--color-error-500` | `#ffffff` | `--color-error-200` | white ! 12px |

### Connector Line
2px height, between dot and next dot. Color per state above. Gap: 0px between dot and connector.

### Spacing
- Dot variant: 8px gap between dots
- Number variant: 16px gap between steps
- Label variant: 24px gap between steps

### Responsive
`< --bp-mobile`: Gap reduces (8→6px for dots, 16→12px for numbers). Labels stack below circles.
