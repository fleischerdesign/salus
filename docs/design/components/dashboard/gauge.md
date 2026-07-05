# Gauge / Meter

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Half-circle arc with needle or fill indicating current value within a range

**Segments:** 3 qualitative zones on the arc: Low (warning-400, left), Normal (tertiary-500, center), High (error-400, right). Boundary values configurable.

**States:** Low value (needle in warning zone) · Normal (needle in tertiary zone) · High (needle in error zone)

**Center text:** Current value (headline-lg, bold) + Unit (body-sm, muted) + Optional label (caption, muted)

**Examples:** Heart rate (60–100 bpm normal range), SpO2 (95–100% normal), Temperature (36.1–37.2°C normal).

**Animation:** Needle rotates into position on load (600ms ease-out).

**Do:** Use for range-based vitals · Show 3 qualitative zones · Put value in center · Animate on load

**Don't:** Use for non-range metrics · Omit zone labels · Use for exact measurements (use stat)

**Accessibility:**
- SVG: `role="img"` with `aria-label` describing value + zone (e.g., "Heart rate: 72 bpm — in normal range (60-100)")
- Zones: described in aria-label, not individually interactive
- Center text: aria-label with value + unit
- Needle: purely visual, position described in text

**Token Values:**
| Token | Value |
|-------|-------|
| --gauge-arc-width | 12px |
| --gauge-low-color | `{colors.warning-400}` |
| --gauge-normal-color | `{colors.tertiary-500}` |
| --gauge-high-color | `{colors.error-400}` |
| --gauge-needle-color | `{colors.slate-800}` |
| --gauge-center-font | `var(--font-headline-lg)` |
| --gauge-animation-duration | 600ms |

**Related:** `viz-progress.md`, `stat.md`, `vital-signs-row.md`

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
