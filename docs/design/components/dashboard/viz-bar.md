# Viz: Bar (Segmented)

**Anatomy:** Header (value + unit) + Segmented horizontal bar (8px height) + Legend

**States:** Default · Hover (tooltip per segment on medium+ widgets) · No-data ("--" placeholder)

**Sizes:** Medium/Large only. Legend hidden on small widgets.

**Bar:** Rounded-full segments. Segment colors: protein (metric-heart-rate), carbs (secondary-400), fat (warning-400). Bar width: proportional to macro distribution.

**Legend:** Color dots (8px) + label (label-sm, slate-500) + value. Two-row wrapped layout.

**Do:** Use for composition/distribution data · Show proportional segments · Hide legend on small

**Don't:** Use for time-series · Use without legend on medium+ widgets · Hardcode segment colors

**Accessibility:**
- Bar: `role="img"` with `aria-label` describing composition (e.g., "Macros: 45% protein, 30% carbs, 25% fat")
- Legend: same as viz-pills legend accessibility
- Segments: proportional width match percentages in aria-label

**Related:** `donut.md`, `viz-pills.md`, `viz-number.md`

## Visual Design

### Appearance
- **Bar:** 8px height, `--radius-full`, full width of widget
- **Segments:** proportional width, color per data category, 0 gap (segments touch)
- **Header:** value + unit, `--font-headline-md`, above bar, gap 8px
- **Legend:** below bar, gap 8px. Row of color dots (8px) + label (`--font-label-sm`, `--color-slate-500`) + value

### Segment Colors
Default palette: protein (`--color-metric-heart-rate`), carbs (`--color-secondary-400`), fat (`--color-warning-400`). Customizable per metric type.

### States
| State | Visual |
|-------|--------|
| Default | Segments visible, legend visible (medium+) |
| Hover segment | `chart-tooltip` appears (see chart-tooltip.md) |
| No data | `"--"` placeholder, empty bar (`--color-slate-100`) |

### Sizes
| Widget Size | Bar | Legend |
|-------------|-----|--------|
| Medium+ | 8px bar, legend visible | — |
| Small | not available | — |

### Responsive
Bar width fills widget. Legend wraps to 2 columns on narrow widgets.
