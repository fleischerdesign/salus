# Tab Bar

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Horizontal row of tab triggers + Content area below (shows active tab content)

**States:** Active tab (primary text + 2px primary bottom-border) · Inactive tab (slate-600 text, transparent border) · Hover (slate-100 bg) · Disabled (opacity 0.5)

**Triggers:** label-md font, padding: 12px 16px, min-width: 90px. Icon optional (left of label). 2px bottom border for active indicator.

**Content:** Loaded via HTMX on tab click. Preserves active tab state in URL hash or query param.

**Responsive:** Overflow tabs scroll horizontally on mobile (with fade indicators at edges).

**Do:** Use for 3-8 related views · Preserve active tab in URL · Scroll overflow on mobile · Show clear active indicator

**Don't:** Use for >8 tabs · Use as primary navigation (use TopAppBar) · Omit URL state preservation
