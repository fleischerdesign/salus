# Pagination

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Previous button + Page numbers + Next button + Optional "Items per page" selector + "Showing X-Y of Z" label

**States:** First page (Previous disabled) · Middle page · Last page (Next disabled) · Single page (hidden)

**Page numbers:** Compact: show first, last, current ± 2, ellipsis for large gaps. Active page: primary-50 bg, primary-600 text.

**Sizes:** Standard (40px buttons) · Compact (32px)

**Interaction:** HTMX GET with page query param. `hx-target` replaces content area. URL preserved for shareability.

**Do:** Show total item count · Keep page buttons large enough to tap · Preserve URL state

**Don't:** Show pagination for <10 items · Omit page size options · Break browser back button
