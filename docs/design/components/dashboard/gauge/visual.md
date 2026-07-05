## Visual Design

### Appearance
- **Arc:** half-circle SVG, 12px stroke width, `--color-slate-100` track
- **Zones:** 3 colored segments on arc — Low (left, `--color-warning-400`), Normal (center, `--color-tertiary-500`), High (right, `--color-error-400`)
- **Needle:** `--color-slate-800`, 2px width, rotates from center to value position
- **Center text:** value (`--font-headline-lg`, bold) + unit (`--font-body-sm`, `--color-slate-500`) + label (`--font-caption`, `--color-slate-500`)
- **Size:** 160×100px (half circle)

### Zone Boundaries
Configurable per metric. Default: Low 0-33%, Normal 33-66%, High 66-100% of range.

### Colors
| Zone | Color | Meaning |
|------|-------|---------|
| Low | `--color-warning-400` | Below normal range |
| Normal | `--color-tertiary-500` | Within healthy range |
| High | `--color-error-400` | Above normal range |

### Animation
Needle: rotate 0→target position, 600ms ease-out on load.

### Spacing
- Arc width: 12px
- Center text: stacked vertically, gap 2px
- Size: 160×100px
