# Date Picker

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Input field (shows selected date) + Calendar icon + Dropdown calendar panel

**Calendar panel:** Month/year header with prev/next arrows + Day grid (7 columns, Su-Sa headers) + Today indicator

**States:** Closed · Open · Date selected · Range selected (start/end/in-range) · Disabled dates

**Interaction:** Click input opens panel. Click date selects and closes. Arrow keys navigate within open panel. Escape closes.

**Format:** Display: locale-aware (e.g. "Jul 4, 2026"). Value: ISO 8601 (YYYY-MM-DD).

**Do:** Support keyboard navigation · Show today indicator · Allow typing date directly · Respect locale

**Don't:** Reinvent native picker on mobile (use `<input type="date">`) · Omit month/year quick navigation · Break with keyboard
