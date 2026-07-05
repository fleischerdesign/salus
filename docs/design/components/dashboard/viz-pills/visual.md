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
