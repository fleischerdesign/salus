# Tabbed Sidebar

**Tokens:** Reuses `--nav-*` tokens

**Anatomy:** Sidebar (240px, right-border) + Content area (flex-1)

**Sidebar links:** label-md font, full-width, 3px left border (transparent → primary when active). Hover: slate-50 bg.

**Responsive (<900px):** Sidebar becomes horizontal scrollable tab row above content instead of left panel.

**States:** Default · Active (primary-50 bg, 3px primary left-border, primary text)

**Do:** Use for settings/admin sections · Keep labels short · Maintain consistent sidebar width

**Don't:** Use for primary navigation (use TopAppBar) · Mix navigation styles on same page

**Responsive:** Desktop: 240px fixed sidebar + fluid content. Below 900px: sidebar becomes horizontal scrollable tab row above content.

**Accessibility:**
- Sidebar: `<nav>` with `aria-label="Settings navigation"` or similar
- Active link: `aria-current="page"`
- Keyboard: Tab through links, no special arrow-key handling needed for simple list
- Responsive: horizontal tab row gets `role="tablist"`, each tab gets `role="tab"` with `aria-selected`

**Composition:** Sidebar (Link list) + Content area (flex-1). Sidebar is part of tabbed-layout container.

**Related:** `tab-bar.md`, `top-app-bar.md`, `link.md`

## Visual Design

### Desktop Layout
- **Sidebar:** 240px fixed width, `1px solid --color-slate-200` right border, full height
- **Content:** flex-1, left of sidebar
- **Link default:** `--font-label-md`, padding 12px 16px, `--color-slate-600`, full-width
- **Link hover:** `--color-slate-50` bg
- **Link active:** `--color-primary-50` bg, `--color-primary` text, `3px solid --color-primary` left border

### States

| State | Background | Text Color | Left Border |
|-------|-----------|------------|-------------|
| Default | transparent | `--color-slate-600` | none |
| Hover | `--color-slate-50` | `--color-slate-700` | none |
| Active | `--color-primary-50` | `--color-primary` | `3px solid --color-primary` |

### Mobile (< 900px)
Sidebar transforms to horizontal scrollable tab row above content. Same colors, but `2px solid --color-primary` bottom border (instead of left border) for active state. Font: `--font-body-sm`.

### Spacing
- Sidebar width: 240px
- Link padding: 12px 16px
- Left border: 3px, flush with sidebar left edge
