## Visual Design

### Appearance
- **Layout:** Horizontal row, centered. Buttons + ellipsis + label
- **Button:** 40×40px, ghost style, `--font-label-md`, `--color-slate-700`
- **Active page:** `--color-primary-50` bg, `--color-primary-600` text, `--font-label-md` bold
- **Ellipsis:** `--color-slate-400`, `--font-label-md`, not interactive
- **Info label:** `--font-body-sm`, `--color-slate-500`, left-aligned or above on mobile

### States

| Element | Default | Hover | Disabled |
|---------|---------|-------|----------|
| Page button | Ghost (transparent bg, slate-700) | `--color-slate-100` bg | opacity 0.5, cursor not-allowed |
| Active page | `--color-primary-50` bg, `--color-primary-600` | No change | — |
| Prev/Next | Ghost | `--color-slate-100` | opacity 0.5 |

### Sizes
| Size | Button | Font | Use |
|------|--------|------|-----|
| Standard | 40×40px | `--font-label-md` | Desktop |
| Compact | 32×32px | `--font-body-sm` | Mobile, narrow |

### Edge Cases
- Single page: hidden entirely
- 2-5 pages: show all
- 6+ pages: first, last, current ±2, ellipsis for gaps

### Spacing
- Button↔Button gap: 4px
- Prev/Next↔Page numbers gap: 8px
- Info label↔Buttons gap: 16px
