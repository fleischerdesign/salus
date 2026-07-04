# Day Navigator

**Anatomy:** Previous-day arrow + Date (clickable, opens native date picker) + Next-day arrow + "Today" button (only when not today)

**States:** Default · Date hover (primary color) · "Today" button shown/hidden · Previous arrow hidden when at earliest date

**Date format:** Locale-aware. Desktop: "Wednesday, July 4, 2026". Mobile: shortened.

**Interaction:** Prev/Next via hx-get with date query param. Date click opens native `<input type="date">` with hx-trigger="change". Today button visible only when viewing past date.

**Do:** Use for daily dashboards · Show weekday name · Provide quick "Today" return

**Don't:** Allow navigation to future dates (unless relevant) · Use custom date picker (native is more accessible)
