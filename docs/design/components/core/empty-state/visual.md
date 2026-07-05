## Visual Design

### Appearance
Vertical stack, centered in parent. Icon → Title → Description → CTA button.

### Variants by Container

| Container | Icon Size | Icon Opacity | Title Font | Description Font | CTA |
|-----------|-----------|-------------|------------|-----------------|-----|
| Card | 48px | 0.4 | `--font-headline-md` | `--font-body-sm` | Optional |
| Widget | 40px | 0.4 | `--font-body-sm` (600) | `--font-caption` | Optional |
| Feed / Page | 64px | 0.4 | `--font-headline-lg` | `--font-body-md` | Yes |
| Table cell | 20px | 0.4 | `--font-label-sm` | None | None |
| Inline | 20px | 0.4 | `--font-body-sm` (600) | None | None |

### Colors
- Icon: `--color-slate-400`, opacity 0.4
- Title: `--color-slate-700`
- Description: `--color-slate-500`, max-width 360px

### Spacing
- Icon↔Title: 16px
- Title↔Description: 8px
- Description↔CTA: 24px
