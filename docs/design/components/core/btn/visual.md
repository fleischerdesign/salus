## Visual Design

### Variants

| Variant | Background | Text Color | Border | Icon Color | Hover Bg | Press Bg |
|---------|-----------|-----------|--------|------------|---------|----------|
| Primary | `--color-primary` | `--color-on-primary` | none | `--color-on-primary` | `--color-primary-600` | `--color-primary-700` |
| Secondary | transparent | `--color-primary` | `1px solid --color-primary` | `--color-primary` | `--color-primary-50` | `--color-primary-100` |
| Ghost | transparent | `--color-primary` | none | `--color-primary` | `--color-primary-50` | `--color-primary-100` |
| Danger | `--color-error-50` | `--color-error-700` | none | `--color-error-600` | `--color-error-100` | `--color-error-200` |
| Small | `--color-slate-100` | `--color-slate-700` | `1px solid --color-slate-200` | `--color-slate-500` | `--color-slate-200` | `--color-slate-300` |

### Sizes

| Size | Height | Padding | Font | Icon Size | Icon↔Label |
|------|--------|---------|------|-----------|------------|
| Standard | 44px | 10px 20px | `--font-label-md` | 20px | 8px |
| Compact | 32px | 6px 12px | `--font-label-sm` | 16px | 6px |
| Icon-only | 28×28px | 0 | — | 18px | — |

### States

| State | Visual | Duration |
|-------|--------|----------|
| Default | Variant defaults | — |
| Hover | Background transitions to hover color | 150ms ease-default |
| Focus | Standard focus ring (2px primary-500, 2px offset) | instant |
| Active/Press | Background darkens, scale 0.98 | instant |
| Disabled | Opacity 0.5, cursor not-allowed | — |
| Loading | Spinner (16px) replaces label, `aria-busy="true"` | — |
| Success flash | Background → tertiary-100, reverts after 600ms | 600ms |

### Spacing
- Icon↔Label: 8px (standard), 6px (compact)
- Button-group gap: 8px, vertical stack below `--bp-mobile`
- Full-width below `--bp-mobile`

### Radius & Elevation
- Standard/Ghost/Danger: `--radius-md` (8px)
- Small: `--radius-sm` (4px)
- Icon-only: `--radius-full`
- No shadow. Flat by default.
