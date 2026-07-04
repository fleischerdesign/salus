# Print Styles

> Status: **Design spec only — not yet implemented.**

**Global `@media print` rules:**

- **Hide:** Navigation (TopAppBar, sidebar, tabs), buttons (all), modals, tooltips, toasts, interactive elements
- **Show:** Content cards, tables, charts, watermarks, patient header
- **Typography:** Black text (#000), 10-12pt size. Remove background colors (except watermarks). Force white backgrounds.
- **Tables:** Repeat `<thead>` on every page. Avoid row splitting across pages (`break-inside: avoid`).
- **Links:** Show URL in parentheses after link text.
- **Margins:** 1.5cm all sides. 0.5cm for @page.
- **Watermark:** Force visibility (see `watermark.md`).

**Component-specific print rules:**
- Charts: render as simplified black/white or include data table alternative
- Widgets: hide chrome, show data only
- Vital signs: show as compact table

**Do:** Hide interactive UI · Show data cleanly · Force watermark · Repeat table headers

**Don't:** Print navigation · Print background colors · Keep buttons visible · Split vital signs across pages
