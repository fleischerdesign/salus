## Visual Design

### Appearance
- **Chart:** SVG polyline, 30px height, full widget width
- **Line:** `--color-primary`, 2px stroke, smooth curves (cubic bezier)
- **Fill area (optional):** `--color-primary` at 5% opacity below line
- **Header:** value + unit + delta, above chart
- **Sub-label:** `--font-body-sm`, `--color-slate-500`, below chart

### States
| State | Line | Fill Area |
|-------|------|-----------|
| Default | `--color-primary`, 2px | 5% opacity |
| Upward trend | `--color-tertiary-600` | `--color-tertiary` 5% |
| Downward trend | `--color-error-600` | `--color-error` 5% |
| Single data point | Flat line | none |
| No data | Empty chart, "--" | — |

### Progress Overlay (when target exists)
Bar 8px height, `--color-slate-100` track, `--color-primary` fill. Below sparkline, 4px gap.

### Spacing
- Chart height: 30px
- Header↔Chart: 4px
- Chart↔Progress overlay: 4px
