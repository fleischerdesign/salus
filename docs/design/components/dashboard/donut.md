# Donut / Ring Chart

> Status: **Design spec only — not yet implemented.**

**Anatomy:** SVG ring showing proportion of parts to whole. Center: total value or label.

**States:** Default · Hover (per segment via chart-tooltip) · No-data (empty ring, "--" in center) · Single segment (full ring, one color)

**Segments:** Stroke-dasharray based on proportions. Colors from color family tokens. 3-6 segments max.

**Center text:** Large total value (headline-md, bold) + Label (caption, muted). Or: primary metric + unit.

**Legend:** Below chart, matching segment colors. Dots (8px) + label + value + percentage. Can be hidden on small widgets.

**Animation:** Stroke-dasharray transition 800ms ease-out on load.

**Do:** Use for 3-6 segment proportions · Show legend · Animate on load · Put key number in center

**Don't:** Use for >6 segments · Use for time series · Omit labels/legend

**Accessibility:**
- SVG: `role="img"` with `aria-label` describing proportions (e.g., "Calories: 45% protein, 30% carbs, 25% fat")
- Center text: `aria-label` with total value
- Legend: list with color dots + labels + values + percentages

**Token Values:**
| Token | Value |
|-------|-------|
| --donut-ring-width | 8px |
| --donut-center-font | `var(--font-headline-md)` |
| --donut-center-label-font | `var(--font-caption)` |
| --donut-animation-duration | `var(--duration-glacial)` |

**Related:** `viz-bar.md`, `viz-pills.md`, `viz-progress.md`

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
