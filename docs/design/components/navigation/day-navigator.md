# Day Navigator

**Anatomy:** Previous-day arrow + Date (clickable, opens native date picker) + Next-day arrow + "Today" button (only when not today)

**States:** Default · Date hover (primary color) · "Today" button shown/hidden · Previous arrow hidden when at earliest date

**Date format:** Locale-aware. Desktop: "Wednesday, July 4, 2026". Mobile: shortened.

**Interaction:** Prev/Next via hx-get with date query param. Date click opens native `<input type="date">` with hx-trigger="change". Today button visible only when viewing past date.

**Do:** Use for daily dashboards · Show weekday name · Provide quick "Today" return

**Don't:** Allow navigation to future dates (unless relevant) · Use custom date picker (native is more accessible)

**Responsive:** Date format shortens on mobile (weekday + short date). Today button stays visible but may wrap below navigator on narrow screens.

**Accessibility:**
- Previous/Next: `<button>` with `aria-label="Previous day"` / `"Next day"`
- Date display: `<button>` opening native date picker, `aria-label="Change date — current: {formatted date}"`
- Today button: `aria-label="Go to today"`
- Disabled arrows: `disabled` attribute when at boundary
- Keyboard: Tab through, Enter/Space activates

**Token Values:**
| Token | Value |
|-------|-------|
| --day-nav-bg | `{colors.slate-50}` |
| --day-nav-radius | `var(--radius-md)` |
| --day-nav-date-font | `var(--font-label-md)` |
| --day-nav-date-hover | `{colors.primary}` |

**Related:** `date-picker.md`, `btn.md`, `icon.md`

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
