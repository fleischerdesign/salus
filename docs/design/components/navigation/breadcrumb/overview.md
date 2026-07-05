# Breadcrumbs

> **Status: Design spec only — not yet implemented.**

**Anatomy:** Horizontal link trail: Home > Section > Current Page

**Separator:** `/` or `›` character, slate-400. 8px spacing.

**States:** Default link (slate-500) · Hover (primary) · Current/last (slate-900, no link, bold) · Current page always last item, not clickable.

**Responsive:** Last 1-2 items kept; earlier items collapsed to "..." dropdown on mobile.

**Placement:** Below TopAppBar, above page header. 16px vertical padding.

**Do:** Show full path for context · Make current page non-clickable · Collapse on mobile

**Don't:** Use for single-level pages · Make every item a link · Skip the "Home" root

**Accessibility:**
- Container: `<nav>` with `aria-label="Breadcrumb"`
- List: `<ol>` (ordered list, reflecting hierarchy)
- Current page: `aria-current="page"`, not a link
- Separator: `aria-hidden="true"` (purely visual)
- Collapsed items: button with `aria-label="Show more breadcrumbs"`

**Token Values:**
| Token | Value |
|-------|-------|
| --breadcrumb-color | `{colors.slate-500}` |
| --breadcrumb-hover-color | `{colors.primary}` |
| --breadcrumb-active-color | `{colors.slate-900}` |
| --breadcrumb-separator | `{colors.slate-400}` |

**Responsive:** Collapses to "..." dropdown on mobile for intermediate items.

**Related:** `link.md`, `top-app-bar.md`
