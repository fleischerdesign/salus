# Viz: Pills

**Anatomy:** Header (value + unit + delta) + SVG pill chart (110px height) + Color legend

**States:** Default · Hover (per segment via chart-tooltip) · No-data (empty chart with placeholder)

**Sizes:** Medium/Large only. Not available in small.

**Chart:** SVG-rendered pill-shaped segments representing heart rate zones or sleep stages. Segments use ResizeObserver for responsive width. Zones/segments: Awake (warning-400), Light (secondary-400), Deep (primary-400), REM (metric-sleep).

**Legend:** Horizontal, centered below chart. Color dots (8px) + label (label-sm, slate-500).

**Do:** Use for zone/stage breakdowns · Show color legend · Make responsive

**Don't:** Use for trend data (use sparkline) · Omit legend · Hardcode segment colors

**Accessibility:**
- SVG: `role="img"` with `aria-label` describing distribution (e.g., "Sleep: 2h awake, 3h light, 1.5h deep, 2h REM")
- Legend items: list with color dots + text labels
- Color dots: `aria-hidden="true"` (label text describes the segment)

**Related:** `viz-bar.md`, `donut.md`, `sleep-*` tokens

## Visual Design

### Appearance
- **Chart:** SVG, 110px height, pill-shaped segments (horizontal)
- **Segment colors:** Awake (`--color-warning-400`), Light (`--color-secondary-400`), Deep (`--color-primary-400`), REM (`--color-metric-sleep`)
- **Header:** value + unit, `--font-headline-md`, above chart
- **Legend:** below chart. 8px dots + label (`--font-label-sm`, `--color-slate-500`) + value

### Pill Segments
Each segment is a rounded rectangle. Width proportional to percentage. Gap: 0 between segments.

### States
| State | Visual |
|-------|--------|
| Default | Segments + legend |
| Hover segment | `chart-tooltip` appears |
| Single segment | One pill, full width |
| No data | Empty chart, "--" placeholder |

### Responsive
Chart width: responsive via ResizeObserver. Legend wraps at narrow widths.

### Spacing
- Chart height: 110px
- Header↔Chart: 8px
- Chart↔Legend: 8px
