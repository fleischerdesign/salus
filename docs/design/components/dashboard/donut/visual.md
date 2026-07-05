## Visual Design

### Appearance
- **Ring:** SVG, 8px stroke width, `--radius-full` caps, 3-6 segments
- **Track:** `--color-slate-100`, full circle behind segments
- **Center:** total value (`--font-headline-md`, bold) + label (`--font-caption`, `--color-slate-500`)
- **Legend:** below chart, horizontal row. Dot 8px + label (`--font-label-sm`) + value + percentage
- **Size:** 120×120px (medium widget), 90×90px (compact)

### Segment Colors
Default palette: user-configured per data category. 5-color sequential: `--color-primary` scale. 

### Animation
Stroke-dasharray: 0→target on load. 800ms ease-out.

### States
| State | Ring | Center | Legend |
|-------|------|--------|--------|
| Default | Proportional segments | Total value + label | Visible |
| Single segment | Full solid ring | Total | Single entry |
| No data | Empty track (slate-100 only) | "--" | Not shown |

### Spacing
- Ring width: 8px
- Center↔Ring gap: 4px padding inside ring
- Legend gap: 8px between items
