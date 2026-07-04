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

**Related:** `date-picker.md`, `button.md`, `icon.md`
