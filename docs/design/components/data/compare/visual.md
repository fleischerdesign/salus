## Visual Design

### Horizontal Layout
- Left (previous period): value + label, muted
- Arrow: → 18px icon, `--color-slate-400`, centered
- Right (current period): value + label + delta, prominent
- Gap: 8px between elements

### Vertical Layout
- Top (current): large value + label + delta, prominent
- Bottom (previous): smaller value + label, muted, 8px gap below top

### Colors

| Element | Color |
|---------|-------|
| Current value | `--color-on-surface` |
| Previous value | `--color-slate-500` |
| Period label | `--font-body-sm`, `--color-slate-500` |
| Positive delta | `--color-tertiary-600`, ↑ |
| Negative delta | `--color-error-600`, ↓ |
| Neutral delta | `--color-slate-500`, → |

### Delta
Arrow icon 16px + percentage/absolute value, `--font-label-sm`, 4px gap from value.

### Spacing
- Horizontal gap: 8px
- Vertical gap: 8px
- Arrow icon: 18px, centered between periods

### Responsive
`< --bp-mobile`: Horizontal → vertical layout. Arrow rotates 90° (↓) between top and bottom.
