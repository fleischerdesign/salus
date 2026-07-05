# Pagination

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Previous button + Page numbers + Next button + Optional "Items per page" selector + "Showing X-Y of Z" label

**States:** First page (Previous disabled) · Middle page · Last page (Next disabled) · Single page (hidden)

**Page numbers:** Compact: show first, last, current ± 2, ellipsis for large gaps. Active page: primary-50 bg, primary-600 text.

**Sizes:** Standard (40px buttons) · Compact (32px)

**Interaction:** HTMX GET with page query param. `hx-target` replaces content area. URL preserved for shareability.

**Do:** Show total item count · Keep page buttons large enough to tap · Preserve URL state

**Don't:** Show pagination for <10 items · Omit page size options · Break browser back button

**Responsive:** Page buttons reduce to compact size on mobile. Items-per-page selector may move below or hide on narrow screens. "Showing X-Y of Z" label wraps.

**Accessibility:**
- Container: `<nav>` with `aria-label="Pagination"`
- Page buttons: `<button>` elements (not `<a>` for same-page navigation). `aria-current="page"` on active page
- Ellipsis: `aria-hidden="true"` or `aria-label="More pages"`
- Previous/Next: `aria-label="Previous page"` / `"Next page"`
- Items per page selector: `<label>` + `<select>`, `aria-label="Items per page"`

**Token Values:**
| Token | Value |
|-------|-------|
| --pagination-btn-size | 40px |
| --pagination-active-bg | `{colors.primary-50}` |
| --pagination-active-text | `{colors.primary-600}` |
| --pagination-gap | `4px` |

**Composition:** Previous button + Page buttons + Ellipsis + Next button + Optional items-per-page selector + "Showing X-Y of Z" label.

**Related:** `table.md`, `btn.md`, `select.md`

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
