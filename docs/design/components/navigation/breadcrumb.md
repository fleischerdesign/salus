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

## Visual Design

### Appearance
- **Layout:** Horizontal row, `--font-body-sm` (14px), gap 8px between segments
- **Link default:** `--color-slate-500`, no underline
- **Link hover:** `--color-primary`, no underline
- **Current (last):** `--color-slate-900`, bold (600), not clickable
- **Separator:** `/` character, `--color-slate-400`, 8px gap both sides
- **Container:** `<nav>` below top-app-bar, 16px vertical padding

### States

| Segment | Color | Weight | Clickable |
|---------|-------|--------|-----------|
| Link (default) | `--color-slate-500` | 400 | Yes |
| Link (hover) | `--color-primary` | 400 | Yes |
| Current | `--color-slate-900` | 600 | No |
| Current (hover) | No change | 600 | No |

### Mobile Collapse
On `< --bp-mobile`: show only last 1-2 segments. Earlier segments collapsed to "..." dropdown trigger. Dropdown: ghost button, 24×24px, `more_horiz` icon. Click shows full breadcrumb in dropdown (same style as nav-dropdown).

### Spacing
- Segment gap: 8px (4px each side of separator)
- Separator: 4px each side
- Container padding: 16px top/bottom
