# Layout — Grid System & Responsive

**Container:** Max-width 1440px, centered with auto margins. Padding: 40px horizontal (desktop), 16px (mobile).

**Grid:** 12-column CSS Grid. Gap: 24px.

**Breakpoints:**
| Breakpoint | Width | Columns | Margins |
|-----------|-------|---------|---------|
| Mobile | <600px | 4 col | 16px |
| Tablet | 600-1024px | 8 col | 24px |
| Desktop | >1024px | 12 col | 40px |

**Dashboard grid:** 4-column grid. Widgets span 1 (small), 2 (medium), or 4 (large) columns.
**Analytics grid:** 12-column grid. Sections span 4, 6, or 8 columns.
**Goal grid:** 3-column grid. Collapses to 1 column on mobile.

**TopAppBar:** Full width, sticky, 64px height. Content restricted to container-max-width internally.

**Page content:** `.container` class wraps all page content below TopAppBar.

**Tabbed layouts (Settings, Admin):** 240px sidebar + fluid content area. Below 900px: sidebar becomes horizontal tab row above content.

**Connections layout:** 380px invite form + fluid peer grid. Below 900px: vertical stack.

**Do:** Use CSS Grid not floats · Respect container max-width · Collapse to single column on mobile

**Don't:** Use fixed pixel widths for content · Overflow container · Mix grid and flex for same layout
