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
