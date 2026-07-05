# Viz: Sparkline

**Anatomy:** SVG polyline chart (30px height, full width) + Optional progress bar overlay + Sub-label

**States:** Default · With target (progress bar overlay visible) · No-data (empty chart, "--" placeholder) · Single data point (flat line, no curve)

**Sizes:**
- Medium/Large only. Not available in small (small widgets use viz-number).

**Chart:** Polyline with smooth curves. Color: primary. No axes, no grids. Data points connected, filled area optional (5% opacity).

**Overlay:** Progress bar (8px height, slate-100 track, primary fill, 0.5s transition) shown below sparkline when target value exists.

**Do:** Use for time-series trends at a glance · Show progress overlay when target exists · Keep minimal

**Don't:** Add axes or grids (use full chart for that) · Show sparkline without context label · Use for single data point

**Accessibility:**
- SVG: `role="img"` with `aria-label` describing trend (e.g., "Steps trend over the past 7 days: upward, from 6,000 to 8,400")
- Data points: not individually interactive; summary trend in aria-label
- Overlay progress bar: inherits progress-bar accessibility

**Related:** `viz-number.md`, `viz-bar.md`, `progress-bar.md`

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
