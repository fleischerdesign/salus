# Donut / Ring Chart

> Status: **Design spec only — not yet implemented.**

**Anatomy:** SVG ring showing proportion of parts to whole. Center: total value or label.

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
