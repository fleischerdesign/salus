## Visual Design

### Appearance
- **Background:** `--color-slate-800`
- **Text:** `--color-slate-50`, `--font-label-sm` (12px)
- **Border:** `1px solid rgba(255,255,255,0.15)`
- **Padding:** 8px
- **Radius:** 6px
- **Pointer cursor follower:** no (appears near data point, not at cursor)

### Content Structure
- Date: `--font-caption` (11px), `--color-slate-300`
- Value: bold, `--font-label-sm` (12px, 600), `--color-slate-50`
- Optional unit: after value, normal weight
- Optional secondary value: below, `--color-slate-400`

### Positioning
- Offset: 12px from data point
- Auto-adjust: avoids chart boundaries (flips side if near edge)
- Prefers top of data point (bottom if no space)

### States
| State | Opacity | Transform | Duration |
|-------|---------|-----------|----------|
| Hidden | 0 | scale(0.95) | — |
| Entering | 0→1 | scale(0.95→1) | 150ms ease-out |
| Visible | 1 | scale(1) | — |
| Exiting | 1→0 | scale(1→0.95) | 100ms ease-in |

### Spacing
- Offset from data point: 12px
- Padding: 8px
- Tripod/pointer arrow: 6px triangle, matches bg color
