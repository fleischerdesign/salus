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

## Visual Design

### Appearance
- **Card:** matches card (white bg, slate-200 border, radius-md), compact padding: 16px
- **Accent bar:** 4px height, top of card, full width, color per metric/trend
- **Icon:** 24px, left of value, colored by metric type
- **Value:** `--font-headline-md` (20px, 600), `--color-on-surface`
- **Label:** `--font-body-sm`, `--color-slate-500`, below value
- **Delta:** `--font-label-sm`, arrow + percentage, right of value, 8px gap

### Accent Colors
| Trend | Accent Bar Color | Icon Color |
|-------|-----------------|------------|
| Positive | `--color-tertiary-500` | `--color-tertiary-500` |
| Negative | `--color-error-500` | `--color-error-500` |
| Neutral | `--color-primary-500` | `--color-primary-500` |

### Sizes
| Size | Layout | Cards/Row |
|------|--------|-----------|
| Compact | Icon inline left, value + label stacked | 3-4 |
| Standard | Icon top, value + label stacked | 2 |

### Spacing
- Padding: 16px
- Icon↔Value: 8px
- Value↔Label: 2px
- Value↔Delta: 8px (right)

### Responsive
Desktop: 3-4/row, tablet: 2/row, mobile: 1/row full-width.
