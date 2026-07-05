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
