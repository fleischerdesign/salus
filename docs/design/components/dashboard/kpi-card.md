# KPI Card

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Compact card (icon + value + label + delta) with colored accent border

**States:** Default · Positive trend (tertiary accent) · Negative trend (error accent) · Neutral

**Sizes:** Compact (inline, 3-4 per row) · Standard (card, 2 per row)

**Accent border:** 4px top border, color varies by trend direction and metric type.

**Content:** Metric icon (24px, colored) + Large value (headline-md) + Label (body-sm, muted) + Delta percentage (label-sm, colored arrow).

**Do:** Use for dashboard metric summaries · Show trend direction · Keep compact · Color-code by metric

**Don't:** Use for detailed data (use viz charts) · Overload with info beyond value+label+delta · Mix with unrelated metrics in same row

**Responsive:** 3-4 cards per row on desktop, 2 on tablet, single column on mobile. Card width fluid within grid constraints.

**Accessibility:**
- Card: `role="region"` with `aria-label` from metric name
- Value: `aria-label` with full description + unit + trend
- Accent border: `aria-hidden="true"` (decorative, information duplicated in text)

**Token Values:**
| Token | Value |
|-------|-------|
| --kpi-accent-bar-height | 4px |
| --kpi-accent-positive | `{colors.tertiary-500}` |
| --kpi-accent-negative | `{colors.error-500}` |
| --kpi-accent-neutral | `{colors.primary-500}` |
| --kpi-icon-size | 24px |
| --kpi-value-font | `var(--font-headline-md)` |

**Composition:** Card with accent bar (4px top) containing: Icon + Value + Label + Delta. 3-4 per row on desktop.

**Related:** `card.md`, `stat.md`, `widget.md`, `compare.md`
