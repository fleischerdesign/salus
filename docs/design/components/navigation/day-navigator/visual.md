## Visual Design

### Appearance
- **Container:** `--color-slate-50` bg, `--radius-md`, centered row, padding 8px 12px
- **Arrow buttons:** 36×36px ghost, 20px chevron icons, `--color-slate-600` → `--color-primary` hover
- **Date display:** `--font-label-md`, `--color-on-surface`, clickable, hover: `--color-primary`
- **Today button:** ghost sm, `--font-label-sm`, visible only when not today

### States
| Element | Default | Hover | Disabled |
|---------|---------|-------|----------|
| Prev arrow | Ghost, slate-600 | Primary bg-50, primary icon | Hidden (at earliest) |
| Next arrow | Ghost, slate-600 | Primary bg-50, primary icon | Disabled (future dates) |
| Date | `--color-on-surface` | `--color-primary` | — |
| Today btn | Ghost sm | `--color-slate-100` | — |

### Date Format
Desktop: "Wednesday, July 4, 2026". Mobile: "Wed, Jul 4, 2026".

### Spacing
- Arrow gap: 8px from date
- Date: centered between arrows
- Today: 12px right of next arrow, shown only when viewing past date
