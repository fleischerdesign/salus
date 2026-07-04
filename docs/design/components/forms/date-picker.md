# Date Picker

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Input field (shows selected date) + Calendar icon + Dropdown calendar panel

**Calendar panel:** Month/year header with prev/next arrows + Day grid (7 columns, Su-Sa headers) + Today indicator

**States:** Closed · Open · Date selected · Range selected (start/end/in-range) · Disabled dates

**Interaction:** Click input opens panel. Click date selects and closes. Arrow keys navigate within open panel. Escape closes.

**Format:** Display: locale-aware (e.g. "Jul 4, 2026"). Value: ISO 8601 (YYYY-MM-DD).

**Do:** Support keyboard navigation · Show today indicator · Allow typing date directly · Respect locale

**Don't:** Reinvent native picker on mobile (use `<input type="date">`) · Omit month/year quick navigation · Break with keyboard

**Accessibility:**
- Input: `<input type="date">` with `<label>` association
- Calendar button: `aria-label="Open date picker"`, `aria-expanded` on toggle
- Calendar panel: `role="dialog"` or `role="application"` with live region
- Days: `role="grid"`, each cell `role="gridcell"` with `aria-selected` and `aria-label`
- Keyboard: Arrow keys navigate days, Page Up/Down changes months, Enter selects, Escape closes
- Today: `aria-current="date"`

**Token Values:**
| Token | Value |
|-------|-------|
| --date-picker-input-width | `200px` |
| --date-picker-calendar-width | `280px` |
| --date-picker-cell-size | `36px` |
| --date-picker-today-border | `2px solid {colors.primary}` |
| --date-picker-selected-bg | `{colors.primary}` |
| --date-picker-header-font | `var(--font-label-md)` |
| --date-picker-z-index | `var(--z-dropdown)` |

**Related:** `input.md`, `day-navigator.md`, `modal.md`
